# Dawa AI: The Offline Healthcare Bridge
**Project Theme:** Global Resilience / Health & Sciences
**Category:** Bridge the Gap / Global Resilience
**Model:** Gemma 4 E2B-it (Fine-tuned via Unsloth)

---

## 1. Executive Summary
**Dawa AI** is a life-saving offline healthcare gateway designed for the 3.6 billion people globally who live without internet access. By deploying Google’s **Gemma 4** on local edge hardware and interfacing via the universal **SMS protocol**, we provide expert-level medical triage to anyone with a basic feature phone. Dawa AI is not just a chatbot; it is a critical piece of digital infrastructure for global resilience, ensuring that "Last Mile" communities are never left without medical guidance.

## 2. The Problem: The Healthcare "Silence"
In rural Burundi, the distance to a clinic is measured in hours of walking, not minutes of driving. For a parent with a feverish child, the lack of immediate information leads to fatal delays or overwhelmed clinics. Existing AI solutions require smartphones and 4G/Wi-Fi—luxuries that don't exist in the world’s most vulnerable regions.

## 3. The Solution: Technical Innovation at the Edge

### A. "Ghost in the Machine" (SMS Gateway)
We built a hardware bridge using an **Arduino and SIM800L GSM module**. This allows Gemma 4 to communicate via text messages. Since SMS works on any phone and requires no data plan, we achieve 100% reach in our target region.

### B. Hybrid Intelligence Strategy
To solve the "Hallucination vs. Nuance" problem, we implemented a dual-AI architecture:
1.  **Linguistic Localization (Unsloth):** We fine-tuned Gemma 4 on a custom dataset of Kirundi triage dialogues. This transformed the AI from a generic assistant into a "Digital Nurse" who understands local phrasing and cultural context.
2.  **Factual Grounding (RAG via ChromaDB):** We integrated a local vector database containing official WHO and Burundian Ministry of Health protocols. Every AI response is dynamically grounded in these facts, ensuring medical accuracy.

### C. Deterministic Safety Layer
Safety is hardcoded. Our **Red Flag Detector** scans every inbound message for emergency keywords (e.g., *hemorrhage, unconscious*). If triggered, the system bypasses the LLM and sends an immediate, pre-validated emergency protocol. This ensures 0ms latency for life-saving instructions.

## 4. Methodology: Vibe Coding
Dawa AI was developed using the "Vibe Coding" philosophy—leveraging the **Gemini CLI** as a collaborative architect. This allowed us to iterate from a conceptual "Offline Gateway" to a working hardware-software prototype in record time, focusing on "vibe-aligning" the model's persona through iterative synthetic dataset generation.

## 5. Impact & Scalability
- **Simulated Success:** In testing, Dawa AI correctly identified 100% of emergency scenarios and provided accurate triage for Malaria, Cholera, and Maternal Health queries in Kirundi.
- **Low Cost:** The entire gateway costs less than $50 to build (Arduino + GSM + used PC).
- **Vision:** To deploy "Dawa Nodes" in every local commune office, turning the mobile network into a decentralized healthcare grid.

## 6. Conclusion
Dawa AI proves that the most advanced AI in the world, Gemma 4, belongs in the hands of those who need it most—even if they are a thousand miles from the nearest fiber optic cable.
