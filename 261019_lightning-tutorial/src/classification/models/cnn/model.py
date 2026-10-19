import torch
import torch.nn as nn
import torchvision.models as tvm


class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=2):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False,
        )
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x


class CustomCnnBackbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.stage1 = ConvBlock(3, 32)
        self.stage2 = ConvBlock(32, 64)
        self.stage3 = ConvBlock(64, 128)
        self.stage4 = ConvBlock(128, 256)
        self.stage5 = ConvBlock(256, 512)

    def forward(self, images):
        c1 = self.stage1(images)
        c2 = self.stage2(c1)
        c3 = self.stage3(c2)
        c4 = self.stage4(c3)
        c5 = self.stage5(c4)
        return {"final": c5, "stages": [c1, c2, c3, c4, c5]}


class ClassificationModel(nn.Module):
    def __init__(self, backbone="resnet50", num_classes=10, weights_path=None):
        super().__init__()
        if backbone not in ("custom", "resnet18", "resnet50", "efficientnet_b0"):
            raise ValueError(f"Unsupported backbone: {backbone!r}")
        if (
            not isinstance(num_classes, int)
            or isinstance(num_classes, bool)
            or num_classes < 1
        ):
            raise ValueError("num_classes must be a positive integer")
        self.backbone_name = backbone

        if backbone == "custom":
            if weights_path is not None:
                raise ValueError(
                    "custom does not accept backbone weights; "
                    "use load_state_dict for trained weights"
                )
            self.backbone = CustomCnnBackbone()
            self.pool = nn.AdaptiveAvgPool2d(1)
            self.classifier = nn.Linear(512, num_classes)
            return

        if backbone == "resnet18":
            self.backbone = tvm.resnet18(weights=None)
        elif backbone == "resnet50":
            self.backbone = tvm.resnet50(weights=None)
        else:
            self.backbone = tvm.efficientnet_b0(weights=None)

        if weights_path is not None:
            state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
            self.backbone.load_state_dict(state_dict, strict=True)

        # Load ImageNet weights before replacing the original classification head.
        if backbone in ("resnet18", "resnet50"):
            self.backbone.fc = nn.Linear(self.backbone.fc.in_features, num_classes)
        else:
            in_features = self.backbone.classifier[1].in_features
            self.backbone.classifier[1] = nn.Linear(in_features, num_classes)

    def forward(self, images):
        outputs = self.backbone(images)
        if self.backbone_name == "custom":
            features = outputs["final"]
            return self.classifier(self.pool(features).flatten(1))
        return outputs
