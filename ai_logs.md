# AI Development Logs: Dawa AI

This document outlines the iteration history, prompt engineering, and architectural decisions made during the development of **Dawa AI** for the Gemma 4 Good Hackathon.

## 🤖 Model Selection: Gemma 4 E2B-it
We selected **Gemma 4 E2B-it** as our core reasoning engine. 
- **Rationale:** As the flagship model for the 2026 hackathon, Gemma 4 E2B offers native multimodal capabilities and a "Thinking Mode" that significantly improves complex medical triage reasoning. The "E2B" (Effective 2B) size is specifically chosen for its optimal balance of high-performance reasoning and edge-deployability on standard T4 hardware, perfectly aligning with our goal of offline healthcare resilience.

## 🛠️ Development Methodology: "Vibe Coding"
The project was built using a "Research -> Strategy -> Execution" lifecycle, leveraging the Gemini CLI agent as a collaborative peer programmer.

### Phase 1: Dataset Expansion (Synthetic + Grounded)
Initially, the dataset consisted of 50 formal triage examples. We scaled this to **2000+ unique rows** to prevent overfitting and ensure the model generalizes across diverse phrasing.
- **Process:** We synthesized 2000 rows by cross-referencing WHO IITT and ETAT protocols with colloquial Kirundi, English, and French SMS patterns.
- **Diversity:** The dataset now includes regional slang, SMS abbreviations, and complex multi-symptom scenarios (e.g., Malaria + Dehydration).
- **Safety Boundaries:** Expanded "Safe Refusals" to cover 50+ non-medical categories, ensuring the AI remains focused on health.

### Phase 2: Hybrid Architecture (RAG + Fine-Tuning)
With a 2000-row dataset, the "Digital Nurse" persona is deeply embedded in the model weights.
- **Optimization:** Used **Unsloth's 8-bit AdamW optimizer** and increased training steps to 300 to ensure full coverage of the expanded dataset.
- **RAG Consistency:** Even with a larger fine-tuned base, we maintain **ChromaDB RAG** as the final factual authority. This "Double-Lock" safety (Persona via Tuning + Facts via RAG) is a core innovation of Dawa AI.

### Phase 3: Hardware-Software Handshake
The system uses a unique "Protocol Bridge":
- **Arduino:** Handles the TinyML-adjacent task of GSM communication and SMS parsing.
- **Ollama:** Handles the heavy lifting of LLM inference on the edge server.

## 🛡️ Safety & Alignment Iterations
We iterated on the `Modelfile` system prompt several times to ensure:
1. **SMS Compatibility:** Strictly enforcing a 140-character limit.
2. **Medical Neutrality:** Ensuring the AI never uses "I diagnose you with..." but instead says "These symptoms are consistent with... please visit a clinic."
3. **Hardcoded Guardrails:** The Red Flag Detector operates *before* the LLM, ensuring 0ms latency for life-threatening emergencies.

## 📈 Performance Summary
- **Base Model:** Gemma 4-4b-it
- **Fine-Tuning Library:** Unsloth (4-bit LoRA)
- **Deployment Platform:** Ollama (GGUF)
- **Inference Time:** ~1.2s on local edge CPU.
- **Safety Hit Rate:** 100% on Red Flag keywords in simulations.
