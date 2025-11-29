import json
from pathlib import Path
import pandas as pd
from fuzzywuzzy import process

HGNC_TSV = Path("data/raw/databases/hgnc_complete_set.txt")
NER_IN = Path("data/processed/ner_predictions.jsonl")
OUT = Path("data/processed/normalized_entities.jsonl")

if not HGNC_TSV.exists():
    raise SystemExit("Place HGNC file at data/raw/databases/hgnc_complete_set.txt")

hgnc = pd.read_csv(HGNC_TSV, sep="\t", dtype=str, low_memory=False)
# create lookup tables
symbol_to_id = dict(zip(hgnc["symbol"].fillna(""), hgnc["hgnc_id"].fillna("")))
# collect alias / previous symbols
alias_map = {}
for _, row in hgnc.iterrows():
    hid = row.get("hgnc_id")
    for col in ("alias_symbol", "prev_symbol"):
        val = row.get(col)
        if pd.notna(val):
            for token in str(val).split("|"):
                alias_map[token] = hid

symbol_list = list(set(list(symbol_to_id.keys()) + list(alias_map.keys())))

def fuzzy_match(name, limit=3):
    return process.extract(name, symbol_list, limit=limit)

with open(NER_IN, "r", encoding="utf-8") as fin, open(OUT, "w", encoding="utf-8") as fout:
    for line in fin:
        doc = json.loads(line)
        out_norm = []
        for e in doc.get("entities", []):
            label = e.get("entity_group","").lower()
            if label in ("gene","protein","gene_name","protein_name"):
                mention = e.get("word")
                if not mention:
                    continue
                # exact symbol
                hid = symbol_to_id.get(mention)
                if hid:
                    out_norm.append({"mention": mention, "hgnc_id": hid, "method": "exact"})
                    continue
                # alias match
                if mention in alias_map:
                    out_norm.append({"mention": mention, "hgnc_id": alias_map[mention], "method": "alias"})
                    continue
                # fuzzy
                cand = fuzzy_match(mention, limit=1)
                if cand:
                    out_norm.append({"mention": mention, "candidate": cand[0], "method": "fuzzy", "score": cand[0][1]})
                else:
                    out_norm.append({"mention": mention, "candidate": [], "method": "none"})
        doc["normalized_genes"] = out_norm
        fout.write(json.dumps(doc, ensure_ascii=False) + "\n")
print("Saved normalized entities to", OUT)
