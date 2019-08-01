# -*- coding: utf-8 -*-

import io
import itertools
import json
import unittest
from pathlib import Path
from typing import List, Tuple

import requests
import responses
from parameterized import parameterized

from . import Article, ArticleId, fetch, fetch_and_parse, parse_args

TEST_DATA_DIR = Path(__file__).parent.absolute() / "data"


def _get_test_resource(fname):
    with open(TEST_DATA_DIR / fname) as f:
        return f.read()


BASIC_ARTICLE = Article(
    "BlockQuick: Super-Light Client Protocol for Blockchain",
    ["Dominic Letz"],
    (
        "Today server authentication is largely handled through Public Key "
        "Infrastructure (PKI) in both the private and the public sector."
    ),
    ["cryptographic protocols / blockchain", "proof of work"],
    "2019/579",
)


class ArticleTests(unittest.TestCase):
    # modified from https://ia.cr/2019/579
    def test_parse_html_basic(self) -> None:
        actual = Article.parse_html(_get_test_resource("basic.html"))
        self.assertEqual(actual, BASIC_ARTICLE)

    # modified from https://ia.cr/2019/579
    def test_cite_basic(self) -> None:
        self.assertEqual(BASIC_ARTICLE.bibtex, _get_test_resource("basic.bib"))

    # modified from https://ia.cr/2019/579
    def test_to_dict_basic(self) -> None:
        res = BASIC_ARTICLE.to_dict()
        self.assertEqual(res.pop("title"), BASIC_ARTICLE.title)
        self.assertEqual(res.pop("authors"), BASIC_ARTICLE.authors)
        self.assertEqual(res.pop("abstract"), BASIC_ARTICLE.abstract)
        self.assertEqual(res.pop("keywords"), BASIC_ARTICLE.keywords)
        self.assertEqual(res.pop("id"), BASIC_ARTICLE.id)
        self.assertEqual(res.pop("bibtex"), BASIC_ARTICLE.bibtex)
        self.assertEqual(res.pop("pdf_link"), BASIC_ARTICLE.pdf_link)
        self.assertFalse(res)  # no extra keys

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

    def test_cite_multi_author(self) -> None:
        article = Article.parse_html(_get_test_resource("multi-paragraph.html"))
        self.assertEqual(article.bibtex, _get_test_resource("multi-paragraph.bib"))

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

    # modified from https://ia.cr/2007/478
    def test_cite_multi_paragraph2(self) -> None:
        article = Article.parse_html(_get_test_resource("multi-paragraph2.html"))
        self.assertEqual(article.bibtex, _get_test_resource("multi-paragraph2.bib"))

    def test_parse_html_no_keywords(self) -> None:
        actual = Article.parse_html(_get_test_resource("no-keywords.html"))
        self.assertEqual(actual.keywords, [])

    def test_pdf_link(self) -> None:
        article = Article("Title", ["Author"], "Abstract", [], "2000/123")
        self.assertEqual(article.pdf_link, "https://eprint.iacr.org/2000/123.pdf")


def _make_identifier_variations(id_: str) -> List[str]:
    _PREFIXES = ["http://", "https://", ""]
    _HOSTS = ["ia.cr", "eprint.iacr.org"]
    return [f"{prefix}{host}/{id_}" for host in _HOSTS for prefix in _PREFIXES] + [id_]


def _make_test_cases(ids: List[str]) -> List[Tuple[str, str]]:
    return [(v, id_) for id_ in ids for v in _make_identifier_variations(id_)]


class ArticleIdTests(unittest.TestCase):
    @parameterized.expand(_make_test_cases(["1990/000", "2000/123", "2020/9999"]))
    def test_validate_good(self, id_string: str, id_: str) -> None:
        article_id = ArticleId.from_string(id_string)
        self.assertEqual(article_id.id, id_)

    @parameterized.expand(
        _make_test_cases(["abcdef", "20020/123", "1990-000", "200/123", "2019/0123"])
    )
    def test_validate_bad(self, id_string: str, id_: str) -> None:
        del id_  # unused in test_validate_bad
        with self.assertRaises(ValueError):
            ArticleId.from_string(id_string)


class IacrFetcherTests(unittest.TestCase):
    @parameterized.expand([(["1990/000"],), (["2000/234"],)])
    def test_parse_args_good(self, argv: List[str]) -> None:
        parse_args(argv)

    @parameterized.expand([(["1990/000", "extra"],), ([],), (["123/456"],)])
    def test_parse_args_bad(self, argv: List[str]) -> None:
        with self.assertRaises(SystemExit):
            parse_args(argv)

    @responses.activate
    def test_fetch_good(self) -> None:
        article_id = ArticleId("2009/123")
        responses.add(
            responses.GET,
            "https://eprint.iacr.org/2009/123",
            body="<html />",
            status=200,
        )
        html = fetch(article_id)
        self.assertEqual(html, "<html />")

    @responses.activate
    def test_fetch_bad(self) -> None:
        article_id = ArticleId("2009/123")
        responses.add(
            responses.GET,
            "https://eprint.iacr.org/2009/123",
            body="not found",
            status=404,
        )
        with self.assertRaises(requests.exceptions.HTTPError):
            fetch(article_id)

    @responses.activate
    def test_fetch_and_parse_good(self) -> None:
        responses.add(
            responses.GET,
            "https://eprint.iacr.org/2009/123",
            body=_get_test_resource("basic.html"),
            status=200,
        )

        json_str = fetch_and_parse(["2009/123"])

        parsed_article = Article.from_dict(json.loads(json_str))
        self.assertEqual(parsed_article, BASIC_ARTICLE)

    @responses.activate
    def test_fetch_and_parse_bad(self) -> None:
        responses.add(
            responses.GET,
            "https://eprint.iacr.org/2009/123",
            body="not found",
            status=404,
        )
        with self.assertRaises(requests.exceptions.HTTPError):
            fetch_and_parse(["2009/123"])


if __name__ == "__main__":
    unittest.main()
