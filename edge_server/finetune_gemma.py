from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. Configuration
model_name = "google/gemma-4-4b-it" # Use the specific Gemma 4 variant
max_seq_length = 2048
dataset_file = "medical_dataset_kirundi.jsonl"

# 2. Load Model and Tokenizer with Unsloth (4-bit quantization for efficiency)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    load_in_4bit = True,
)

# 3. Add LoRA adapters for fine-tuning
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
)

# 4. Load Dataset
dataset = load_dataset("json", data_files=dataset_file, split="train")

# 5. Define Trainer
trainer = SFTTrainer(
    model = model,
    train_dataset = dataset,
    dataset_text_field = "instruction", # Adjust based on your template
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        output_dir = "outputs",
    ),
)

# 6. Train
trainer.train()

# 7. Save the Fine-Tuned Model (LoRA)
model.save_pretrained("gemma-4-dawa-kirundi")
tokenizer.save_pretrained("gemma-4-dawa-kirundi")

# 8. Export to GGUF for Ollama
# We merge the LoRA adapters into the base model and save as GGUF
print("Exporting model to GGUF format for Ollama...")
model.save_pretrained_gguf(
    "gemma-4-dawa-kirundi-gguf",
    tokenizer,
    quantization_method = "q4_k_m", # Standard high-quality 4-bit quantization
)
print("Fine-tuning and GGUF export complete. Model saved to 'gemma-4-dawa-kirundi-gguf'.")
