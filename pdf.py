
import fitz
import os


class PDFEditor:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def get_page_count(self):
        return len(self.doc)

    def extract_text(self, page_number=None):
        if page_number is not None:
            return self.doc[page_number].get_text()

        return [
            page.get_text()
            for page in self.doc
        ]

    def add_text(self, page_number, text, x=50, y=50,
                 fontsize=12, color=(0, 0, 0)):

        page = self.doc[page_number]

        page.insert_text(
            (x, y),
            text,
            fontsize=fontsize,
            color=color
        )

    def search_text(self, text):
        results = []

        for index, page in enumerate(self.doc):
            matches = page.search_for(text)

            for rect in matches:
                results.append({
                    "page": index,
                    "position": rect
                })

        return results

    def replace_text(self, old_text, new_text):
        """
        Basic visual replacement.
        This covers matching text with white rectangles
        and inserts replacement text.
        Review the output for layout issues.
        """

        for page in self.doc:
            matches = page.search_for(old_text)

            for rect in matches:
                page.add_redact_annot(
                    rect,
                    fill=(1, 1, 1)
                )

            if matches:
                page.apply_redactions()

                for rect in matches:
                    page.insert_textbox(
                        rect,
                        new_text,
                        fontsize=10,
                        color=(0, 0, 0)
                    )

    def add_image(self, page_number, image_path,
                  rect=(50, 50, 200, 200)):

        page = self.doc[page_number]
        page.insert_image(
            fitz.Rect(*rect),
            filename=image_path
        )

    def rotate_page(self, page_number, degrees=90):
        page = self.doc[page_number]
        page.set_rotation(degrees)

    def delete_page(self, page_number):
        self.doc.delete_page(page_number)

    def add_watermark(self, text):
        for page in self.doc:
            page.insert_text(
                (100, 100),
                text,
                fontsize=35,
                color=(0.7, 0.7, 0.7),
                overlay=True
            )

    def save(self, output_path):
        self.doc.save(output_path)

    def close(self):
        self.doc.close()

    @staticmethod
    def merge_pdfs(pdf_files, output_path):
        merged = fitz.open()

        for file in pdf_files:
            source = fitz.open(file)
            merged.insert_pdf(source)
            source.close()

        merged.save(output_path)
        merged.close()

    @staticmethod
    def extract_pages(pdf_path, output_path,
                      start_page, end_page):

        source = fitz.open(pdf_path)
        output = fitz.open()

        output.insert_pdf(
            source,
            from_page=start_page,
            to_page=end_page
        )

        output.save(output_path)

        output.close()
        source.close()


# Example usage

if __name__ == "__main__":

    editor = PDFEditor("input.pdf")

    print("Pages:", editor.get_page_count())

    print(editor.extract_text())

    editor.add_text(
        page_number=0,
        text="Modified PDF",
        x=100,
        y=100,
        fontsize=16
    )

    editor.add_watermark("CONFIDENTIAL")

    editor.save("modified.pdf")

    editor.close()

    print("PDF modified successfully!")
