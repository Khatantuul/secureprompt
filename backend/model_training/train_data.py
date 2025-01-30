"""
Generates a dataset for training a model by processing synthetic data and templates.

This script receives synthetic data and templates, tokenizes the templates using the Hugging Face Transformers library,
and labels the tokens that correspond to sensitive data. The resulting dataset is suitable for training a model to
identify sensitive information in text.

The `TrainingTokenDataset` class processes the templates and synthetic data to create the dataset. 

The `print_alignment` function is a helper function that prints the token-label alignment for a specific example in the
dataset, which is useful for debugging and understanding the dataset structure.

Note:
- The dataset is generated for training and evaluation purposes only and should NOT be used with real sensitive data.
- The script relies on the Hugging Face Transformers library for tokenization.
"""

from regex import E
from torch.utils.data import Dataset
import string, torch
from training_datasets.generated_synthetic_data import synthetic_data
from training_datasets.injected_templates import injected_templates
from transformers import AutoTokenizer, AutoModelForTokenClassification, Trainer, TrainingArguments
from evaluation_datasets.eval_generated_synthetic_data import Eval_synthetic_data
from evaluation_datasets.eval_injected_templates import Eval_injected_templates


class TrainingTokenDataset(Dataset):
    def __init__(self, injected_templates, synthetic_data, tokenizer, max_length=512):
        self.encodings = []
        self.labels = []
        
        PUNCTUATION_TOKENS = set(string.punctuation)
        
        for i in range(len(injected_templates)):
            try:
                # 1: Getting full encoding first to handle special tokens
                encoding = tokenizer(
                    injected_templates[i],
                    truncation=True,
                    padding='max_length',
                    max_length=max_length,
                    return_tensors="pt",
                    return_offsets_mapping=True,  
                    add_special_tokens=True
                )
                    
                # Initializing all labels as NOT_SENSITIVE
                labels = [0] * len(encoding['input_ids'][0])
                
                # Mark special tokens as -100 (ignored in loss calculation)
                for pos in range(len(encoding['input_ids'][0])):
                    if encoding['input_ids'][0][pos] in [tokenizer.cls_token_id, 
                                                       tokenizer.sep_token_id, 
                                                       tokenizer.pad_token_id]:
                        labels[pos] = -100
                
                # 2: Finding and labeling sensitive data
                
                for synthetic_item in synthetic_data[i]:
                    synthetic_str = str(synthetic_item)
                    # Find all occurrences of sensitive data in the template
                    start_idx = 0
                    while True:
                        pos = injected_templates[i].find(synthetic_str, start_idx)
                        if pos == -1:
                            break
                            
                        # Find which tokens correspond to these character positions
                        char_to_token = encoding.char_to_token(0, pos)
                        end_pos = pos + len(synthetic_str)
                        end_token = encoding.char_to_token(0, end_pos - 1)
                        
                        if char_to_token is not None and end_token is not None:
                            # Label all tokens in this range as SENSITIVE
                            for token_idx in range(char_to_token, end_token + 1):
                                # Only label if it's not a special token
                                if labels[token_idx] != -100:
                                    token = tokenizer.convert_ids_to_tokens(
                                        encoding['input_ids'][0][token_idx].item()
                                    )
                                    # Not marking punctuation as sensitive
                                    if token not in PUNCTUATION_TOKENS:
                                        labels[token_idx] = 1
                        
                        start_idx = pos + 1
                
                self.encodings.append({key: val.squeeze(0) for key, val in encoding.items()})
                self.labels.append(labels)
            except Exception as e:
                print(f"Error processing template {i}: {e}")
                continue  
        
        # Debug
        print(f"Length of self.encodings: {len(self.encodings)}")
        print(f"Length of self.labels: {len(self.labels)}")

    def __getitem__(self, idx):
        item = {key: val for key, val in self.encodings[idx].items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)

def print_alignment(dataset, idx, tokenizer):
    """Helper function to print token-label alignment for debugging"""

    item = dataset[idx]
    input_ids = item['input_ids']
    labels = item['labels']
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    
    print("\nToken-Label alignment:")
    print("-" * 50)
    for token, label in zip(tokens, labels):
        label_text = "SENSITIVE" if label == 1 else "NOT_SENSITIVE" if label == 0 else "IGNORED"
        print(f"Token: {token:15} Label: {label_text}")
    
if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/codebert-base",
        add_prefix_space=True
    )
    
    # Validating input data
    assert len(injected_templates) == len(synthetic_data), \
        "Number of templates must match number of sensitive data items"
    
    # Training dataset
    dataset = TrainingTokenDataset(
        injected_templates=injected_templates,
        synthetic_data=synthetic_data,
        tokenizer=tokenizer
    )
    
    
    eval_dataset = TrainingTokenDataset(
        injected_templates=Eval_injected_templates,
        synthetic_data=Eval_synthetic_data,
        tokenizer=tokenizer
    )
    #Training starts here

    model = AutoModelForTokenClassification.from_pretrained("microsoft/codebert-base", num_labels=2)

    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=4,  
        eval_strategy="epoch",
        logging_dir="./logs",
        save_strategy="epoch",
        save_total_limit=2,
        fp16=False, 
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        eval_dataset=eval_dataset,
    )

    trainer.train()