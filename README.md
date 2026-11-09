# Pink CTF

A self-contained misc/stego challenge built around **QWERTZ-99** encoding,
**QWERTZ-98** password salting, and the channel-difference image format from
[`QWERTZexe/QWERTZ-99`](https://github.com/QWERTZexe/QWERTZ-99).

## Contents

```
pink-ctf/
├── challenge/
│   ├── DESCRIPTION.md   player-facing prompt
│   ├── secure.png       handout image
│   └── pink.qmap        handout substitution map
├── src/
│   ├── qwertz99.py      reference implementation
│   └── generate.py      builds a fresh instance
├── solve.py             solver
├── WRITEUP.md           full solution
└── requirements.txt
```

## Solve the shipped challenge

```bash
python3 -m pip install -r requirements.txt

python3 solve.py --password 13371337
python3 solve.py --wordlist /usr/share/wordlists/rockyou.txt
```

Output:

```
password: 13371337
plaintext: Hey, thanks for trusting QWERTZ 99 with your most sensitive data! ...
inner plaintext: PINK{NiNeTyNiNeQwErTzEs}
flag: PINK{NiNeTyNiNeQwErTzEs}
```

## Build a fresh instance

```bash
python3 src/generate.py --out build/fresh --seed 1234
python3 solve.py --image build/fresh/secure.png \
                 --qmap  build/fresh/pink.qmap \
                 --password 13371337
```

Reusing the shipped map reproduces the exact inner ciphertext:

```bash
python3 src/generate.py --mapping challenge/pink.qmap --out build/original-map
```

## Flag

`PINK{NiNeTyNiNeQwErTzEs}`
# pinkctf-writeup
