import torch
from torchvision import tv_tensors
from torchvision.transforms import v2
from torchvision.transforms.v2 import functional as functional


class MVTecTransform:
    def __init__(self, image_size: int = 256):
        self.compose = v2.Compose([
            v2.Resize((image_size, image_size), antialias=True),
            v2.ToDtype({tv_tensors.Image: torch.float32, tv_tensors.Mask: torch.int64}, scale=True),
            v2.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ])

    def __call__(self, image, target=None):
        image = functional.to_image(image)
        if target is None:
            return self.compose(image)
        if not target:
            return self.compose(image), {}
        image, mask = self.compose(image, tv_tensors.Mask(target["mask"]))
        return image, {**target, "mask": mask.to(torch.int64)}
