# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import torch
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from transformers import AdamW, GPT2LMHeadModel, GPT2Tokenizer
import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from transformers import GPT2Tokenizer, GPT2LMHeadModel, AdamW

jupyter_black.load()

# %%
# Load the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Manually set the padding token
tokenizer.pad_token = tokenizer.eos_token


# Define a function to load and tokenize the dataset
def load_and_tokenize_dataset(file_path, tokenizer):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    # Tokenize the dataset
    tokenized_dataset = [
        tensor
        for line in tqdm(lines)
        if (
            tensor := tokenizer(line.strip(), return_tensors="pt")["input_ids"].squeeze(
                dim=0
            )
        ).numel()
        and tensor.dim() == 1
    ]
    return tokenized_dataset


# Load and tokenize your dataset
file_path = "titles.txt"
tokenized_dataset = load_and_tokenize_dataset(file_path, tokenizer)
len(tokenized_dataset)


# %%
def collate_fn(batch):
    # Pad sequences to the same length
    batch_padded = pad_sequence(
        batch,
        batch_first=True,
        padding_value=tokenizer.pad_token_id,
    )
    return batch_padded


class BoardGameTitlesDataset(Dataset):
    def __init__(self, tokenized_dataset):
        self.tokenized_dataset = tokenized_dataset

    def __len__(self):
        return len(self.tokenized_dataset)

    def __getitem__(self, idx):
        return self.tokenized_dataset[idx]


# Create a dataset and dataloader
dataset = BoardGameTitlesDataset(tokenized_dataset)
dataloader = DataLoader(dataset, batch_size=64, shuffle=True, collate_fn=collate_fn)

# %%
# Load the model
model = GPT2LMHeadModel.from_pretrained('gpt2')

# Set the model in training mode
model.train()

# Define optimizer
optimizer = AdamW(model.parameters(), lr=5e-5)

# Training loop
epochs = 3
for epoch in range(epochs):
    for batch in dataloader:
        optimizer.zero_grad()
        outputs = model(batch, labels=batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        print(f'Epoch: {epoch}, Loss: {loss.item()}')

# Save the fine-tuned model
model.save_pretrained('./fine_tuned_gpt2_board_games')
tokenizer.save_pretrained('./fine_tuned_gpt2_board_games')


# %%
# Load the fine-tuned model and tokenizer
model = GPT2LMHeadModel.from_pretrained('./fine_tuned_gpt2_board_games')
tokenizer = GPT2Tokenizer.from_pretrained('./fine_tuned_gpt2_board_games')

# Generate new board game titles
input_text = "Board Game Title: "
input_ids = tokenizer.encode(input_text, return_tensors='pt')
output = model.generate(
    input_ids, 
    max_length=20, 
    num_return_sequences=5, 
    no_repeat_ngram_size=2, 
    early_stopping=True
)

# Decode and print the generated titles
for i, sequence in enumerate(output):
    print(f'Title {i+1}: {tokenizer.decode(sequence, skip_special_tokens=True)}')

