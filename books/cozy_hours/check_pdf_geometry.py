"""Run with a Python environment containing pdfplumber."""
import json
from pathlib import Path
import pdfplumber

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/cozy_hours'
with pdfplumber.open(OUT/'interior.pdf') as pdf:
    assert len(pdf.pages)==124
    errors=[]
    for n,page in enumerate(pdf.pages,1):
        left,right=(45,576) if n%2 else (36,567)
        assert page.width==612 and page.height==792
        for char in page.chars:
            if char['text'].strip() and (char['x0']<left-.1 or char['x1']>right+.1 or char['top']<18 or char['bottom']>774):
                errors.append((n,char['text'],char['x0'],char['x1'],char['top'],char['bottom']))
    assert not errors,errors[:20]
with pdfplumber.open(OUT/'cover_wrap.pdf') as pdf:
    page=pdf.pages[0]
    assert abs(page.width-17.529248*72)<.01 and page.height==810
    assert all(c['x0']>=27 and c['x1']<=page.width-27 and c['top']>=27 and c['bottom']<=783 for c in page.chars)
report=json.loads((OUT/'validation.json').read_text())
report['pdf_text_geometry']='passed: every character checked on all 124 interior pages and full cover'
(OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Every interior and cover character fits the checked safe bounds.')
