import requests
from pathlib import Path

DATA_RAW = Path("data/raw")
DATA_RAW.mkdir(parents=True, exist_ok=True)

def fetch_pubmed_abstract(pmid: str) -> str:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.text

if __name__ == "__main__":
    sample_pmids = ["31452104","30049270","31086495"]  # small sample list
    for pmid in sample_pmids:
        try:
            xml = fetch_pubmed_abstract(pmid)
            out = DATA_RAW / f"{pmid}.xml"
            out.write_text(xml, encoding="utf-8")
            print("Saved", out)
        except Exception as e:
            print("Error fetching", pmid, e)
