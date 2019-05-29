# -*- coding: utf-8 -*-

import io
import unittest
from pathlib import Path

from parameterized import parameterized

from . import Article, ArticleId

TEST_DATA_DIR = Path(__file__).parent.absolute() / "data"


def _get_test_resource(fname):
    with open(TEST_DATA_DIR / fname) as f:
        return f.read()


class ArticleTests(unittest.TestCase):
    # modified from https://ia.cr/2019/579
    def test_parse_html_basic(self) -> None:
        actual = Article.parse_html(_get_test_resource("basic.html"))
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
    def test_parse_html_multi_author(self) -> None:
        article = Article.parse_html(_get_test_resource("multi-paragraph.html"))
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

    # modified from https://ia.cr/2019/549
    def test_parse_html_multi_paragraph(self) -> None:
        article = Article.parse_html(_get_test_resource("multi-paragraph.html"))
        expected_abstract = _get_test_resource("multi-paragraph-abstract.txt").rstrip()
        self.assertEqual(article.abstract, expected_abstract)

    # modified from https://ia.cr/2007/478
    def test_parse_html_multi_paragraph2(self) -> None:
        article = Article.parse_html(_get_test_resource("multi-paragraph2.html"))
        expected_abstract = _get_test_resource("multi-paragraph2-abstract.txt").rstrip()
        self.assertEqual(article.abstract, expected_abstract)

    def test_pdf_link(self) -> None:
        article = Article("Title", ["Author"], "Abstract", [], "2000/123")
        self.assertEqual(article.pdf_link, "https://eprint.iacr.org/2000/123.pdf")


class ArticleIdTests(unittest.TestCase):
    @parameterized.expand([("1990/000",), ("2000/123",), ("2020/999",)])
    def test_validate_good(self, id_: str) -> None:
        article_id = ArticleId.from_string(id_)
        self.assertEqual(article_id.id, id_)

    @parameterized.expand(
        [("abcdef"), ("20020/123"), ("1990-000",), ("200/123",), ("2020/9999",)]
    )
    def test_validate_bad(self, id_: str) -> None:
        with self.assertRaises(ValueError):
            ArticleId.from_string(id_)


if __name__ == "__main__":
    unittest.main()
