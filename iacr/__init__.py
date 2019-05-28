# -*- coding: utf-8 -*-
import re
from typing import List

import attr
from bs4 import BeautifulSoup

BASE_URL = "https://eprint.iacr.org/"


def _fix_spaces(text: str) -> str:
    return re.sub("  +", " ", text).strip()


def _fix_spaces_list(texts: List[str]):
    return list(map(_fix_spaces, texts))


@attr.s(auto_attribs=True)
class Article:

    title: str
    authors: List[str]
    abstract: str
    keywords: List[str]
    id: str

    @property
    def pdf_link(self) -> str:
        return BASE_URL + f"{self.id}.pdf"

    @classmethod
    def parse_html(cls, html: str) -> "Article":
        soup = BeautifulSoup(html, "html.parser")
        title = _fix_spaces(soup.find("b").text)
        authors = _fix_spaces_list(soup.find("i").text.split(" and "))
        abstract = _fix_spaces(
            soup.find("b", text="Abstract: ").next_sibling.replace("\n", " ")
        )
        keywords = _fix_spaces_list(
            soup.find("b", text="Category / Keywords: ").next_sibling.split(",")
        )
        short_url = soup.find("b", text="Short URL: ").next_sibling.text
        _, _, id_ = short_url.partition("/")
        return cls(title, authors, abstract, keywords, id_)


def main() -> int:
    pass


if __name__ == "__main__":
    main()
