import enum
import re

from models import Anime, Entry, KindKinds, ParserData


RE_SEASON = re.compile(r"(?P<year>\d+).*Season \((?P<season>\d).*Quarter\)")
RE_ANIME = re.compile(r"\[(?P<name>.*)\]\((?P<mal>.*)\)(?:\n\*\*(?P<aliases>.*)\*\*)?")
RE_ENTRIES = re.compile(r"Theme title(?:\|.*)+\n-(?:\|:-:)+\n(?P<data>.*)")
RE_ENTRY = re.compile(r'(?:(?P<kind>OP|ED)(?P<number>\d+)?(?: V(?P<version>\d+))? ?"(?P<title>.*)" ?(?:(?:by)? (?P<artist>.{2,}))?|\|)\|(?:\[(?P<meta>.*)\]\((?:(?P<link>https://animethemes.moe/.*\.webm)|https://files.catbox.moe/.*\.webm)?\)|-)')  # NOQA
RE_LINK = re.compile(r"https://animethemes.moe/video/.*-(?P<kind>OP|ED)(?P<number>\d+)(?:v(?P<version>\d+))?(?:-.*)?\.webm")  # NOQA


def parse_year(year_data: str, data: ParserData):
    # Season block always start with "##2000"
    seasons_data = re.compile(r"\n##(?!#)").split(year_data)[1:]
    for season_data in seasons_data:
        parse_season(season_data, data)


def parse_season(season_data: str, data: ParserData):
    # Separate season metadata from actual season data
    season_meta, season_data = re.compile(r"\n\n").split(season_data, 1)

    if (match := RE_SEASON.match(season_meta)) is None:
        print(f"SESSON ERROR: {season_meta}")
        return {}

    season = match["season"]
    year = match["year"]

    # Anime entries always start with "###[One Piece]"
    animes_data = season_data.split("###")[1:]
    for anime_data in animes_data:
        name, mal, aliases, entries = parse_anime_data(anime_data, data)
        anime = Anime(name=name, season=season, year=year, entries=entries, mal=mal, aliases=aliases)
        data.add_anime(anime)


def parse_anime_data(anime_data: str, data: ParserData) -> (str, str, list, list):
    # Separate anime metadata from actual entries
    anime_meta, anime_data = re.compile(r"\n ?\n?(?!\*\*)").split(anime_data.strip(), 1)

    if (match := RE_ANIME.match(anime_meta)) is None:
        print(f"ANIME ERROR: {anime_meta}")
        return {}

    name = match["name"]
    mal = match["mal"]
    aliases = match["aliases"]
    if aliases:
        aliases = aliases.split(", ")
    else:
        aliases = []

    # Separate multiple translations
    anime_data = anime_data.strip().split("\n\n")
    # Main translation will always be None
    if RE_ENTRIES.match(anime_data[0]):
        anime_data.insert(0, None)
    else:
        anime_data[0] = None

    entries = []
    for region, entries_data in zip(*[iter(anime_data)] * 2):
        if (match := RE_ENTRIES.match(entries_data)) is None:
            print(f"ENTRIES DATA ERROR: {entries_data}\nREF ANIME: {anime_data}")

        entries_data = entries_data.splitlines()[2:]
        for entry_data in entries_data:
            entry_dict = parse_entry_data(entry_data)
            if not entry_dict:
                continue

            # try:
            entry = Entry(**entry_dict, region=region, parser_data=data)
            # except Exception:
            #     print(f'ISSUE ON ENTRY: {entry_dict}')
            #     continue

            entries.append(entry)

    return name, mal, aliases, entries


def parse_entry_data(entry_data: str) -> dict:
    if (match := RE_ENTRY.match(entry_data)) is None:
        return

    entry_dict = match.groupdict()
    if entry_dict["kind"] is None:
        match = RE_LINK.match(entry_dict["link"])
        if not match:
            print(f"LINK ERROR: {entry_dict['link']}")
            return

        entry_dict.update(match.groupdict())

    if entry_dict["kind"] == "OP":
        entry_dict["kind"] = KindKinds.OP
    else:
        entry_dict["kind"] = KindKinds.ED

    if entry_dict["number"]:
        entry_dict["number"] = int(entry_dict["number"])

    if entry_dict['meta']:
        entry_dict['meta'] = entry_dict['meta'].replace("/", "").replace("\\", "")

    return entry_dict
