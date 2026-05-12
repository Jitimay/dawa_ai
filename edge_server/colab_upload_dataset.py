"""
DAWA AI: STYLED DATASET UPLOAD (PC -> COLAB)
-------------------------------------------
This script follows the user's preferred visual style and verification logic.
It handles the initial upload of 'medical_dataset_kirundi.jsonl' from a local PC.
"""

from google.colab import files
import os
import shutil

def upload_dataset_styled():
    print("="*50)
    print("📁 PLEASE UPLOAD YOUR DATASET")
    print("="*50)
    print("\nFile must be named: medical_dataset_kirundi.jsonl")
    print("Format: each line is a JSON object with 'instruction', 'context', 'response' fields")
    print("\nExample line:")
    print('{"instruction": "What is malaria?", "context": "Rural clinic", "response": "Malaria is caused by parasites..."}')
    print("\n" + "="*50)

    # Upload file
    uploaded = files.upload()

    # Move to correct location
    for filename in uploaded.keys():
        if filename.endswith(".jsonl"):
            # Move and rename to the standard path
            shutil.move(filename, "/content/medical_dataset_kirundi.jsonl")
            print(f"\n✅ Dataset uploaded successfully: {filename}")
            print(f"📍 Saved to: /content/medical_dataset_kirundi.jsonl")
            
            # Show first few lines to verify
            print("\n📊 First 2 lines of your dataset:")
            try:
                with open("/content/medical_dataset_kirundi.jsonl", "r") as f:
                    for i, line in enumerate(f):
                        if i < 2:
                            print(f"  Line {i+1}: {line.strip()[:100]}...")
                        else:
                            break
            except Exception as e:
                print(f"  [!] Could not read file for preview: {e}")
            break
    else:
        print("\n❌ Error: No .jsonl file was uploaded!")
        return

    # Set the path for training (this makes it global in the notebook if needed)
    dataset_file = "/content/medical_dataset_kirundi.jsonl"
    print(f"\n✅ Dataset path verified and set to: {dataset_file}")
    print("="*50)

if __name__ == "__main__":
    upload_dataset_styled()
