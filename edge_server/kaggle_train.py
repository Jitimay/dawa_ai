# DAWA AI: Kaggle/Colab Training Script
# This script automates the full fine-tuning and GGUF export process.

import os

# 1. Install necessary libraries (specific for Kaggle/Colab environments)
print("Installing Unsloth and dependencies...")
# Added unsloth_zoo which is now a required dependency for newer Unsloth versions
os.system('pip install --no-deps "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" -q')
os.system('pip install unsloth_zoo --no-deps -q')
os.system('pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes -q')

from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 2. Configuration
model_name = "google/gemma-4-4b-it" 
max_seq_length = 2048
# Updated to match your Kaggle dataset path
dataset_file = "/kaggle/input/medical-data-set-kirundi/medical_dataset_kirundi.jsonl" 

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

# 5. Load and Format Dataset
print(f"Loading dataset: {dataset_file}")
dataset = load_dataset("json", data_files=dataset_file, split="train")

# Define a formatting function to combine instruction and context
def format_prompts(examples):
    instructions = examples["instruction"]
    contexts = examples["context"]
    responses = examples["response"]
    texts = []
    for instruction, context, response in zip(instructions, contexts, responses):
        # Format consistent with how the Modelfile and ai_engine.py will use it
        text = f"Context: {context}\nPatient: {instruction}\nNurse: {response}"
        texts.append(text)
    return { "text" : texts }

dataset = dataset.map(format_prompts, batched = True)

# 6. Define Trainer
trainer = SFTTrainer(
    model = model,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 150, # Increased for the 126+ rows to ensure better persona lock-in
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
