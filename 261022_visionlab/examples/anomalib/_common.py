import os

from anomalib.data import MVTecAD


class LocalMVTecAD(MVTecAD):
    # Check local data instead of downloading missing files.
    def prepare_data(self):
        for folder in ("train/good", "test", "ground_truth"):
            path = os.path.join(str(self.root), self.category, folder)
            if not os.path.isdir(path):
                raise FileNotFoundError(path)
