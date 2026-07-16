# src/api.py: Provide public data, ROI, and profile functions for notebook validation.

def load_data(data_path, rotation):
    """Load a rotated 2D grayscale MIM image with source metadata."""
    import os

    import numpy as np
    import tifffile

    try:
        path = os.fspath(data_path)
    except TypeError as error:
        raise ValueError(f"Invalid data path: {data_path!r}") from error

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Data path does not exist: {path}")
    if rotation not in (-90, 0, 90):
        raise ValueError(
            f"Unsupported rotation for data path {path}: {rotation}. "
            "Supported values are -90, 0, and 90."
        )

    try:
        image = np.asarray(tifffile.imread(path))
    except Exception as error:
        raise ValueError(f"Unable to read 2D grayscale image: {path}") from error

    if image.ndim != 2:
        raise ValueError(
            f"Expected a 2D grayscale image at {path}, but received shape {image.shape}."
        )
    if image.shape[0] <= 0 or image.shape[1] <= 0:
        raise ValueError(f"Image has an invalid shape at {path}: {image.shape}.")
    if not np.isfinite(image).all():
        raise ValueError(f"Image contains non-finite values: {path}")

    if rotation == 90:
        image = np.rot90(image, k=1)
    elif rotation == -90:
        image = np.rot90(image, k=-1)
    else:
        image = image.copy()

    return {
        "data_path": path,
        "source_filename": os.path.basename(path),
        "condition": os.path.basename(os.path.dirname(path)),
        "sample_id": os.path.basename(path)[:16],
        "rotation": rotation,
        "image": image,
    }


def create_data(output_dir, num_data=1, seed=42):
    """Create reproducible TIFF-backed MIM samples with periodic line artifacts."""
    import os

    import numpy as np
    import tifffile

    try:
        output_dir = os.path.abspath(os.fspath(output_dir))
        num_data = int(num_data)
        seed = int(seed)
    except (TypeError, ValueError) as error:
        raise ValueError("output_dir, num_data, and seed must be valid values.") from error
    if num_data <= 0:
        raise ValueError(f"num_data must be greater than zero: {num_data}.")

    os.makedirs(output_dir, exist_ok=True)
    image_height = 1404
    image_width = 648
    y_position = np.arange(image_height, dtype=np.float64)[:, np.newaxis]
    x_position = np.arange(image_width, dtype=np.float64)[np.newaxis, :]
    random_generator = np.random.default_rng(seed)
    data_paths = []
    created_paths = []
    samples = []

    for index in range(num_data):
        horizontal_period_px = 43 + (index % 4) * 7
        vertical_period_px = 29 + (index % 3) * 6
        horizontal_phase = random_generator.uniform(0.0, 2.0 * np.pi)
        vertical_phase = random_generator.uniform(0.0, 2.0 * np.pi)
        sample_id = f"SYNTH{seed % 100000000:08d}{index + 1:03d}"
        data_path = os.path.join(output_dir, f"{sample_id}_periodic.mim")

        if not os.path.isfile(data_path):
            background = (
                500.0
                + 12.0 * np.sin(2.0 * np.pi * y_position / image_height)
                + 8.0 * np.cos(2.0 * np.pi * x_position / image_width)
            )
            horizontal_lines = 22.0 * np.sin(
                2.0 * np.pi * y_position / horizontal_period_px + horizontal_phase
            )
            vertical_lines = 16.0 * np.sin(
                2.0 * np.pi * x_position / vertical_period_px + vertical_phase
            )
            fiducial = -380.0 * np.exp(
                -(
                    ((x_position - image_width * 0.95) / 11.0) ** 2
                    + ((y_position - image_height * 0.50) / 18.0) ** 2
                )
            )
            noise = random_generator.normal(0.0, 2.0, (image_height, image_width))
            image = np.clip(
                np.rint(background + horizontal_lines + vertical_lines + fiducial + noise),
                0,
                np.iinfo(np.uint16).max,
            ).astype(np.uint16)
            tifffile.imwrite(data_path, image, photometric="minisblack", metadata=None)
            created_paths.append(data_path)

        data_paths.append(data_path)
        samples.append(
            {
                "data_path": data_path,
                "sample_id": sample_id,
                "image_shape": (image_height, image_width),
                "dtype": "uint16",
                "horizontal_period_px": horizontal_period_px,
                "vertical_period_px": vertical_period_px,
                "created": data_path in created_paths,
            }
        )

    return {
        "output_dir": output_dir,
        "seed": seed,
        "data_paths": data_paths,
        "created_paths": created_paths,
        "samples": samples,
    }


