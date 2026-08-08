# src/fft.py: GUI-independent file discovery, image loading and analysis API skeleton

import glob
import os

import matplotlib.patches
import numpy as np
import tifffile

ALLOWED_ROTATIONS = (-90, 0, 90, 180)


class Settings:
    """Analysis settings edited from the Settings tab."""

    def __init__(
        self,
        physical_width_mm=0.0,
        physical_height_mm=0.0,
        rotation=0,
        rois=None,
        averaging_band_size_px=0,
        reference_band_size_px=0,
        low_pass_cutoff=0.0,
        high_pass_cutoff=0.0,
        top_k=1,
    ):
        self.physical_width_mm = physical_width_mm
        self.physical_height_mm = physical_height_mm
        self.rotation = rotation
        self.rois = rois if rois is not None else []
        self.averaging_band_size_px = averaging_band_size_px
        self.reference_band_size_px = reference_band_size_px
        self.low_pass_cutoff = low_pass_cutoff
        self.high_pass_cutoff = high_pass_cutoff
        self.top_k = top_k


def find_image_paths(root, pattern="*.mim"):
    """Find image file paths under root matching pattern."""

    return sorted(glob.glob(os.path.join(root, "**", pattern), recursive=True))


def get_image(image_path, rotation=0):
    """Load an image from image_path and rotate it."""

    if rotation not in ALLOWED_ROTATIONS:
        raise ValueError("rotation must be one of %s" % (ALLOWED_ROTATIONS,))
    image = np.asarray(tifffile.imread(image_path))
    if image.ndim != 2:
        raise ValueError("image must be 2D, got shape %s" % (image.shape,))
    if rotation != 0:
        image = np.rot90(image, k=rotation // 90)
    return image


def get_roi(image, roi):
    """Crop the normalized-coordinate roi region from image."""

    raise NotImplementedError("get_roi is not implemented yet")


def compute_raw_profile(roi, direction="horizontal"):
    """Average roi along direction into a raw profile."""

    raise NotImplementedError("compute_raw_profile is not implemented yet")


def compute_norm_profile(raw_profile, averaging_band_size_px, reference_band_size_px):
    """Smooth raw_profile and compute the dL/L(%) profile."""

    raise NotImplementedError("compute_norm_profile is not implemented yet")


def compute_fft_spectrum(profile, px_to_mm=None):
    """Compute the FFT amplitude spectrum of profile."""

    raise NotImplementedError("compute_fft_spectrum is not implemented yet")


def compute_fft_peaks(spectrum, num_peaks=1):
    """Find the top num_peaks peaks in spectrum."""

    raise NotImplementedError("compute_fft_peaks is not implemented yet")


def compute_bandpass_profile(profile, low_pass_cutoff, high_pass_cutoff, px_to_mm=None):
    """Remove frequencies outside the cutoffs and inverse-transform profile."""

    raise NotImplementedError("compute_bandpass_profile is not implemented yet")


def compute_peak2valley(profile):
    """Compute the peak-to-valley amplitude of profile."""

    raise NotImplementedError("compute_peak2valley is not implemented yet")


def show_image(image, roi=None):
    """Display image and roi in a new standalone figure."""

    raise NotImplementedError("show_image is not implemented yet")


def draw_image(ax, image, roi=None):
    """Draw image and roi onto the given Axes."""

    ax.clear()
    ax.imshow(image, cmap="gray")
    if roi is None:
        return
    rois = [roi] if isinstance(roi, dict) else roi
    height, width = image.shape
    for spine in ax.spines.values():
        spine.set_visible(False)
    for item in rois:
        x = item["xmin"] * width
        y = item["ymin"] * height
        w = (item["xmax"] - item["xmin"]) * width
        h = (item["ymax"] - item["ymin"]) * height
        rect = matplotlib.patches.Rectangle(
            (x, y), w, h, fill=False, edgecolor=item.get("color"), linewidth=2, label=item.get("label")
        )
        ax.add_patch(rect)


def show_profiles(profiles, labels=[]):
    """Display one or more profiles in a new standalone figure."""

    raise NotImplementedError("show_profiles is not implemented yet")


def draw_profiles(ax, profiles, labels=[]):
    """Draw one or more profiles onto the given Axes."""

    raise NotImplementedError("draw_profiles is not implemented yet")


def show_spectrums(spectrums, labels=[]):
    """Display one or more spectrums in a new standalone figure."""

    raise NotImplementedError("show_spectrums is not implemented yet")


def draw_spectrums(ax, spectrums, labels=[]):
    """Draw one or more spectrums onto the given Axes."""

    raise NotImplementedError("draw_spectrums is not implemented yet")


def show_spectrum_peaks(spectrum, peaks):
    """Display a spectrum with its peaks in a new standalone figure."""

    raise NotImplementedError("show_spectrum_peaks is not implemented yet")


def draw_spectrum_peaks(ax, spectrum, peaks):
    """Draw a spectrum with its peaks onto the given Axes."""

    raise NotImplementedError("draw_spectrum_peaks is not implemented yet")


def show_peak2valley(profile, peak2valley):
    """Display a profile with its peak-to-valley amplitude in a new standalone figure."""

    raise NotImplementedError("show_peak2valley is not implemented yet")


def draw_peak2valley(ax, profile, peak2valley):
    """Draw a profile with its peak-to-valley amplitude onto the given Axes."""

    raise NotImplementedError("draw_peak2valley is not implemented yet")
