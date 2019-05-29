# -*- coding: utf-8 -*-
import argparse
import functools
import json
import re
import sys
from typing import List

import attr
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://eprint.iacr.org"


def _fix_spaces(text: str) -> str:
    return re.sub("  +", " ", text).strip()


def _fix_spaces_list(texts: List[str]) -> List[str]:
    return list(map(_fix_spaces, texts))


def _parse_abstract(soup: BeautifulSoup) -> str:
    abstract_paras = []
    first_paragraph = soup.find("b", text="Abstract: ").next_sibling
    abstract_paras.append(str(first_paragraph).replace("\n", " "))
    curr_paragraph = first_paragraph.parent.next_sibling
    while curr_paragraph.b is None:  # the next <b> tag is for "Category / Keywords"
        abstract_paras.append(str(curr_paragraph.get_text().replace("\n", " ")))
        curr_paragraph = curr_paragraph.next_sibling
    return "\n\n".join(_fix_spaces_list(abstract_paras))


@attr.s(auto_attribs=True)
class Article:

    title: str
    authors: List[str]
    abstract: str
    keywords: List[str]
    id: str

    @property
    def pdf_link(self) -> str:
        return f"{BASE_URL}/{self.id}.pdf"

    @classmethod
    def parse_html(cls, html: str) -> "Article":
        soup = BeautifulSoup(html, "html5lib")
        title = _fix_spaces(soup.find("b").text)
        authors = _fix_spaces_list(soup.find("i").text.split(" and "))
        keywords = _fix_spaces_list(
            soup.find("b", text="Category / Keywords: ").next_sibling.split(",")
        )
        abstract = _parse_abstract(soup)
        short_url = soup.find("b", text="Short URL: ").next_sibling.text
        _, _, id_ = short_url.partition("/")
        return cls(title, authors, abstract, keywords, id_)


@attr.s(auto_attribs=True)
class ArticleId:

    id: str

    @classmethod
    def from_string(cls, id_: str) -> "ArticleId":
        if not re.match(r"\d{4}/\d{3}$", id_):
            raise ValueError(f"Expected article ID of the form '2009/123'. Got {id_}")
        return cls(id_)


def _wrap_validator_for_argparse(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as err:
            raise argparse.ArgumentTypeError(str(err))

    return wrapped


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and parse the metadata of a paper in the IACR ePrint archive"
    )
    parser.add_argument(
        "article_id",
        type=_wrap_validator_for_argparse(ArticleId.from_string),
        help="The article ID. For example, 2009/123.",
    )
    return parser.parse_args(argv)


def fetch(article_id: ArticleId) -> str:
    r = requests.get(f"{BASE_URL}/{article_id.id}")
    r.raise_for_status()
    return r.text


def fetch_and_parse(argv: List[str]) -> str:
    args = parse_args(argv)
    article = Article.parse_html(fetch(args.article_id))
    return json.dumps(attr.asdict(article))


def main(argv: List[str]) -> None:
    try:
        sys.stdout.write(fetch_and_parse(argv) + "\n")
    except Exception as err:  # pylint: disable=broad-except
        sys.stderr.write(f"Error: {err}")
