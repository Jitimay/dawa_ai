import chromadb
from chromadb.utils import embedding_functions

# Initialize local ChromaDB
# This will create a 'medical_knowledge' folder to persist data
client = chromadb.PersistentClient(path="./medical_knowledge")

# Use a lightweight embedding model suitable for edge devices
# In a real scenario, you'd download the model files for fully offline use
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")

collection = client.get_or_create_collection(
    name="triage_guidelines",
    embedding_function=embed_fn
)

def add_guideline(text, metadata):
    """Adds a medical guideline snippet to the vector store."""
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[str(hash(text))]
    )

def query_guidelines(query_text, n_results=2):
    """Searches for relevant medical guidelines based on patient symptoms."""
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results['documents'][0] if results['documents'] else []

# INITIAL SEED DATA (Burundi-specific examples)
if __name__ == "__main__":
    seed_data = [
        # MALARIA
        {"text": "Ibimenyetso vya Malaria: Umuriro, gushaka kudandaza, kuribwa umutwe. Ivuriro: Kunywa imiti ya Coartem. Urashobora gufata paracetamol ku muriro.", "meta": {"topic": "malaria", "lang": "kirundi"}},
        {"text": "Symptoms of Malaria: Fever, nausea, headache. Treatment: Coartem medication at clinic. You can take paracetamol for fever.", "meta": {"topic": "malaria", "lang": "english"}},
        {"text": "Symptômes de la Malaria: Fièvre, nausées, maux de tête. Traitement: Médicament Coartem à la clinique. Vous pouvez prendre du paracétamol pour la fièvre.", "meta": {"topic": "malaria", "lang": "french"}},
        
        # CHOLERA / HYGIENE
        {"text": "Ibimenyetso vy'indwara y'impisanzuya (Cholera): Gucibwamwo cane, kudandaza. Gutabara: Kunywa amazi yateguwe (SRO). Karaba n'isabuni.", "meta": {"topic": "cholera", "lang": "kirundi"}},
        {"text": "Cholera symptoms: Severe diarrhea, vomiting. Action: Drink Oral Rehydration Salts (ORS). Wash hands with soap.", "meta": {"topic": "cholera", "lang": "english"}},
        
        # MATERNAL HEALTH
        {"text": "Abagore bibungenze: Ibimenyetso bishobora gutera amakenga: Amaraso asohoka, umutwe urya cane, amaso ahumye. Genda kwa muganga ubu nyene.", "meta": {"topic": "maternal", "lang": "kirundi"}},
        {"text": "Maternal Health: Warning signs include vaginal bleeding, severe headache, blurred vision. Go to the hospital immediately.", "meta": {"topic": "maternal", "lang": "english"}},
        
        # NUTRITION
        {"text": "Imirire mibi (Malnutrition): Ibimenyetso: Ukugabanuka k'ibiro, ukubyimba amaguru. Genda ku kigo c'amagara y'abantu uze guhabwa imfashanyo.", "meta": {"topic": "nutrition", "lang": "kirundi"}},
        
        # GENERAL RED FLAGS
        {"text": "Red Flags: Unconsciousness, severe bleeding, difficulty breathing, convulsions. ACTION: Immediate hospital transfer.", "meta": {"topic": "emergency", "lang": "english"}},
        {"text": "Urgence: Ukubura ubwenge, amaraso menshi, guhumeka nabi, gutitira. ACTION: Genda kwa muganga ubu nyene.", "meta": {"topic": "emergency", "lang": "kirundi"}},

        # TUBERCULOSIS (TB)
        {"text": "Ibimenyetso vya TB (Igituntu): Inkorora imaze igihe kirekire, kubira ibyuya ijoro, gutakaza ibiro. Genda kwa muganga upimwe igituza.", "meta": {"topic": "tb", "lang": "kirundi"}},
        {"text": "Symptoms of Tuberculosis (TB): Persistent cough, night sweats, weight loss. Action: Visit clinic for chest screening.", "meta": {"topic": "tb", "lang": "english"}},

        # POISONING
        {"text": "Kunywa uburozi (Poisoning): Ibimenyetso: Ukuraguza, gucibwamwo, gutitira. ACTION: Genda kwa muganga ubu nyene! Ntutebe.", "meta": {"topic": "poisoning", "lang": "kirundi"}},
        {"text": "Accidental Poisoning: Symptoms include vomiting, diarrhea, convulsions. ACTION: Immediate hospital transfer. Do not wait.", "meta": {"topic": "poisoning", "lang": "english"}},

        # SNAKE BITE
        {"text": "Kurumwa n'incira (Snake bite): ACTION: Ntukiruke, funga hejuru y'aho yarumye gato, genda kwa muganga ubu nyene!", "meta": {"topic": "snake_bite", "lang": "kirundi"}},
        {"text": "Snake bite: ACTION: Keep the limb still, apply a light bandage above the bite, and go to the hospital immediately.", "meta": {"topic": "snake_bite", "lang": "english"}},

        # DEHYDRATION
        {"text": "Ubukame bw'amazi (Dehydration): Ibimenyetso: Amaso acecetse, iyeri ryasutse (ku mwana), intege nke. Gutabara: Nywa amazi ya SRO vuba.", "meta": {"topic": "dehydration", "lang": "kirundi"}},
        {"text": "Dehydration: Symptoms include sunken eyes, sunken fontanelle (in infants), extreme weakness. Action: Drink Oral Rehydration Salts (ORS) immediately.", "meta": {"topic": "dehydration", "lang": "english"}},

        # WATER SAFETY
        {"text": "Kwirinda indwara z'amazi: Banze uyateke amazi cyangwa uyashiremo umuti (Sur'Eau) mbere yo kuyanywa kugira wirinde impisanzuya.", "meta": {"topic": "hygiene", "lang": "kirundi"}},
        {"text": "Water Safety: Boil water or use treatment (Sur'Eau) before drinking to prevent diarrhea and cholera.", "meta": {"topic": "hygiene", "lang": "english"}}
    ]
    
    for item in seed_data:
        add_guideline(item["text"], item["meta"])
    print(f"Vector database expanded with {len(seed_data)} health protocols.")
