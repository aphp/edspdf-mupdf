![Tests](https://img.shields.io/github/actions/workflow/status/aphp/edspdf-mupdf/tests.yml?branch=main&label=tests&style=flat-square)
[![Documentation](https://img.shields.io/github/actions/workflow/status/aphp/edspdf-mupdf/documentation.yml?branch=main&label=docs&style=flat-square)](https://aphp.github.io/edspdf-mupdf/latest/)
[![PyPI](https://img.shields.io/pypi/v/edspdf-mupdf?color=blue&style=flat-square)](https://pypi.org/project/edspdf-mupdf/)
[![Codecov](https://img.shields.io/codecov/c/github/aphp/edspdf-mupdf?logo=codecov&style=flat-square)](https://codecov.io/gh/aphp/edspdf-mupdf)
[![DOI](https://zenodo.org/badge/517726737.svg)](https://zenodo.org/badge/latestdoi/517726737)

# edspdf-mupdf

edspdf-mupdf provides a MuPdf-based PDF parser component for [EDS-PDF](https://github.com/aphp/edspdf)

Beware, MuPdf is **AGPL-licensed**: edspdf-mupdf is therefore also AGPL-licensed, and any model depending on this component must be too.

## Getting started

Install the library with pip:

<div class="termy">

```console
$ pip install edspdf-mupdf
```

</div>

## Usage

```
from edspdf import Pipeline

model = Pipeline()
model.add_pipe('mupdf-extractor')

model(pdf_bytes)
```

Visit the [documentation](https://aphp.github.io/edspdf/) for more information!

## Acknowledgement

We would like to thank [Assistance Publique – Hôpitaux de Paris](https://www.aphp.fr/)
and [AP-HP Foundation](https://fondationrechercheaphp.fr/) for funding this project.
