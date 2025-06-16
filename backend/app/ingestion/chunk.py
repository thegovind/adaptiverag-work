import tiktoken
import hashlib
from typing import Iterator, Dict

def chunk_document(text: str, *, size: int = 1000, overlap: int = 20, company: str = "", year: int = 0) -> Iterator[Dict]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    
    for i in range(0, len(tokens), size - overlap):
        window = tokens[i : i + size]
        chunk_text = enc.decode(window)
        
        if len(chunk_text.strip()) < 50:
            continue
            
        chunk_id = hashlib.md5(f"{company}_{year}_{chunk_text}".encode()).hexdigest()
        
        yield {
            "id": chunk_id,
            "content": chunk_text.strip(),
            "source": f"{company}_{year}_10-K",
            "company": company,
            "year": year
        }
