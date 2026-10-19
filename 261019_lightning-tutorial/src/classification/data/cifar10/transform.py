import torch
from torchvision.transforms import v2


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class CIFAR10Transform(v2.Compose):
    def __init__(self, train=False, image_size=224):
        if image_size < 1:
            raise ValueError("image_size must be positive")
        operations = []
        if train:
            operations.extend([v2.RandomCrop(32, padding=4), v2.RandomHorizontalFlip()])
        operations.extend([
            v2.Resize((image_size, image_size), antialias=True),
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])
        super().__init__(operations)
