"""Reproducible production edition using the project's word-search engine.

Run from repository root: .venv/Scripts/python.exe -X utf8 books/cozy_hours/build.py
The main application and its existing renderers remain unchanged.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from reportlab.lib.colors import CMYKColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader
from wordsearch.domain.grid import GridGenerationFailure
from wordsearch.generation.difficulty import DifficultyLevel
from wordsearch.generation.grid import generate_word_search_grid

SOURCE = Path(__file__).parent
OUT = ROOT / 'output' / 'pdf' / 'cozy_hours'
TITLE = 'Cozy Hours Word Search'
SUBTITLE = '80 Large-Print Puzzles for Adults with No Backward Words'
AUTHOR = 'Rowan Fernvale'
W, H = 612, 792
SIZE = 15
ALL_DIRECTIONS = [(r, c) for r in (-1, 0, 1) for c in (-1, 0, 1) if r or c]
PROFANITY = {'FUCK', 'SHIT', 'CUNT', 'DICK', 'SLUT', 'PISS', 'COCK', 'PORN', 'RAPE'}
COZY_NOTES = {
    'A Slow Morning': 'Let the first cup be a small ceremony, with nowhere to rush.',
    'The Reading Nook': 'A bookmark keeps your place; the story can take you anywhere.',
    'Tea for Two': 'Steeping time is a little pause built into every cup.',
    'Coffee Shop Pause': 'Take a seat, notice the aroma, and let the day wait.',
    'By the Fireplace': 'A soft crackle and a warm blanket make a fine kind of company.',
    'Rain at the Window': 'Rain on the glass turns an ordinary window into a little show.',
    'Fresh Linen': 'Fresh sheets can make bedtime feel like a small new beginning.',
    'An Evening Bath': 'Warm water, a soft towel, and nowhere else to be.',
    'Candlelit Corners': 'A gentle glow can make even a quiet corner feel special.',
    'Turning In': 'A familiar bedtime ritual is a gentle invitation to rest.',
    'Fresh from the Oven': 'The smell of something baking is an invitation to gather.',
    'Cookie Tin': 'A cookie tin is a small promise of something sweet.',
    'A Loaf of Bread': 'Bread dough takes its time; some good things do, too.',
    'Soup on the Stove': 'A simmering pot can make the kitchen feel like home.',
    'Pancake Breakfast': 'A stack of pancakes can turn breakfast into an occasion.',
    'The Spice Shelf': 'A pinch of spice can bring a favorite meal to mind.',
    'Pie on the Table': 'The first slice need not be perfect to taste like home.',
    'Sunday Dinner': 'Passing a dish around gives everyone a reason to linger.',
    'The Pantry': 'A well-stocked pantry makes a simple meal feel possible.',
    'Sweet Little Treats': 'A tiny treat can turn an everyday pause into a celebration.',
    'The Knitting Basket': 'One stitch at a time is still a lovely way to make progress.',
    'Crochet Afternoon': 'A hook, a skein, and a quiet hour are a fine start.',
    'Patchwork Pieces': 'Small scraps can come together to make something lasting.',
    'A Sewing Drawer': 'A loose button is just an excuse to slow down and mend.',
    'Watercolor Morning': 'A little water can turn a dab of pigment into a new color.',
    'Pottery Studio': 'A lump of clay can become something useful with patient hands.',
    'Pressed Flowers': 'A pressed petal keeps a little color from a day outdoors.',
    'Paper Crafts': 'A folded page can become a crane, a card, or a surprise.',
    'A Letter by Hand': 'A handwritten note gives a few thoughtful words a keepsake feel.',
    'A Journal Page': 'A blank page is a quiet place to set down a thought.',
    'The Potting Bench': 'A little soil under your nails is a sign of a good afternoon.',
    'Herbs by the Door': 'Snip a leaf, breathe in, and bring the garden to the table.',
    'Cottage Flowers': 'A handful of garden blooms can brighten an ordinary room.',
    'The Vegetable Patch': 'The best garden harvests often begin with a small seed.',
    'Backyard Birds': 'Pause for a moment and the garden may offer its own birdsong.',
    'The Butterfly Garden': 'A bright flower can turn a garden visit into a small wonder.',
    'The Garden Path': 'A familiar path can feel new when you take it slowly.',
    'Orchard Afternoon': 'An orchard invites you to look up, wander, and taste the season.',
    'Houseplant Corner': 'A sunny windowsill can be a tiny garden of its own.',
    'Garden Visitors': 'Leave a quiet corner for the little visitors passing through.',
    'Woodland Walk': 'Look closely: a woodland floor is full of tiny details.',
    'Trees Along the Way': 'A tree gives a familiar walk a place to pause in the shade.',
    'At the Lake': 'A few quiet minutes by the water can soften a busy day.',
    'A Country Picnic': 'Simple food tastes lovely when the view is part of the table.',
    'Coastal Stroll': 'Follow the shoreline and let the waves set an easy pace.',
    'Mountain Air': 'A deep breath outdoors can make the world feel wide again.',
    'A Sky Full of Stars': 'Give your eyes a moment to adjust and the night sky opens up.',
    'Autumn Footsteps': 'A crisp leaf underfoot is autumn saying hello.',
    'Winter Quiet': 'A fresh snowfall can make even a familiar street feel hushed.',
    'Spring Returns': 'The first new leaves are a lovely reminder that seasons turn.',
    'The Bookshop': 'A bookshop is full of journeys waiting quietly on the shelves.',
    'A Village Bakery': 'A warm loaf is a small pleasure worth taking home.',
    'The Farmers Market': 'A market stroll lets the colors of the season choose your basket.',
    'A Train Window': 'Watch the view change and let the miles do the planning.',
    'Cabin Weekend': 'A cabin stay is permission to trade a schedule for a slower day.',
    'Seaside Cottage': 'Open a window and let the sea breeze join your afternoon.',
    'The Antique Shop': 'Every well-loved object seems to have a story of its own.',
    'Afternoon at the Library': 'A library offers a quiet seat and more worlds than you can count.',
    'The Flower Shop': 'A few stems in a jar can make a whole room feel brighter.',
    'A Park Bench': 'A park bench is a good place to watch the day go by.',
    'Game Night': 'A favorite game makes room for laughter around the table.',
    'The Jigsaw Table': 'One piece at a time, and the picture slowly finds its way.',
    'Movie at Home': 'A familiar film and a soft blanket make a cozy double feature.',
    'Listening to Records': 'Let one whole side play without skipping ahead.',
    'Family Photos': 'Old photographs turn a quiet moment into a shared story.',
    'A Friendly Visit': 'A little conversation can make an ordinary afternoon feel full.',
    'A Cat on the Sofa': 'If the cat has chosen your lap, you may be there a while.',
    'Walking the Dog': "A dog's favorite route can help you notice your own neighborhood.",
    'A Thoughtful Gift': 'The smallest gift can say, “I thought of you.”',
    'A Shared Table': 'A meal shared slowly is about more than what is on the plate.',
    'Little Things to Notice': 'A patch of sunlight can be the best part of a room.',
    'Colors of Comfort': 'Notice the colors that make a familiar place feel like yours.',
    'Soft Textures': 'A favorite blanket is a small comfort you can reach for.',
    'Gentle Sounds': 'Listen for the quiet sounds that are easy to miss.',
    'Familiar Fragrances': 'A familiar scent can bring a comforting memory close.',
    'A Quiet Desk': 'Clear a little space and let one thought have the whole page.',
    'A Gentle Stretch': 'A small stretch is a kind way to greet a new hour.',
    'A Leisurely Saturday': 'A day without rushing leaves room for pleasant surprises.',
    'Treasured Keepsakes': 'A keepsake is a small object holding a much bigger memory.',
    'One More Cozy Hour': 'There is always time to make one more quiet moment your own.',
}


def normalize(word):
    return word.replace(' ', '')


def occurrences(grid, word):
    hits = []
    for r in range(SIZE):
        for c in range(SIZE):
            for dr, dc in ALL_DIRECTIONS:
                er, ec = r + dr * (len(word)-1), c + dc * (len(word)-1)
                if 0 <= er < SIZE and 0 <= ec < SIZE:
                    if ''.join(grid[r+dr*k][c+dc*k] for k in range(len(word))) == word:
                        hits.append((r, c, dr, dc))
    return hits


def load_content():
    puzzles = []
    for line in (SOURCE / 'puzzles.txt').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        section, title, raw = line.split('|')
        words = raw.split(',')
        assert len(words) == 15, (title, len(words))
        normalized = [normalize(w) for w in words]
        assert len(set(normalized)) == 15, title
        assert all(re.fullmatch('[A-Z ]+', w) for w in words), title
        assert all(4 <= len(w) <= SIZE for w in normalized), (title, normalized)
        assert not [(w,b) for w in normalized for b in PROFANITY if b in w or b in w[::-1]], title
        assert not [(a, b) for a in normalized for b in normalized if a != b and a in b], title
        puzzles.append(dict(section=section, title=title, words=words, fact=COZY_NOTES[title]))
    assert len(puzzles) == 80
    assert {p['title'] for p in puzzles} == set(COZY_NOTES)
    assert len({p['title'] for p in puzzles}) == 80
    assert len({p['section'] for p in puzzles}) == 8
    return puzzles


def generate(puzzles):
    for i, puzzle in enumerate(puzzles):
        words = [normalize(w) for w in puzzle['words']]
        for attempt in range(1000):
            seed = 20261118 + i * 10000 + attempt
            result = generate_word_search_grid(words, DifficultyLevel.EASY, SIZE, seed=seed)
            if isinstance(result, GridGenerationFailure):
                continue
            if any(len(occurrences(result.grid, word)) != 1 for word in words):
                continue
            if any(occurrences(result.grid, word) for word in PROFANITY):
                continue
            for placed in result.placed_words:
                assert placed.d_row >= 0 and placed.d_col >= 0
                assert placed.d_row + placed.d_col == 1
                assert occurrences(result.grid, placed.word) == [placed.position]
            puzzle.update(grid=[list(row) for row in result.grid],
                          placements=[asdict(p) for p in result.placed_words], seed=seed)
            if (i+1) % 10 == 0:
                print(f'Validated {i+1}/80 puzzles', flush=True)
            break
        else:
            raise RuntimeError(f'Could not validate puzzle {i+1}: {puzzle["title"]}')
    assert len({''.join(''.join(r) for r in p['grid']) for p in puzzles}) == 80


def fonts():
    folder = ROOT / 'fonts' / 'montserrat' / 'static'
    for name, file in [('Sans', 'Montserrat-Regular.ttf'), ('Medium', 'Montserrat-Medium.ttf'),
                       ('Bold', 'Montserrat-SemiBold.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(folder / file)))
    pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'fonts/abril_fatface/AbrilFatface-Regular.ttf')))


def text(c, x, y, content, size=12, font='Sans', align='left', color=black):
    c.setFillColor(color)
    c.setFont(font, size)
    getattr(c, {'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,content)


def paragraph(c, x, y, content, width, size=13, leading=21, color=black, font='Sans'):
    words, line = content.split(), ''
    for word in words:
        candidate = (line + ' ' + word).strip()
        if pdfmetrics.stringWidth(candidate, font, size) > width and line:
            text(c,x,y,line,size,font,color=color)
            y -= leading
            line = word
        else:
            line = candidate
    if line:
        text(c,x,y,line,size,font,color=color)
    return y-leading


def bounds(page):
    return (45,576) if page % 2 else (36,567)


def footer(c,page):
    left,right=bounds(page)
    text(c,(left+right)/2,31,str(page),10,align='center')


def sparkle(c,x,y,size=4):
    c.saveState()
    c.setStrokeGray(.58)
    c.setLineWidth(.7)
    c.line(x-size,y,x+size,y)
    c.line(x,y-size,x,y+size)
    c.line(x-size*.55,y-size*.55,x+size*.55,y+size*.55)
    c.line(x-size*.55,y+size*.55,x+size*.55,y-size*.55)
    c.restoreState()


def holly_sprig(c,x,y,direction=1):
    c.saveState()
    c.setStrokeGray(.58)
    c.setFillGray(.96)
    c.setLineWidth(.75)
    c.line(x,y,x+direction*25,y+3)
    for offset,side in ((5,1),(12,-1),(19,1)):
        leaf_x=x+direction*offset
        leaf_y=y+offset*.12
        leaf=c.beginPath()
        leaf.moveTo(leaf_x,leaf_y)
        leaf.curveTo(leaf_x+direction*2,leaf_y+side*2,
                     leaf_x+direction*6,leaf_y+side*6,
                     leaf_x+direction*9,leaf_y+side*7)
        leaf.curveTo(leaf_x+direction*7,leaf_y+side*3,
                     leaf_x+direction*3,leaf_y+side,
                     leaf_x,leaf_y)
        leaf.close()
        c.drawPath(leaf,fill=1,stroke=1)
    c.setFillGray(.72)
    for berry_x,berry_y in ((25,3),(29,5),(29,1)):
        c.circle(x+direction*berry_x,y+berry_y,1.5,fill=1,stroke=1)
    c.restoreState()


def title_flourish(c,cx,y):
    c.saveState()
    c.setStrokeGray(.62)
    c.setLineWidth(.7)
    c.line(cx-43,y,cx-9,y)
    c.line(cx+9,y,cx+43,y)
    sparkle(c,cx,y,3)
    c.restoreState()


def cozy_note(c,fact,left,right):
    card_left=left+24
    card_right=right-24
    card_bottom=632
    card_top=665
    c.saveState()
    c.setStrokeGray(.58)
    c.setLineWidth(.8)
    c.roundRect(card_left,card_bottom,card_right-card_left,card_top-card_bottom,8,fill=0,stroke=1)
    label_width=91
    c.setFillColor(white)
    c.rect((left+right-label_width)/2,card_top-2,label_width,5,fill=1,stroke=0)
    text(c,(left+right)/2,card_top-1,'A COZY NOTE',8,'Bold',align='center',color=black)
    sparkle(c,card_left+14,(card_bottom+card_top)/2,3)
    sparkle(c,card_right-14,(card_bottom+card_top)/2,3)
    assert pdfmetrics.stringWidth(fact,'Sans',10) <= card_right-card_left-46, fact
    text(c,(left+right)/2,card_bottom+10,fact,10,'Sans',align='center')
    c.restoreState()


def word_bank_heading(c,cx,y):
    c.saveState()
    c.setStrokeGray(.65)
    c.setLineWidth(.7)
    c.line(cx-78,y+3,cx-39,y+3)
    c.line(cx+39,y+3,cx+78,y+3)
    sparkle(c,cx-86,y+3,2)
    sparkle(c,cx+86,y+3,2)
    text(c,cx,y,'WORDS TO FIND',8,'Bold',align='center')
    c.restoreState()


def grid(c,puzzle,cx,top,cell=30,size=22,solution=False):
    x0=cx-SIZE*cell/2
    y0=top-SIZE*cell
    if solution:
        c.saveState()
        c.setStrokeGray(.78)
        c.setLineWidth(cell*.75)
        c.setLineCap(1)
        for p in puzzle['placements']:
            x=x0+(p['col']+.5)*cell
            y=top-(p['row']+.5)*cell
            c.line(x,y,x+p['d_col']*(len(p['word'])-1)*cell,y-p['d_row']*(len(p['word'])-1)*cell)
        c.restoreState()
    c.setStrokeGray(.25)
    c.setLineWidth(.75)
    c.rect(x0-6,y0-6,SIZE*cell+12,SIZE*cell+12)
    for r,row in enumerate(puzzle['grid']):
        for col,letter in enumerate(row):
            text(c,x0+(col+.5)*cell,top-(r+.5)*cell-size*.35,letter,size,'Medium',align='center')


def interior(puzzles):
    path=OUT/'interior.pdf'
    c=canvas.Canvas(str(path),pagesize=(W,H),pageCompression=1)
    c.setTitle(TITLE)
    c.setAuthor(AUTHOR)
    c.setSubject(SUBTITLE)
    c.setCreator('Cozy Hours production edition')
    # 1: title, 2: ownership and publishing note, 3: instructions, 4: contents.
    text(c,306,650,'COZY HOURS',46,'Display',align='center')
    text(c,306,591,'WORD SEARCH',33,'Bold',align='center')
    text(c,306,524,'80 Large-Print Puzzles for Adults',18,align='center')
    text(c,306,495,'with No Backward Words',18,align='center')
    c.setLineWidth(.8)
    c.line(226,455,386,455)
    text(c,306,408,'Small comforts. A little time for yourself.',14,align='center')
    text(c,306,184,AUTHOR,17,'Bold',align='center')
    c.showPage()
    text(c,54,676,'Make yourself at home.',30,'Display')
    paragraph(c,54,625,'This book belongs to',480,16)
    c.line(54,557,470,557)
    text(c,54,481,'A gift from',16)
    c.line(54,443,470,443)
    paragraph(c,54,330,'Find a comfortable spot, pick a puzzle, and enjoy a few quiet minutes. Start at the beginning or choose whichever theme suits your day.',475,15,25)
    paragraph(c,54,166,f'{TITLE} | {AUTHOR}. First edition, 2026. Puzzles and layout prepared for this edition. Solutions begin on page 85.',475,10,16)
    text(c,54,94,'For personal enjoyment. All puzzles include complete solutions.',10)
    footer(c,2)
    c.showPage()
    text(c,54,716,'A simple way to unwind',30,'Display')
    y=652
    for heading,body in [
        ('1. Choose your puzzle','Each page has a 15 x 15 grid and 15 words or phrases to find.'),
        ('2. Look across and down','Words read from left to right or from top to bottom. There are no backward or diagonal words.'),
        ('3. Ignore the spaces','Phrases appear without spaces in the grid. For example, WARM DRINK appears as WARMDRINK.'),
        ('4. Mark each find','Circle or underline each word in the list when you find it. Words can cross or share letters.'),
        ('5. Check when you like','The answer page is printed in the footer of each puzzle. Answers use shaded lines, with two puzzles per page.')]:
        text(c,54,y,heading,17,'Bold')
        y=paragraph(c,54,y-28,body,485,14,22)-30
    text(c,54,123,'There is no timer. Enjoy the search at your own pace.',13,'Medium')
    text(c,54,91,'Puzzle letters: 22 pt. Word lists and solution letters: 16 pt.',10)
    footer(c,3)
    c.showPage()
    text(c,54,712,'Choose a cozy moment',30,'Display')
    text(c,54,674,'Eight themes. Ten puzzles in each.',15)
    sections=list(dict.fromkeys(p['section'] for p in puzzles))
    for i,section in enumerate(sections):
        y=606-i*54
        text(c,54,y,f'{i+1:02}',13,'Bold')
        text(c,98,y,section,18,'Medium')
        text(c,546,y,str(5+i*10),16,align='right')
        c.setStrokeGray(.75)
        c.line(98,y-14,546,y-14)
    text(c,98,130,'Solutions',18,'Medium')
    text(c,546,130,'85',16,align='right')
    footer(c,4)
    c.showPage()
    for i,p in enumerate(puzzles):
        page=i+5
        left,right=bounds(page)
        cx=(left+right)/2
        text(c,left,745,p['section'].upper(),10,'Bold')
        text(c,right,745,f'{i+1:02} / 80',10,'Bold',align='right')
        holly_sprig(c,left+7,727)
        holly_sprig(c,right-7,727,-1)
        title_size=min(29, (right-left)*29/pdfmetrics.stringWidth(p['title'],'Display',29))
        text(c,cx,706,p['title'],title_size,'Display',align='center')
        title_flourish(c,cx,691)
        cozy_note(c,p['fact'],left,right)
        grid(c,p,cx,615)
        word_bank_heading(c,cx,142)
        column_width=(right-left)/3
        for j,word in enumerate(sorted(p['words'])):
            col,row=divmod(j,5)
            entry_width=pdfmetrics.stringWidth(word,'Sans',16)
            assert entry_width <= column_width, word
            x=left+(col+.5)*column_width-entry_width/2
            y=124-row*19
            text(c,x,y,word,16)
        text(c,right,31,f'Answers p. {85+i//2}',8,align='right')
        footer(c,page)
        c.showPage()
    for pair in range(40):
        page=85+pair
        left,right=bounds(page)
        cx=(left+right)/2
        text(c,left,748,'SOLUTIONS',11,'Bold')
        text(c,right,748,'COZY HOURS',10,'Medium',align='right')
        for slot in range(2):
            i=pair*2+slot
            p=puzzles[i]
            y=711-slot*346
            text(c,cx,y,f'{i+1:02}  {p["title"]}',17,'Bold',align='center')
            text(c,cx,y-21,f'Puzzle on page {i+5}',10,align='center')
            grid(c,p,cx,y-40,cell=18,size=16,solution=True)
        footer(c,page)
        c.showPage()
    c.save()
    return path


# Original vector illustration: an open book, cup, and leafy stems.
def still_life(c,cx,y,scale=1):
    cream=CMYKColor(0,.03,.12,0)
    gold=CMYKColor(.05,.26,.69,.05)
    rust=CMYKColor(.10,.66,.72,.18)
    sage=CMYKColor(.32,.13,.35,.13)
    dark=CMYKColor(.73,.38,.48,.45)
    c.saveState()
    c.translate(cx,y)
    c.scale(scale,scale)
    c.setFillColor(sage)
    c.ellipse(-200,-17,200,17,fill=1,stroke=0)
    c.setFillColor(gold)
    c.roundRect(-151,0,195,28,5,fill=1,stroke=0)
    c.setFillColor(cream)
    c.rect(-141,7,178,12,fill=1,stroke=0)
    # Open pages, as two gently curved shapes.
    for sign in (-1,1):
        p=c.beginPath(); p.moveTo(-25,38); p.curveTo(-25+sign*45,60,-25+sign*90,48,-25+sign*115,53)
        p.lineTo(-25+sign*106,96); p.curveTo(-25+sign*60,102,-25+sign*20,105,-25,82); p.close()
        c.setFillColor(cream); c.setStrokeColor(dark); c.setLineWidth(2); c.drawPath(p,fill=1,stroke=1)
        c.setLineWidth(.7)
        for dy in (0,9,18):
            c.line(-25+sign*16,66+dy,-25+sign*91,72+dy)
    # Cup, handle and steam.
    c.setStrokeColor(rust); c.setLineWidth(10); c.circle(126,63,22,stroke=1,fill=0)
    c.setFillColor(rust); c.roundRect(35,15,91,83,17,stroke=0,fill=1)
    c.setFillColor(cream); c.ellipse(38,88,123,105,stroke=0,fill=1)
    c.setFillColor(dark); c.ellipse(43,91,118,101,stroke=0,fill=1)
    c.setStrokeColor(cream); c.setLineWidth(2)
    for x in (62,83,104):
        p=c.beginPath(); p.moveTo(x,116); p.curveTo(x-12,132,x+12,145,x,160); c.drawPath(p)
    # Sprigs behind the book.
    c.setStrokeColor(sage); c.setFillColor(sage); c.setLineWidth(3)
    c.line(-143,20,-174,166)
    for yy in (65,92,119,146):
        xx=-143-(yy-20)*31/146
        for sign in (-1,1):
            p=c.beginPath(); p.moveTo(xx,yy); p.curveTo(xx+sign*12,yy+28,xx+sign*38,yy+25,xx+sign*31,yy+9); p.curveTo(xx+sign*20,yy-2,xx+sign*7,yy-3,xx,yy); c.drawPath(p,fill=1,stroke=0)
    c.restoreState()


def cover(page_count):
    spine=page_count*.002252*72
    bleed=9
    width=2*W+spine+2*bleed
    height=H+2*bleed
    path=OUT/'cover_wrap.pdf'
    c=canvas.Canvas(str(path),pagesize=(width,height),pageCompression=1)
    c.setTitle(TITLE+' - paperback cover')
    c.setAuthor(AUTHOR)
    dark=CMYKColor(.73,.38,.48,.45)
    cream=CMYKColor(0,.03,.12,0)
    gold=CMYKColor(.05,.26,.69,.05)
    c.setFillColor(dark); c.rect(0,0,width,height,fill=1,stroke=0)
    front=bleed+W+spine
    center=front+W/2
    c.setStrokeColor(gold); c.setLineWidth(1)
    c.roundRect(front+27,bleed+27,W-54,H-54,16,fill=0,stroke=1)
    text(c,center,735,'80 LARGE-PRINT PUZZLES',15,'Bold',align='center',color=cream)
    text(c,center,648,'Cozy Hours',68,'Display',align='center',color=cream)
    text(c,center,585,'WORD SEARCH',36,'Bold',align='center',color=gold)
    text(c,center,540,'FOR ADULTS',14,'Medium',align='center',color=cream)
    still_life(c,center,288,1.08)
    text(c,center,226,'Small comforts.',21,'Display',align='center',color=cream)
    text(c,center,196,'A little time for yourself.',21,'Display',align='center',color=cream)
    text(c,center,137,'WITH NO BACKWARD WORDS',15,'Bold',align='center',color=gold)
    text(c,center,72,AUTHOR.upper(),14,'Medium',align='center',color=cream)
    # Spine (no barcode here); all text well inside the printable spine width.
    c.saveState(); c.translate(bleed+W+spine/2, height/2); c.rotate(90)
    text(c,0,-3,'COZY HOURS WORD SEARCH  /  ROWAN FERNVALE',8,'Bold',align='center',color=cream)
    c.restoreState()
    backx=bleed+48
    text(c,backx,700,'Your next quiet moment',31,'Display',color=cream)
    text(c,backx,658,'starts here.',31,'Display',color=cream)
    y=paragraph(c,backx,604,'Put the kettle on, find your favorite chair, and settle into 80 themed word searches inspired by the small pleasures of everyday life.',W-96,17,27,cream)
    y=paragraph(c,backx,y-20,'From a reading nook and a village bakery to garden paths and a lakeside stroll, each puzzle offers a fresh little escape.',W-96,17,27,cream)
    for label in ['80 puzzles, with 15 words to find in each', 'Large 22-point puzzle letters', 'Across and down only - no diagonal words', 'Clear word lists in centered columns', 'Complete solutions included']:
        y-=31
        text(c,backx,y,'+  '+label,13,'Medium',color=cream)
    text(c,backx,211,'A thoughtful gift. A pleasure all year round.',13,'Medium',color=gold)
    # KDP barcode reserved area: 2 x 1.2 in, >= .25 in from trim/spine.
    c.setFillColor(white)
    c.rect(bleed+W-162,bleed+36,144,86.4,fill=1,stroke=0)
    c.save()
    return path,dict(width_in=width/72,height_in=height/72,spine_in=spine/72,bleed_in=.125)


def verify_pdf(path, expected_pages, puzzles):
    reader=PdfReader(path)
    assert len(reader.pages)==expected_pages
    assert not reader.is_encrypted
    for p in reader.pages:
        assert float(p.mediabox.width)==W and float(p.mediabox.height)==H
        fonts_used=p['/Resources'].get('/Font',{})
        for ref in fonts_used.values():
            f=ref.get_object()
            if f.get('/BaseFont')=='/Helvetica':
                continue  # ReportLab's unused default resource.
            descriptor=f.get('/FontDescriptor')
            assert descriptor and descriptor.get_object().get('/FontFile2'),f
    for i in range(80):
        content=reader.pages[i+4].extract_text()
        assert 'Across and down only' not in content
        assert f'Answers p. {85+i//2}' in content
        assert puzzles[i]['fact'] in content
        assert 'A COZY NOTE' in content
        assert 'WORDS TO FIND' in content
    for i in range(40):
        content=reader.pages[84+i].extract_text()
        assert f'Puzzle on page {5+i*2}' in content
        assert f'Puzzle on page {6+i*2}' in content


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    puzzles=load_content()
    generate(puzzles)
    fonts()
    interior_path=interior(puzzles)
    verify_pdf(interior_path,124,puzzles)
    cover_path,cover_spec=cover(124)
    counts=Counter(normalize(w) for p in puzzles for w in p['words'])
    report=dict(title=TITLE,subtitle=SUBTITLE,author=AUTHOR,puzzles=80,word_entries=1200,
                distinct_entries=len(counts),most_repeated=counts.most_common(15),pages=124,
                trim_in=[8.5,11],interior_ink='black',paper='white',interior_bleed=False,
                inner_margin_in=.625,outer_margin_in=.5,grid_font_pt=22,word_list_font_pt=16,
                solution_font_pt=16,unique_target_occurrences=True,directions=['right','down'],
                restricted_word_scan=sorted(PROFANITY),cover=cover_spec,
                files={p.name:p.stat().st_size for p in [interior_path,cover_path]},
                cozy_notes=80,word_list_alignment='centered in three columns',
                print_cost_usd=round(1+.017*124,3),royalty_at_9_99_usd=round(.6*9.99-(1+.017*124),3),
                digital_checks='passed',visual_checks='sampled pages: 5, 42, 85',
                physical_proof='not ordered',
                ai_generated_text=True,ai_generated_artwork=True)
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'puzzles_and_solutions.json').write_text(json.dumps(puzzles,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
