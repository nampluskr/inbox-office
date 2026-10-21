import os

import torch


class Predictor:
    def __init__(
        self,
        model,
        preprocess=None,
        postprocess=None,
        device="cpu",
    ):
        self.device = torch.device(device)
        self.model = model.to(self.device).eval()
        self.preprocess = preprocess
        self.postprocess = postprocess

    def load_weights(self, path):
        state_dict = torch.load(path, map_location="cpu", weights_only=True)
        self.model.load_state_dict(state_dict, strict=True)
        self.model.eval()

    def save_weights(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def predict(self, image):
        tensor = self.preprocess(image) if self.preprocess is not None else image
        if not isinstance(tensor, torch.Tensor) or tensor.ndim != 3:
            raise ValueError("Expected a CHW tensor; supply preprocess for raw images")
        return self.predict_batch(tensor.unsqueeze(0))

    @torch.inference_mode()
    def predict_batch(self, batch):
        # Prepared batches bypass sample preprocessing.
        if not isinstance(batch, torch.Tensor) or batch.ndim != 4 or not batch.is_floating_point():
            raise ValueError("Expected an already transformed floating-point NCHW tensor")
        self.model.eval()
        outputs = self.model(batch.to(self.device))
        return self.postprocess(outputs) if self.postprocess is not None else outputs
