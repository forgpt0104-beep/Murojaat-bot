"""Small pagination helper used by "My Appeals" and admin search results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Page:
    page: int
    per_page: int
    total_items: int

    @property
    def offset(self) -> int:
        return self.page * self.per_page

    @property
    def total_pages(self) -> int:
        if self.total_items <= 0:
            return 1
        return (self.total_items + self.per_page - 1) // self.per_page
