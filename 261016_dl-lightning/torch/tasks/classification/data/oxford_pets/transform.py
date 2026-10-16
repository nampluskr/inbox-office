import torch
from torchvision.transforms import v2


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class OxfordPetsTransform(v2.Compose):
    def __init__(self, train=False, image_size=224):
        if image_size < 1:
            raise ValueError("image_size must be positive")
        if train:
            operations = [
                v2.RandomResizedCrop(image_size, scale=(0.7, 1.0), antialias=True),
                v2.RandomHorizontalFlip(p=0.5),
            ]
        else:
            operations = [
                v2.Resize(int(image_size * 256 / 224), antialias=True),
                v2.CenterCrop(image_size),
            ]
        operations.extend([
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
        super().__init__(operations)
