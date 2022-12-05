import pytest
from blocks_ground_truth import blank_blocks, pdf_blocks, styles_blocks

from edspdf_mupdf import MuPdfExtractor


def test_mupdf(pdf, styles_pdf, blank_pdf):
    extractor = MuPdfExtractor(extract_style=False)

    pytest.nested_approx(extractor(pdf).lines, pdf_blocks, abs=5e-2)
    pytest.nested_approx(extractor(styles_pdf).lines, styles_blocks, abs=5e-2)
    pytest.nested_approx(extractor(blank_pdf).lines, blank_blocks, abs=5e-2)
