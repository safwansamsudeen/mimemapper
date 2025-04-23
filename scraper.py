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
INVALID_EXTS = [
    "none",
    "n/a",
    "not",
    "applicable",
    "undefined",
    "unknown",
    "and",
]
BLACKLISTED_TYPES = {"application/timestamp-query": [".TSQ", "TSR"]}


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
        with open("./mime_to_ext.json") as f:
            map = json.load(f)
    except FileNotFoundError:
        map = {}

    try:
        for row in reader:
            type = row[1]
            if type in map:
                continue
            exts = get_extension(type)
            map[type] = exts
            if exts:
                print(f'Adding "{exts}" for {type}')
    finally:
        print("Exiting", root)
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
        return []
    return extract_extension(content)


def extract_extension(content):
    content = content.lower()
    # `application/srgs` doesn't have a colon
    if (index := content.find(":", content.find("file extension"))) != -1:
        content = content[index:]
    else:
        content = content[content.find("file extension") + 15 :]

    end_of_line = content.find("\n")
    len_line = len(content[:end_of_line].strip())
    # Be more stringent when it's a new line
    new_line = False
    while (
        (len_line < 2 or len_line > 20)
        and ("." not in content[:end_of_line])
        and content[:end_of_line].strip()
    ):
        new_line = True
        content = content[end_of_line + 1 :]
        end_of_line = content.find("\n")
        len_line = len(content[:end_of_line].strip())
    res = parse_quotes(content)
    if not res:
        res = parse_plain(content, new_line or len(content[:end_of_line].split()) > 3)
    if not res:
        res = parse_next_lines(content)
    return [
        w
        for ext in res
        if (w := ext.strip(punctuation + whitespace)) and w not in INVALID_EXTS
    ]


def parse_plain(content, require_dot=False):
    """Used to parse a regular line"""
    s = ""
    index = 0
    while index < len(content) and content[index] != "\n":
        s += content[index]
        index += 1
    res = s.lower()
    exts = res.replace(",", " ").split()
    return [k for k in exts if k.startswith(".")] if require_dot else exts


def parse_quotes(content):
    k = content[0 : content.find("\n")].split('"')
    if k[1::2]:
        return k[1::2]
    k = content[0 : content.find("\n")].split("'")
    return k[1::2]


def parse_next_lines(content):
    """
    Used when file extension is in a new line, like application/vnd.sqlite3
    """
    lines = content.split("\n")
    try:
        line = next(x for x in lines if x.strip(whitespace + punctuation))
        return parse_plain(line.strip(), True)
    except StopIteration:
        return []


if __name__ == "__main__":
    main()
