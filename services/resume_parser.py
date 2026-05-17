from pypdf import PdfReader


class ResumeParser:


    @staticmethod
    def parse_pdf(file_path):

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            text += (
                page.extract_text() or ""
            )

        return text