def show_data(data_path, rotation):
    """Return a grayscale overview figure without opening a UI window."""
    import matplotlib.pyplot as plt

    image_data = load_data(data_path, rotation)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(image_data["image"], cmap="gray")
    ax.set_title(image_data["source_filename"])
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def load_roi(data_path, rotation, roi):
    """Return one validated normalized ROI crop and its pixel bounds."""
    image_data = load_data(data_path, rotation)

    if not isinstance(roi, dict):
        raise ValueError(
            f"ROI for data path {image_data['data_path']} must be a dictionary."
        )

    required_keys = ("key", "name", "color", "xmin", "xmax", "ymin", "ymax")
    missing_keys = [key for key in required_keys if key not in roi]
    if missing_keys:
        raise ValueError(
            f"ROI for data path {image_data['data_path']} is missing keys: "
            f"{', '.join(missing_keys)}."
        )

    roi_key = str(roi["key"])
    try:
        normalized_roi = {
            "key": roi_key,
            "name": str(roi["name"]),
            "color": str(roi["color"]),
            "xmin": float(roi["xmin"]),
            "xmax": float(roi["xmax"]),
            "ymin": float(roi["ymin"]),
            "ymax": float(roi["ymax"]),
        }
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"ROI {roi_key!r} has non-numeric normalized bounds for "
            f"data path {image_data['data_path']}."
        ) from error

    xmin = normalized_roi["xmin"]
    xmax = normalized_roi["xmax"]
    ymin = normalized_roi["ymin"]
    ymax = normalized_roi["ymax"]
    if not (0 <= xmin < xmax <= 1 and 0 <= ymin < ymax <= 1):
        raise ValueError(
            f"Invalid ROI {roi_key!r} for data path {image_data['data_path']}: "
            "bounds must satisfy 0 <= xmin < xmax <= 1 and "
            "0 <= ymin < ymax <= 1."
        )

    image_height, image_width = image_data["image"].shape
    x0 = int(image_width * xmin)
    x1 = int(image_width * xmax)
    y0 = int(image_height * ymin)
    y1 = int(image_height * ymax)
    if x1 <= x0 or y1 <= y0 or x1 > image_width or y1 > image_height:
        raise ValueError(
            f"ROI {roi_key!r} is outside image bounds for data path "
            f"{image_data['data_path']}."
        )

    width = x1 - x0
    height = y1 - y0
    return {
        "image_data": image_data,
        "roi": normalized_roi,
        "pixel_bounds": (x0, y0, width, height),
        "crop": image_data["image"][y0:y1, x0:x1],
    }


