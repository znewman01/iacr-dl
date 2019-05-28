# -*- coding: utf-8 -*-

import io
import unittest
from pathlib import Path

from . import Article


# Test Case Wishlist
# - paragraphs in abstract
# - multiple authors
TEST_DATA_DIR = Path(__file__).parent.absolute() / "data"


def _get_html(fname):
    with open(TEST_DATA_DIR / fname) as f:
        return f.read()


class ArticleTests(unittest.TestCase):
    # modified from https://ia.cr/2019/579
    def test_parse_html_basic(self) -> None:
        actual = Article.parse_html(_get_html("basic.html"))
        expected = Article(
            "BlockQuick: Super-Light Client Protocol for Blockchain",
            ["Dominic Letz"],
            (
                "Today server authentication is largely handled through Public Key "
                "Infrastructure (PKI) in both the private and the public sector."
            ),
            ["cryptographic protocols / blockchain", "proof of work"],
            "2019/579",
        )
        self.assertEqual(actual, expected)

    # modified from https://ia.cr/2019/549
    def test_parse_html_multi_author(self):
        article = Article.parse_html(_get_html("multi-paragraph.html"))
        self.assertEqual(
            article.authors,
            [
                "Arka Rai Choudhuri",
                "Pavel Hubacek",
                "Chethan Kamath",
                "Krzysztof Pietrzak",
                "Alon Rosen",
                "Guy N. Rothblum",
            ],
        )

    def test_pdf_link(self) -> None:
        article = Article("Title", ["Author"], "Abstract", [], "2000/123")
        self.assertEqual(article.pdf_link, "https://eprint.iacr.org/2000/123.pdf")


if __name__ == "__main__":
    unittest.main()
