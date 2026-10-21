from src.anomaly_detection.data.common.dataset import AnomalyTransform, FolderAnomalyDataset


class BTADDataset(FolderAnomalyDataset):
    normal_name = "ok"
    extensions = (".bmp", ".png")
    mask_suffix = ""
    mask_extensions = (".png", ".bmp")

    def __init__(self, root, train=True, category="01", transform=None):
        if category not in ("01", "02", "03"):
            raise ValueError("BTAD category must be '01', '02', or '03'")
        super().__init__(root, train=train, category=category, transform=transform)


class BTADTransform(AnomalyTransform):
    pass
