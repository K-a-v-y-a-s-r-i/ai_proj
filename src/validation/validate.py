import pandas as pd
from pathlib import Path

DG_FILE = Path("data/raw/databases/disgenet_curated.tsv")

if DG_FILE.exists():
    dg = pd.read_csv(DG_FILE, sep="\t", low_memory=False)
else:
    dg = None
    print("DisGeNET file not found. Place disgenet_curated.tsv at data/raw/databases/ to enable novelty checks.")

def check_known(gene_symbol: str, disease_name: str) -> bool:
    if dg is None:
        return False
    hits = dg[(dg["geneSymbol"].str.upper() == gene_symbol.upper()) &
              (dg["diseaseName"].str.contains(disease_name, case=False, na=False))]
    return not hits.empty

def novelty_score(gene_symbol: str, disease_name: str) -> float:
    return 0.0 if check_known(gene_symbol, disease_name) else 1.0

if __name__ == "__main__":
    gene = "BRCA1"
    disease = "breast cancer"
    print("Novelty score for BRCA1 / breast cancer:", novelty_score(gene, disease))
