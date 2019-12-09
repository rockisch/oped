import re


RE_SEASON = re.compile(r"(?P<year>\d+).*Season \((?P<season>\d).*Quarter\)")
RE_ANIME = re.compile(r"\[(?P<name>.*)\]\((?P<mal>.*)\)(?:\n\*\*(?P<aliases>.*)\*\*)?")
RE_ENTRIES = re.compile(r"Theme title(?:\|.*)+\n-(?:\|:-:)+\n(?P<data>.*)")
RE_ENTRY = re.compile(
    r'(?:(?P<k>OP|ED)(?P<n>\d+)?(?: V(?P<v>\d+))? ?"(?P<t>.*)" ?(?:(?:by)? (?P<a>.{2,}))?|\|)\|(?:\[(?P<m>.*)\]\((?:(?P<l>https://animethemes.moe/.*\.webm)|https://files.catbox.moe/.*\.webm)?\)|-)'
)
RE_LINK = re.compile(r"https://animethemes.moe/video/.*-(?P<k>OP|ED)(?P<n>\d+)(?:v(?P<v>\d+))?(?:-.*)?\.webm")


def parse_year(year_data: str, data: dict):
    year_entries = {}
    # Season block always start with "##2000"
    seasons_data = re.compile(r"\n##(?!#)").split(year_data)[1:]
    for season_data in seasons_data:
        year_entries.update(parse_season(season_data, data))

    return year_entries


def parse_season(season_data: str, data: dict) -> dict:
    # Separate season metadata from actual season data
    season_meta, season_data = re.compile(r"\n\n").split(season_data, 1)

    if (match := RE_SEASON.match(season_meta)) is None:
        print(f"SESSON ERROR: {season_meta}")
        return {}

    season = match["season"]
    year = match["year"]

    season_entries = {}
    # Anime entries always start with "###[One Piece]"
    animes_data = season_data.split("###")[1:]
    for anime_data in animes_data:
        name, mal, aliases, entries = parse_anime(anime_data, data)
        anime_entry = [name, mal, season, year, entries]
        anime_id = len(data["animes"])

        if aliases:
            for alias in aliases:
                data["aliases"][alias] = anime_id

        data["animes"][anime_id] = anime_entry

    return season_entries


def parse_anime(anime_data: str, data: dict) -> (str, str, list, list):
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
    for version, entries_data in zip(*[iter(anime_data)] * 2):
        if (match := RE_ENTRIES.match(entries_data)) is None:
            print(f"ENTRIES DATA ERROR: {entries_data}\nREF ANIME: {anime_data}")

        entries_data = entries_data.splitlines()[2:]
        for entry_data in entries_data:
            entry = parse_entry(entry_data)
            if entry is None:
                print(f"ENTRY ERROR: {entry_data}\nREF ANIME: {anime_data}")
                continue

            if entry["l"] is None:
                continue

            if version:
                entry["r"] = version

            if entry["m"] in data["__metas"]:
                entry["m"] = data["__metas"][entry["m"]]
            else:
                meta_id = len(data["metas"])
                data["metas"][meta_id] = entry["m"]
                data["__metas"][entry["m"]] = meta_id
                entry["m"] = meta_id

            if "a" in entry:
                if entry["a"] in data["__artists"]:
                    entry["a"] = data["__artists"][entry["a"]]
                else:
                    artist_id = len(data["artists"])
                    data["artists"][artist_id] = entry["a"]
                    data["__artists"][entry["a"]] = artist_id
                    entry["a"] = artist_id

            if "r" in entry:
                if entry["r"] in data["__regions"]:
                    entry["r"] = data["__regions"][entry["r"]]
                else:
                    region_id = len(data["regions"])
                    data["regions"][region_id] = entry["r"]
                    data["__regions"][entry["r"]] = region_id
                    entry["r"] = region_id

            entries.append(entry)

    return name, mal, aliases, entries


def parse_entry(entry_data: str) -> dict:
    if (match := RE_ENTRY.match(entry_data)) is None:
        return

    entry = match.groupdict()

    if entry["l"] is None:
        return entry

    if entry["k"] is None:
        match = RE_LINK.match(entry["l"])
        if not match:
            print(f"LINK ERROR: {entry['l']}")
            return

        entry.update(match.groupdict())

    if entry["k"] == "OP":
        entry["k"] = 1
    else:
        entry["k"] = 2

    if entry["n"]:
        entry["n"] = int(entry["n"])

    for k in list(entry):
        if entry[k] is None:
            del entry[k]

    entry["m"] = entry["m"].replace("/", "").replace("\\", "")

    return entry
