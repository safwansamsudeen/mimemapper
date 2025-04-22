import requests
import csv, json
from string import punctuation, whitespace

REGISTRIES = [
    "application",
    "audio",
    "font",
    "haptics",
    "image",
    "message",
    "model",
    "text",
    "video",
]
ROOT_URL = "https://www.iana.org/assignments/media-types/"
INVALID_EXTS = ["none", "n/a", "not applicable", "undefined", "unknown", "and"]


def main():
    for registry in REGISTRIES:
        get_mime_types(registry)


def get_mime_types(root):
    r = requests.get(f"{ROOT_URL}{root}.csv")
    content = r.content.decode()
    reader = csv.reader(content.splitlines())
    next(reader)
    print(f"Loaded '{root}'")
    try:
        with open("./results.json") as f:
            map = json.load(f)
    except FileNotFoundError:
        map = {}

    try:
        for row in reader:
            type = row[1]

            if type in map:
                continue
            exts = get_extension(type)

            for ext in exts.split(",") if "," in exts else exts.split():
                if ext and ext not in INVALID_EXTS and len(ext) < 10:
                    ext = ext.strip(punctuation + whitespace)
                    if ext.startswith("and"):
                        ext = ext[3:].strip(punctuation + whitespace)
                    print(f"Adding {ext} for {type}")
                    map.setdefault(type, [])
                    map[type].append(ext)
                elif type not in map:
                    map[type] = []
    finally:
        with open("./mime_to_ext.json", "w") as f:
            json.dump(map, f)

        # Reverse mapping
        EXT_TO_MIME_MAP = {}
        for mime, exts in map.items():
            for ext in exts:
                EXT_TO_MIME_MAP.setdefault(ext, [])
                EXT_TO_MIME_MAP[ext].append(mime)
        for k in EXT_TO_MIME_MAP.values():
            k.sort(key=len)
        with open("./ext_to_mime.json", "w") as f:
            json.dump(EXT_TO_MIME_MAP, f)
        return


def get_extension(mime_type):
    r = requests.get(ROOT_URL + mime_type)
    content = r.content.decode().lower()
    if not "file extension" in content:
        return ""
    return extract_extension(content)


def extract_extension(content):
    content = content.lower()
    index = content.find(":", content.find("file extension"))
    res = parse_quotes(content, index)
    if not res:
        res = parse_plain(content, index)
    if not res:
        res = parse_next_lines(content, index)
    return [
        w
        for ext in res
        if (w := ext.strip(punctuation + whitespace)) not in INVALID_EXTS
    ]


def parse_plain(content, index):
    """Used to parse"""
    s = ""
    while index < len(content) and content[index] != "\n":
        s += content[index]
        index += 1
    res = s.strip(punctuation + whitespace).lower()
    return res.replace(",", " ").split()


def parse_quotes(content, index):
    k = content[index : content.find("\n", index)].split('"')
    return k[1::2]


def parse_next_lines(content, index):
    """
    Used when file extension is in a new line, like application/vnd.sqlite3
    """
    lines = content[index:].split("\n")
    try:
        line = next(x for x in lines if x.strip(whitespace + punctuation))
        return parse_plain(line.strip(), 0)
    except StopIteration:
        return []


if __name__ == "__main__":
    s1 = """Additional information :

    1. Deprecated alias names for this type : N/A
    2. Magic number(s) : No sequence of bytes can uniquely identify an HTML document.
    3. File extension(s) : "html" and "htm" are commonly used.
    4. Macintosh file type code : TEXT
    5. Object Identifiers: N/A
    """
    s2 = """
Additional information :

1. Magic number(s) : N/A
2. File extension(s) : aml, test, and four
3. Macintosh file type code : N/A
4. Object Identifiers: N/A"""

    s3 = """
    File extensions:

    .db, .sqlite, .sqlite3
    (".db" does not uniquely identify SQLite database files.
    Other extensions are commonly used.)

    Macintosh file type code:
    """
    print(extract_extension(s1))
    print(extract_extension(s2))
    print(extract_extension(s3))
    # main()

## Known Issues
## Fails for most fonts, as they have extensions in an unusual format
