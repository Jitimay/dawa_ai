"""
DAWA AI: EXTREME MEMORY-OPTIMIZED COLAB SCRIPT
----------------------------------------------
Designed for Gemma 4 E2B-it on standard T4 GPUs.
Uses fragment-prevention and aggressive cache clearing.
"""

import os

# 1. CRITICAL: Set memory management before any imports
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from google.colab import files
import gc

def main():
    print("\n" + "="*50)
    print("   DAWA AI: EXTREME MEMORY PIPELINE   ")
    print("="*50 + "\n")

    # 0. Upload Dataset from PC
    dataset_file = "medical_dataset_kirundi.jsonl" 
    if not os.path.exists(dataset_file):
        print("📁 Please select 'medical_dataset_kirundi.jsonl' from your PC...")
        uploaded = files.upload()
        for filename in uploaded.keys():
            if filename != dataset_file:
                os.rename(filename, dataset_file)
    else:
        print(f"✅ Dataset '{dataset_file}' already present.")

    # 1. Clear memory aggressively
    torch.cuda.empty_cache()
    gc.collect()

    # 2. Load Model with Extreme Optimizations
    print("[2/6] Loading Gemma 4 E2B-it (Fragment Prevention Mode)...")
    model_name = "google/gemma-4-E2B-it" 
    max_seq_length = 2048

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = max_seq_length,
        load_in_4bit = True,
        device_map = "auto",
        torch_dtype = torch.float16,
        low_cpu_mem_usage = True,
    )

    # 3. Add LoRA adapters
    print("[3/6] Applying LoRA optimization...")
    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_alpha = 16,
        lora_dropout = 0,
        bias = "none",
    )

    # 4. Load Dataset
    print(f"[4/6] Loading dataset...")
    dataset = load_dataset("json", data_files=dataset_file, split="train")

    # 5. Fine-Tuning
    print("[5/6] Starting Training (Estimated: 25 mins)...")
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "instruction", 
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
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
    
    # Final cache clear before training
    torch.cuda.empty_cache()
    gc.collect()
    
    trainer.train()

    # 6. Export to GGUF
    print("[6/6] Exporting to GGUF...")
    export_folder = "dawa_nurse_model"
    model.save_pretrained_gguf(
        export_folder, 
        tokenizer, 
        quantization_method = "q4_k_m"
    )

    # Trigger Download
    print("🏁 Training complete! Downloading .gguf file...")
    for root, dirs, files_list in os.walk(export_folder):
        for file in files_list:
            if file.endswith(".gguf"):
                files.download(os.path.join(root, file))

if __name__ == "__main__":
    main()
