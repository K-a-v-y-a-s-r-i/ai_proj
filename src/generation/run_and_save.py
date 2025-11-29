import json
from pathlib import Path
from src.generation.generate import generate_hypothesis
from src.validation.validate import novelty_score

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_and_save(gene: str, disease: str, k: int = 5):
    print(f"Generating hypothesis for {gene} / {disease}...")
    hypothesis, evidence = generate_hypothesis(gene, disease, k=k)

    # Compute novelty
    novelty = novelty_score(gene, disease)

    result = {
        "gene": gene,
        "disease": disease,
        "hypothesis": hypothesis,
        "novelty_score": novelty,
        "evidence": evidence
    }

    out_file = OUTPUT_DIR / f"{gene}_{disease.replace(' ', '_')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Saved results to {out_file}")
    print("Hypothesis:", hypothesis)
    print("Novelty score:", novelty)
    return hypothesis, evidence

if __name__ == "__main__":
    run_and_save("BRCA1", "breast cancer", k=5)
