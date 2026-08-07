import csv
import os
from glob import glob

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import tifffile
from scipy.signal import find_peaks


def _direction_label(direction):
    """Return the user-visible analyzed line direction."""
    return "Horizontal Lines" if direction == "horizontal" else "Vertical Lines"


def create_data(output_dir, width, height, num_data=1, seed=42):
    """Create reproducible TIFF-backed MIM samples with periodic line artifacts."""
    os.makedirs(output_dir, exist_ok=True)
    y = np.arange(height, dtype=np.float64)[:, np.newaxis]
    x = np.arange(width, dtype=np.float64)[np.newaxis, :]

    for index in range(num_data):
        h_period = 43 + (index % 4) * 7
        v_period = 29 + (index % 3) * 6
        sample_id = f"SYNTH{seed % 100000000:08d}{index + 1:03d}"
        data_path = os.path.join(output_dir, f"{sample_id}_periodic.mim")

        if not os.path.isfile(data_path):
            rng = np.random.default_rng([seed, index])
            h_phase = rng.uniform(0.0, 2.0 * np.pi)
            v_phase = rng.uniform(0.0, 2.0 * np.pi)
            background = 500.0 + 12.0 * np.sin(2.0 * np.pi * y / height) \
                + 8.0 * np.cos(2.0 * np.pi * x / width)
            h_lines = 22.0 * np.sin(2.0 * np.pi * y / h_period + h_phase)
            v_lines = 16.0 * np.sin(2.0 * np.pi * x / v_period + v_phase)
            fiducial = -380.0 * np.exp(-(((x - width * 0.50) / 18.0) ** 2 \
                    + ((y - height * 0.05) / 11.0) ** 2))
            noise = rng.normal(0.0, 2.0, (height, width))
            data = np.clip(np.rint(background + h_lines + v_lines + fiducial + noise), 0,
                np.iinfo(np.uint16).max).astype(np.uint16)
            tifffile.imwrite(data_path, data, photometric="minisblack", metadata=None)


def get_paths(data_dir, pattern="*.mim"):
    """Recursively find data file paths under data_dir matching a glob pattern."""
    return glob(os.path.join(data_dir, "**", pattern), recursive=True)


def get_data(data_path, rotation=0, roi=None):
    """Load a TIFF-backed MIM sample cropped to a fractional ROI."""
    data = tifffile.imread(data_path)
    if rotation == 90:
        data = np.rot90(data, k=1)
    elif rotation == -90:
        data = np.rot90(data, k=-1)
    else:
        data = data.copy()

    if roi is None:
        return data

    height, width = data.shape[:2]
    xmin = round(roi["xmin"] * width)
    xmax = round(roi["xmax"] * width)
    ymin = round(roi["ymin"] * height)
    ymax = round(roi["ymax"] * height)
    return data[ymin:ymax, xmin:xmax]


def show_data(data_path, rotation=0, roi=None, save_path=None):
    """Show a TIFF-backed MIM sample with ROI rectangles overlaid."""
    data = get_data(data_path, rotation=rotation)
    height, width = data.shape[:2]

    fig, ax = plt.subplots()
    ax.imshow(data, cmap="gray")

    for roi_ in roi or []:
        xmin = roi_["xmin"] * width
        xmax = roi_["xmax"] * width
        ymin = roi_["ymin"] * height
        ymax = roi_["ymax"] * height
        ax.add_patch(Rectangle(
            (xmin, ymin), xmax - xmin, ymax - ymin, linewidth=2,
            facecolor="none", edgecolor=roi_.get("color", "tab:red"), label=roi_.get("label")))

    if roi:
        ax.legend()
    if save_path is not None:
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        fig.savefig(save_path)
    plt.show()
    return fig, ax


