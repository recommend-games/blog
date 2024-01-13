from pathlib import Path
from torch import nn
from torch import optim
from torch.utils.data import DataLoader
from torchvision.models import resnet50, ResNet50_Weights

from cover_classifier.data import BoardGameDataset


def train(data_dir: str | Path, images_dir: str | Path):
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)

    data_dir = Path(data_dir).resolve()
    images_dir = Path(images_dir).resolve()

    dataset = BoardGameDataset(
        games_file=data_dir / "scraped" / "bgg_GameItem.jl",
        types_file=data_dir / "scraped" / "bgg_GameType.csv",
        image_root_dir=images_dir,
        transform=weights.transforms,
    )
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

    num_classes = len(dataset.classes)
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 10
    for epoch in range(num_epochs):
        for inputs, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels.int())
            loss.backward()
            optimizer.step()
