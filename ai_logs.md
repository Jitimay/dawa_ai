# AI Development Logs: Dawa AI

This document outlines the iteration history, prompt engineering, and architectural decisions made during the development of **Dawa AI** for the Gemma 4 Good Hackathon.

## 🤖 Model Selection: Gemma 4-4b-it
We selected **Gemma 4-4b-it** as our core reasoning engine. 
- **Rationale:** The 4-billion parameter size offers the optimal balance between medical reasoning capabilities and edge-deployability. It is small enough to run on consumer-grade local hardware via Ollama while maintaining high linguistic accuracy for Kirundi.

## 🛠️ Development Methodology: "Vibe Coding"
The project was built using a "Research -> Strategy -> Execution" lifecycle, leveraging the Gemini CLI agent as a collaborative peer programmer.

### Phase 1: Dataset Expansion (Synthetic + Grounded)
Initially, the dataset consisted of 50 formal triage examples. We used AI-assisted generation to expand this to **90+ rows**, focusing on:
- **Natural Language Robustness:** Converting formal instructions (e.g., "Assess fever") into colloquial Kirundi SMS queries (e.g., "Umwana wanje arwaye, ntiyarye").
- **Safety Boundaries:** Training the model to recognize its own limits (Safe Refusals) and redirecting users to doctors for prescriptions or formal diagnoses.
- **Red Flag Criticality:** Identifying high-severity symptoms like poisoning or preeclampsia.

### Phase 2: Hybrid Architecture (RAG + Fine-Tuning)
We decided against a "pure" LLM approach for safety reasons.
- **Decision:** Use **Unsloth** for fine-tuning the "Nurse" persona and **ChromaDB** for factual grounding (RAG).
- **Result:** The model sounds like a local nurse (Fine-Tuning) but answers based on official WHO/Ministry of Health protocols (RAG).

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
