import math
import random
import re
from PIL import Image


SYMBOLS = {"-": 11}
for _i in range(11):
    SYMBOLS[str(_i)] = _i
REVERSE_SYMBOLS = {v: k for k, v in SYMBOLS.items()}


def load_qmap(path):
    content = open(path, "r", encoding="utf-8").read().strip()
    if not content.startswith("[QMAP]"):
        raise ValueError("not a QMAP file")
    content = content[6:]
    char_len = re.search(r"\{c:(\d+)\}", content)
    supports98 = re.search(r"\{s:([01])\}", content)
    if not char_len or not supports98:
        raise ValueError("missing QMAP header fields")
    mappings = {
        "_char": int(char_len.group(1)),
        "_supports98": bool(int(supports98.group(1))),
    }
    for key, value in re.findall(r"\((\d+)\|(\d+)\)", content):
        mappings[chr(int(key))] = value
    return mappings


def save_qmap(mappings, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("[QMAP]")
        f.write("{c:%d}" % mappings["_char"])
        f.write("{s:%d}" % (1 if mappings["_supports98"] else 0))
        for key, value in mappings.items():
            if not key.startswith("_"):
                f.write("(%d|%s)" % (ord(key), value))


def random_mapping(charset, seed=None):
    rng = random.Random(seed)
    codes = list(range(100, 999))
    rng.shuffle(codes)
    mappings = {"_char": 3, "_supports98": True}
    for ch in charset:
        mappings[ch] = str(codes.pop())
    return mappings


def get_pw(password, mappings):
    acc = 0
    product = 1
    for ch in password:
        code = int(mappings[ch])
        acc = acc * 1000 + code
        product *= code
    return acc * product


def encode(text, mappings):
    width = mappings["_char"]
    body = "".join(str(mappings[ch]).zfill(width) for ch in text)
    return body + "99"


def decode(text, mappings):
    if not text.endswith("99"):
        raise ValueError("encoded text must end with 99")
    body = text[:-2]
    width = mappings["_char"]
    if len(body) % width:
        raise ValueError("encoded body has invalid length")
    reverse = {}
    for key, value in mappings.items():
        if not key.startswith("_"):
            reverse[str(value)] = key
    out = []
    for i in range(0, len(body), width):
        chunk = body[i : i + width]
        if chunk not in reverse:
            raise ValueError("malformed chunk %r" % chunk)
        out.append(reverse[chunk])
    return "".join(out)


def salt(encoded, password_value):
    if not encoded.endswith("99"):
        raise ValueError("encoded text must end with 99")
    return str(int(encoded[:-2]) * int(password_value)) + "-98"


def unsalt(salted, password_value):
    if not salted.endswith("-98"):
        raise ValueError("salted text must end with -98")
    return str(int(salted[:-3]) // int(password_value)) + "99"


def make_image(text, path, seed=None):
    rng = random.Random(seed)
    numbers = [SYMBOLS[ch] for ch in text]
    side = math.ceil(math.sqrt(len(numbers)))
    img = Image.new("RGBA", (side, side))
    pixels = img.load()
    for idx, num in enumerate(numbers):
        x, y = idx % side, idx // side
        pos = idx % 4
        m1 = rng.randint(0, 255)
        m2 = rng.randint(0, 255)
        channels = [0, 0, 0, 0]
        channels[pos] = (num + m1) % 256
        channels[(pos + 1) % 4] = m1
        channels[(pos + 2) % 4] = m2
        channels[(pos + 3) % 4] = (num + m2) % 256
        pixels[x, y] = tuple(channels)
    img.save(path)
    return path


def decode_image(path):
    img = Image.open(path)
    pixels = img.load()
    width, height = img.size
    result = []
    for idx in range(width * height):
        x, y = idx % width, idx // width
        channels = pixels[x, y]
        pos = idx % 4
        main_val = channels[pos]
        m1 = channels[(pos + 1) % 4]
        m2 = channels[(pos + 2) % 4]
        last_val = channels[(pos + 3) % 4]
        candidate1 = (main_val - m1) % 256
        candidate2 = (last_val - m2) % 256
        if candidate1 == candidate2 and 0 <= candidate1 <= 11:
            result.append(REVERSE_SYMBOLS[candidate1])
    while result and result[-1] == "0":
        result.pop()
    return "".join(result)
