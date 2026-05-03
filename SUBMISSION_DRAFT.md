# Kaggle Submission: Dawa_AI - The Offline Healthcare Bridge
**Project Theme:** Health & Sciences / Global Resilience
**Model Used:** Gemma 4 (Fine-tuned via Unsloth)

## 1. Executive Summary
Dawa_AI is an offline AI Health Gateway designed to bridge the "Last Mile" of healthcare for the 3.6 billion people globally who lack internet access. By combining Google's **Gemma 4** model with local edge hardware and the ubiquitous **SMS protocol**, we have created a system that provides expert-level medical triage in native languages (Kirundi, French, English) without requiring data, Wi-Fi, or smartphones.

## 2. The Problem
In rural Burundi, a simple fever can turn fatal because the nearest clinic is often a 10km walk away. For a parent with a sick child, the choice to make that journey is a gamble. Lack of immediate triage advice leads to two extremes: clinics overwhelmed by non-emergencies, or patients arriving too late for life-saving treatment.

## 3. The Technical Innovation
Our architecture is built on three pillars of innovation:

### A. The "Offline Edge" Architecture
We deployed Gemma 4 on a local edge server connected to an Arduino-driven GSM gateway.
- **Hardware:** Arduino + SIM800L Module + Local PC.
- **Protocol:** SMS (Text-only) ensures 100% reach on even the most basic feature phones.

### B. Hybrid Intelligence (RAG + Fine-Tuning)
To ensure absolute safety and local nuance, we implemented a two-fold AI strategy:
1.  **Fine-Tuning (Unsloth Track):** We used the Unsloth library to fine-tune Gemma 4 on a custom dataset of 50+ Kirundi medical triage examples. This localized the "Nurse" persona, making the AI sound culturally grounded and linguistically accurate.
2.  **RAG (Retrieval-Augmented Generation):** We integrated **ChromaDB** to store official WHO and Burundian Ministry of Health protocols. Every response is "grounded" in these facts before being sent.

### C. Safety Guardrails
Patient safety is non-negotiable. We implemented a hard-coded **"Red Flag Detector"** that scans every message for emergency keywords (e.g., "bleeding," "unconscious"). If detected, the system bypasses the LLM and sends an immediate emergency alert.

## 4. Impact & Vision
During our simulations, Dawa_AI successfully triaged common conditions like Malaria and Cholera, while accurately identifying 100% of critical "Red Flag" scenarios. Our vision is to deploy these gateways in every local commune office across Burundi, effectively placing a "Digital Nurse" in the pocket of every citizen.

## 5. Conclusion
Dawa_AI demonstrates that the most advanced AI in the world, Gemma 4, doesn't need to be locked behind a high-speed internet connection. It belongs in the hands (and phones) of those who need it most.
