import json

with open("./results.json") as f:
    MIME_TO_EXT_MAP = json.load(f)

EXT_TO_MIME_MAP = {}
for mime, exts in MIME_TO_EXT_MAP.items():
    for ext in exts:
        EXT_TO_MIME_MAP.setdefault(ext, [])
        EXT_TO_MIME_MAP[ext].append(mime)


def get_mime_type(ext, all=False):
    if ext not in EXT_TO_MIME_MAP:
        return
    mimes = sorted(EXT_TO_MIME_MAP[ext], key=len)
    if all:
        return mimes
    return mimes[0] if EXT_TO_MIME_MAP[ext] else None


def get_extension(mime, all=False):
    return MIME_TO_EXT_MAP[mime] if all else MIME_TO_EXT_MAP[mime][0]


print(get_mime_type("sqlite"))
