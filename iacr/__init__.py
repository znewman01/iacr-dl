# -*- coding: utf-8 -*-
import re
from typing import List

import attr
from bs4 import BeautifulSoup

BASE_URL = "https://eprint.iacr.org/"


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
        return BASE_URL + f"{self.id}.pdf"

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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
