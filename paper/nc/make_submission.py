"""Build the Neurocomputing upload package in paper/nc/submission/ (gitignored).

  01_manuscript.pdf            the built PDF (for a PDF-only first submission)
  02_highlights.txt            3-5 bullets, one per line
  03_cover_letter.txt          letter body, for pasting or upload
  04_author_biographies.txt    the three biographies, as printed in the PDF
  05_photo_*.jpg               passport-type photographs
  06_latex_source.zip          flat LaTeX source (no subfolders: Editorial
                               Manager stores uploads flat), verified to compile
  abstract_plain.txt, form_fields.txt   text to paste into the form

Usage: python paper/nc/make_submission.py paper   (after bash paper/nc/build.sh)
"""
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PAPER = Path(sys.argv[1]).resolve()
NC = PAPER / "nc"
OUT = NC / "submission"
SRC = OUT / "latex_source"
TEXBIN = Path("D:/texlive/2026/bin/windows")
TEMPLATE = NC / "NCTemplate" / "els-cas-templates"

# Clear what this script writes; keep anything else (SUBMISSION_CHECKLIST.md).
if SRC.exists():
    shutil.rmtree(SRC)
for old in OUT.glob("0[1-6]_*"):
    old.unlink()
SRC.mkdir(parents=True)

# ---------- flat LaTeX source ----------
INPUTS = ["abstract", "highlights", "s1_intro", "s2_background", "s3_collapse",
          "s4_theory", "s5_prevalence", "s6_merging", "s7_discussion",
          "s8_conclusion", "declarations", "app_theory", "app_prereg",
          "app_merging", "app_campaign", "app_details", "bios"]


def flatten(text):
    text = re.sub(r"\\input\{nc/([A-Za-z0-9_]+)\}", r"\\input{\1}", text)
    text = text.replace(r"\IfFileExists{nc/bios.tex}", r"\IfFileExists{bios.tex}")
    text = text.replace("nc/figures/", "").replace("nc/photos/", "")
    return text


root = flatten((PAPER / "neurocomputing.tex").read_text(encoding="utf-8"))
code = "\n".join(l.split("%", 1)[0] for l in root.splitlines())
assert "{nc/" not in code, re.findall(r"\{nc/[^}]*\}", code)
(SRC / "neurocomputing.tex").write_text(root, encoding="utf-8")
shutil.copy(PAPER / "preamble.tex", SRC / "preamble.tex")
shutil.copy(PAPER / "references.bib", SRC / "references.bib")
for name in INPUTS:
    t = flatten((NC / f"{name}.tex").read_text(encoding="utf-8"))
    for m in re.findall(r"\\(?:includegraphics(?:\[[^]]*\])?|input)\{([^}]*)\}", t):
        assert "/" not in m or m.startswith("#"), (name, m)
    (SRC / f"{name}.tex").write_text(t, encoding="utf-8")
for f in sorted((NC / "figures").glob("*.pdf")):
    shutil.copy(f, SRC / f.name)
photos = sorted((NC / "photos").glob("photo_*.jpg"))
assert len(photos) == 3, photos
for f in photos:
    shutil.copy(f, SRC / f.name)
for f in ("cas-sc.cls", "cas-common.sty"):
    shutil.copy(TEMPLATE / f, SRC / f)
bst = subprocess.run([str(TEXBIN / "kpsewhich.exe"), "elsarticle-num-names.bst"],
                     capture_output=True, text=True).stdout.strip()
shutil.copy(bst, SRC / "elsarticle-num-names.bst")

# compile in the flat folder with nothing but TeX Live's defaults on the path
env = {k: v for k, v in __import__("os").environ.items()
       if k not in ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS")}
run = lambda exe, *a: subprocess.run([str(TEXBIN / f"{exe}.exe"), *a], cwd=SRC,
                                     env=env, capture_output=True, text=True)
for step in (["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "neurocomputing"],
             ["bibtex", "neurocomputing"],
             ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "neurocomputing"],
             ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "neurocomputing"]):
    r = run(*step)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        sys.exit(f"flat build failed at {step[0]}")
