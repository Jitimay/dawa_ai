# Dawa AI: The Offline Healthcare Bridge
**Project Theme:** Global Resilience / Health & Sciences
**Model:** Gemma 4 E2B-it (Fine-tuned via Unsloth)
**Interface:** SMS (Offline GSM Gateway)

---

## 🌍 The Mission
**Dawa AI** is an offline AI Health Gateway designed to bridge the "Last Mile" of healthcare for the 3.6 billion people globally who lack internet access. By combining Google's **Gemma 4** model with local edge hardware and the ubiquitous **SMS protocol**, we provide expert-level medical triage in native languages (Kirundi, French, English) without requiring data, Wi-Fi, or smartphones.

### 🏆 Grand Prize trajectory:
- **Offline First:** Runs 100% without internet.
- **Inclusive:** Accessible via $10 feature phones.
- **Safety Centric:** Hybrid RAG + Deterministic "Red Flag" Guardrails.
- **Localized:** Fine-tuned for rural Burundian linguistic and medical contexts.

---

## 🛠️ System Architecture

### 1. Hardware Layer (The Gateway)
- **Arduino (Uno/RP2040):** Handles serial parsing and power management.
- **SIM800L GSM Module:** Provides the cellular link for SMS.
- **Local PC/Edge Server:** Runs the LLM and Database.

### 2. AI Layer (The Brain)
- **Gemma 4-4b-it:** Quantized to 4-bit (GGUF) for high-speed edge inference.
- **Unsloth Fine-Tuning:** Optimized for the "Digital Nurse" persona in Kirundi.
- **ChromaDB (RAG):** Grounding every response in official WHO & Burundian health protocols.

---

## 🔌 Hardware Setup (The "Foolproof" Guide)

### Wiring Diagram (ASCII)
```text
  [ SIM800L ]        [ ARDUINO ]        [ PC / SERVER ]
  VCC (5V/2A) <----> 5V (External)
  GND         <----> GND
  TX          <----> Pin 0 (RX)
  RX          <----> Pin 1 (TX)
                     USB Port <---------> USB Port (Serial)
```
*Note: Ensure the SIM800L has a separate 2A power source for GSM stability.*

---

## 🚀 Installation & Reproducibility

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/dawa_ai.git
cd dawa_ai/edge_server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. AI Model Preparation
1. **Ollama:** Install [Ollama](https://ollama.ai/).
2. **Build the Model:**
   ```bash
   # Navigate to edge_server/
   ollama create dawa-nurse -f Modelfile
   ```

### 3. Hardware Firmware
1. Open `hardware_gateway/hardware_gateway.ino` in the Arduino IDE.
2. Select your board and flash the code.

### 4. Running the System
1. Connect the Arduino via USB.
2. Start the edge server:
   ```bash
   python main.py
   ```
3. The server will automatically detect the Arduino and announce: `[3/3] System Online.`

---

## 📖 How to Test (SMS Protocol)

To simulate a patient interaction, send these SMS messages to the gateway's SIM number:

1.  **Verify:** `REG|MAJIDAWA_2026` (Unlocks the system).
2.  **Language:** `LANG|KIRUNDI` (Default) or `LANG|ENGLISH`.
3.  **Triage Query:** `Umwana wanje afise umuriro.` (My child has a fever).
4.  **Red Flag Test:** `Ndafise amaraso menshi.` (I have heavy bleeding).
    *   *Result:* Immediate emergency redirection, bypassing AI.

---

## 🛡️ Safety & Grounding
Dawa AI employs a **Deterministic Guardrail Layer**. Every message is scanned for emergency keywords *before* reaching the LLM. If a "Red Flag" is detected, a pre-validated medical emergency instruction is sent instantly to minimize latency and maximize reliability.

---

## ⚖️ License
Licensed under **CC-BY 4.0**. Created for the **Gemma 4 Good Hackathon**.
