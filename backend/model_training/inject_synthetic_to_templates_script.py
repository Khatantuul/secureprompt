"""
Generates synthetic data and injects it into language templates to create synthetic prompts for model training and evaluation.

This script uses the `SyntheticDataGenerator` class from the `synthetic_sample_data_generator` module to generate synthetic data.
It then randomly selects language templates from the `language_templates` module and injects the synthetic data into the templates.

The generated synthetic prompts are saved to the following files in the `training_datasets` directory:
- `generated_synthetic_data.py`: Contains the generated synthetic data.
- `injected_templates.py`: Contains the templates with injected synthetic data.

For evaluation purposes, the script also generates synthetic evaluation data and injects it into evaluation templates. 
The results are saved to the following files in the `evaluation_datasets` directory:
- `eval_generated_synthetic_data.py`: Contains the generated synthetic evaluation data.
- `eval_injected_templates.py`: Contains the evaluation templates with injected synthetic data.

These synthetic prompts are used to train and evaluate a model for identifying sensitive data in code snippets.

Disclaimer:
This script is intended for use in the model training and evaluation process only. The generated data is synthetic and should NOT be used in production or any context where real sensitive data is required.
"""

import os, random
from training_datasets.language_templates import templates
from synthetic_sample_data_generator import SyntheticDataGenerator
from evaluation_datasets.eval_templates import eval_templates
from test_datasets.test_templates import test_templates

synthetic_generator = SyntheticDataGenerator()

# print(os.getcwd())
num_prompts = 100

all_synthetic_data = []
all_templates = []
for i in range(num_prompts):
    language = random.choice(list(templates.keys()))
    template = templates[language]

    synthetic_api_keys = synthetic_generator.run_all_api_methods()
    synthetic_api_key = random.choice(synthetic_api_keys)
    synthetic_password = synthetic_generator.generate_password()
    synthetic_token = synthetic_generator.generate_jwt_like()
    synthetic_secret_key = synthetic_generator.generate_base64_key()

    
    injected_template = template.format(API_KEY=synthetic_api_key, PASSWORD=synthetic_password, TOKEN=synthetic_token, SECRET_KEY=synthetic_secret_key )
    all_templates.append(injected_template)
    all_synthetic_data.append((synthetic_api_key, synthetic_password, synthetic_token, synthetic_secret_key))

directory = os.path.join(os.getcwd(), 'model_training', 'training_datasets')
os.makedirs(directory, exist_ok=True)

filename = os.path.join(directory, "generated_synthetic_data.py")
with open(filename, 'w') as fw:
    fw.write(f"synthetic_data = {all_synthetic_data}", )
filename = os.path.join(directory, "injected_templates.py")
with open(filename, 'w') as fw:
    fw.write(f"injected_templates = {all_templates}", )


eval_all_synthetic_data = []
eval_all_templates = []
eval_data_num_prompts = 20 
for i in range(eval_data_num_prompts):
    eval_language = random.choice(list(eval_templates.keys()))
    eval_template = eval_templates[eval_language]

    eval_api_keys = synthetic_generator.run_all_api_methods()
    random_eval_api_key = random.choice(eval_api_keys)
    eval_password = synthetic_generator.generate_password()
    eval_token = synthetic_generator.generate_jwt_like()
    eval_secret_key = synthetic_generator.generate_base64_key()

    eval_injected_template = eval_template.format(API_KEY=random_eval_api_key, PASSWORD=eval_password, TOKEN=eval_token, SECRET_KEY=eval_secret_key)
    eval_all_templates.append(eval_injected_template)
    eval_all_synthetic_data.append((random_eval_api_key,eval_password,eval_token,eval_secret_key))


eval_directory = os.path.join(os.getcwd(), 'model_training', 'evaluation_datasets')
os.makedirs(eval_directory, exist_ok=True)

filename = os.path.join(eval_directory, "eval_generated_synthetic_data.py")
with open(filename, 'w') as ew:
    ew.write(f"Eval_synthetic_data = {eval_all_synthetic_data}",)
filename = os.path.join(eval_directory, "eval_injected_templates.py")
with open(filename, 'w') as ew:
    ew.write(f"Eval_injected_templates = {eval_all_templates}",)


test_all_synthetic_data = []
test_all_templates = []
test_data_num_prompts = 20 

for i in range(test_data_num_prompts):
    test_language = random.choice(list(test_templates.keys()))
    test_template = test_templates[test_language]

    test_api_keys = synthetic_generator.run_all_api_methods()
    random_test_api_key = random.choice(test_api_keys)
    test_password = synthetic_generator.generate_password()
    test_token = synthetic_generator.generate_jwt_like()
    test_secret_key = synthetic_generator.generate_base64_key()

    test_injected_template = test_template.format(API_KEY=random_test_api_key, PASSWORD=test_password, TOKEN=test_token, SECRET_KEY=test_secret_key)
    test_all_templates.append(test_injected_template)
    test_all_synthetic_data.append((random_test_api_key,test_password,test_token,test_secret_key))


test_directory = os.path.join(os.getcwd(), 'model_training', 'test_datasets')
os.makedirs(test_directory, exist_ok=True)

filename = os.path.join(test_directory, "test_generated_synthetic_data.py")
with open(filename, 'w') as tw:
    tw.write(f"test_synthetic_data = {test_all_synthetic_data}",)
filename = os.path.join(test_directory, "test_injected_templates.py")
with open(filename, 'w') as tw:
    tw.write(f"test_injected_templates = {test_all_templates}",)


