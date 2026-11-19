"""Render every page and make contact sheets for editorial inspection."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/cozy_hours'
TMP=ROOT/'tmp/pdfs/cozy_hours'
TMP.mkdir(parents=True,exist_ok=True)
subprocess.run(['pdftoppm','-scale-to','500','-png',str(OUT/'interior.pdf'),str(TMP/'page')],check=True)
pages=sorted(TMP.glob('page-*.png'))
assert len(pages)==124
for start in range(0,124,25):
    sheet=Image.new('RGB',(1250,1750),'#dddddd')
    draw=ImageDraw.Draw(sheet)
    for k,path in enumerate(pages[start:start+25]):
        im=Image.open(path).convert('RGB')
        im.thumbnail((240,315))
        x=(k%5)*250+(250-im.width)//2
        y=(k//5)*350+20
        sheet.paste(im,(x,y))
        draw.text(((k%5)*250+10,(k//5)*350+337),f'PAGE {start+k+1}',fill='black')
    sheet.save(TMP/f'contact-{start//25+1}.png')
subprocess.run(['pdftoppm','-r','110','-singlefile','-png',str(OUT/'cover_wrap.pdf'),str(OUT/'cover_preview')],check=True)
# Crop of the rendered final PDF, not a separate design.
cover=Image.open(OUT/'cover_preview.png')
front_left=round((.125+8.5+.279248)*110)
front=cover.crop((front_left,round(.125*110),front_left+round(8.5*110),round(11.125*110)))
front.save(OUT/'front_cover.png')
for page in (3,5,42,84,85,124):
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r','110','-singlefile','-png',str(OUT/'interior.pdf'),str(TMP/f'detail-{page}')],check=True)
print('Rendered 124 pages, 5 contact sheets, 6 detail pages and cover.')
