import re, json
from pathlib import Path
import nltk
nltk.download("punkt", quiet=True)
from nltk import sent_tokenize

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "passages.jsonl"

def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\[\d+\]", "", s)
    s = s.replace("\n", " ")
    return s.strip()

def extract_text_from_pubmed_xml(xml: str) -> str:
    # very lightweight extractor for development
    m = re.search(r"<AbstractText.*?>(.*?)</AbstractText>", xml, flags=re.S|re.I)
    if m:
        return re.sub(r"<.*?>", "", m.group(1)).strip()
    # fallback: try ArticleTitle
    m2 = re.search(r"<ArticleTitle.*?>(.*?)</ArticleTitle>", xml, flags=re.S|re.I)
    if m2:
        return re.sub(r"<.*?>", "", m2.group(1)).strip()
    return ""

def passages_from_text(text: str, sentences_per_passage: int = 3):
    if not text:
        return []
    sents = sent_tokenize(text)
    return [" ".join(sents[i:i+sentences_per_passage]) for i in range(0, len(sents), sentences_per_passage)]

if __name__ == "__main__":
    xml_files = list(RAW_DIR.glob("*.xml"))
    if not xml_files:
        print("No XML files found in data/raw/ — run ingestion first.")
    with open(OUT_FILE, "w", encoding="utf-8") as fout:
        for f in xml_files:
            raw = f.read_text(encoding="utf-8", errors="ignore")
            txt = extract_text_from_pubmed_xml(raw)
            txt = clean_text(txt)
            for p in passages_from_text(txt, sentences_per_passage=3):
                record = {"source": f.name, "text": p}
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
    print("Wrote passages to", OUT_FILE)
