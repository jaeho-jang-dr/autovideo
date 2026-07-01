# -*- coding: utf-8 -*-
"""48샷 키프레임 프롬프트 빌더 → kf_shots.tsv (key \t ref(or NONE) \t prompt).
실사=real/ 캐릭터 ref + 사실풍, 애니=anim/ 캐릭터 ref + 플랫, 무캐릭터/개념=ref 없음(text→image)."""
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

REAL_STYLE = ("cinematic semi-realistic painterly illustration, soft realistic lighting and textures, "
              "historical Joseon-era Korea, dignified warm mood, 16:9 wide cinematic composition. "
              "No text, no watermark, no captions, no subtitles.")
ANIM_STYLE = ("warm friendly modern Korean webtoon / flat vector illustration, simplified clean lines, "
              "soft pastel colors, NORMAL human proportions (NOT chibi), 16:9 wide composition. "
              "No text, no watermark, no captions, no subtitles.")

CHAR = {
    "child":     ("young boy prince Chungnyeong (child Sejong), SAME boyish face, child hanbok and small black hat", "child"),
    "youth":     ("the young man Chungnyeong (youth Sejong), SAME young adult face, scholar's hat and hanbok", "youth"),
    "youngking": ("the YOUNG King Sejong, SAME young face, black ikseongwan royal crown, red gonryongpo robe with golden dragon roundels", "youngking"),
    "mid":       ("middle-aged King Sejong, SAME face, full dark beard, black ikseongwan royal crown, red gonryongpo robe with golden dragon roundels", "mid"),
    "old":       ("elderly King Sejong, SAME dignified aged face with white-streaked beard, black ikseongwan royal crown, red gonryongpo robe", "old"),
}

