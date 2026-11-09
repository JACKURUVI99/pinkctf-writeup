# Pink CTF - Pink

## Summary

`secure.png` contains an image encoded with the QWERTZ-99 channel-difference
format. Decoding it yields a QWERTZ-98 salted number. The number must be divided
by a password-derived value before the inner QWERTZ-99 data can be decoded.

The password is `13371337` and the flag is:

```
PINK{NiNeTyNiNeQwErTzEs}
```

## Files

- `secure.png` - encoded image
- `pink.qmap` - QWERTZ character map

The description also contains a small hint:

```
978b8b8f8cc5d0d098968b978a9dd19c9092d0aea8baadaba59a879ad0aea8baadaba5d2c6c6
```

XORing each byte with `0xff` turns it into:

```
https://github.com/QWERTZexe/QWERTZ-99
```

That repository documents the QWERTZ-99 format.

## QMAP format

The map begins with `[QMAP]{c:3}{s:1}`. `c:3` means every character is encoded
as a three-digit number. `s:1` means QWERTZ-98 salting is supported. The rest of
the file is a list of `(codepoint|code)` pairs, for example:

```
(32|223)   space
(33|182)   !
(34|734)   "
```

The map has 826 entries. Encoding a string replaces each character with its
three-digit code and appends the marker `99`.

## Decoding the image

QWERTZ-99 stores one symbol per pixel. Every pixel is a 4-channel RGBA value,
and the symbol is hidden in a channel selected by the pixel index modulo four.
The two neighbouring channels hold random masks. The fourth channel contains a
second copy of the symbol XORed with the second mask.

For pixel `i`, with `p = i % 4`:

```
main  = channels[p]
mask1 = channels[(p + 1) % 4]
mask2 = channels[(p + 2) % 4]
last  = channels[(p + 3) % 4]

symbol1 = (main - mask1) mod 256
symbol2 = (last - mask2) mod 256
```

If both candidates agree and the value is between 0 and 11, that value is the
symbol. Trailing zero symbols are padding and are removed.

The decoded image is a 620-digit salted number ending in `-98`.

## QWERTZ-98 salting

`-98` marks a QWERTZ-98 salted value:

```
salted = str(outer_number * password_value) + "-98"
```

The password value is not a simple hash. For a password, each character is
looked up in the QMAP. The codes are concatenated into one number, and all of
the codes are also multiplied together:

```
acc = 0
product = 1
for ch in password:
    code = int(mapping[ch])
    acc = acc * 1000 + code
    product *= code

password_value = acc * product
```

To undo the salt, divide the number by `password_value` and append `99`. If the
division has a remainder, or the resulting string is not a valid QWERTZ-99
length, the password is wrong.

The password is `13371337`. Its map values produce a divisor that evenly divides
the 620-digit salted number.

## Decoding the plaintext

After unsalting, the outer QWERTZ-99 text is:

```
Hey, thanks for trusting QWERTZ 99 with your most sensitive data! Here is your sensitive data in case you forgot it: 72756517940796217918417988128949817918417988139449732784728936932725112499
```

The final three-digit block is another QWERTZ-99 value. Decoding it yields:

```
PINK{NiNeTyNiNeQwErTzEs}
```

## Reproducing the solve

```bash
python3 -m pip install -r requirements.txt

python3 solve.py --password 13371337
```

Output:

```
salted number digits: 620
password: 13371337
plaintext: Hey, thanks for trusting QWERTZ 99 with your most sensitive data! Here is your sensitive data in case you forgot it: 72756517940796217918417988128949817918417988139449732784728936932725112499
inner value: 72756517940796217918417988128949817918417988139449732784728936932725112499
inner plaintext: PINK{NiNeTyNiNeQwErTzEs}
flag: PINK{NiNeTyNiNeQwErTzEs}
```

The solver can also search a wordlist:

```bash
python3 solve.py --wordlist /usr/share/wordlists/rockyou.txt
```

or brute-force short numeric passwords:

```bash
python3 solve.py --digits 8
```

## Regenerating the challenge

The shipped mapping can be used to reproduce the exact inner ciphertext:

```bash
python3 src/generate.py --mapping challenge/pink.qmap --out build/original-map
```

A fresh mapping can be generated with a seed:

```bash
python3 src/generate.py --out build/fresh --seed 1234
python3 solve.py --image build/fresh/secure.png \
                 --qmap  build/fresh/pink.qmap \
                 --password 13371337
```
