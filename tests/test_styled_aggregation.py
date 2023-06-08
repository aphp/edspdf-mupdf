from itertools import cycle

import edspdf
from edspdf.pipes.aggregators.simple import SimpleAggregator
from edspdf.structures import Page, PDFDoc, TextBox
from edspdf_mupdf import MuPdfExtractor


def test_no_style():
    doc = PDFDoc(
        content=b"",
        pages=[],
    )
    doc.pages = [
        Page(doc=doc, page_num=0, width=1, height=1),
        Page(doc=doc, page_num=1, width=1, height=1),
    ]
    # fmt: off
    doc.content_boxes = [
        TextBox(doc=doc, page_num=0, x0=0.1, y0=0.1, x1=0.5, y1=0.2, label="body", text="Begin"),  # noqa: E501
        TextBox(doc=doc, page_num=0, x0=0.6, y0=0.1, x1=0.7, y1=0.2, label="body", text="and"),  # noqa: E501
        TextBox(doc=doc, page_num=0, x0=0.8, y0=0.1, x1=0.9, y1=0.2, label="body", text="end."),  # noqa: E501
        TextBox(doc=doc, page_num=1, x0=0.8, y0=0.1, x1=0.9, y1=0.2, label="body", text="New page"),  # noqa: E501
    ]  # fmt: on

    aggregator = SimpleAggregator()
    assert aggregator(doc).aggregated_texts["body"].text == "Begin and end.\n\nNew page"


def test_styled_aggregation(styles_pdf):
    extractor = MuPdfExtractor(extract_style=True)
    aggregator = SimpleAggregator()

    doc = extractor(styles_pdf)
    for b, label in zip(doc.text_boxes, cycle(["header", "body"])):
        b.label = label
    doc = aggregator(doc)
    texts = {k: v.text for k, v in doc.aggregated_texts.items()}
    props = {k: v.properties for k, v in doc.aggregated_texts.items()}

    assert set(texts.keys()) == {"body", "header"}
    assert isinstance(props["body"], list)

    for value in props.values():
        assert value[0].begin == 0

    pairs = set()
    for label in texts.keys():
        for prop in props[label]:
            pairs.add(
                (
                    texts[label][prop.begin : prop.end],
                    " ".join(
                        filter(
                            bool,
                            (
                                ("italic" if prop.italic else ""),
                                ("bold" if prop.bold else ""),
                            ),
                        )
                    ),
                )
            )

    assert pairs == {
        ("This is a", ""),
        ("test", "bold"),
        ("to check EDS-PDF’s", ""),
        ("ability", "italic"),
        ("to detect changing styles.", ""),
        ("Let’s up the stakes, with", ""),
        ("intra", "italic"),
        ("-word change. Or better yet,", ""),
        ("this mi", "bold"),
        ("ght be hard.", ""),
    }


def test_styled_aggregation_letter(letter_pdf):
    extractor = MuPdfExtractor(extract_style=True)
    aggregator = SimpleAggregator()

    doc = extractor(letter_pdf)
    for b, label in zip(doc.content_boxes, cycle(["header", "body"])):
        b.label = label
    doc = aggregator(doc)
    texts = {k: v.text for k, v in doc.aggregated_texts.items()}
    props = {k: v.properties for k, v in doc.aggregated_texts.items()}

    assert set(texts.keys()) == {"body", "header"}
    assert isinstance(props["body"], list)

    for value in props.values():
        assert value[0].begin == 0

    pairs = set()
    for label in texts.keys():
        for prop in props[label]:
            pairs.add(
                (
                    texts[label][prop.begin : prop.end],
                    " ".join(
                        filter(
                            bool,
                            (
                                ("italic" if prop.italic else ""),
                                ("bold" if prop.bold else ""),
                            ),
                        )
                    ),
                )
            )


