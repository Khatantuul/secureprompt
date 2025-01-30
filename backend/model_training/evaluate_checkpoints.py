from transformers import AutoModelForTokenClassification, TrainingArguments, Trainer
from transformers import AutoTokenizer
from data_preparation import create_datasets, TrainingTokenDataset
from test_datasets.test_generated_synthetic_data import test_synthetic_data
from test_datasets.test_injected_templates import test_injected_templates

def evaluate_checkpoint(checkpoint_path, dataset, tokenizer):
    print(f"\nEvaluating checkpoint: {checkpoint_path}")
    model = AutoModelForTokenClassification.from_pretrained(checkpoint_path)
    model.eval()

    eval_args = TrainingArguments(
        output_dir="./eval_results",
        do_train=False,
        do_eval=True,
        per_device_eval_batch_size=4,
        report_to="none"
    )

    evaluator = Trainer(
        model=model,
        args=eval_args,
        eval_dataset=dataset,
        tokenizer=tokenizer
    )

    metrics = evaluator.evaluate()
    print(f"Metrics for {checkpoint_path}:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
    return metrics

def main():
   
    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/codebert-base",
        add_prefix_space=True
    )

    test_dataset = create_datasets(tokenizer, test_injected_templates, test_synthetic_data)
    print(f"Test dataset size: {len(test_dataset)}")

    # evaluating both checkpoints with the test dataset
    model_50_results = evaluate_checkpoint("results/checkpoint-50", test_dataset, tokenizer)
    model_75_results = evaluate_checkpoint("results/checkpoint-75", test_dataset, tokenizer)

    
    if model_50_results['eval_loss'] < model_75_results['eval_loss']:
        print("\nCheckpoint-50 performs better!")
        best_checkpoint = "results/checkpoint-50"
    else:
        print("\nCheckpoint-75 performs better!")
        best_checkpoint = "results/checkpoint-75"

    print(f"\nBest checkpoint: {best_checkpoint}")
    print(f"Best eval loss: {min(model_50_results['eval_loss'], model_75_results['eval_loss']):.4f}")

if __name__ == "__main__":
    main()