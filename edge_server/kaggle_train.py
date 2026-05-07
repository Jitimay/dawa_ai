# DAWA AI: Kaggle/Colab Training Script
# This script automates the full fine-tuning and GGUF export process.

import os

# 1. Install necessary libraries (specific for Kaggle/Colab environments)
print("Installing Unsloth and dependencies...")
os.system('pip install --no-deps "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" -q')
os.system('pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes -q')

from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 2. Configuration
model_name = "google/gemma-4-4b-it" 
max_seq_length = 2048
dataset_file = "medical_dataset_kirundi.jsonl" # Ensure this file is uploaded to the same directory

# 3. Load Model and Tokenizer (4-bit quantization)
print("Loading Gemma 4-4b-it...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    load_in_4bit = True,
)

# 4. Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
)

# 5. Load Dataset
print(f"Loading dataset: {dataset_file}")
dataset = load_dataset("json", data_files=dataset_file, split="train")

# 6. Define Trainer
trainer = SFTTrainer(
    model = model,
    train_dataset = dataset,
    dataset_text_field = "instruction", # We will use the 'instruction' field for now
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 100, # Increased steps for better learning of the 90+ rows
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        output_dir = "outputs",
    ),
)

# 7. Train
print("Starting training...")
trainer.train()

# 8. Export to GGUF for Ollama
print("Exporting model to GGUF (4-bit)...")
model.save_pretrained_gguf(
    "dawa_nurse_model",
    tokenizer,
    quantization_method = "q4_k_m",
)

print("\n" + "="*50)
print("SUCCESS: Model 'dawa_nurse_model' has been created.")
print("Download the .gguf file from the 'dawa_nurse_model' folder.")
print("Then, run: 'ollama create dawa-nurse -f Modelfile' on your local machine.")
print("="*50)
