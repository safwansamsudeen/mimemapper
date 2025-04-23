TEST_MIME_TYPES = {
    "magic._pyc_": None,
    "application.pdf": "application/pdf",
    "hey.key": "application/vnd.apple.keynote",
    "drive.docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "test.html": "text/html",
    "test.mp4": "video/mp4",
    "recording.mp3": "audio/mpeg",
    "recording.txt": "text/plain",
}

from src import get_mime_type

for file_name, ext in TEST_MIME_TYPES.items():
    res = get_mime_type(file_name.split(".")[-1])
    assert res == ext, f"Expected {ext}, got {res}"

print(f"{len(TEST_MIME_TYPES)} extensions tested - all of them passed.")
