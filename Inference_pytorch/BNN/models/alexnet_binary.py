import torch.nn as nn
import torchvision.transforms as transforms
from .binarized_modules import  BinarizeLinear,BinarizeConv2d

__all__ = ['alexnet_binary']

class AlexNetOWT_BN(nn.Module):

    def __init__(self, hwArgs, num_classes=1000):
        super(AlexNetOWT_BN, self).__init__()
        self.ratioInfl=1
        self.features = nn.Sequential(
            BinarizeConv2d(3, int(64*self.ratioInfl), hwArgs=hwArgs, name="Conv0_", kernel_size=11, stride=4, padding=2),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.BatchNorm2d(int(64*self.ratioInfl)),
            nn.Hardtanh(inplace=True),

            BinarizeConv2d(int(64*self.ratioInfl), int(192*self.ratioInfl), hwArgs=hwArgs, name="Conv1_", kernel_size=5, padding=2),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.BatchNorm2d(int(192*self.ratioInfl)),
            nn.Hardtanh(inplace=True),

            BinarizeConv2d(int(192*self.ratioInfl), int(384*self.ratioInfl), hwArgs=hwArgs, name="Conv2_", kernel_size=3, padding=1),
            nn.BatchNorm2d(int(384*self.ratioInfl)),
            nn.Hardtanh(inplace=True),

            BinarizeConv2d(int(384*self.ratioInfl), int(384*self.ratioInfl), hwArgs=hwArgs, name="Conv3_", kernel_size=3, padding=1),
            nn.BatchNorm2d(int(384*self.ratioInfl)),
            nn.Hardtanh(inplace=True),

            BinarizeConv2d(int(384*self.ratioInfl), 256, hwArgs=hwArgs, name="Conv4_", kernel_size=3, padding=1),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.BatchNorm2d(256),
            nn.Hardtanh(inplace=True)

        )
        self.classifier = nn.Sequential(
            BinarizeLinear(256 * 6 * 6, 4096, hwArgs=hwArgs, name="FC0_"),
            nn.BatchNorm1d(4096),
            nn.Hardtanh(inplace=True),
            #nn.Dropout(0.5),
            BinarizeLinear(4096, 4096, hwArgs=hwArgs, name="FC1_"),
            nn.BatchNorm1d(4096),
            nn.Hardtanh(inplace=True),
            #nn.Dropout(0.5),
            BinarizeLinear(4096, num_classes, hwArgs=hwArgs, name="FC2_"),
            nn.BatchNorm1d(num_classes),
            nn.LogSoftmax()
        )

        #self.regime = {
        #    0: {'optimizer': 'SGD', 'lr': 1e-2,
        #        'weight_decay': 5e-4, 'momentum': 0.9},
        #    10: {'lr': 5e-3},
        #    15: {'lr': 1e-3, 'weight_decay': 0},
        #    20: {'lr': 5e-4},
        #    25: {'lr': 1e-4}
        #}
        self.regime = {
            0: {'optimizer': 'Adam', 'lr': 5e-3},
            20: {'lr': 1e-3},
            30: {'lr': 5e-4},
            35: {'lr': 1e-4},
            40: {'lr': 1e-5}
        }
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])
        self.input_transform = {
            'train': transforms.Compose([
                transforms.Scale(256),
                transforms.RandomCrop(224),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                normalize
            ]),
            'eval': transforms.Compose([
                transforms.Scale(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                normalize
            ])
        }

    def forward(self, x):
        x = self.features(x)
        x = x.view(-1, 256 * 6 * 6)
        x = self.classifier(x)
        return x


def alexnet_binary(hwArgs, **kwargs):
    num_classes = getattr(kwargs, 'num_classes', 1000)
    print("num_classes = ", num_classes)
    return AlexNetOWT_BN(hwArgs, num_classes)
