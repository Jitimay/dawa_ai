"""
DAWA AI: Google Colab Training Script
------------------------------------
This script is designed to be run in a Google Colab environment with a T4 GPU.
It fine-tunes Gemma 4 on the Dawa AI Kirundi medical dataset.

INSTRUCTIONS:
1. Open colab.new
2. Change Runtime to T4 GPU.
3. Run: !pip install unsloth && pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes
4. Upload 'final_training_dataset.jsonl' to the Colab file explorer.
5. Run this script.
"""

from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from google.colab import drive
import os

# 1. Setup Storage
print("[1/8] Setting up Google Drive...")
drive.mount('/content/drive')
OUTPUT_DIR = "/content/drive/MyDrive/dawa_ai_model"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. Configuration
print("[2/8] Configuring model parameters...")
model_name = "google/gemma-4-4b-it" 
max_seq_length = 2048
dataset_file = "medical_dataset_kirundi.jsonl" 

# 3. Load Model and Tokenizer with Unsloth
print("[3/8] Loading Gemma 4 (4-bit)...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    load_in_4bit = True,
)

# 4. Add LoRA adapters
print("[4/8] Adding LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
)

# 5. Load Dataset
print("[5/8] Loading 2000-row dataset...")
dataset = load_dataset("json", data_files=dataset_file, split="train")

# 6. Define Trainer
print("[6/8] Initializing SFTTrainer...")
trainer = SFTTrainer(
    model = model,
    train_dataset = dataset,
    dataset_text_field = "instruction", 
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 300, 
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 5,
        output_dir = "outputs",
        optim = "adamw_8bit",
    ),
)

# 7. Train
print("[7/8] Starting Training (estimated 25-30 mins)...")
trainer.train()

# 8. Export to GGUF for Ollama
print("[8/8] Exporting to GGUF (4-bit quantization)...")
model.save_pretrained_gguf(
    "dawa-nurse-gemma4", 
    tokenizer, 
    quantization_method = "q4_k_m"
)

# Final Copy to Drive
print(f"Finalizing... Copying weights to {OUTPUT_DIR}")
os.system(f"cp dawa-nurse-gemma4/*.gguf {OUTPUT_DIR}/")

print("\n" + "="*40)
print("SUCCESS: Your model is ready!")
print(f"Download the .gguf file from your Google Drive: {OUTPUT_DIR}")
print("="*40)