def test_unsorted_aggregation(letter_pdf):
    pipeline = edspdf.Pipeline()
    pipeline.add_pipe("mupdf-extractor", config={"sort_mode": "none"})
    pipeline.add_pipe(
        "mask-classifier",
        config={"x0": 0.0, "x1": 1, "y0": 0.3, "y1": 0.5},
    )
    pipeline.add_pipe("simple-aggregator", config={"sort": False})
    doc = pipeline(letter_pdf)

    # fmt: off
    assert doc.aggregated_texts["body"].text == """\
SANTÉ PUBLIQUE

Pr  ABC
\uf028 : 01 23 45 67 89
\uf02a: a.bc@aphp.fr

Pr  ABC
\uf028 : 01 23 45 67 89
\uf02a: a.bc@aphp.fr

Pr  ABC
\uf028 : 01 23 45 67 89
\uf02a: a.bc@aphp.fr Cher Pr ABC, Cher DEF,

Nous souhaitons remercier le CSE pour son avis favorable quant à l’accès aux données de
l’Entrepôt de Données de Santé du projet n° XXXX.

Nous avons bien pris connaissance des conditions requises pour cet avis favorable, c’est
pourquoi nous nous engageons par la présente à :

• Informer individuellement les patients concernés par la recherche, admis à l'AP-HP
avant juillet 2017, sortis vivants, et non réadmis depuis.

• Effectuer une demande d'autorisation à la CNIL en cas d'appariement avec d’autres"""
    # fmt: on


def test_sorted_lines_aggregation(letter_pdf):
    pipeline = edspdf.Pipeline()
    pipeline.add_pipe("mupdf-extractor", config={"sort_mode": "lines"})
    pipeline.add_pipe(
        "mask-classifier",
        config={"x0": 0.0, "x1": 1, "y0": 0.3, "y1": 0.5},
    )
    pipeline.add_pipe("simple-aggregator", config={"sort": False})
    doc = pipeline(letter_pdf)

    # fmt: off
    assert doc.aggregated_texts["body"].text == """\
Cher Pr ABC, Cher DEF,

SANTÉ PUBLIQUE
Nous souhaitons remercier le CSE pour son avis favorable quant à l’accès aux données de
Pr  ABC l’Entrepôt de Données de Santé du projet n° XXXX.
\uf028 : 01 23 45 67 89
\uf02a: a.bc@aphp.fr Nous avons bien pris connaissance des conditions requises pour cet avis favorable, c’est
pourquoi nous nous engageons par la présente à :
Pr  ABC
\uf028 : 01 23 45 67 89
• Informer individuellement les patients concernés par la recherche, admis à l'AP-HP
\uf02a: a.bc@aphp.fr
avant juillet 2017, sortis vivants, et non réadmis depuis.
Pr  ABC
\uf028 : 01 23 45 67 89 • Effectuer une demande d'autorisation à la CNIL en cas d'appariement avec d’autres
\uf02a: a.bc@aphp.fr"""  # noqa: E501
    # fmt: on


def test_sorted_blocks_aggregation(letter_pdf):
    pipeline = edspdf.Pipeline()
    pipeline.add_pipe("mupdf-extractor", config={"sort_mode": "blocks"})
    pipeline.add_pipe(
        "mask-classifier",
        config={"x0": 0.0, "x1": 1, "y0": 0.3, "y1": 0.5},
    )
    pipeline.add_pipe("simple-aggregator", config={"sort": False})
    doc = pipeline(letter_pdf)

    # fmt: off
    assert doc.aggregated_texts["body"].text == """\
Cher Pr ABC, Cher DEF,

SANTÉ PUBLIQUE
Nous souhaitons remercier le CSE pour son avis favorable quant à l’accès aux données de
Pr  ABC
\uf028 : 01 23 45 67 89
\uf02a: a.bc@aphp.fr

Pr  ABC
\uf028 : 01 23 45 67 89
\uf02a: a.bc@aphp.fr l’Entrepôt de Données de Santé du projet n° XXXX.

Nous avons bien pris connaissance des conditions requises pour cet avis favorable, c’est

• Informer individuellement les patients concernés par la recherche, admis à l'AP-HP
avant juillet 2017, sortis vivants, et non réadmis depuis. pourquoi nous nous engageons par la présente à :

• Effectuer une demande d'autorisation à la CNIL en cas d'appariement avec d’autres Pr  ABC
\uf028 : 01 23 45 67 89
\uf02a: a.bc@aphp.fr"""  # noqa: E501
    # fmt: on
