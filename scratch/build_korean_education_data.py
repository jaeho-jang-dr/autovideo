# -*- coding: utf-8 -*-
import os

target_dir = r"d:\Entertainments\DevEnvironment\autovideo\korean_education"
os.makedirs(target_dir, exist_ok=True)

# 90 Scenes: Scene 0 to Scene 89
scenes = []

# Part 1: Prologue & The Birth of Hangeul (0 - 9)
scenes.append({
    "num": 0,
    "text": "안녕하세요! 세상에서 가장 쉽고 과학적인 문자, 한글의 세계에 오신 것을 환영합니다.",
    "text_en": "Hello! Welcome to the world of Hangul, the easiest and most scientific alphabet in the world.",
    "motion": ":: [zoom_bounce] a clean 2D vector line art book opens, Korean letters (한글) gently float up on a solid flat beige background (#F5F5F0), camera slowly zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a clean open book with Korean letters (한글) gently floating up, camera slowly zooming in, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 1,
    "text": "조선 초기, 글을 읽지 못하는 백성들은 많은 사회적 불이익을 겪었습니다.",
    "text_en": "In the early Joseon Dynasty, commoners who could not read faced many social disadvantages.",
    "motion": ":: [pulse] commoners looking helpless at a public notice board covered in complex Chinese characters on a solid flat background (#F5F5F0), camera slowly panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), simple silhouettes of commoners looking at a public notice board, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 2,
    "text": "중국의 한자는 배우기 너무 복잡해 일반 백성들이 지식을 쌓기 불가능했죠.",
    "text_en": "Chinese characters were too complex to learn, making it impossible for ordinary people to gain knowledge.",
    "motion": ":: [rotation] a scholar surrounded by towering stacks of heavy Chinese scrolls on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), stacks of heavy scrolls and book volumes around a small desk, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 3,
    "text": "백성들의 고통을 가엾이 여긴 세종대왕은 쉬운 고유 문자를 창제하려 했습니다.",
    "text_en": "King Sejong, who pitied the suffering of his people, sought to create an easy, native writing system.",
    "motion": ":: [zoom_bounce] King Sejong observing the quiet daily life of ordinary peasants on a solid flat background (#F5F5F0), camera zooming in slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), silhouette of a king looking out of a palace window, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 4,
    "text": "한자를 옹호하는 지배층의 반대에도 불구하고 세종은 비밀리에 작업을 계속했죠.",
    "text_en": "Despite opposition from the ruling class who defended Chinese characters, Sejong continued his work in secret.",
    "motion": ":: [shake] stately silhouettes of noble scholars gesturing in heated debate on a solid flat background (#F5F5F0), camera slowly shaking side to side",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), profiles of scholars in heated debate with expressive hand gestures, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 5,
    "text": "마침내 1446년, 백성을 가르치는 바른 소리, '훈민정음'이 세상에 반포됩니다.",
    "text_en": "Finally, in 1446, Hunminjeongeum, meaning 'the proper sounds for instructing the people', was promulgated.",
    "motion": ":: [zoom_bounce] a historic parchment unfurling, exposing the original Hangul glyphs on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a clean scroll unfurling showing geometric Korean letters, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 6,
    "text": "글이란 마땅히 모두가 편리하게 써야 한다는 세종의 애민 정신이 깃들어 있습니다.",
    "text_en": "It embodies Sejong's love for the people, believing that writing should be easily used by everyone.",
    "motion": ":: [pulse] clean line art of hands joining to hold a glowing Korean letter on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), two hands cupped together holding a glowing Korean character, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 7,
    "text": "한글은 단순히 소리를 적는 표음문자를 넘어 모양에 소리 성질을 담은 자질 문자입니다.",
    "text_en": "Hangul is not just a phonetic alphabet; it is a featural alphabet where letter shapes reflect phonetic properties.",
    "motion": ":: [zoom_bounce] graphical diagram contrasting alphabet letters with modular blocks on a solid flat background (#F5F5F0), camera slowly zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), diagram comparing separate letters to grouped syllable blocks, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 8,
    "text": "지혜로운 자는 아침에, 어리석은 자도 열흘이면 다 깨칠 정도로 배움이 쉽습니다.",
    "text_en": "A wise man can learn it in a morning, and even a simple man can learn it in ten days.",
    "motion": ":: [pulse] a candle glowing next to a page, indicating quick study times on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a burning candle next to an open book, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 9,
    "text": "오늘날 세계 유수의 언어학자들은 한글을 가장 정교한 글자로 극찬하고 있죠.",
    "text_en": "Today, leading linguists worldwide praise Hangul as the most sophisticated writing system.",
    "motion": ":: [rotation] a stylized globe surrounded by magnifying glasses and pens on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a simple globe outline surrounded by pens and icons, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 2: Consonant Articulation & The 5 Base Shapes (10 - 19)
scenes.append({
    "num": 10,
    "text": "한글의 자음은 소리를 낼 때 발음 기관이 움직이는 형태를 고스란히 본떴습니다.",
    "text_en": "Hangul's consonants mimic the actual shape of the vocal organs when producing sound.",
    "motion": ":: [zoom_bounce] human profile showing oral tract, lips, tongue, and throat in black outline on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), sagittal cross-section of a human head showing vocal organs, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 11,
    "text": "자음 ㄱ은 혀뿌리가 목구멍을 막는 형태에서 따온 모양입니다.",
    "text_en": "The consonant 'G [k/g]' represents the root of the tongue blocking the throat.",
    "motion": ":: [pulse] detailed oral cavity: back of the tongue raised to block the throat path on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), close-up of oral cavity diagram with the back of tongue raised to block throat, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 12,
    "text": "자음 ㄴ은 혀끝이 윗잇몸에 가볍게 닿아 스치는 혀의 모습을 담았습니다.",
    "text_en": "The consonant 'N' depicts the tip of the tongue touching the upper gums.",
    "motion": ":: [pulse] oral cavity: tongue tip touching the alveolar ridge with yellow path on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), close-up of tongue tip touching the area behind upper teeth, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 13,
    "text": "자음 ㅁ은 네모난 입술이 서로 만나 소리를 닫고 여는 입의 입술 윤곽입니다.",
    "text_en": "The consonant 'M' is the outline of the lips meeting to open and close sounds.",
    "motion": ":: [pulse] closed lips highlighted in yellow, opening slightly to let sound out on a solid flat background (#F5F5F0), camera slowly zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), frontal outline of closed lips forming a square shape, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 14,
    "text": "자음 ㅅ은 공기를 마찰시키는 단단한 치아, 즉 이의 뾰족한 모양입니다.",
    "text_en": "The consonant 'S' represents the sharp shape of teeth where air friction is created.",
    "motion": ":: [zoom_bounce] a sharp, clean outline of teeth, showing sibilant airflow passing through on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), diagram of human teeth with air flowing through, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 15,
    "text": "자음 ㅇ은 열려 있는 둥근 목구멍의 단면을 고스란히 형상화한 것입니다.",
    "text_en": "The consonant 'NG' mimics the circular cross-section of the open throat.",
    "motion": ":: [pulse] throat cavity shown in circular cross-section, glowing softly on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), simple circular outline representing an open throat, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 16,
    "text": "혀를 뒤로 당겨 목구멍을 좁힐 때 느껴지는 ㄱ소리의 발음 구조를 보시죠.",
    "text_en": "Let's look at the structure of the 'G' sound when the tongue pulls back, narrowing the throat.",
    "motion": ":: [pulse] tongue drawing back toward the soft palate (Velar position) on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), tongue moving backwards to block the pharynx, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 17,
    "text": "ㄴ소리를 낼 때 혀끝이 윗잇몸을 튕기며 내는 공기의 차단을 느껴보세요.",
    "text_en": "Feel the blockage of air as the tongue tip taps the upper gums when making the 'N' sound.",
    "motion": ":: [zoom_bounce] tongue tip tapping behind upper teeth (Alveolar position) on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), tongue tip pressed against the alveolar ridge, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 18,
    "text": "입술이 닫혀 소리가 모였다가 터지는 ㅁ소리의 편안한 양순음 움직임.",
    "text_en": "The comfortable bilabial movement of the 'M' sound, where lips close to gather sound and then release.",
    "motion": ":: [pulse] flat lips closing and opening horizontally on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), human profile focusing on lips closing tightly then opening, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 19,
    "text": "ㅅ소리가 새어 나올 때 혀끝이 아랫니 안쪽에 살짝 머무는 치경 마찰음.",
    "text_en": "The alveolar fricative 'S' sound, where the tongue tip rests slightly behind the lower teeth as air escapes.",
    "motion": ":: [pulse] tongue positioned behind lower teeth, showing frictional air channel on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), air passing between tongue tip and teeth, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 3: Stroke Addition & Consonant Completion (20 - 29)
scenes.append({
    "num": 20,
    "text": "기본 다섯 글자에서 소리가 강해질 때 획을 더해가는 '가획의 원리'입니다.",
    "text_en": "This is the 'principle of stroke addition', adding lines to base shapes as sounds become stronger.",
    "motion": ":: [zoom_bounce] 'ㄱ' morphing into 'ㅋ' as a yellow stroke is drawn horizontally on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㄱ' changing to 'ㅋ' with a stroke drawn, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 21,
    "text": "ㄱ에 가획하여 ㅋ이 되며, 거센 공기의 뿜어냄이 시각적으로 더해집니다.",
    "text_en": "Adding a stroke to 'ㄱ' makes 'ㅋ', visually representing a stronger burst of air.",
    "motion": ":: [pulse] 'ㄱ' showing a sudden burst of air as the line for 'ㅋ' is added on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㅋ' with air particle bursts representing aspiration, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 22,
    "text": "ㄴ에 획을 더해 ㄷ이 되고, 다시 한 번 획을 추가해 ㅌ이 탄생합니다.",
    "text_en": "Adding a stroke to 'ㄴ' makes 'ㄷ', and adding another makes 'ㅌ'.",
    "motion": ":: [rotation] sequence: 'ㄴ ➡️ ㄷ ➡️ ㅌ' with yellow lines drawing the new strokes on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), sequential morphing of letters from 'ㄴ' to 'ㄷ' to 'ㅌ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 23,
    "text": "ㅁ에 획을 세워 ㅂ을 만들고, 위아래 획을 더 확장해 ㅍ을 완성합니다.",
    "text_en": "Extending strokes on 'ㅁ' creates 'ㅂ', and adding more horizontal strokes completes 'ㅍ'.",
    "motion": ":: [zoom_bounce] sequence: 'ㅁ ➡️ ㅂ ➡️ ㅍ' with clean outline transformation on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), sequential morphing of letters from 'ㅁ' to 'ㅂ' to 'ㅍ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 24,
    "text": "ㅅ에 획을 얹어 ㅈ을 만들고, 다시 획을 얹어 거센소리 ㅊ으로 나아갑니다.",
    "text_en": "Adding a top stroke to 'ㅅ' creates 'ㅈ', and another makes the aspirated 'ㅊ'.",
    "motion": ":: [pulse] sequence: 'ㅅ ➡️ ㅈ ➡️ ㅊ' with yellow strokes added at the top on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), sequential morphing of letters from 'ㅅ' to 'ㅈ' to 'ㅊ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 25,
    "text": "ㅇ에 획을 얹어 ㅎ을 만들어, 거센 숨소리가 목구멍을 통과함을 나타냅니다.",
    "text_en": "Adding strokes to 'ㅇ' forms 'ㅎ', representing strong breath passing through the throat.",
    "motion": ":: [pulse] sequence: 'ㅇ ➡️ ㆆ ➡️ ㅎ' with vertical strokes growing upwards on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters 'ㅇ' and 'ㅎ' with a small line above, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 26,
    "text": "글자를 나란히 두 개 겹쳐 쓰면, 더 단단하고 팽팽한 경음(쌍자음)이 됩니다.",
    "text_en": "Writing two identical letters side-by-side forms a tense, double consonant (Tense Sound).",
    "motion": ":: [zoom_bounce] 'ㄱ' duplication to form 'ㄲ' with a tightening circle around it on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㄲ' forming from two 'ㄱ's, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 27,
    "text": "ㄲ, ㄸ, ㅃ, ㅆ, ㅉ을 각각 쌍자음이라 부르며, 후두의 긴장을 표현하죠.",
    "text_en": "ㄲ, ㄸ, ㅃ, ㅆ, and ㅉ are called double consonants, expressing tension in the larynx.",
    "motion": ":: [pulse] all 5 tense consonants displayed in tight, bold black outlines on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a clean grid displaying ㄲ, ㄸ, ㅃ, ㅆ, ㅉ, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 28,
    "text": "설소리 ㄴ에 가획하지 않고, 혀를 굴려 흘려내는 특수 자음 ㄹ이 만들어집니다.",
    "text_en": "Instead of adding regular strokes, the flowing liquid 'ㄹ' is created by curling the tongue.",
    "motion": ":: [zoom_bounce] 'ㄴ' shifting dynamically into 'ㄹ', demonstrating lateral fluid motion on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㄹ' with wavy liquid flow arrows, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 29,
    "text": "이렇게 한글은 기본 5자에서 파생된 총 19개의 완벽한 자음 체계를 갖춥니다.",
    "text_en": "Thus, Hangul establishes a complete system of 19 consonants derived from the 5 base shapes.",
    "motion": ":: [rotation] grid of all 19 Korean consonants displayed neatly on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a neat grid of all 19 Korean consonants, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 4: Vowel Philosophy & Cheon-Ji-In (30 - 39)
scenes.append({
    "num": 30,
    "text": "모음은 자음과 완전히 다르게, 우주의 세 기본 요소인 천지인을 결합해 짭니다.",
    "text_en": "Vowels are structured differently, combining the three core cosmic elements: Sky, Earth, and Human.",
    "motion": ":: [zoom_bounce] a compass showing sky, ground, and human walking in the middle on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), three geometric symbols representing sky, land, and human, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 31,
    "text": "첫째는 둥근 하늘의 모양을 상형한 하늘 '아래아'의 둥근 점입니다.",
    "text_en": "First is the round dot representing the sky, called 'Araea' (•).",
    "motion": ":: [pulse] a large circular dot (•) glowing in the center of the frame on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a clean round circle dot in the center of the frame, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 32,
    "text": "둘째는 평평하게 펼쳐진 대지의 모양을 본뜬 땅 '으'의 가로선입니다.",
    "text_en": "Second is the horizontal line representing the flat earth, 'EU' (ㅡ).",
    "motion": ":: [pulse] a clean, infinite horizontal line (ㅡ) on a solid flat background (#F5F5F0), camera slowly panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a bold horizontal line stretch across the center, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 33,
    "text": "셋째는 하늘과 땅 사이에 서서 존재하는 사람 '이'의 세로선입니다.",
    "text_en": "Third is the vertical line representing a standing human, 'I' (ㅣ).",
    "motion": ":: [zoom_bounce] a clean, standing vertical line (ㅣ) on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a bold vertical line in the center of the frame, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 34,
    "text": "하늘과 사람, 그리고 땅이 한데 만나 섞이며 한글의 기본 모음이 태어납니다.",
    "text_en": "When Sky, Human, and Earth meet and combine, the basic vowels of Hangul are born.",
    "motion": ":: [pulse] dot, horizontal line, and vertical line sliding together on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), dot, vertical line, and horizontal line merging together, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 35,
    "text": "세로선 오른쪽에 하늘(•)이 뜨면 ㅏ, 왼쪽에 해가 지면 ㅓ가 됩니다.",
    "text_en": "If the sky (•) rises to the right of the human (ㅣ), it is 'A [a]'; to the left, it is 'EO [ʌ]'.",
    "motion": ":: [zoom_bounce] 'ㅣ' with dot moving right to make 'ㅏ', then left to make 'ㅓ' on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㅣ' with a dot jumping to its right to form 'ㅏ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 36,
    "text": "가로선 위로 하늘이 뜨면 ㅗ, 가로선 아래로 하늘이 숨으면 ㅜ가 됩니다.",
    "text_en": "If the sky rises above the earth (ㅡ), it is 'O [o]'; below the earth, it is 'U [u]'.",
    "motion": ":: [pulse] 'ㅡ' with dot moving top to make 'ㅗ', then bottom to make 'ㅜ' on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㅡ' with a dot jumping above to form 'ㅗ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 37,
    "text": "해의 기운이 위와 밖으로 뻗어나가는 ㅏ, ㅗ는 밝고 긍정적인 양의 모음입니다.",
    "text_en": "The vowels 'ㅏ' and 'ㅗ', stretching outward and upward, are bright 'Yang' vowels.",
    "motion": ":: [rotation] vowels ㅏ, ㅗ glowing in warm yellow, accompanied by a small sun icon on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters ㅏ and ㅗ next to a small line-art sun, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 38,
    "text": "해의 기운이 안과 아래로 깃드는 ㅓ, ㅜ는 어둡고 차분한 음의 모음입니다.",
    "text_en": "The vowels 'ㅓ' and 'ㅜ', drawing inward and downward, are deep, calm 'Yin' vowels.",
    "motion": ":: [zoom_bounce] vowels ㅓ, ㅜ in cool black, accompanied by a small cloud icon on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters ㅓ and ㅜ next to a small line-art cloud, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 39,
    "text": "하늘, 땅, 사람이 조화를 이루어 한글 모음의 기본 네 기둥을 완성합니다.",
    "text_en": "Sky, Earth, and Human harmonize to complete the four base pillars of Hangul vowels.",
    "motion": ":: [pulse] grid of ㅏ, ㅓ, ㅗ, ㅜ on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), grid containing letters ㅏ, ㅓ, ㅗ, ㅜ, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 5: Compound Vowels & The 21-Vowel Grid (40 - 49)
scenes.append({
    "num": 40,
    "text": "하늘의 기운(•)을 두 번씩 더 결합하면, y계열의 이중모음이 탄생합니다.",
    "text_en": "Adding the sky element twice creates y-glide diphthongs.",
    "motion": ":: [zoom_bounce] 'ㅏ' adding another short stroke to become 'ㅑ' dynamically on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㅏ' transforming into 'ㅑ' with a new horizontal stroke, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 41,
    "text": "해를 두 번 얹어 야, 여, 요, 유가 되어 소리가 한 층 다채로워집니다.",
    "text_en": "Adding it twice yields YA, YEO, YO, and YU, enriching the vowel spectrum.",
    "motion": ":: [pulse] letters ㅑ, ㅕ, ㅛ, ㅠ transitioning in sequence on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), clean grid displaying ㅑ, ㅕ, ㅛ, ㅠ, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 42,
    "text": "모음 ㅣ와 다른 모음들이 한데 결합하여 새로운 합성 모음을 만듭니다.",
    "text_en": "The vertical vowel 'I' merges with other vowels to create compound vowels.",
    "motion": ":: [pulse] 'ㅏ' and 'ㅣ' sliding together to merge into 'ㅐ' on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter 'ㅏ' and 'ㅣ' merging into 'ㅐ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 43,
    "text": "ㅏ와 ㅣ가 만나 ㅐ가 되고, ㅓ와 ㅣ가 만나 ㅔ가 되어 발음이 고정됩니다.",
    "text_en": "ㅏ and ㅣ form 'AE', while ㅓ and ㅣ form 'E'.",
    "motion": ":: [zoom_bounce] 'ㅐ' and 'ㅔ' displayed side-by-side on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters ㅐ and ㅔ shown together, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 44,
    "text": "이중모음 ㅑ와 ㅣ가 만나 얘, ㅕ와 ㅣ가 만나 예가 되는 정교한 합성.",
    "text_en": "The diphthongs YA and YEO combine with 'I' to form 'YAE' and 'YE'.",
    "motion": ":: [pulse] '얘' and '예' sliding into place on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters 얘 and 예 appearing side-by-side, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 45,
    "text": "가로 모음 ㅗ, ㅜ와 세로 모음들이 만나 입술을 둥글려 소리 내는 복합 모음.",
    "text_en": "Horizontal vowels (ㅗ, ㅜ) combine with vertical ones to make rounded diphthongs.",
    "motion": ":: [zoom_bounce] 'ㅗ' and 'ㅏ' merging into 'ㅘ' with a circular motion arrow on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters 'ㅗ' and 'ㅏ' joining to form 'ㅘ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 46,
    "text": "오와 아가 만나 와가 되고, 우와 어가 만나 워가 되어 이중 조음이 흐릅니다.",
    "text_en": "O and A make 'WA'; U and EO make 'WO', flowing into double articulation.",
    "motion": ":: [pulse] 'ㅘ' and 'ㅝ' transitioning on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters ㅘ and ㅝ side-by-side, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 47,
    "text": "외와 위, 그리고 왜와 웨까지 입술을 모으며 혀를 움직이는 모음들.",
    "text_en": "OE, WI, and even WAE and WE require rounding the lips and shifting the tongue.",
    "motion": ":: [rotation] letters ㅚ, ㅟ, ㅙ, ㅞ displayed on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), grid containing ㅚ, ㅟ, ㅙ, ㅞ, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 48,
    "text": "가장 복잡해 보이는 ㅡ와 ㅣ의 결합, 의는 한 획으로 이어지는 조화입니다.",
    "text_en": "The seemingly complex combination of ㅡ and ㅣ, 'UI', is a harmonious single flow.",
    "motion": ":: [zoom_bounce] 'ㅡ' and 'ㅣ' sliding close to form 'ㅢ' on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters 'ㅡ' and 'ㅣ' merging into 'ㅢ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 49,
    "text": "이렇게 기본 3자에서 출발한 한글은 총 21개의 풍부한 모음 체계를 자랑합니다.",
    "text_en": "Starting from just 3 base shapes, Hangul boasts a rich system of 21 vowels.",
    "motion": ":: [pulse] grid of all 21 Korean vowels on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a clean grid showing all 21 Korean vowels, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 6: Articulatory Differences & Consonant Mastery (50 - 59)
scenes.append({
    "num": 50,
    "text": "평음, 격음, 경음의 미세한 공기 압력과 성대 긴장의 차이를 배워봅시다.",
    "text_en": "Let's learn the subtle differences in air pressure and vocal cord tension among plain, aspirated, and tense sounds.",
    "motion": ":: [zoom_bounce] mouth illustration with a pressure dial showing low, medium, and high levels on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), simple throat and mouth diagram with a dial showing three levels, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 51,
    "text": "ㄱ은 숨을 아주 부드럽고 가볍게 내보내며 내는 가장 편안한 소리입니다.",
    "text_en": "'G' is a relaxed plain sound, releasing air very softly and lightly.",
    "motion": ":: [pulse] air particles flowing slowly out of the mouth in a flat line on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), mouth profile with a gentle, slow wave of air particles coming out, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 52,
    "text": "ㅋ은 가슴 깊은 곳에서 공기를 강하게 뿜어내며 뱉는 거센 소리입니다.",
    "text_en": "'K' is an aspirated sound, forcefully expelling air from deep within.",
    "motion": ":: [zoom_bounce] a large puff of air particles shooting out of the mouth on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), mouth profile with a powerful, fast burst of air particles shooting out, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 53,
    "text": "ㄲ은 공기를 내보내지 않고, 성대를 꽉 조였다가 터뜨리는 단단한 소리입니다.",
    "text_en": "'KK' is a tense sound, compressing the vocal cords with almost no escaping air.",
    "motion": ":: [pulse] tight constriction in the throat, no air particles escaping the mouth on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), throat diagram showing constriction and a blocked air passage, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 54,
    "text": "평음 ㄱ과 격음 ㅋ의 차이는 손바닥을 입에 대고 바람을 느껴보면 쉽습니다.",
    "text_en": "You can feel the difference between plain 'G' and aspirated 'K' by putting your hand in front of your mouth.",
    "motion": ":: [zoom_bounce] a hand in front of the mouth feeling the breeze of ㅋ on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a simple line-art hand placed in front of an open mouth, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 55,
    "text": "평음 ㄱ과 경음 ㄲ은 영어의 key와 sky의 k소리 차이와 같습니다.",
    "text_en": "The contrast between plain 'G' and tense 'KK' is like the 'K' in 'key' versus 'sky'.",
    "motion": ":: [pulse] English text 'Key' vs. 'sKy', highlighting the 'K' in sky in yellow on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), text showing 'key' and 'sky' with the 'k' in 'sky' highlighted in bright yellow, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 56,
    "text": "입 앞에 얇은 종이를 두고 ㅋ을 할 때만 종이가 강하게 흔들려야 합니다.",
    "text_en": "Hold a thin sheet of paper; it should bend back dramatically only when you pronounce 'K'.",
    "motion": ":: [shake] a sheet of paper bending back dramatically for ㅋ on a solid flat background (#F5F5F0), camera slowly shaking",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), profile of mouth blowing air at a sheet of paper that is bending back, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 57,
    "text": "경음 ㄲ을 낼 때는 첫 모음의 톤을 높은 음으로 강하게 질러 발음하세요.",
    "text_en": "When making the tense 'KK', pitch the following vowel higher and sharper.",
    "motion": ":: [pulse] musical notes rising suddenly, arrows pointing to high register on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), musical notes on a rising scale, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 58,
    "text": "경음과 격음은 소리를 낼 때 확실하게 맺고 끊는 staccato 느낌을 살립니다.",
    "text_en": "Tense and aspirated sounds should feel crisp, with a distinct staccato separation.",
    "motion": ":: [zoom_bounce] a wave waveform showing high sharp peaks, followed by sharp silences on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a clean audio waveform with high sharp peaks, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 59,
    "text": "ㄱ/ㅋ/ㄲ, ㄷ/ㅌ/ㄸ, ㅂ/ㅍ/ㅃ의 3단계 소리 차이를 완전히 머리로 정돈합니다.",
    "text_en": "Solidify the 3-step difference of G/K/KK, D/T/TT, and B/P/PP in your mind.",
    "motion": ":: [pulse] minimalist table of the stop consonant triplets on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a clean grid table listing the three consonant groups, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 7: Vowel Pronunciation Mastery (60 - 69)
scenes.append({
    "num": 60,
    "text": "외국인이 가장 어려워하는 대표적인 모음들의 정밀 조음 메커니즘.",
    "text_en": "Here is the precise articulation mechanism for the vowels that foreigners find hardest.",
    "motion": ":: [zoom_bounce] silhouette showing tongue height inside the mouth on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), sagittal oral cavity diagram showing tongue height, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 61,
    "text": "으를 발음할 때는 입술을 양옆으로 길게 찢어 미소를 지으며 발음해야 합니다.",
    "text_en": "To pronounce 'EU [ɯ]', stretch your lips wide to the sides as if smiling.",
    "motion": ":: [pulse] mouth stretched wide in a smile, with left/right tension arrows in yellow on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a wide smiling mouth with horizontal arrows pulling outward, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 62,
    "text": "입술을 둥글게 오므리지 않고 납작하게 둔 채, 혀 뒷부분만 올려주세요.",
    "text_en": "Keep the lips flat and unrounded, raising only the back of your tongue.",
    "motion": ":: [pulse] tongue raised in the back, lips flat (Unrounded close back vowel) on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), oral cavity profile showing the back of the tongue raised close to the palate, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 63,
    "text": "어를 발음할 때는 턱을 아래로 크게 벌리고, 입술은 둥글리지 않고 편안히 둡니다.",
    "text_en": "To pronounce 'EO [ʌ]', drop your jaw low while keeping your lips relaxed and flat.",
    "motion": ":: [zoom_bounce] vertical jaw open arrow, relaxed flat lips (Open-mid back vowel) on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), mouth profile with a vertical arrow pulling the jaw down, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 64,
    "text": "오를 발음할 때는 빨대를 문 것처럼 입술을 아주 작고 둥글게 모아야 합니다.",
    "text_en": "To pronounce 'O [o]', round your lips into a small, tight circle as if holding a straw.",
    "motion": ":: [pulse] mouth rounded into a small, tight circle with circle guide on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), front view of lips puckered into a tight circle, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 65,
    "text": "턱을 벌려 넓게 내는 어, 입술을 오므려 좁게 내는 오의 확연한 구강 차이.",
    "text_en": "Compare the wide jaw of 'EO' versus the tight circular lips of 'O'.",
    "motion": ":: [zoom_bounce] side-by-side comparison: vertical wide open vs. tight circular lips on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), side-by-side mouth shapes: one wide open vertically, one rounded tightly, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 66,
    "text": "우는 입술을 오보다 더 둥글고 팽팽하게 모아서 앞으로 쭉 내밀어 줍니다.",
    "text_en": "For 'U [u]', purse your lips even tighter than 'O' and project them forward.",
    "motion": ":: [pulse] lips puckered and projecting forward (Rounded close back vowel) on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), side profile of lips pushed forward, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 67,
    "text": "입을 아주 작고 강하게 오므리는 우, 그리고 중간 크기 모음 오의 차이.",
    "text_en": "Spot the difference: the tiny, tense circle of 'U' versus the medium circle of 'O'.",
    "motion": ":: [pulse] overlay comparison: small circle (우) inside a medium circle (오) on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), two concentric circles representing lip size differences, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 68,
    "text": "거울을 보고 ㅓ와 으를 발음할 때 입술이 동그랗게 변하지 않는지 꼭 체크하세요.",
    "text_en": "Check in a mirror to make sure your lips do not round when saying 'EO' and 'EU'.",
    "motion": ":: [zoom_bounce] hand holding a mirror reflecting flat, unrounded lips on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a hand holding a small hand mirror showing a flat smile, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 69,
    "text": "으, 어, 오, 우의 혀의 높이와 입술 모양의 조화를 완벽하게 내 것으로 만듭니다.",
    "text_en": "Fully master the combination of tongue height and lip rounding for EU, EO, O, and U.",
    "motion": ":: [pulse] a clean graph showing Vowel Height vs. Lip Rounding on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a simple two-axis graph mapping vowel coordinates, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 8: Syllable Assembly & Block Structure (70 - 79)
scenes.append({
    "num": 70,
    "text": "한글은 자모를 옆으로 늘어놓지 않고 하나의 음절 블록 안에 모아씁니다.",
    "text_en": "Instead of aligning letters side-by-side, Hangul groups them into syllable blocks.",
    "motion": ":: [zoom_bounce] left-to-right letters sliding to stack inside a square block on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letters 'ㄱ' 'ㅏ' 'ㅇ' assembling into a square box, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 71,
    "text": "모음의 획이 수직(ㅣ)으로 서 있으면, 자음의 오른쪽에 나란히 붙입니다.",
    "text_en": "If the vowel has a vertical stroke (ㅣ), it sits to the right of the consonant.",
    "motion": ":: [pulse] template grid showing Initial Consonant (left) + Vowel (right) on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a block divided into a left half and a right half, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 72,
    "text": "모음의 획이 수평(ㅡ)으로 누워 있으면, 자음의 아래쪽에 얹어 씁니다.",
    "text_en": "If the vowel has a horizontal stroke (ㅡ), it sits directly under the consonant.",
    "motion": ":: [pulse] template grid showing Initial Consonant (top) + Vowel (bottom) on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a block divided into a top half and a bottom half, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 73,
    "text": "가로와 세로 획이 모두 있는 모음은 자음의 오른쪽과 아래쪽을 모두 감쌉니다.",
    "text_en": "Vowels with both horizontal and vertical strokes wrap around the right and bottom of the consonant.",
    "motion": ":: [zoom_bounce] template showing consonant tucked inside the corner of a L-shaped vowel on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), block diagram showing a corner layout shape, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 74,
    "text": "음절의 맨 밑바닥에 마지막으로 붙여 쓰는 자음을 '받침(종성)'이라 합니다.",
    "text_en": "The final consonant placed at the very bottom of a syllable is called 'Batchim'.",
    "motion": ":: [pulse] syllable block where the bottom section is highlighted in yellow on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a three-part syllable block with the bottom chamber highlighted, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 75,
    "text": "자음과 모음 결합 아래에 받침 자음이 조립되어 삼층 구조의 강을 완성하죠.",
    "text_en": "A final consonant joins below, completing a 3-layered syllable like 'GANG'.",
    "motion": ":: [zoom_bounce] 'ㄱ ➡️ 가 ➡️ 강' step-by-step block assembly animation on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), syllables growing from 'ㄱ' to '가' to '강' in steps, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 76,
    "text": "받침으로 쓰이는 자음은 많지만, 실제 발음은 오직 7개의 소리로 제한됩니다.",
    "text_en": "Though many consonants can be written as Batchim, they are pronounced as only 7 sounds.",
    "motion": ":: [pulse] 7 letters (ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ) popping up on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), seven distinct Korean letters appearing in a row, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 77,
    "text": "ㅅ, ㅆ, ㅈ, ㅊ, ㄷ, ㅌ, ㅎ 받침은 모두 바닥에서 대표음 ㄷ[t]로 발음됩니다.",
    "text_en": "The final consonants ㅅ, ㅆ, ㅈ, ㅊ, ㄷ, ㅌ, and ㅎ all collapse into the representative 'D [t]' sound.",
    "motion": ":: [pulse] cluster of consonants falling and merging into a single 'ㄷ' block on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), multiple letters falling and merging into a single 'ㄷ', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 78,
    "text": "받침소리는 공기를 밖으로 터뜨리지 않고 입안에서 딱 멈추는 불파음입니다.",
    "text_en": "Batchim sounds are unreleased, stopping air flow abruptly inside the mouth.",
    "motion": ":: [zoom_bounce] an arrow stopping abruptly at the barrier of closed lips/teeth on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a motion arrow hitting a flat barrier and stopping, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 79,
    "text": "때로는 두 자음이 겹쳐 쓰이는 겹받침이 오며, 원칙에 따라 하나만 소리 납니다.",
    "text_en": "Sometimes double/complex Batchims appear, where only one consonant is voiced.",
    "motion": ":: [pulse] block '닭' showing the 'ㄱ' sound highlighted while 'ㄹ' fades away on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), letter '닭' where 'ㄹ' fades out and 'ㄱ' turns bright yellow, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 9: Sound Change Rules & Phonology (80 - 88)
scenes.append({
    "num": 80,
    "text": "받침 뒤에 빈자리인 ㅇ이 오면, 받침소리가 뒷자리로 넘어가 연음됩니다.",
    "text_en": "When a Batchim is followed by an empty 'ㅇ', the sound links over to the next syllable.",
    "motion": ":: [pulse] '한국어' transforming into [한구거] with a sliding yellow arrow on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), text showing '한국어' shifting to '한구거' with a curved arrow, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 81,
    "text": "밥을은 [바블]로, 꽃이는 [꼬치]로 소리가 흐르듯 자연스럽게 이어지죠.",
    "text_en": "'Babeul' is read as [ba-beul], and 'kkochi' as [kko-chi], flowing naturally.",
    "motion": ":: [zoom_bounce] text: '밥을 ➡️ [바블]', '꽃이 ➡️ [꼬치]' on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), text '밥을' morphing to '[바블]', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 82,
    "text": "ㄱ, ㄷ, ㅂ 뒤에 ㄴ, ㅁ이 오면, 소리가 부드러운 비음 ㅇ, ㄴ, ㅁ으로 변합니다.",
    "text_en": "When G, D, B meet N or M, they shift to soft nasal sounds: NG, N, M.",
    "motion": ":: [pulse] '국물' turning into [궁물] with a yellow nose icon glowing on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), outline of a nose glowing to show nasal airflow, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 83,
    "text": "감사합니다의 합니는 함니로 발음되어 훨씬 발음하기 부드러워집니다.",
    "text_en": "In 'Gamsahamnida', 'hap-ni' is pronounced as [ham-ni], making it smoother to say.",
    "motion": ":: [zoom_bounce] text: '합니다 ➡️ [함니다]' with a smooth curve underneath on a solid flat background (#F5F5F0), camera zooming out",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), text showing '합니다' turning into '[함니다]', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 84,
    "text": "ㄷ, ㅌ 받침 뒤에 모음 ㅣ가 오면 ㅈ, ㅊ으로 입을 가볍게 치켜 올립니다.",
    "text_en": "When a final D or T meets the vowel 'I', it palatalizes into J or CH.",
    "motion": ":: [pulse] '같이' transforming into [가치] with tooth/tongue movement line on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), text '같이' morphing to '[가치]' with a small curved arrow, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 85,
    "text": "굳이는 [구지]로, 같이는 [가치]로 발음되는 현상은 영어의 would you와 유사하죠.",
    "text_en": "Reading 'gudi' as [guji] and 'gati' as [gachi] is similar to 'would you' in English.",
    "motion": ":: [pulse] text: '굳이 ➡️ [구지]', 'Would you ➡️ Would-chu' on a solid flat background (#F5F5F0), camera panning right",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), text 'would you' next to '굳이' with phonetic changes, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 86,
    "text": "ㄴ과 ㄹ이 서로 이웃해 만나면, 두 소리 모두 매끄러운 ㄹㄹ소리로 바뀝니다.",
    "text_en": "When N and L meet, both assimilate into a smooth, liquid double 'L' sound.",
    "motion": ":: [zoom_bounce] '신라' morphing into [실라], '설날' into [설랄] on a solid flat background (#F5F5F0), camera zooming in",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), text '신라' turning to '[실라]', single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 87,
    "text": "영어가 강세에 따라 움직인다면, 한국어는 음절박자로 평평하게 흐릅니다.",
    "text_en": "While English moves to stress-based rhythm, Korean flows flatly based on syllable blocks.",
    "motion": ":: [pulse] English stress waves (peaks/valleys) vs. Korean blocks (even, flat line) on a solid flat background (#F5F5F0), camera panning slowly",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), comparison of a bumpy wave line and a flat straight line with small boxes, single accent color (#FFD700) for highlights. Clean flat design."
})
scenes.append({
    "num": 88,
    "text": "단어들을 뚝뚝 끊어 읽지 말고, 연음과 발음 변화를 타며 흘리듯 읽으세요.",
    "text_en": "Rather than chopping words apart, let them glide, riding the natural sound changes.",
    "motion": ":: [pulse] a paper boat sailing smoothly over a wavy line representing fluent speech on a solid flat background (#F5F5F0), camera slowly tilting",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a simple paper boat outline floating smoothly on a single line wave, single accent color (#FFD700) for highlights. Clean flat design."
})

# Part 10: Epilogue & Graduation (89)
scenes.append({
    "num": 89,
    "text": "한글을 마스터한 여러분을 축하합니다! 새로운 한글의 여정을 구독과 좋아요로!",
    "text_en": "Congratulations on mastering Hangul! Join our new learning journey with a subscribe and like!",
    "motion": ":: [rotation] graduation cap in minimalist line art, subscribe/bell button popping on a solid flat background (#F5F5F0), camera slowly rotating",
    "prompt": "Ultra-minimalist 2D vector line art illustration, clean black outlines on a solid flat background (#F5F5F0), a simple graduation cap outline and a bell icon popping up, single accent color (#FFD700) for highlights. Clean flat design."
})

# Write to scenario.txt
scenario_path = os.path.join(target_dir, "scenario.txt")
with open(scenario_path, "w", encoding="utf-8") as f:
    for s in scenes:
        f.write(f"[Scene {s['num']}]\n")
        f.write(f"text: {s['text']}\n")
        f.write(f"text_en: {s['text_en']}\n")
        f.write(f"motion: {s['motion']}\n\n")

# Write to prompts_for_veo.txt
prompts_path = os.path.join(target_dir, "prompts_for_veo.txt")
with open(prompts_path, "w", encoding="utf-8") as f:
    for s in scenes:
        f.write(f"[Scene {s['num']}] {s['prompt']}\n")

print("Generated 90-scene scenario.txt and prompts_for_veo.txt successfully!")