log = (SRC / "neurocomputing.log").read_text(encoding="latin-1")
undef = len(re.findall(r"undefined", log))
print("flat build: undefined refs/cites:", undef)
assert undef == 0

import fitz  # PyMuPDF
a = fitz.open(PAPER / "neurocomputing.pdf")
b = fitz.open(SRC / "neurocomputing.pdf")
ta = " ".join("".join(p.get_text() for p in a).split())
tb = " ".join("".join(p.get_text() for p in b).split())
print(f"pages: main {len(a)}, flat {len(b)}; text identical: {ta == tb}")
assert len(a) == len(b) and ta == tb
a.close(); b.close()

keep = [p for p in SRC.iterdir()
        if p.suffix in {".tex", ".bib", ".bbl", ".cls", ".sty", ".bst", ".pdf", ".jpg"}
        and p.name != "neurocomputing.pdf"]
with zipfile.ZipFile(OUT / "06_latex_source.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(keep):
        z.write(p, p.name)
print("zip:", len(keep), "files")

# ---------- the other upload files ----------
shutil.copy(PAPER / "neurocomputing.pdf", OUT / "01_manuscript.pdf")

hl = (NC / "highlights_upload.txt").read_text(encoding="utf-8")
bullets = [l[2:].strip() for l in hl.splitlines() if l.startswith("- ")]
assert 3 <= len(bullets) <= 5 and all(len(b) <= 85 for b in bullets)
(OUT / "02_highlights.txt").write_text(
    "Highlights\n\n" + "\n".join("\u2022 " + b for b in bullets) + "\n", encoding="utf-8")

cl = (NC / "cover_letter.md").read_text(encoding="utf-8")
body = cl.split("\n---\n", 1)[1].strip() + "\n"
(OUT / "03_cover_letter.txt").write_text(body, encoding="utf-8")


def detex(s):
    s = re.sub(r"(?m)^%.*\n", "", s)
    s = s.replace(r"\%", "%").replace("~", " ").replace(r"\&", "&")
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = s.replace("Dr. Garg", "Dr. Garg")
    s = re.sub(r"\$([^$]*)\$", r"\1", s)
    s = s.replace("``", "\u201c").replace("''", "\u201d").replace("'", "\u2019")
    assert "\\" not in s, s[s.index("\\") - 40:s.index("\\") + 40]
    return " ".join(s.split())


bios = (NC / "bios.tex").read_text(encoding="utf-8")
entries = re.findall(r"\\authorbio\{(photo_[a-z]+)\.jpg\}\{(.*?)\}\n\n?(?=\\authorbio|\Z)",
                     bios.split(r"\section*{Author biographies}", 1)[1], re.S)
assert len(entries) == 3, len(entries)
lines = []
for photo, text in entries:
    plain = detex(text)
    lines.append(f"{plain}\n[{len(plain.split())} words; photograph: 05_{photo}.jpg]\n")
    shutil.copy(NC / "photos" / f"{photo}.jpg", OUT / f"05_{photo}.jpg")
(OUT / "04_author_biographies.txt").write_text("\n".join(lines), encoding="utf-8")

abstract = detex((NC / "abstract.tex").read_text(encoding="utf-8"))
(OUT / "abstract_plain.txt").write_text(abstract + "\n", encoding="utf-8")
print("abstract words:", len(abstract.split()))

m = re.search(r"\\begin\{keywords\}(.*?)\\end\{keywords\}", root, re.S)
keywords = [k.strip() for k in " ".join(m.group(1).split()).split(r"\sep")]
t = re.search(r"\\title\[mode=title\]\{(.*?)\}\n\n", root, re.S).group(1)
title = " ".join(t.split())
short = re.search(r"\\shorttitle\{(.*?)\}", root).group(1)
(OUT / "form_fields.txt").write_text(
    f"Title: {title}\nShort title: {short}\nKeywords: {'; '.join(keywords)}\n",
    encoding="utf-8")
print("title:", title)
print("keywords:", keywords)
for p in sorted(OUT.iterdir()):
    print(f"  {p.name:32s} {p.stat().st_size if p.is_file() else '-'}")