# (key, mode, char|None, scene description)
SHOTS = [
 ("S01","real",None,"Gwanghwamun Gate plaza in modern Seoul at golden misty dawn, the great seated BRONZE statue of King Sejong the Great (dark patina bronze, NOT gold), an aerial sweep gliding across the plaza toward the statue, majestic and reverent"),
 ("S02","anim","child","a candle-lit hanok room at night, the little boy prince utterly absorbed in reading an open book, fingertips turning a page, cozy warm glow"),
 ("S03","anim","child","a village schoolroom (seodang); three royal boys — the two elder distracted, only little Chungnyeong sitting upright neatly copying text, the teacher smiling warmly"),
 ("S04","anim","child","the little prince with slightly red tired eyes; gentle adults softly gathering his books away; the boy reaching toward a bundle of books being carried off, wistful"),
 ("S05","anim","child","the little prince in a corner behind a folding paper screen, joyfully discovering ONE last book, eyes shining bright with delight"),
 ("S06","anim","child","a pondside pavilion in spring; the young boy prince speaking earnestly and politely, spring breeze in his sleeves, soft water reflections"),
 ("S07","anim","youth","a quiet amber-lit study; the young man Chungnyeong deeply reading classics, surrounded by tall piles of books, content"),
 ("S08","anim","youth","a curious young man among many things — a gayageum (Korean zither), an astronomy star chart, healing herbs, counting rods — exploring each with bright curiosity"),
 ("S09","anim","youth","an autumn lakeside; the young man calmly watching a distant royal procession far away, maple leaves drifting, serene and detached"),
 ("S10","anim","youth","a kind young prince warmly and humbly greeting palace people, gently bowing to an elderly servant, warm light"),
 ("S11","anim","youth","a palace audience room; an older father king (King Taejong) talking with the young Chungnyeong, the father smiling with quiet pride at his son's wisdom (two figures)"),
 ("S12","anim","youth","a temple courtyard; the young man Chungnyeong standing beside his kind bride Queen Soheon, oriental-painting composition, serene (two figures)"),
 ("S13","anim","youth","a home wooden veranda; the young father with his wife and three happy laughing children, warm soft-focus family scene"),
 ("S14","anim","youth","a back garden at night; the young man gazing up at the bright North Star in a star-filled sky, bamboo silhouettes, contemplative"),
 ("S15","real","youngking","the grand throne hall (Geunjeongjeon) enthronement; a 22-year-old young King Sejong upon the throne with the sun-moon-five-peaks folding screen behind, officials bowing low, an aerial sweep descending to the throne, majestic"),
 ("S16","real","youngking","close on the newly enthroned young king; his hands tremble slightly but his eyes are firm and determined, candlelight"),
 ("S17","real","youngking","the Jiphyeonjeon study hall; the young king gathering talented young scholars among bookshelves, warm amber light, lively"),
 ("S18","real","youngking","deep night in the royal office; the diligent young king reading mountains of books and reports by candlelight, a cold untouched meal beside him"),
 ("S19","real","youngking","golden countryside fields; the young king touring the fields and market, looking closely at the people's lives and talking with a farmer, an aerial sweep over the fields then down"),
 ("S20","real","youngking","a royal council; the king discussing policy with wise senior ministers, brush in hand, incense smoke, low-angle dignified"),
 ("S21","real","youngking","outside a government office; common people in tears over an injustice, the king watching from afar with a pained sympathetic look"),
 ("S22","real","youngking","the king's chamber by candlelight; the king opening and studying an illustrated picture book"),
 ("S23","real",None,"a poor farmhouse at sunset; a farmer couple puzzled, unable to read the Chinese characters beside the pictures in a book, tilting their heads helplessly"),
 ("S24","real","mid","a government courtyard; middle-aged King Sejong in red royal robe watching weeping commoners with an aching sympathetic heart, close on his troubled caring face"),
 ("S25","real","mid","the king's desk in the royal office; sweeping aside illustrations, his brush tip unconsciously doodling little circles and lines, extreme close on the brush"),
 ("S26","real","mid","a midnight chamber; the king with tired eyes studying late, sketching letter-stroke trajectories, cool blue night light, orbiting view"),
 ("S27","real","mid","a snowy night; the king's silhouette behind a paper screen places the final small dot, then gazes up at the night sky"),
 ("S28","anim",None,"cosmic dreamlike concept — many newly created glowing Korean letter shapes overlapping with constellations in the night sky, an aerial cosmic sweep, leave open empty sky space"),
 ("S29","real","mid","a scholars' office; the young scholars with the king happily writing a test book in the new letters, words flowing easily, horizontal tracking"),
 ("S30","real",None,"a palace courtyard in the morning; an official respectfully holding up a memorial scroll of protest, steadicam wide"),
 ("S31","real",None,"between the pillars of the royal office; an upright stern official loudly objecting, other ministers nodding, rack focus depth"),
 ("S32","real","mid","the king listening to repeated objections among piles of books, his face slowly hardening, crane-up with cold shadows"),
 ("S33","real","mid","an extreme close-up of middle-aged King Sejong's face at the very limit of his patience, intense cinematic lighting"),
 ("S34","anim","mid","stylized animation — middle-aged King Sejong standing and speaking firmly and clearly, the whole room glowing warm, low angle, powerful and resolute"),
 ("S35","real",None,"a wide shot — the ministers fallen quiet and respectfully bowing their heads after the king's firm words"),
 ("S36","real","mid","a quiet palace at night under moonlight; the king alone, resolved and firm, lateral dolly"),
 ("S37","anim",None,"surreal educational concept — a warm silvery cross-section diagram of a human mouth and throat showing tongue and lip shapes; leave LARGE empty space around it for letters to be added later; orbit feel"),
 ("S38","anim",None,"pure white hanji paper with a single brush ink stroke and soft ink bleeding; leave LARGE empty clean space for letters to be added later; extreme close brush tip"),
 ("S39","anim",None,"cosmic concept — the North Star above, a round glow (sky), a flat horizontal line (earth), a standing vertical line (person); leave LARGE empty space for letters; descending crane"),
 ("S40","anim",None,"a glowing ring of light with three simple luminous strokes rotating to combine; leave LARGE empty central space for vowel letters to be added later; orbiting"),
 ("S41","real","mid","the sunlit Sujeongjeon courtyard; scholars holding the Hunminjeongeum book and bowing, the king on the throne pleased, calligraphy scattering as golden particles, dolly-in & jib down"),
 ("S42","real","old","the royal office; elderly King Sejong tenderly caressing books written in the new Hangeul, warm engraved light"),
 ("S43","real","old","an examination yard; clerks taking a Hangeul writing test, red circles marking correct answers, crane down"),
 ("S44","real","old","a quiet chamber; the aged king keeping his books close despite weak eyes, heavy diagonal dolly"),
 ("S45","real","old","dawn mist; the gentle view drifting to the pine trees of Yeongneung outside the window, a peaceful tender ending mood"),
 ("S46","real",None,"a museum glass case holding the precious Hunminjeongeum book, dissolving toward bright modern classrooms around the world learning Hangeul, slide then orbit"),
 ("S47","anim",None,"a coda — Korean letter-strokes rising as glowing particles of light, an uplifting bridge between the animated past and the bright present; leave open glowing space for letters"),
 ("S48","real",None,"modern Gwanghwamun Square; a joyful Hangeul Day festival with people from all over the world enjoying Hangeul, letters rising into the autumn sky, horizontal tracking up to a jib-up finale"),
]

def ref_for(mode, char):
    if char is None: return None
    folder = "real" if mode == "real" else "anim"
    return f"sejong_film/{folder}/sejong_{CHAR[char][1]}.png"

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kf_shots.tsv")
n_real = n_anim = n_plain = 0
with open(out, "w", encoding="utf-8") as f:
    for key, mode, char, desc in SHOTS:
        style = REAL_STYLE if mode == "real" else ANIM_STYLE
        ref = ref_for(mode, char)
        if ref:
            idlock = f"Using the uploaded reference of {CHAR[char][0]} as the strict identity guide. "
            prompt = f"{idlock}Draw a WIDE 16:9 scene: {desc}. {style}"
            f.write(f"{key}\t{ref}\t{prompt}\n")
            n_real += mode == "real"; n_anim += mode == "anim"
        else:
            prompt = f"WIDE 16:9 scene: {desc}. {style}"
            f.write(f"{key}\tNONE\t{prompt}\n")
            n_plain += 1
print(f"wrote {out}: total {len(SHOTS)} (real-char {n_real} / anim-char {n_anim} / plain {n_plain})")
