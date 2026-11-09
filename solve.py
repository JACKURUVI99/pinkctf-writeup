import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import qwertz99 as q


SMALL_CANDIDATES = [
    "98", "99", "1337", "13371337", "qwertz", "qwertz99", "qwertz98",
    "QWERTZ", "QWERTZ99", "QWERTZ-99", "pink", "Pink", "PINK", "pinkqmap",
    "password", "secure", "qmap", "weirdnumbers", "allweirdnumbers",
]


def load_wordlist(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            yield line.rstrip("\n").rstrip("\r")


def try_password(password, n, mappings):
    try:
        pw = q.get_pw(password, mappings)
    except KeyError:
        return None
    if pw <= 0 or pw > n or n % pw:
        return None
    body = str(n // pw)
    if len(body) % mappings["_char"]:
        return None
    try:
        plain = q.decode(body + "99", mappings)
    except ValueError:
        return None
    return plain


def solve(image, qmap, password=None, wordlist=None, digits=None):
    mappings = q.load_qmap(qmap)
    salted = q.decode_image(image)
    if not salted.endswith("-98"):
        raise SystemExit("decoded image is not a QWERTZ-98 string: %r" % salted[-8:])
    n = int(salted[:-3])
    print("salted number digits:", len(str(n)))

    found = None
    if password is not None:
        found = (password, try_password(password, n, mappings))
    else:
        for candidate in SMALL_CANDIDATES:
            plain = try_password(candidate, n, mappings)
            if plain is not None:
                found = (candidate, plain)
                break
        if found is None and wordlist:
            for i, candidate in enumerate(load_wordlist(wordlist), 1):
                plain = try_password(candidate, n, mappings)
                if plain is not None:
                    found = (candidate, plain)
                    break
                if i % 500000 == 0:
                    print("tried %d words" % i, flush=True)
        if found is None and digits:
            found = brute_digits(n, mappings, digits)

    if found is None:
        raise SystemExit("password not found")
    candidate, plain = found
    print("password:", candidate)
    print("plaintext:", plain)

    match = re.search(r"(\d{3,99})$", plain)
    if match:
        try:
            inner = q.decode(match.group(1), mappings)
        except ValueError:
            inner = None
        if inner:
            print("inner value:", match.group(1))
            print("inner plaintext:", inner)
            flag = re.search(r"[A-Za-z0-9_]+\{[^}]*\}", inner)
            if flag:
                print("flag:", flag.group(0))
    return plain


def brute_digits(n, mappings, max_len):
    alphabet = [str(d) for d in range(10)]
    def rec(prefix, depth):
        if depth == 0:
            return None
        for ch in alphabet:
            candidate = prefix + ch
            plain = try_password(candidate, n, mappings)
            if plain is not None:
                return (candidate, plain)
        for ch in alphabet:
            result = rec(prefix + ch, depth - 1)
            if result is not None:
                return result
        return None
    return rec("", max_len)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default=os.path.join(here, "challenge", "secure.png"))
    parser.add_argument("--qmap", default=os.path.join(here, "challenge", "pink.qmap"))
    parser.add_argument("--password")
    parser.add_argument("--wordlist")
    parser.add_argument("--digits", type=int)
    args = parser.parse_args()
    solve(args.image, args.qmap, args.password, args.wordlist, args.digits)


if __name__ == "__main__":
    main()
