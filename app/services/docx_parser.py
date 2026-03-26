from docx import Document


class DocxParser:
    def parse(self, path: str) -> dict:
        document = Document(path)
        paragraphs: list[dict] = []
        current_section: str | None = None

        for index, paragraph in enumerate(document.paragraphs, start=1):
            text = paragraph.text.strip()
            if not text:
                continue
            style = paragraph.style.name if paragraph.style else "Normal"
            if style.lower().startswith("heading"):
                current_section = text
            paragraphs.append(
                {
                    "paragraph_ref": f"p_{index:04d}",
                    "style": style,
                    "section": current_section,
                    "text": text,
                    "index": index - 1,
                }
            )

        return {"paragraphs": paragraphs}


docx_parser = DocxParser()
