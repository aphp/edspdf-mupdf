import os
from pathlib import Path

import pytest
from pytest import fixture
from utils import nested_approx

pytest.nested_approx = nested_approx

TEST_DIR = Path(__file__).parent


@pytest.fixture
def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


@fixture(scope="session")
def pdf():
    path = TEST_DIR / "resources" / "test.pdf"
    return path.read_bytes()


@fixture(scope="session")
def blank_pdf():
    path = TEST_DIR / "resources" / "blank.pdf"
    return path.read_bytes()


@fixture(scope="session")
def styles_pdf():
    path = TEST_DIR / "resources" / "styles.pdf"
    return path.read_bytes()


@fixture(scope="session")
def letter_pdf():
    path = TEST_DIR / "resources" / "letter.pdf"
    return path.read_bytes()


@fixture(scope="session")
def error_pdf():
    path = TEST_DIR / "resources" / "error.pdf"
    return path.read_bytes()
