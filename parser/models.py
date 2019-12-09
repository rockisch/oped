from __future__ import annotations

import sqlite3
from sqlite3 import Connection, Cursor
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from utils import get_conn


@dataclass
class Manager:
    model: Any
    table: str
    rows: List[str]

    def _build_equal_where(self, keys: List[str]) -> str:
        wheres = [f"{k}=:{k}" for k in keys]
        return " AND ".join(wheres)

    def _query(self, conn: Connection, **kwargs: Any) -> Cursor:
        where = self._build_equal_where(kwargs.keys())
        c = conn.cursor()
        c.execute(f"SELECT {','.join(self.rows)} FROM {self.table} WHERE {where}", kwargs)
        return c

    @get_conn
    def get(self, conn: Connection, **kwargs: Any) -> Any:
        c = self._query(conn, **kwargs)
        row = c.fetchone()
        return self.model(row)

    @get_conn
    def filter(self, conn: Connection, **kwargs: Any) -> List[Any]:
        c = self._query(conn, **kwargs)
        rows = c.fetchall()
        return [self.model(row) for row in rows]

    @get_conn
    def save(self, conn: Connection, instance: Any):
        sets = f"{'=?,'.join(self.rows)}=?"
        values = [getattr(instance, r) for r in self.rows]

        c = conn.cursor()
        c.execute(f"UPDATE {self.table} SET {sets} WHERE pk=?", *values, instance.pk)


class Model:
    objects: ClassVar[Manager]

    def save(self):
        self.objects.save(self)


class Anime(Model):
    objects: ClassVar[Manager]

    def __init__(self, name: str, pk: int, year: int, season: int, mal: str):
        self.pk = pk
        self.name = name
        self.year = year
        self.season = season
        self.mal = mal

    def entries(self):
        return Entry.objects.filter(anime_pk=self.pk)


Anime.objects = Manager(Anime, "anime", ["name", "year", "season" "mal"])


class Alias(Model):
    objects: ClassVar[Manager]

    def __init__(self, pk: int, anime: Union[Anime, int], name: str):
        self.pk = pk
        self.name = name
        if isinstance(anime, int):
            self.anime_pk = anime
        elif isinstance(anime, Anime):
            self._anime = anime
            self.anime_pk = anime.pk

    @property
    def anime(self):
        if getattr(self, "_anime", None) is None:
            self._anime = Anime.objects.get(pk=self.anime_pk)

        return self._anime


Alias.objects = Manager(Anime, "alias", ["anime_pk", "name"])


class Entry(Model):
    OP = 0
    ED = 1

    objects: ClassVar[Manager]

    def __init__(self, pk: int, anime: Union[Anime, int], name: str, kind: int, artist: str, meta: str):
        self.pk = pk
        self.name = name
        self.kind = kind
        self.artist = artist
        self.meta = meta
        if isinstance(anime, int):
            self.anime_pk = anime
        elif isinstance(anime, Anime):
            self._anime = anime
            self.anime_pk = anime.pk

    @property
    def anime(self):
        if getattr(self, "_anime", None) is None:
            self._anime = Anime.objects.get(pk=self.anime_pk)

        return self._anime


Entry.objects = Manager(Entry, "entry", ["anime_pk", "name", "kind", "artist", "meta"])
