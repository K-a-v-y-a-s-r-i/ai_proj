import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.retrieval.query import retrieve

MODEL = "microsoft/biogpt"

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}  |  Loading model: {MODEL}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL).to(device)

def generate_hypothesis(gene: str, disease: str, k: int = 5):
    """
    Generate hypothesis and evidence for a gene-disease pair.
    """
    passages = retrieve(f"{gene} {disease}", k=k)
    context = "\n".join([p["text"] for p in passages])
    prompt = f"Gene: {gene}\nDisease: {disease}\nContext:\n{context}\nHypothesis:"

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        num_beams=4,
        early_stopping=True
    )

    hypothesis = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return hypothesis, passages

if __name__ == "__main__":
    gene = "BRCA1"
    disease = "breast cancer"
    hyp, evid = generate_hypothesis(gene, disease, k=5)
    print("Generated hypothesis:\n", hyp)
    print("\nSupporting evidence:")
    for p in evid:
        print("-", p["text"][:200], "...")
