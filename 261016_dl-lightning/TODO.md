## 폴더 구조

```bash
src\
- {task_name}\				# classification, anomaly_detection, gan
  - configs\
     - default.yaml
     - data\{dataset_name}.yaml
     - models\{model_name}.yaml
  - data\{dataset_name}\		# mvtec, visa, btad
     - dataset.py
     - transform.py
  - models\{model_name}\		# stfpm, efficientad
     - model.py
     - loss.py
     - metric.py
     - lightning_module.py
     - lightning_cli.py
- inference\predictor.py
- utils\
  - io.py
  - config.py
```


## 임포트 경로

```python
project_dir = os.path.abspath(os.getcwd())
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
source_dir = os.path.join(project_dir, "src")

sys.path.insert(0, source_dir)

from torch.utils.data import Subset, DataLoader
import lightning.pytorch as pl

from classification.data.cifar10.dataset import CIFAR10Dataset
from classification.data.cifar10.transform import CIFAR10Transform
from classification.models.cnn.model import CNNModel

pl.LightningModle
pl.DataModule
pl.Trainer
pl.seed_everthing
pl.callbacks.ModelCheckpoint
pl.loggers.CSVLogger
```
