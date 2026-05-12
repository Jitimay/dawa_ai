"""
DAWA AI: FIXED MEMORY-FRIENDLY GGUF EXPORT
-----------------------------------------
This script is designed to be run in Google Colab AFTER the trainer.train() step.
It ensures the GGUF export doesn't crash the Colab session by limiting
memory and thread usage.

INSTRUCTIONS:
1. Run this in a new cell after your training is finished.
"""

import os
from google.colab import files

def export_model_fixed(model, tokenizer):
    print("\n" + "="*50)
    print("🔄 STARTING MEMORY-FRIENDLY EXPORT...")
    print("="*50)

    # 1. Recompile llama.cpp with lower thread count to prevent memory spikes
    print("[1/3] Optimizing llama.cpp for Colab memory limits...")
    os.system("cd /root/.unsloth/llama.cpp && make clean && make -j2")

    # 2. Export with memory optimizations
    print("[2/3] Quantizing to GGUF (q4_k_m)...")
    export_folder = "dawa_nurse_model"
    
    model.save_pretrained_gguf(
        export_folder,
        tokenizer,
        quantization_method="q4_k_m",
        n_threads=2,           # Critical: limits memory usage
        n_gpu_layers=0,        # Use CPU only for quantization to save VRAM
    )

    # 3. Trigger Download
    print("[3/3] Export complete! Preparing download...")
    
    # Locate the .gguf file (Unsloth creates it inside the folder)
    found_file = False
    for root, dirs, files_list in os.walk(export_folder):
        for file in files_list:
            if file.endswith(".gguf"):
                file_path = os.path.join(root, file)
                print(f"📥 Downloading: {file}")
                files.download(file_path)
                found_file = True
    
    if not found_file:
        print("❌ Error: GGUF file not found. Check the export folder.")

    print("\n" + "="*50)
    print("✅ SUCCESS! Your optimized model is downloading.")
    print("="*50)

# To use this in your notebook, call:
# export_model_fixed(model, tokenizer)