def show_roi(data_path, rotation, roi):
    """Return an overview figure with one normalized ROI overlay."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    roi_data = load_roi(data_path, rotation, roi)
    x0, y0, width, height = roi_data["pixel_bounds"]
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(roi_data["image_data"]["image"], cmap="gray")
    ax.add_patch(
        Rectangle(
            (x0, y0),
            width,
            height,
            fill=False,
            edgecolor=roi_data["roi"]["color"],
            linewidth=2,
        )
    )
    ax.text(
        x0,
        max(0, y0 - 8),
        roi_data["roi"]["name"],
        color=roi_data["roi"]["color"],
    )
    ax.set_title(roi_data["image_data"]["source_filename"])
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def load_profile(
    data_path,
    rotation,
    roi,
    direction,
    *,
    image_width_mm,
    image_height_mm,
    average_filter_size,
    reference_filter_size,
    minimum_peak_width_mm=0.1,
    scan_width_mm=3.0,
):
    """Return one direction-specific profile, scale, and P2V summary."""
    import numpy as np
    from scipy.ndimage import uniform_filter
    from scipy.signal import find_peaks

    if direction not in ("horizontal", "vertical"):
        raise ValueError(
            f"Unsupported direction for data path {data_path}: {direction!r}. "
            "Supported values are 'horizontal' and 'vertical'."
        )

    try:
        image_width_mm = float(image_width_mm)
        image_height_mm = float(image_height_mm)
        average_filter_size = int(average_filter_size)
        reference_filter_size = int(reference_filter_size)
        minimum_peak_width_mm = float(minimum_peak_width_mm)
        scan_width_mm = float(scan_width_mm)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid profile options for data path {data_path}, direction {direction}."
        ) from error

    if (
        not np.isfinite(image_width_mm)
        or not np.isfinite(image_height_mm)
        or image_width_mm <= 0
        or image_height_mm <= 0
    ):
        raise ValueError(
            f"Image dimensions must be finite values greater than zero for "
            f"data path {data_path}, direction {direction}."
        )
    if average_filter_size <= 0 or reference_filter_size <= 0:
        raise ValueError(
            f"Filter sizes must be positive integers for data path {data_path}, "
            f"direction {direction}."
        )
    if (
        not np.isfinite(minimum_peak_width_mm)
        or not np.isfinite(scan_width_mm)
        or minimum_peak_width_mm <= 0
        or scan_width_mm <= 0
    ):
        raise ValueError(
            f"P2V widths must be finite values greater than zero for data path "
            f"{data_path}, direction {direction}."
        )

    roi_data = load_roi(data_path, rotation, roi)
    roi_key = roi_data["roi"]["key"]
    image_float = roi_data["image_data"]["image"].astype(np.float64)
    image_blur = uniform_filter(image_float, size=average_filter_size, mode="reflect")
    image_reference = uniform_filter(
        image_float,
        size=reference_filter_size,
        mode="reflect",
    )
    x0, y0, width, height = roi_data["pixel_bounds"]
    roi_blur = image_blur[y0:y0 + height, x0:x0 + width]
    roi_reference = image_reference[y0:y0 + height, x0:x0 + width]
    image_height_px, image_width_px = image_float.shape

    if direction == "horizontal":
        blur_profile = roi_blur.mean(axis=1)
        reference_profile = roi_reference.mean(axis=1)
        position_axis = "y"
        start_pixel = y0
        pixel_to_mm = image_height_mm / image_height_px
    else:
        blur_profile = roi_blur.mean(axis=0)
        reference_profile = roi_reference.mean(axis=0)
        position_axis = "x"
        start_pixel = x0
        pixel_to_mm = image_width_mm / image_width_px

    if blur_profile.size < 2:
        raise ValueError(
            f"Profile is too short for data path {data_path}, ROI {roi_key!r}, "
            f"direction {direction}."
        )

    profile_percent = np.divide(
        100.0 * (blur_profile - reference_profile),
        reference_profile,
        out=np.full(blur_profile.shape, np.nan, dtype=np.float64),
        where=reference_profile != 0,
    )
    if not np.isfinite(profile_percent).all():
        raise ValueError(
            f"Profile contains non-finite values for data path {data_path}, "
            f"ROI {roi_key!r}, direction {direction}."
        )

    position_pixel = np.arange(profile_percent.size, dtype=np.float64) + start_pixel
    position_mm = position_pixel * pixel_to_mm
    minimum_width_pixels = max(1.0, minimum_peak_width_mm / pixel_to_mm)
    peak_indices, _ = find_peaks(profile_percent, width=minimum_width_pixels)
    valley_indices, _ = find_peaks(-profile_percent, width=minimum_width_pixels)
    peak_to_valley_values = []
    for peak_index in peak_indices:
        nearby_valleys = valley_indices[
            np.abs(peak_index - valley_indices) * pixel_to_mm < scan_width_mm
        ][:10]
        if nearby_valleys.size:
            peak_to_valley_values.append(
                float(profile_percent[peak_index] - np.min(profile_percent[nearby_valleys]))
            )

    return {
        "roi_data": roi_data,
        "direction": direction,
        "position_axis": position_axis,
        "position_pixel": position_pixel,
        "position_mm": position_mm,
        "blur_profile": blur_profile,
        "reference_profile": reference_profile,
        "profile_percent": profile_percent,
        "pixel_to_mm": pixel_to_mm,
        "peak_count": int(len(peak_indices)),
        "matched_peak_count": len(peak_to_valley_values),
        "max_peak_to_valley": (
            float(max(peak_to_valley_values)) if peak_to_valley_values else 0.0
        ),
        "avg_peak_to_valley": (
            float(np.mean(peak_to_valley_values)) if peak_to_valley_values else 0.0
        ),
        "minimum_peak_width_mm": minimum_peak_width_mm,
        "scan_width_mm": scan_width_mm,
    }


def show_profile(data_path, rotation, roi, direction, **profile_options):
    """Return a profile figure and P2V summary without opening a UI window."""
    import matplotlib.pyplot as plt

    result = load_profile(data_path, rotation, roi, direction, **profile_options)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(
        result["position_mm"],
        result["profile_percent"],
        color=result["roi_data"]["roi"]["color"],
    )
    ax.set_xlabel(f"{result['position_axis']} position (mm)")
    ax.set_ylabel("Profile percent")
    ax.set_title(
        f"{result['roi_data']['image_data']['source_filename']} | "
        f"{result['roi_data']['roi']['key']} | {result['direction']} | "
        f"P2V max={result['max_peak_to_valley']:.6g}, "
        f"avg={result['avg_peak_to_valley']:.6g}"
    )
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
