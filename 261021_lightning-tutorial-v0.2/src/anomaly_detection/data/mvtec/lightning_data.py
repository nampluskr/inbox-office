from src.anomaly_detection.data.common.lightning_data import AnomalyLitData
from src.anomaly_detection.data.mvtec.dataset import MVTecDataset


class MVTecLitData(AnomalyLitData):
    dataset_class = MVTecDataset
