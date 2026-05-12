# Dawa AI - Video Production Script

**Project Title:** Dawa AI (formerly Dawa_AI)
**Target Tracks:** Global Resilience, Health & Sciences, Ollama, Unsloth, Safety & Trust.

---

## SCENE 1: THE PROBLEM (0:00 - 0:45)
**Visual:** Slow pan over a rural landscape or a close-up of a basic feature phone with no signal bars. Overlaid text: "Burundi: 11% Internet Access".
**Audio (Voiceover):**
In Burundi, getting sick is not always the problem. Not knowing what to do is. Every year, more than 5.6 million malaria cases are reported in a country of 13 million people. Malaria is the leading cause of hospital visits and deaths. 

**Visual:** A mother looking worried, holding a child (or a symbolic representation). 
**Audio (Voiceover):**
Imagine a mother in a rural village. Her child has a high fever. She doesn’t know if it’s malaria… or something worse. There is no doctor nearby. Only about 20 health workers serve every 10,000 people.

**Visual:** Split screen. Left side: "72% Mobile Phone Access". Right side: "11% Internet Access".
**Audio (Voiceover):**
While 72% of the population has a mobile phone, only 11% can access the internet. For many, reaching a health center takes more than an hour. So she waits. But waiting is dangerous. In Burundi, 78 out of 1,000 children die before age five—not because treatment doesn’t exist, but because it comes too late.

---

## SCENE 2: THE SOLUTION (0:45 - 1:30)
**Visual:** Close up of the Arduino Nano RP2040 Connect and SIM800A hardware setup. Lights are blinking. Transition to the "Dawa AI" logo.
**Audio (Voiceover):**
This is not just a healthcare problem. This is an access problem. We built **Dawa AI**. An AI-powered medical assistant that works through simple SMS. No internet. No smartphone. Just a basic phone.

**Visual:** **DEMO START.** A basic phone sends an SMS: "My child has fever and vomiting."
**Audio (Voiceover):**
A user sends a simple message. Our edge-based gateway, powered by Google’s **Gemma 4**, processes this locally.

**Visual:** Show the Python terminal running `main.py`, seeing the message arrive and Gemma generating a response.
**Audio (Voiceover):**
Dawa AI responds instantly with clear guidance: Possible causes, danger signs to watch for, and an urgency level. 

---

## SCENE 3: THE TECHNOLOGY (1:30 - 2:15)
**Visual:** Technical diagram showing: [Basic Phone] -> [GSM Gateway] -> [Gemma 4 / Ollama] -> [ChromaDB RAG].
**Audio (Voiceover):**
Dawa AI isn't just a chatbot. It is a localized medical expert. We used **Unsloth** to fine-tune Gemma 4 on Kirundi medical data, ensuring linguistic and cultural accuracy. 

**Visual:** Screen recording of `rag_engine.py` or the vector database query.
**Audio (Voiceover):**
Through **Retrieval-Augmented Generation**, every response is grounded in official WHO and Ministry of Health protocols. 

**Visual:** Red text on screen: "EMERGENCY: RED FLAG DETECTED".
**Audio (Voiceover):**
Safety is our priority. A hard-coded "Red Flag" layer monitors every message. If a life-threatening symptom is detected, the system immediately triggers an emergency alert, bypassing the LLM to provide instant, life-saving instructions.

---

## SCENE 4: THE VISION (2:15 - 3:00)
**Visual:** Close up of a person smiling while looking at an SMS response. The hardware setup is shown one last time.
**Audio (Voiceover):**
Dawa AI doesn’t replace doctors. It helps people know when they need one. We are placing a "Digital Nurse" in the pocket of every citizen, regardless of their data plan or location.

**Visual:** Final Slide: "Dawa AI - Bridging the Healthcare Gap. Powered by Gemma 4."
**Audio (Voiceover):**
Because access to life-saving information should not depend on access to the internet.

---

## PRODUCTION TIPS FOR THE TEAM:
1. **The Demo:** When filming the SMS part, make sure the camera is steady. If you can't film a real phone, use an SMS mockup tool, but **definitely** show the real Arduino hardware on your desk.
2. **The Hardware:** Show the SIM card bheing inserted or the antenna of the SIM800L. It emphasizes the "Offline/GSM" aspect which judges love.
3. **The AI:** Briefly show the terminal running Ollama. This proves you are running Gemma 4 locally.
4. **The Silicon:** Mention the **RP2040's dual-core capability** for handling the GSM handshake and triage logic simultaneously.
5. **Tone:** The first half should be slow and serious.
 The second half (Solution) should be energetic and optimistic.
