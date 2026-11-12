# Generator

Python scripts that draw all 103 schematics with [schemdraw](https://schemdraw.readthedocs.io/)
(matplotlib backend) and write the index files.

```sh
python -m venv .venv
.venv/bin/pip install -r gen/requirements.txt
.venv/bin/python gen/build.py            # all 103 -> svg/ and png/ in the repo root
.venv/bin/python gen/build.py 53 76      # selected circuits only
.venv/bin/python gen/build.py --out DIR  # write somewhere else
.venv/bin/python gen/make_index.py       # index.csv, index.md, index.html
```

Text is set in DejaVu Sans, which must be installed (it ships with matplotlib).

| File | Contents |
|---|---|
| `lib.py` | Drawing helpers (`Sch` class): parts, op amps, transistors, house style, output |
| `trim.py` | Crops PNG/SVG, adds the white background and SVG `<title>`/`<desc>` |
| `reg.py` | `@circuit(number, section, title)` registry |
| `c_basic.py` | 01–25 Basic Circuits |
| `c_gen.py` | 26–42 Signal Generation |
| `c_proc1.py` … `c_proc4.py` | 43–88 Signal Processing |
| `c_fund.py` | 89–103 Fundamentals |
| `build.py`, `make_index.py` | Command-line entry points |

Output: PNG at 300 DPI (RGB on white) and SVG with text as outlines, a white
background rect, and accessible `<title>`/`<desc>`.
