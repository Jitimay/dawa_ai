# Dawa AI: The Offline Healthcare Bridge

**Dawa AI** is an offline AI Health Gateway designed to bridge the "Last Mile" of healthcare for the 3.6 billion people globally who lack internet access. By combining Google's **Gemma 4** model with local edge hardware and the ubiquitous **SMS protocol**, we provide expert-level medical triage in native languages without requiring data, Wi-Fi, or smartphones.

---

## 🚀 Technical Innovation

### 1. The "Offline Edge" Architecture
We deployed Gemma 4 on a local edge server connected to an Arduino-driven GSM gateway.
- **Hardware:** Arduino + SIM800L GSM Module + Local PC.
- **Protocol:** SMS (Text-only) ensures 100% reach on basic feature phones.

### 2. Hybrid Intelligence (RAG + Fine-Tuning)
To ensure absolute safety and local nuance, we implemented a two-fold AI strategy:
- **Fine-Tuning (Unsloth):** Gemma 4 was fine-tuned on a custom dataset of Kirundi medical triage examples, optimizing it for the "Nurse" persona and local linguistic accuracy.
- **RAG (ChromaDB):** We integrated a vector database to store official WHO and Burundian Ministry of Health protocols. Every response is grounded in these facts to eliminate hallucinations.

### 3. Safety Guardrails
- **Red Flag Detector:** A hard-coded emergency scanner that identifies life-threatening keywords (e.g., "bleeding", "unconscious") and bypasses the AI to provide immediate emergency instructions.

---

## 🛠️ Setup & Installation

### Prerequisites
- **Hardware:** Arduino (Uno/Mega/RP2040) + SIM800L Module.
- **Software:** 
  - Python 3.10+
  - [Ollama](https://ollama.ai/)
  - [Unsloth](https://github.com/unslothai/unsloth)

### Step 1: Fine-Tuning (The Unsloth Advantage)
1. Navigate to `edge_server/`.
2. Run the fine-tuning script:
   ```bash
   python finetune_gemma.py
   ```
3. This will generate a `gemma-4-dawa-kirundi-gguf` folder containing the optimized GGUF weights.

### Step 2: Model Deployment (Ollama)
1. Create the specialized nurse model:
   ```bash
   ollama create dawa-nurse -f Modelfile
   ```

### Step 3: Hardware Setup
1. Flash `hardware_gateway/hardware_gateway.ino` to your Arduino.
2. Connect the SIM800L module (ensure it has a valid SIM card).

### Step 4: Run the Gateway
1. Start the edge server:
   ```bash
   python main.py
   ```

---

## 📖 How to Use (SMS Interface)

1. **Register:** Send `REG|MAJIDAWA_2026` to the gateway's phone number.
2. **Set Language:** Send `LANG|KIRUNDI` (or FRENCH/ENGLISH).
3. **Triage:** Send your symptoms (e.g., "Umwana afise umuriro").
4. **Emergency:** If you mention "bleeding" or "unconscious," the system will trigger a **Red Flag** alert instantly.
5. **Reset:** Send `RESET` to start a new conversation thread.

---

## 🛡️ Safety & Grounding Proof
The system logs every RAG retrieval. In the `edge_server` terminal, you will see:
```text
--- RAG GROUNDING ---
User Query: Fever and headache.
Retrieved Protocol: Ibimenyetso vya Malaria: Umuriro... Ivuriro: Kunywa imiti ya Coartem.
---------------------
```
This ensures that every AI response is tethered to official medical guidelines, making it a reliable tool for rural health workers and parents.

---

## ⚖️ License
This project is licensed under **CC-BY 4.0** as per the Gemma 4 Good Hackathon requirements.
