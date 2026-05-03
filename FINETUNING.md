# Fine-Tuning Gemma 4 for Dawa_AI

To win the **Unsloth Track ($10,000)** in the Gemma 4 Good Hackathon, you need to fine-tune the model to better understand Kirundi medical terms and triage logic.

## Prerequisites
1. A GPU (NVIDIA T4, L4, or A100 - available for free on Kaggle/Colab).
2. Install Unsloth: `pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"`

## Workflow
1. **Data Collection:** Add more examples to `medical_dataset_kirundi.jsonl`. Focus on common symptoms and the correct Kirundi responses.
2. **Run Training:** Execute `python finetune_gemma.py`. This uses Unsloth to make training 2x faster and use 70% less memory.
3. **Export:** Once trained, you can export the model to GGUF format (for use with Ollama) using Unsloth's built-in export functions.

## Why this wins
- **Localization:** Gemma 4 is great, but its Kirundi might be "stiff." Fine-tuning makes it sound like a local nurse.
- **Safety:** By training on official Burundian Ministry of Health data, you ensure the "Nurse" persona never hallucinates dangerous advice.
