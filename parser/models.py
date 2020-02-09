from __future__ import annotations

import enum
from dataclasses import dataclass, InitVar
from typing import Dict, List, Optional, Union


class EntryKinds(str, enum.Enum):
    KIND = 'k'
    TITLE = 't'
    NUMBER = 'n'
    VERSION = 'v'
    LINK = 'l'
    ARTIST = 'a'
    REGION = 'r'
    META = 'm'


class KindKinds(enum.IntEnum):
    OP = 1
    ED = 2


Id = int


@dataclass
class Entry:
    parser_data: InitVar[ParserData]

    kind: KindKinds
    title: str
    link: Union[str, List[str]]
    number: Optional[int] = None
    version: Optional[int] = None
    artist: Optional[Id] = None
    region: Optional[Id] = None
    meta: Optional[Id] = None

    def __post_init__(self, parser_data):
        if self.artist:
            self.artist = parser_data.get_artist_id(self.artist)

        if self.region:
            self.region = parser_data.get_region_id(self.region)

        if self.meta:
            self.meta = parser_data.get_meta_id(self.meta)

    def serialize(self):
        data = {
            EntryKinds.KIND: self.kind,
            EntryKinds.TITLE: self.title,
            EntryKinds.LINK: self.link,
        }

        if self.number:
            data[EntryKinds.NUMBER] = self.number
        if self.artist:
            data[EntryKinds.ARTIST] = self.artist
        if self.region:
            data[EntryKinds.REGION] = self.region
        if self.meta:
            data[EntryKinds.META] = self.meta

        return data


@dataclass
class Anime:
    name: str
    season: int
    year: int
    entries: List[Entry]
    mal: Optional[str] = None
    aliases: Optional[List[str]] = None

    def __post_init__(self):
        version_entries = []
        for entry in self.entries[:]:
            if entry.version is not None and int(entry.version) != 1:
                version_entries.append(entry)
                self.entries.remove(entry)

        for version_entry in version_entries:
            for entry in self.entries:
                if all(getattr(version_entry, key) == getattr(entry, key) for key in ('title', 'kind', 'number')):
                    if isinstance(entry.link, dict):
                        entry.link[version_entry.version] = version_entry.link
                    else:
                        entry.link = {
                            entry.version or 1: entry.link,
                            version_entry.version: version_entry.link,
                        }

    def serialize(self):
        entries = [entry.serialize() for entry in self.entries]
        return [self.name, self.season, self.year, entries, self.mal, self.aliases]


class ParserData:
    def __init__(self):
        self.animes: Dict[Id, Anime] = {}
        self.metas: Dict[Id, str] = {}
        self.artists: Dict[Id, str] = {}
        self.regions: Dict[Id, str] = {}

        self._metas: Dict[str, Id] = {}
        self._artists: Dict[str, Id] = {}
        self._regions: Dict[str, Id] = {}

    def get_artist_id(self, artist: str):
        if artist in self._artists:
            return self._artists[artist]
        else:
            artist_id = len(self.artists)
            self.artists[artist_id] = artist
            self._artists[artist] = artist_id
            return artist_id

    def get_region_id(self, region: str):
        if region in self._regions:
            return self._regions[region]
        else:
            region_id = len(self.regions)
            self.regions[region_id] = region
            self._regions[region] = region_id
            return region_id

    def get_meta_id(self, meta: str):
        if meta in self._metas:
            return self._metas[meta]
        else:
            meta_id = len(self.metas)
            self.metas[meta_id] = meta
            self._metas[meta] = meta_id
            return meta_id

    def add_anime(self, anime: Anime):
        anime_id = len(self.animes)
        self.animes[anime_id] = anime

    def serialize(self):
        animes = {k: v.serialize() for k, v in self.animes.items()}
        return {
            "animes": animes,
            "metas": self.metas,
            "artists": self.artists,
            "regions": self.regions,
        }
