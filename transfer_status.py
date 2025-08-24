# file: transfer_status.py

from __future__ import annotations

import sys
from typing import Iterable, List, Sequence, Tuple

import requests
from bs4 import BeautifulSoup, Tag


DEFAULT_URL = "https://www3.mpifr-bonn.mpg.de/cgi-bin/showtransfers.cgi"


def _fetch_website(url: str, *, timeout: float = 20) -> str:
    """Return HTML for *url*.

    Why: default `timeout` avoids hangs when caller omits it.
    """
    if not url:
        raise ValueError("url must be a non-empty string")
    try:
        resp = requests.get(
            url,
            timeout=timeout,  # why: explicit keyword prevents param-mix bugs
            headers={"User-Agent": "Mozilla/5.0 (compatible; TransferStatus/1.0)"},
        )
        resp.raise_for_status()
        # Prefer detected encoding; some pages omit charset
        resp.encoding = resp.apparent_encoding or resp.encoding
        return resp.text
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc


def _parse_html(html: str) -> BeautifulSoup:
    """Parse HTML into BeautifulSoup tree."""
    return BeautifulSoup(html, "html.parser")


def _normalize_text(s: str) -> str:
    """Collapse whitespace and trim. Why: stable matching/printing."""
    return " ".join(s.split()).strip()


def extract_table_after_heading(soup: BeautifulSoup, heading_text: str) -> Tuple[List[str], List[List[str]]]:
    """Find the first <table> that follows a heading whose text *contains* `heading_text` (case-insensitive).

    Returns (headers, rows). Raises ValueError if not found.
    """
    target = None
    needle = heading_text.lower()

    for h in soup.find_all([f"h{i}" for i in range(1, 7)]):
        txt = _normalize_text(h.get_text(" "))
        if needle in txt.lower():
            target = h
            break

    if target is None:
        raise ValueError(f"Heading containing '{heading_text}' not found")

    table = target.find_next("table")
    if table is None:
        raise ValueError(f"No <table> found after heading '{heading_text}'")

    return _table_to_matrix(table)


def _table_to_matrix(table: Tag) -> Tuple[List[str], List[List[str]]]:
    """Convert a <table> to (headers, rows) of strings.

    - Uses first row with <th> as header; else first row's <td>.
    - Handles <thead>/<tbody> if present.
    - Strips cell text and normalizes whitespace.
    """
    rows: List[Tag] = table.find_all("tr")
    if not rows:
        return [], []

    # Find header row
    header_cells = None
    header_row_idx = None
    for idx, tr in enumerate(rows):
        ths = tr.find_all("th")
        if ths:
            header_cells = ths
            header_row_idx = idx
            break

    if header_cells is None:
        # Fallback: first row's <td> as headers
        first_tds = rows[0].find_all(["td", "th"])  # be lenient
        headers = [(_normalize_text(td.get_text(" ")) or f"col{i+1}") for i, td in enumerate(first_tds)]
        data_trs = rows[1:]
    else:
        headers = [(_normalize_text(th.get_text(" ")) or f"col{i+1}") for i, th in enumerate(header_cells)]
        data_trs = rows[header_row_idx + 1 :]

    data: List[List[str]] = []
    for tr in data_trs:
        cells = tr.find_all(["td", "th"])
        # Pad/truncate to header length to stay rectangular
        values = [_normalize_text(td.get_text(" ")) for td in cells]
        if not values:
            continue
        # Fit to header size
        if len(values) < len(headers):
            values += [""] * (len(headers) - len(values))
        elif len(values) > len(headers):
            values = values[: len(headers)]
        data.append(values)

    return headers, data


def _print_matrix(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    """Pretty-print a small table to the terminal with minimal dependencies."""
    if not headers:
        print("(no headers)")
        return

    # Column widths
    widths = [len(h) for h in headers]
    for r in rows:
        for i, val in enumerate(r):
            if i < len(widths):
                widths[i] = max(widths[i], len(val))

    def fmt_row(vals: Sequence[str]) -> str:
        cells = [str(vals[i]).ljust(widths[i]) for i in range(len(headers))]
        return " | ".join(cells)

    # Header
    print(fmt_row(headers))
    print("-+-".join("-" * w for w in widths))

    # Data
    for r in rows:
        if r[1].find(self, "nn")
            print(fmt_row(r))


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    heading = "List of Active Data Transfers"  # change to match another section if desired

    html = _fetch_website(DEFAULT_URL)
    soup = _parse_html(html)

    try:
        headers, data = extract_table_after_heading(soup, heading)
    except ValueError as err:
        print(f"Error: {err}")
        return 2

    _print_matrix(headers, data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