def get_profile(data_path, rotation=0, roi=None, direction="horizontal", px_to_mm=None):
    """Load 1-D intensity profile(s) averaged along rows or columns for FFT analysis."""
    if isinstance(roi, list):
        return [
            get_profile(data_path, rotation=rotation, roi=roi_, direction=direction, px_to_mm=px_to_mm)
            for roi_ in roi
        ]

    data = get_data(data_path, rotation=rotation, roi=roi)
    y = data.mean(axis=1) if direction == "horizontal" else data.mean(axis=0)
    positions = np.arange(y.size)
    if px_to_mm is not None:
        positions = positions * px_to_mm
    return list(zip(positions, y))


def show_profile(data_path, rotation=0, roi=None, direction="horizontal", figsize=(6, 3), save_path=None, px_to_mm=None):
    """Show the 1-D intensity profile(s) used for FFT analysis."""
    roi_list = roi if isinstance(roi, list) else [roi]
    profiles = get_profile(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    profiles = profiles if isinstance(roi, list) else [profiles]

    fig, ax = plt.subplots(figsize=figsize)
    for roi_, points in zip(roi_list, profiles):
        color = roi_.get("color") if roi_ else None
        label = roi_.get("label") if roi_ else None
        positions, y = zip(*points)
        ax.plot(positions, y, color=color, label=label)
    ax.set_xlabel("Position (mm)" if px_to_mm is not None else "Position (px)")
    ax.set_ylabel("Mean intensity")
    ax.set_title(f"{_direction_label(direction)} - Profile")
    if any(roi__.get("label") for roi__ in roi_list if roi__):
        ax.legend()
    if save_path is not None:
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        fig.savefig(save_path)
    plt.show()
    return fig, ax


def get_profile_peaks(data_path, rotation=0, roi=None, direction="horizontal", px_to_mm=None):
    """Find local maxima (peaks) and minima (valleys) in the 1-D intensity profile(s)."""
    if isinstance(roi, list):
        return [
            get_profile_peaks(data_path, rotation=rotation, roi=roi_, direction=direction, px_to_mm=px_to_mm)
            for roi_ in roi
        ]

    points = get_profile(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    positions, y = zip(*points)
    positions, y = np.array(positions), np.array(y)

    peak_indices, _ = find_peaks(y)
    valley_indices, _ = find_peaks(-y)
    peaks = list(zip(positions[peak_indices], y[peak_indices]))
    valleys = list(zip(positions[valley_indices], y[valley_indices]))
    return peaks, valleys


def get_peak2valley(data_path, rotation=0, roi=None, direction="horizontal", px_to_mm=None):
    """Compute adjacent peak-to-valley amplitude differences in the profile."""
    if isinstance(roi, list):
        return [
            get_peak2valley(data_path, rotation=rotation, roi=roi_, direction=direction, px_to_mm=px_to_mm)
            for roi_ in roi
        ]

    peaks, valleys = get_profile_peaks(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    peak_positions, peak_y = zip(*peaks) if peaks else ((), ())
    valley_positions, valley_y = zip(*valleys) if valleys else ((), ())

    positions = np.concatenate([peak_positions, valley_positions])
    y = np.concatenate([peak_y, valley_y])
    is_peak = np.concatenate([
        np.ones(len(peak_positions), dtype=bool),
        np.zeros(len(valley_positions), dtype=bool),
    ])
    order = np.argsort(positions)
    y, is_peak = y[order], is_peak[order]

    diffs = np.abs(np.diff(y))
    adjacent_mask = is_peak[:-1] != is_peak[1:]
    return list(diffs[adjacent_mask])


def show_profile_peaks(data_path, rotation=0, roi=None, direction="horizontal", figsize=(6, 3), save_path=None, px_to_mm=None):
    """Show the 1-D intensity profile(s) with peak/valley positions marked."""
    roi_list = roi if isinstance(roi, list) else [roi]
    profiles = get_profile(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    profiles = profiles if isinstance(roi, list) else [profiles]
    peaks_valleys = get_profile_peaks(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    peaks_valleys = peaks_valleys if isinstance(roi, list) else [peaks_valleys]

    fig, ax = plt.subplots(figsize=figsize)
    for roi_, points, (peaks, valleys) in zip(roi_list, profiles, peaks_valleys):
        color = roi_.get("color") if roi_ else None
        label = roi_.get("label") if roi_ else None
        positions, y = zip(*points)
        line, = ax.plot(positions, y, color=color, label=label)
        if peaks:
            peak_positions, peak_y = zip(*peaks)
            ax.scatter(peak_positions, peak_y, color=line.get_color(), marker="^", zorder=3)
        if valleys:
            valley_positions, valley_y = zip(*valleys)
            ax.scatter(valley_positions, valley_y, color=line.get_color(), marker="v", zorder=3)
    ax.set_xlabel("Position (mm)" if px_to_mm is not None else "Position (px)")
    ax.set_ylabel("Mean intensity")
    ax.set_title(f"{_direction_label(direction)} - Profile Peaks")
    if any(roi__.get("label") for roi__ in roi_list if roi__):
        ax.legend()
    if save_path is not None:
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        fig.savefig(save_path)
    plt.show()
    return fig, ax


def get_fft(data_path, rotation=0, roi=None, direction="horizontal", px_to_mm=None):
    """Compute the amplitude spectrum of the 1-D intensity profile(s) for FFT analysis."""
    if isinstance(roi, list):
        return [
            get_fft(data_path, rotation=rotation, roi=roi_, direction=direction, px_to_mm=px_to_mm)
            for roi_ in roi
        ]

    points = get_profile(data_path, rotation=rotation, roi=roi, direction=direction)
    _, y = zip(*points)
    y = np.array(y)
    y = y - y.mean()
    n = y.size

    spectrum = np.abs(np.fft.rfft(y)) / n
    freq = np.fft.rfftfreq(n)
    if px_to_mm is not None:
        freq = freq / px_to_mm
    return list(zip(freq, spectrum))


def show_fft(data_path, rotation=0, roi=None, direction="horizontal", figsize=(6, 3), save_path=None, px_to_mm=None):
    """Show the amplitude spectrum of the 1-D intensity profile(s) for FFT analysis."""
    roi_list = roi if isinstance(roi, list) else [roi]
    spectra = get_fft(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    spectra = spectra if isinstance(roi, list) else [spectra]

    fig, ax = plt.subplots(figsize=figsize)
    for roi_, points in zip(roi_list, spectra):
        color = roi_.get("color") if roi_ else None
        label = roi_.get("label") if roi_ else None
        freq, spectrum = zip(*points)
        ax.plot(freq, spectrum, color=color, label=label)
    ax.set_xlabel("Frequency (cycles/mm)" if px_to_mm is not None else "Frequency (cycles/px)")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"{_direction_label(direction)} - FFT Intensity")
    if any(roi__.get("label") for roi__ in roi_list if roi__):
        ax.legend()
    if save_path is not None:
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        fig.savefig(save_path)
    plt.show()
    return fig, ax


def get_fft_peaks(data_path, rotation=0, roi=None, direction="horizontal", num_peaks=1, px_to_mm=None):
    """Find the dominant frequency peak(s) in the amplitude spectrum for FFT analysis."""
    if isinstance(roi, list):
        return [
            get_fft_peaks(
                data_path, rotation=rotation, roi=roi_, direction=direction,
                num_peaks=num_peaks, px_to_mm=px_to_mm,
            )
            for roi_ in roi
        ]

    points = get_fft(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    freq, spectrum = zip(*points)
    freq, spectrum = np.array(freq), np.array(spectrum)

    order = np.argsort(spectrum[1:])[::-1] + 1
    indices = order[:num_peaks]
    return list(zip(freq[indices], spectrum[indices]))


def show_fft_peaks(data_path, rotation=0, roi=None, direction="horizontal", num_peaks=1, figsize=(6, 3), save_path=None, px_to_mm=None):
    """Show the amplitude spectrum with dominant frequency peak(s) marked for FFT analysis."""
    roi_list = roi if isinstance(roi, list) else [roi]
    spectra = get_fft(data_path, rotation=rotation, roi=roi, direction=direction, px_to_mm=px_to_mm)
    spectra = spectra if isinstance(roi, list) else [spectra]
    peaks = get_fft_peaks(
        data_path, rotation=rotation, roi=roi, direction=direction,
        num_peaks=num_peaks, px_to_mm=px_to_mm,
    )
    peaks = peaks if isinstance(roi, list) else [peaks]

    fig, ax = plt.subplots(figsize=figsize)
    for roi_, points, peak_points in zip(roi_list, spectra, peaks):
        color = roi_.get("color") if roi_ else None
        label = roi_.get("label") if roi_ else None
        freq, spectrum = zip(*points)
        line, = ax.plot(freq, spectrum, color=color, label=label)
        if peak_points:
            peak_freq, peak_spectrum = zip(*peak_points)
            ax.scatter(peak_freq, peak_spectrum, color=line.get_color(), marker="x", zorder=3)
    ax.set_xlabel("Frequency (cycles/mm)" if px_to_mm is not None else "Frequency (cycles/px)")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"{_direction_label(direction)} - FFT Peaks")
    if any(roi__.get("label") for roi__ in roi_list if roi__):
        ax.legend()
    if save_path is not None:
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        fig.savefig(save_path)
    plt.show()
    return fig, ax


def _write_csv(path, header, rows):
    """Write rows to a CSV file, creating parent directories as needed."""
    save_dir = os.path.dirname(path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def save_profile_csv(points, path, px_to_mm=None):
    """Save get_profile() result(s) to a CSV file."""
    x_header = "x_mm" if px_to_mm is not None else "x_px"
    if points and isinstance(points[0], list):
        header = ["roi_index", x_header, "y"]
        rows = [(i, x, y) for i, roi_points in enumerate(points) for x, y in roi_points]
    else:
        header = [x_header, "y"]
        rows = points
    _write_csv(path, header, rows)


def save_profile_peaks_csv(peaks, valleys, path):
    """Save get_profile_peaks() result(s) to a CSV file."""
    if peaks and isinstance(peaks[0], list):
        header = ["roi_index", "kind", "x", "y"]
        rows = []
        for i, (roi_peaks, roi_valleys) in enumerate(zip(peaks, valleys)):
            entries = [(x, y, "peak") for x, y in roi_peaks] + [(x, y, "valley") for x, y in roi_valleys]
            entries.sort(key=lambda entry: entry[0])
            rows.extend((i, kind, x, y) for x, y, kind in entries)
    else:
        header = ["kind", "x", "y"]
        entries = [(x, y, "peak") for x, y in peaks] + [(x, y, "valley") for x, y in valleys]
        entries.sort(key=lambda entry: entry[0])
        rows = [(kind, x, y) for x, y, kind in entries]
    _write_csv(path, header, rows)


def save_peak2valley_csv(diffs, path):
    """Save get_peak2valley() result(s) to a CSV file."""
    if diffs and isinstance(diffs[0], list):
        header = ["roi_index", "index", "diff"]
        rows = [(i, j, diff) for i, roi_diffs in enumerate(diffs) for j, diff in enumerate(roi_diffs)]
    else:
        header = ["index", "diff"]
        rows = [(j, diff) for j, diff in enumerate(diffs)]
    _write_csv(path, header, rows)


def save_fft_csv(points, path, px_to_mm=None):
    """Save get_fft() result(s) to a CSV file."""
    freq_header = "freq_mm" if px_to_mm is not None else "freq_px"
    if points and isinstance(points[0], list):
        header = ["roi_index", freq_header, "amplitude"]
        rows = [(i, freq, amp) for i, roi_points in enumerate(points) for freq, amp in roi_points]
    else:
        header = [freq_header, "amplitude"]
        rows = points
    _write_csv(path, header, rows)


def save_fft_peaks_csv(points, path, px_to_mm=None):
    """Save get_fft_peaks() result(s) to a CSV file."""
    save_fft_csv(points, path, px_to_mm=px_to_mm)
