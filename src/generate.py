import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qwertz99 as q


INTRO = (
    "Hey, thanks for trusting QWERTZ 99 with your most sensitive data! "
    "Here is your sensitive data in case you forgot it: "
)
CHARSET = "".join(chr(c) for c in range(32, 127))
DEFAULT_FLAG = "PINK{NiNeTyNiNeQwErTzEs}"
DEFAULT_PASSWORD = "13371337"


def build(mapping, flag, password, out_dir, seed):
    os.makedirs(out_dir, exist_ok=True)
    inner = q.encode(flag, mapping)
    plain = INTRO + inner
    outer = q.encode(plain, mapping)
    password_value = q.get_pw(password, mapping)
    salted = q.salt(outer, password_value)
    q.save_qmap(mapping, os.path.join(out_dir, "pink.qmap"))
    q.make_image(salted, os.path.join(out_dir, "secure.png"), seed=seed)
    return {
        "flag": flag,
        "password": password,
        "plaintext": plain,
        "salted": salted,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "build"))
    parser.add_argument("--flag", default=DEFAULT_FLAG)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--mapping")
    parser.add_argument("--seed", type=int, default=99)
    args = parser.parse_args()

    if args.mapping:
        mapping = q.load_qmap(args.mapping)
    else:
        mapping = q.random_mapping(CHARSET, seed=args.seed)

    info = build(mapping, args.flag, args.password, args.out, args.seed)
    print("wrote", os.path.join(args.out, "pink.qmap"))
    print("wrote", os.path.join(args.out, "secure.png"))
    print("flag:", info["flag"])
    print("password:", info["password"])
    print("plaintext:", info["plaintext"])


if __name__ == "__main__":
    main()
