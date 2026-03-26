import re

import fitz


class PdfParser:
    def parse(self, path: str) -> dict:
        doc = fitz.open(path)
        excerpts: list[dict] = []

        for page_index, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            for line in page_text.splitlines():
                cleaned = line.strip()
                if not cleaned or len(cleaned) < 20:
                    continue
                excerpts.append(
                    {
                        "page": page_index,
                        "text": cleaned,
                        "similarity_score": self._extract_similarity(cleaned),
                        "risk_type": self._detect_risk(cleaned),
                        "low_confidence_parse": False,
                    }
                )

        return {"excerpts": excerpts}

    def _extract_similarity(self, text: str) -> float:
        match = re.search(r"(\d{1,3})\s*%", text)
        if not match:
            return 0.7
        return max(0.0, min(float(match.group(1)) / 100.0, 1.0))

    def _detect_risk(self, text: str) -> str:
        lowered = text.lower()
        if "citation" in lowered or "trich dan" in lowered:
            return "MISSING_CITATION"
        if "verbatim" in lowered:
            return "VERBATIM"
        if "similar" in lowered or "tuong dong" in lowered:
            return "CLOSE_PARAPHRASE"
        return "OTHER"


pdf_parser = PdfParser()
