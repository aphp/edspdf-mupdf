import multiprocessing
import platform

try:
    if platform.system() == "Darwin":
        multiprocessing.set_start_method("spawn")
except:
    pass

from io import BytesIO
from typing import Union

import fitz as mupdf
from edspdf import Component, registry
from edspdf.models import PDFDoc, SpannedStyle, TextBox


@registry.factory.register("mupdf-extractor")
class MuPdfExtractor(Component[Union[str, PDFDoc], PDFDoc]):
    def __init__(
        self,
        extract_style: bool = False,
        raise_on_error: bool = False,
    ):
        """
        Extractor object. Given a PDF byte stream, produces a list of elements.

        Parameters
        ----------
        extract_style : bool
            Extract style
        raise_on_error: bool
            Whether to raise an error when parsing a corrupted PDF (defauts to False)
        """
        super().__init__()

        self.extract_style = extract_style
        self.raise_on_error = raise_on_error

    def __call__(self, doc: Union[PDFDoc, bytes]) -> PDFDoc:
        """
        Extract lines from a PDF from all lines in the PDF.

        Arguments
        ---------
        doc:
            PDF document

        Returns
        -------
        PDFDoc:
            PDF document
        """

        if not isinstance(doc, PDFDoc):
            content = bytes(doc)
            doc = PDFDoc(id=str(hash(content)), content=content)
        content = doc.content

        try:
            mupdf_doc = mupdf.Document(stream=BytesIO(content))
        except Exception:
            if self.raise_on_error:
                raise
            doc.lines = []
            doc.error = True
            return doc

        lines = []
        page_count = 0
        for page_no, page in enumerate(mupdf_doc):
            page_count += 1

            w, h = page.mediabox_size

            for b in page.get_textpage().extractDICT()["blocks"]:
                for line in b["lines"]:
                    text = ""
                    styles = []
                    for span in line["spans"]:
                        span_text = (
                            span["text"].encode("utf-8", "ignore").decode("utf-8")
                        )
                        if len(text) == 0:
                            text = span_text.lstrip()
                        else:
                            text += span_text

                        if self.extract_style:
                            end = len(text.rstrip())
                            begin = end - len(span_text.strip())
                            lower_font = span["font"].lower()
                            styles.append(
                                SpannedStyle(
                                    fontname=span["font"],
                                    italic="italic" in lower_font,
                                    bold="bold" in lower_font,
                                    begin=begin,
                                    end=end,
                                )
                            )
                    text = text.rstrip()
                    if len(text) > 0:
                        x0 = line["bbox"][0] / w
                        y0 = line["bbox"][1] / h
                        x1 = line["bbox"][2] / w
                        y1 = line["bbox"][3] / h

                        for _ in range(page.rotation // 90):
                            x0, y0, x1, y1 = 1 - y1, x0, 1 - y0, x1

                        lines.append(
                            TextBox(
                                x0=x0,
                                x1=x1,
                                y0=y0,
                                y1=y1,
                                page_width=w,
                                page_height=h,
                                text=text,
                                page=page_no,
                                styles=tuple(styles),
                            )
                        )

        doc.lines = sorted(
            [
                line
                for line in lines
                if line.x0 >= 0
                and line.y0 >= 0
                and line.x1 <= 1
                and line.y1 <= 1
                and len(line.text.strip()) > 0
            ]
        )

        return doc
