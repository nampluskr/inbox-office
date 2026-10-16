## 폴더 구조

```
src\
- {task_name}\				# classification, segmentation, detection, anomaly_detection, autoencoder, vae, gan
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
     - lighting_model.py
- utils\
  - seed.py
  - io.py
  - config.py
- lit
```

## 임포트 경로

```
project_dir = os.path.abspath(os.getcwd())
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
source_dir = os.path.join(project_dir, "src")


from src.
```
