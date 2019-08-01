# -*- coding: utf-8 -*-
import argparse
import functools
import json
import re
import sys
import textwrap
from typing import Dict, List, Union

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


def _parse_keywords(soup: BeautifulSoup) -> List[str]:
    keywords_elem = soup.find("b", text="Category / Keywords: ").next_sibling
    if not keywords_elem:
        return []
    return _fix_spaces_list(keywords_elem.split(","))


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

    @property
    def bibtex(self) -> str:
        id_with_colons = self.id.replace("/", ":")
        authors = " and ".join(self.authors)
        year, _, _ = self.id.partition("/")
        return textwrap.dedent(
            f"""\
            @misc{{cryptoeprint:{id_with_colons},
                author = {{{authors}}},
                title = {{{self.title}}},
                howpublished = {{Cryptology ePrint Archive, Report {self.id}}},
                year = {{{year}}},
                note = {{\\url{{{BASE_URL}/{self.id}}}}},
            }}
            """
        )

    @classmethod
    def parse_html(cls, html: str) -> "Article":
        soup = BeautifulSoup(html, "html5lib")
        title = _fix_spaces(soup.find("b").text)
        authors = _fix_spaces_list(soup.find("i").text.split(" and "))
        keywords = _parse_keywords(soup)
        abstract = _parse_abstract(soup)
        short_url = soup.find("b", text="Short URL: ").next_sibling.text
        _, _, id_ = short_url.partition("/")
        return cls(title, authors, abstract, keywords, id_)

    def to_dict(self) -> Dict[str, Union[str, List[str]]]:
        res = attr.asdict(self)
        res["bibtex"] = self.bibtex
        res["pdf_link"] = self.pdf_link
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, List[str]]]) -> "Article":
        data = data.copy()
        data.pop("bibtex")
        data.pop("pdf_link")
        return cls(**data)


@attr.s(auto_attribs=True)
class ArticleId:

    id: str

    @classmethod
    def from_string(cls, id_: str) -> "ArticleId":
        match = re.match((
            r"(?:"
            r"(?P<scheme>(?:http://)|(?:https://))?"
            r"(?P<host>(?:ia.cr/)|(?:eprint.iacr.org/))"
            r")?"
            r"(?P<id>\d{4}/\d{3})$"), id_)
        if not match:
            raise ValueError("Expected article ID of the form '2009/123', "
                             "'eprint.iacr.org/2009/123', or 'https://ia.cr/2009/123'."
                             f"Got {id_}")
        return cls(match.group("id"))


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
    return json.dumps(article.to_dict())


def main(argv: List[str]) -> None:
    try:
        sys.stdout.write(fetch_and_parse(argv) + "\n")
    except Exception as err:  # pylint: disable=broad-except
        sys.stderr.write(f"Error: {err}")
