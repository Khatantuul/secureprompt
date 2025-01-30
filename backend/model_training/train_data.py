"""
This script is used to train a model to identify sensitive information in text data.
It uses the Hugging Face Transformers library to load a pre-trained model and tokenizer,
and fine-tunes the model on a dataset of synthetic data and templates.
The `create_datasets` function generates the training and evaluation datasets for the model.
The `main` function loads the model and tokenizer, creates the datasets, and trains the model.

"""

from transformers import AutoModelForTokenClassification, TrainingArguments, Trainer
from transformers import AutoTokenizer
from data_preparation import create_datasets

def main():
    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/codebert-base",
        add_prefix_space=True
    )
    
    train_dataset, eval_dataset = create_datasets(tokenizer)
    
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
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )
    
    trainer.train()

if __name__ == "__main__":
    main()