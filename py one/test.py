import random
import datetime
from collections import defaultdict

# Test find_keywords
keywords = {
    "salom": ["salom", "assalom", "hi", "hello", "qale"],
    "vaqt": ["vaqt", "soat", "time", "vaqti"],
    "sana": ["sana", "date", "kun"],
}


def find_keywords(message_text):
    msg = message_text.lower()
    found = set()
    for key, syns in keywords.items():
        if any(syn in msg for syn in syns):
            found.add(key)
    return found


# Test
print("Test 1:", find_keywords("salom vaqt"))
print("Test 2:", find_keywords("SALOM"))
print("Test 3:", find_keywords("salomlar"))
print("Test 4:", find_keywords("hello time"))
print("Test 5:", find_keywords("unknown"))
