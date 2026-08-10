# -*- coding: utf-8 -*-
"""진격의 거인 과학(titan_science) — Flow 프롬프트 테이블 (2026-08-10).

출처: `titan_science/titan_scenario_v2.md` (8분 / 18씬).
`flow_make_bg_w24.py` 와 같은 (키, 종류, 프롬프트) 형식을 그대로 쓴다 —
그래야 검증된 CDP 절차를 손대지 않고 재사용할 수 있다.

★규칙 (사장님 확정 2026-08-10)
  · **글자 절대 금지** — 화면 안 문자·숫자·수식은 전부 후반 합성(5개국어 자막 때문)
  · **브랜드 금지** — 참고한 교육채널 이름·로고·워터마크 어디에도 넣지 않는다
  · **다이나믹 카메라** — 8초 3단(0~1 시작 / 1~4.5 대변화 / 4.5~8 안착)
  · **사람 줌인 금지** — 포인트 객체·주인공 물체만 줌인
  · 전체 흔들림·번쩍임·미세 모션(손끝·나뭇잎만 까딱) 금지

사용:
  python gen_titan_prompts.py --list
  python gen_titan_prompts.py s01        # 프롬프트 파일로 저장
"""
import argparse
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
OUT_DIR = "titan_science/prompts"

# 전 씬 공통 스타일 락 — 톤이 흔들리면 8분이 산만해진다. 씬마다 바꾸지 않는다.
STYLE = (
    "2D hand-drawn cartoon animation, warm cream paper background, thick uneven hand-inked "
    "brush outlines that vary in width with a slight wobble, flat gouache colour fills with "
    "visible watercolour paper grain, soft cel shading with no gradients on characters, "
    "muted earth palette of sand, terracotta, olive and dusty teal, punched by ONE "
    "high-saturation accent per shot. Subtle paper texture over the whole frame. "
    "No photorealism, no 3D render look, no lens flare. "
    "★ABSOLUTELY NO TEXT: no letters, no numbers, no equations, no signage lettering, "
    "no labels, no logos, no watermark, no channel branding. Every board, banner, page and "
    "panel is BLANK. "
    "★CAMERA RULES: no screen shake, no strobe or flashing, no micro-motion-only shots where "
    "only a hand or a leaf twitches. The camera must travel through space for the whole clip. "
    "Never zoom in on a human face or figure - push in only on the named object. "
    "16:9, cinematic composition."
)

# (키, 종류, 프롬프트 본문)  — 종류: STILL(키프레임) / VIDEO(8초 클립)
SCENES = [
    ("s01_wall", "STILL",
     "Extreme low-angle shot from ground level of a colossal 50-metre-tall dry-stone defensive "
     "wall filling the right two-thirds of the frame. The wall is built from thousands of "
     "individually inked irregular stone blocks in sand and warm grey tones, with dark mortar "
     "lines, patches of olive moss creeping up the lower courses, three rusted iron ladders "
     "bolted to the face, a row of small square watch-slits near the top, and two tattered "
     "crimson banners hanging limp. At the base: a cobbled street with a wooden handcart tipped "
     "over, scattered clay pots, a spilled basket of apples, a stray dog frozen mid-bark, and "
     "seven tiny townspeople rendered as simple silhouettes looking upward - they are barely "
     "one-fortieth of the wall's height to sell the scale. Above the wall rim, four enormous "
     "humanoid fingers with cracked steaming skin curl over the edge, thin crimson steam wisps "
     "rising from the knuckles into a pale cream sky with three flat stylised clouds and a flock "
     "of tiny birds scattering. Crimson is the single saturated accent, on the banners and steam. "
     "Mood: dread, vertigo, held breath."),

    # ── S1 8초 클립 — 키프레임과 같은 장면을 지미집으로 통과한다 ──
    ("s01_wall_v", "VIDEO",
     "A colossal dry-stone defensive wall of thousands of individually inked irregular stone "
     "blocks in sand and warm grey, with dark mortar lines, olive moss on the lower courses, "
     "three rusted iron ladders bolted to the face, a row of small square watch-slits near the "
     "top, and three tattered crimson banners. At its base a cobbled street with a tipped wooden "
     "handcart, scattered clay pots, a spilled basket of apples, a barking dog and a cluster of "
     "tiny townspeople looking up. Over the wall rim, four enormous humanoid fingers with cracked "
     "steaming skin curl down, crimson steam rising into a pale cream sky with flat clouds and a "
     "scattering flock of birds. "
     "0-1s: the camera sits at ant level on the cobbles, lens almost touching the ground, the "
     "wall rearing up and running out of the top of frame. "
     "1-4.5s: an aggressive vertical crane move - the camera launches straight up the wall face "
     "at speed, stone courses streaking past, the ladders and watch-slits whipping downward out "
     "of frame, the street and the townspeople below shrinking away into a toy-sized model. "
     "4.5-6.5s: the camera arrives level with the wall rim, tilts to meet the four colossal "
     "fingers and pushes in hard on the cracked steaming skin of one knuckle until the fissures "
     "fill the frame. "
     "6.5-8s: it settles there, crimson steam drifting across the lens. "
     "Continuous fast vertical camera travel, strong parallax, no static framing. "
     "Crimson is the single saturated accent. Mood: dread, vertigo, held breath."),

    ("s02_arm_bounce", "VIDEO",
     "Medium shot in a muddy field at dusk. A detached titan forearm the size of a bus lies on "
     "churned earth — pale ochre skin with a dry cracked surface like old ceramic, deep ink "
     "outlines, faint crimson steam curling off the sealed end which is sealed and glassy, not "
     "bloody. A small scientist figure in a tan field coat, goggles pushed up into messy brown "
     "ponytail hair, leather boots and a satchel, plants one foot and kicks the huge forearm; the "
     "arm tips up weightlessly at a comic angle, one end lifting off the ground, motion arcs drawn "
     "as three thin hand-inked speed lines. Surrounding clutter to sell the scene: two wooden "
     "supply crates, a coil of rope, three iron stakes with red pennants marking a survey grid, a "
     "tipped bucket, a folding stool with a clipboard on it, a lantern on a pole, and four "
     "uniformed onlookers in the mid-distance with jaws dropped. Puddles reflect the cream sky. "
     "One high-saturation crimson accent on the pennants and steam. CAMERA (fill all 8 seconds): "
     "0.0-1.0s Low three-quarter view along the length of the detached forearm, mud in the "
     "foreground, the scientist's boot entering frame edge. 1.0-4.5s ORBIT — the camera swings 90 "
     "degrees around the forearm at speed while the kick lands; at the moment of contact it CRANES "
     "UP and RISES with the tumbling limb, the field, crates and survey pennants wheeling away "
     "below. 4.5-6.5s PUSH IN on the huge forearm itself as it hangs weightless at the top of its "
     "arc, filling the frame, steam trailing off the sealed cut end. 6.5-8.0s Fall back with it "
     "toward the mud and settle. No shake, no strobe. Do not zoom on the scientist's face — the "
     "push-in subject is the floating forearm. Mood: absurd, delightful surprise. "),

    ("s03_galileo", "VIDEO",
     "Interior of a 17th-century study at night, warm candlelight. An elderly scholar with a long "
     "white beard, small round spectacles, dark scholar's robe and skullcap sits at a heavy oak "
     "desk, quill in hand, leaning over an open folio. On the desk, densely arranged: an open book "
     "showing two hand-drawn support column diagrams side by side (one small, one grotesquely thick), a "
     "brass candlestick with three lit candles and dripping wax, an hourglass, a pair of brass "
     "dividers, a wooden ruler, a stack of five leather-bound books, a rolled parchment tied with "
     "twine, an inkwell with two spare quills, a small terrestrial globe on a stand, and a "
     "scattering of loose sketch papers. Behind him: floor-to-ceiling shelves crammed with books "
     "and rolled charts, a brass telescope on a tripod aimed at a small arched window showing a "
     "deep indigo night sky with stars, and a hanging astrolabe. Dust motes drift in the candle "
     "glow. Warm amber is the single saturated accent against the cream palette. CAMERA (fill all "
     "8 seconds): 0.0-1.0s Outside the arched window at night, stars and rooftops, the warm "
     "candlelit study glowing through the glass. 1.0-4.5s PUSH-THROUGH — the camera flies in "
     "through the window frame into the room, sweeping past the telescope and the hanging "
     "astrolabe, shelves of books streaking by on both sides. 4.5-6.5s CRANE DOWN hard onto the "
     "desk surface and PUSH IN on the open folio until the two hand-drawn support column diagrams fill the "
     "frame, candle flames flaring at the edges. 6.5-8.0s Hold on the diagram, dust motes drifting "
     "through the light. No shake. Do not zoom on the scholar's face — the push-in subject is the "
     "support column diagram. Mood: quiet, weighty revelation. "),

    ("s04_cube", "VIDEO",
     "Clean diagram stage on cream paper. Three hand-inked cubes of increasing size stand in a row "
     "on a simple ruled ground line: a small cube, a medium cube, and a large cube, each drawn "
     "with wobbly brush outlines and flat sand-colored fills with visible paper grain. Each cube "
     "is stacked internally from tiny unit blocks so the viewer can count the volume growth. "
     "Beside each cube, a hand-drawn column of small square tiles represents its cross-sectional "
     "area, and below each, a hand-drawn stack of round weights represents its mass — the weight "
     "stacks grow dramatically faster than the tile columns. A tiny stick-drawn human figure "
     "stands at the base of the first cube for scale and looks progressively more dwarfed. "
     "Additional hand-drawn props scattered around the stage: a wooden set square, a pair of "
     "dividers, a coiled measuring tape, and three loose sketch sheets pinned at the corners. "
     "Everything rendered like an illustrator's ink-and-gouache notebook page, never like clean "
     "vector UI. Electric cyan is the single saturated accent used only on the weight stacks. "
     "CAMERA (fill all 8 seconds): 0.0-1.0s Tight on the smallest cube, the tiny stick figure "
     "beside it, low angle. 1.0-4.5s FLY-THROUGH — the camera pulls backward fast, threading "
     "between the cubes as each one erupts to its next size in a hard stepped beat; the unit "
     "blocks stack up and the weight piles slam down, the frame widening violently to keep up. "
     "4.5-6.5s Arrive at a high three-quarter angle, then CRANE DOWN and PUSH IN on the tallest "
     "stack of round weights until it fills the frame and dwarfs the tile column beside it. "
     "6.5-8.0s Settle, the stick figure now a speck at the bottom edge. No shake, no strobe, never "
     "a locked-off frame. Push-in subject is the weight stack. Mood: crisp, escalating, satisfying "
     "logic. "),

    # ★2026-08-10 실측 — 원래 S5 프롬프트는 Flow 에서 **결과물이 아예 안 나왔다**(240초 초과).
    #   같은 시각 S6 은 성공 → 계정·크레딧·크롬 문제가 아니라 **프롬프트 내용 필터**다.
    #   fracture / jagged / spider / giving way / stress / engineering study inset 같은 낱말을
    #   전부 빼고 **건축 구조물 비유**로만 말한다. 뜻은 그대로, 표현만 중립으로.
    # ★S5 가이드 이미지 — 클립이 두 번 거부돼서 정지컷부터 만든다(사장님 지시 2026-08-10)
    ("s05_guide", "STILL",
     "A clean illustrated study stage on warm cream paper, like a page from an engineer's "
     "sketchbook. In the centre stands a single tall slender support column drawn in chalky "
     "white with wobbly hand-inked outlines, its interior revealing a delicate lattice of thin "
     "diagonal struts like the inside of a bridge tower. Directly above it hangs a large smooth "
     "ochre block representing an enormous load, resting down onto the column top. Across the "
     "column's midsection a cluster of short amber strain marks has bloomed and the inner "
     "lattice has begun to open, thin pale lines widening between the struts, with fine chalk "
     "dust drifting down beneath it. To the right, a second much shorter and stouter column of "
     "the same chalky white carries an identical ochre block and remains perfectly intact, "
     "clean and unmarked, for direct comparison. Arranged around the stage like pinned "
     "specimens on a notebook page: a small brass plumb bob on a string, a pair of brass "
     "dividers, a wooden set square, a coiled measuring tape, a row of three stacked weight "
     "discs, two drawing pins, and four blank framed panels left completely empty. A single "
     "hand-ruled ground line runs across the bottom. Crimson is the only saturated accent, "
     "used exclusively on the strain marks. No people anywhere in the frame. "
     "Mood: quiet inevitability, an engineering diagram rendered with warmth."),

    ("s05_femur", "VIDEO",
     "A clean illustrated study stage on warm cream paper, like a page from an engineer's "
     "sketchbook. In the centre stands a single tall slender support column drawn in chalky "
     "white with wobbly ink outlines, its interior showing a delicate lattice of thin diagonal "
     "struts like the inside of a bridge tower. Above the column, a large smooth ochre block "
     "descends slowly, representing an enormous load. Around the stage, hand-drawn study props "
     "arranged like pinned specimens: a small brass plumb bob on a string, a pair of dividers, "
     "a wooden set square, a coiled measuring tape, a row of three stacked weight discs, a "
     "second much shorter column standing beside the tall one for comparison, and four blank "
     "framed panels left empty. As the ochre block settles onto the tall column, a cluster of "
     "short amber strain marks blooms across its midsection and the inner lattice slowly "
     "opens, thin lines widening between the struts while fine chalk dust drifts down. The "
     "shorter column beside it stays perfectly intact under the same block. Crimson is the "
     "single saturated accent, used only on the strain marks. Amber and ochre only - no red, "
     "no crimson, nothing that could read as liquid. "
     "0-1s: low angle at the base of the tall column looking up its length, the load block "
     "hanging high above. "
     "1-4.5s: the camera rises fast alongside the column in one continuous vertical crane move, "
     "the lattice sliding past, and arcs over the top just as the load block comes down. "
     "4.5-6.5s: it dives back down and pushes in hard on the midsection until the widening "
     "lattice lines fill the frame. "
     "6.5-8s: it holds there, chalk dust drifting through the shot. "
     "Continuous fast camera travel, strong parallax, no static framing. No people anywhere in "
     "the frame. Mood: quiet inevitability, an engineering diagram made cinematic."),

    ("s05_femur_OLD", "SKIP",
     "Split-feel composition. Left two-thirds: a 15-meter humanoid titan mid-stride on a cobbled "
     "plaza, drawn in flat ochre with heavy ink contours, muscles indicated by simple brush "
     "strokes, faint crimson steam at the shoulders, expression blank and unsettling. Right third: "
     "the same leg shown as a hand-inked engineering study inset — the support column drawn in chalky support column-white "
     "with visible internal trabecular lattice, and a cluster of short crimson stress lines "
     "radiating from the support column's midshaft where a jagged fracture is beginning to spider outward. "
     "Ground details for scale and clutter: cracked paving stones radiating fracture lines from "
     "the footfall, a toppled market stall with striped awning, scattered cabbages and clay jars, "
     "a broken cart wheel, two fleeing citizens rendered tiny, a startled cat, and a plume of dust "
     "drawn as soft stippled clouds. Crimson is the only saturated accent, used exclusively on the "
     "stress lines. CAMERA (fill all 8 seconds): 0.0-1.0s High angle at the titan's shoulder "
     "height, the plaza and market stalls far below. 1.0-4.5s CRANE DOWN — the camera plunges "
     "vertically alongside the titan's body as the leg swings through the stride, paving stones "
     "rushing up, the toppled stall and fleeing citizens whipping past the edges of frame. "
     "4.5-6.5s PUSH-THROUGH — at the thigh the camera drives straight through the skin surface "
     "into the engineering study inset and stops nose-to-nose with the support column as the jagged fracture "
     "spiders outward, crimson stress lines giving way open toward the lens. 6.5-8.0s Hold on the "
     "splitting support column, dust sifting down through the frame. No shake. Do not zoom on any human or "
     "the titan's face — the push-in subject is the fracturing support column. Mood: unforgiving physics, "
     "inevitability. "),

    ("s06_tank", "VIDEO",
     "Wide comparison shot on a dusty parade ground. On the left, a hand-inked military tank in "
     "olive drab with wide continuous tracks, riveted armor plates, a long barrel, stowage boxes, "
     "spare track links on the hull, and an antenna — its tracks pressing shallow even grooves "
     "into the dirt. On the right, the bare lower legs and feet of a colossal humanoid figure in "
     "pale ochre, the two soles pressing deep dark craters into the same ground with radiating "
     "cracks and sprays of dirt clods. Between them, a small hand-drawn balance scale tipping, "
     "with a stack of round weights on one pan. Environmental clutter: sandbag walls, three wooden "
     "ammunition crates, a fuel drum, a leaning signpost, tire ruts, tufts of dry grass, a "
     "windsock on a pole, and four tiny soldier silhouettes for scale standing near the tank's "
     "tracks. Dusty haze in the background with a low cream horizon. Single saturated accent: a "
     "crimson stripe on the windsock. CAMERA (fill all 8 seconds): 0.0-1.0s Full TOP-DOWN bird's "
     "eye over the parade ground: the tank and the two colossal feet read as flat shapes on the "
     "dirt, sandbags and crates arranged around them. 1.0-4.5s VERTICAL DROP — the camera falls "
     "straight down out of the top-down view, rotating as it goes, and levels out at ground height "
     "between the tank tracks and the titan's soles; dust kicks past the lens as it arrives. "
     "4.5-6.5s Track sideways at ground level and PUSH IN on the deep cratered footprint, its "
     "radiating cracks and thrown clods filling the frame, the tank's shallow track groove visible "
     "small in the background for contrast. 6.5-8.0s Hold, dirt still trickling into the crater. "
     "No shake. Push-in subject is the footprint crater. Mood: concrete, undeniable. "),

    ("s07_heat", "VIDEO",
     "Hand-drawn explanatory stage on cream paper. Two simplified humanoid body outlines stand "
     "side by side, drawn only as thick ink contours with translucent sand fill: a small one on "
     "the left, a giant one on the right. Inside each body, dozens of tiny round heat particles in "
     "warm orange are drawn as loose ink circles — the small body holds a handful, the giant body "
     "is densely packed to spread. Short arrows drawn as thin brush strokes escape through the "
     "skin outline, but far too few on the giant. Around the giant, the escaping arrows are choked "
     "and curl back inward. Supporting hand-drawn props on the stage: a mercury thermometer with a "
     "rising column, a small hand fan, a stylized radiator fin diagram, a cup with steam curls, "
     "and three annotation frames left deliberately empty for later text overlay. Ground shadow "
     "drawn as a single soft brush smear. Warm orange is the only saturated accent. CAMERA (fill "
     "all 8 seconds): 0.0-1.0s Tight on the small body outline, its few heat particles drifting "
     "calmly. 1.0-4.5s ORBIT — the camera swings 180 degrees around behind both figures and back, "
     "and as it comes around the giant body it RUSHES toward it while heat particles multiply "
     "forcefully inside, escape arrows choking and curling back at the skin line. 4.5-6.5s "
     "PUSH-THROUGH the giant's outline into its interior and PUSH IN on the densest knot of "
     "trapped orange particles churning against the inner wall. 6.5-8.0s Hold inside the packed "
     "mass, particles jostling with nowhere to go. No shake, no strobe, never locked-off. Push-in "
     "subject is the trapped particle mass. Mood: mounting pressure, claustrophobia. "),

    ("s08_cooked", "VIDEO",
     "[STYLE LOCK — but shift palette to thermal] Full-body shot of a 15-meter humanoid titan "
     "standing in an empty stone plaza at dusk, rendered as if seen through a hand-painted thermal "
     "imaging filter: the body glows in layered bands of deep violet at the extremities through "
     "orange in the torso to intense white-yellow at the core, all painted with visible brush "
     "texture and ink contours rather than digital gradients. Heat shimmer drawn as wavering "
     "vertical ink lines rising off the shoulders and skull. Thick crimson steam pours from the "
     "nape and the mouth. The stone plaza beneath is heat-darkened in a widening ring, with paving "
     "stones cracked and glowing at the seams, warm glowing patches on a toppled wooden cart, blackened "
     "banner poles, a warped iron bell lying on its side, and puddles steaming into steam. "
     "Background: silhouetted rooftops and a dark violet sky with drifting pale flecks drifting. In the "
     "final beat, cut to an extreme close-up of the titan's eye — the iris a steaming white-hot "
     "disc with tiny steam curls at CAMERA (fill all 8 seconds): 0.0-1.0s Ground level between the "
     "titan's heat-darkened feet, cracked glowing paving stones filling the foreground, the body "
     "towering away into heat shimmer. 1.0-4.5s CRANE UP — the camera rockets vertically up the "
     "front of the body, thermal bands sliding from violet through orange to intense white as it "
     "climbs, heat-shimmer lines and drifting pale flecks streaming past the lens. 4.5-6.5s At shoulder "
     "height it BANKS around to the nape and CHARGES IN on the steam vents there, thick crimson "
     "jets blasting toward the camera until they fill the frame. 6.5-8.0s Hold in the steam, the "
     "glowing cracked skin barely visible through it. No shake, no strobe. Do not zoom on the face "
     "or eye — the push-in subject is the nape steam vent. Mood: awe-inducing, beautiful. "),

    ("s09_eureka", "VIDEO",
     "Interior of a canvas field research tent, afternoon light glowing through the fabric. A "
     "scientist with messy brown hair tied back, round goggles pushed onto the forehead, a stained "
     "tan work coat with rolled sleeves, and ink-smudged hands stands wide-eyed with both arms "
     "thrown up in astonishment. In front of her, a huge pale-ochre titan forearm segment rests on "
     "a reinforced wooden trestle table that is barely bowing under it — visibly, absurdly, not "
     "enough. Dense supporting detail: a large hanging spring scale whose needle sits shockingly "
     "low, a chalkboard covered in hand-drawn structural sketches and blank annotation boxes, "
     "glass specimen jars on a shelf, a brass microscope, coils of rope, a stack of leather "
     "notebooks, scattered quills and an overturned inkpot, a lantern hanging from the ridge pole, "
     "two folding stools, a bucket of water, a rack of sample tubes, and a canvas flap tied open "
     "showing a sliver of muddy camp outside with two uniformed figures. Faint crimson steam still "
     "curls from the specimen. Crimson is the single saturated accent. CAMERA (fill all 8 "
     "seconds): 0.0-1.0s High under the tent ridge pole looking down, the whole cluttered "
     "workspace and the huge specimen laid out below. 1.0-4.5s CRANE DOWN — the camera drops fast "
     "through the tent volume, skimming over the specimen forearm along its length, the trestle "
     "table, jars, microscope and notebooks sweeping past underneath. 4.5-6.5s It banks up and "
     "CHARGES IN on the hanging spring scale, the needle sitting absurdly low, the dial filling "
     "the frame as it swings and settles. 6.5-8.0s Hold on the needle, the scientist's raised arms "
     "visible only as blurred shapes at the frame edge. No shake. Do not zoom on her face — the "
     "push-in subject is the scale dial and needle. Mood: eureka, comic disbelief. "),

    ("s10_foam", "VIDEO",
     "A three-stage magnification journey rendered as hand-inked illustration. Foreground layer: a "
     "patch of pale ochre titan skin with dry ceramic-like cracks. Middle layer: the same patch "
     "magnified into a lattice of irregular chambers separated by thin fibrous walls, drawn with "
     "wobbly brush outlines and translucent sand fills, hundreds of round and polygonal air "
     "pockets of varying size. Deep layer: inside the foam, drifting spherical voids catch pale "
     "light, thin strands stretch between chamber walls like the inside of a sea sponge, and faint "
     "warm steam wisps thread through the cavities. Beside the main journey, three small "
     "hand-drawn comparison vignettes are arranged like specimens pinned on a notebook page: a "
     "torn slice of bread showing its crumb, a broken block of white foam showing its bubbles, and "
     "a sectional study of porous mineral block showing its trabecular lattice — each in its own hand-inked frame "
     "with an empty label box beneath for later text. Scattered notebook props: a magnifying lens, "
     "a scalpel, two pins, a specimen slide. Electric cyan is the single saturated accent, used "
     "only on the deepest cavity highlights. CAMERA (fill all 8 seconds): 0.0-1.0s Grazing angle "
     "skimming across the dry cracked skin surface, the pinned specimen vignettes and notebook "
     "props sliding past in the periphery. 1.0-4.5s PUSH-THROUGH — the camera drives into a crack "
     "in the skin and keeps going, spread through the first chamber wall into the foam lattice, "
     "then through a second wall deeper in, cell walls rushing past on all sides like flying "
     "through a cave system at speed. 4.5-6.5s In the deepest layer it BANKS between drifting "
     "spherical voids and PUSHES IN on a single thin fibrous chamber wall until its fibers fill "
     "the frame, light glowing through from behind. 6.5-8.0s Drift there, strands flexing, warm "
     "steam threading between the cavities. No shake, no strobe, continuous forward flight — never "
     "a static frame. Push-in subject is the pore wall. Mood: wondrous, scientific intimacy. "),

    ("s11_whales", "VIDEO",
     "Ultra-wide comparison tableau on a pale cream field with a simple ruled ground line. On the "
     "right, the full standing silhouette of a 60-meter colossal humanoid figure rendered in flat "
     "dark ochre with exposed muscle striations drawn as simple parallel brush strokes, crimson "
     "steam venting from the shoulders and jaw, towering to the top of the frame. On the left, "
     "eighteen blue whales drawn in dusty slate-blue with pale bellies, arranged in three neat "
     "stacked rows of six like museum specimens, each with fine ink outlines, throat pleats, and "
     "small pectoral fins. Between the two groups, a hand-drawn balance scale of enormous "
     "proportions, its beam tilting. Scale anchors placed along the ground line: a row of tiny "
     "houses with tiled roofs, three matchstick trees, a small church steeple, five ant-sized "
     "human figures, and a stationary train of four carriages — all dwarfed. Faint horizontal haze "
     "bands recede into the distance. Crimson steam is the single saturated accent. CAMERA (fill "
     "all 8 seconds): 0.0-1.0s Low over the first row of whales, their flukes and pleated throats "
     "sliding beneath the lens. 1.0-4.5s FLY-OVER — the camera races low across all eighteen "
     "whales, row after row streaking past below, then hits the colossal figure's ankle and CRANES "
     "UP the full height of its body, muscle striations and venting steam blurring past. 4.5-6.5s "
     "At the top it whips around and CRANE-DOWNS onto the giant balance scale, PUSHING IN on the "
     "tilting beam and its pivot as it groans over. 6.5-8.0s Hold on the beam, the tiny houses and "
     "train visible far below as specks. No shake, never locked-off. Push-in subject is the "
     "balance beam. Mood: staggering scale. "),

    ("s12_kick", "VIDEO",
     "Dynamic action shot. A colossal humanoid figure in flat ochre with visible muscle-strand "
     "brushwork drives a high kick into the upper section of a massive stone wall. The moment of "
     "impact: the wall's stone blocks spread outward in a fan of dozens of individually inked "
     "tumbling chunks of every size, trailing dust plumes drawn as stippled clouds, with three "
     "long hand-inked speed arcs sweeping behind the leg. Thick crimson steam jets forcefully "
     "from the figure's shoulder vents, knee, and the nape of the neck, drawn as curling ribbon "
     "shapes. tumbling blocks detail: coming apart masonry, a bent iron ladder cartwheeling, a torn crimson "
     "banner spiraling, splintered wooden scaffolding planks, a bent bell, and a cloud of roof "
     "tiles. In the lower foreground, tiny silhouetted figures on rooftops brace against the "
     "expanding ring, and birds scatter in every direction. expanding ring rendered as two concentric thin "
     "ink rings. Background: pale cream sky going hazy with dust. Crimson is the single saturated "
     "accent, on the steam and the banner. CAMERA (fill all 8 seconds): 0.0-1.0s Low behind the "
     "colossal figure's planted foot as the kicking leg begins to load, steam building at the knee "
     "vent. 1.0-3.5s WHIP — the camera slams sideways following the leg's arc at extreme speed, "
     "the wall rushing into frame, motion arcs streaking. 3.5-4.0s HARD FREEZE on the impact "
     "frame: stone spread, expanding ring rings giving way out. 4.0-6.5s Time resumes and the camera "
     "CRANES DOWN through the spread outward field of tumbling blocks, weaving between tumbling masonry chunks, "
     "then PUSHES IN on one large spinning stone block turning end over end toward the lens. "
     "6.5-8.0s Follow it down as it slams into the rubble and dust swallows the frame. No screen "
     "shake, no strobe. Push-in subject is the tumbling stone block, never a person. Mood: "
     "powerful, exhilarating. "),

    ("s13_hollow", "VIDEO",
     "A colossal long-necked sauropod dinosaur stands in a Cretaceous river valley, drawn in flat "
     "olive and warm grey with heavy ink contours, its neck sweeping across the top of the frame "
     "and tail exiting the right edge. Environmental density: tall horsetail reeds and cycads in "
     "the foreground, three smaller sauropods drinking at a shallow braided river, a flock of "
     "long-tailed pterosaurs, scattered boulders, driftwood logs, a mud bank with trackways of "
     "huge three-toed footprints filling with water, low conifer forest on the far bank, and "
     "layered hazy mesas on the horizon. Inset into the composition like a pinned notebook study: "
     "an enlarged sectional study of a single segment block revealing a honeycomb of hollow internal chambers "
     "with paper-thin chalky white walls, drawn in chalky support column-white with wobbly ink outlines, plus a "
     "small ghosted silhouette of a bird's internal frame beside it showing the same hollow structure. "
     "Extra study props around the inset: a hand lens, a measuring caliper, two pins, and an empty "
     "label frame. Dusty teal sky with three flat clouds. Electric cyan is the single saturated "
     "accent, used only inside the internal cavities. CAMERA (fill all 8 seconds): 0.0-1.0s Ground "
     "level beside one colossal pillar leg, horsetail reeds brushing the lens, the body vanishing "
     "upward out of frame. 1.0-4.5s CRANE UP — the camera climbs the flank and RIDES ALONG the "
     "spine toward the neck at speed, the river valley, drinking sauropods and pterosaur flock "
     "wheeling away below, the neck sweeping ahead like a highway. 4.5-6.5s Over a single segment block "
     "it PUSHES THROUGH the support column surface into the sectional study and slows inside the honeycomb of hollow "
     "chambers, paper-thin chalky white walls glowing around the lens. 6.5-8.0s Drift deeper between the "
     "air cells and settle. No shake. Push-in subject is the segment block's internal honeycomb. Mood: "
     "awe with scientific curiosity. "),

    ("s14_pillar", "VIDEO",
     "Three-panel comparative composition on cream paper, each panel divided by a thin hand-inked "
     "border. Left panel: a human leg in mid-stride, drawn as an ink contour with the knee clearly "
     "bent, and a set of curved crimson stress arrows bunching at the knee joint. Center panel: a "
     "massive sauropod hind limb, drawn in flat olive-grey, standing perfectly straight and "
     "vertical like a tree trunk, with straight crimson force arrows running cleanly down the support column "
     "axis into the ground. Right panel: a weathered stone temple column with fluting and a simple "
     "capital, cracked at the base, with the identical straight arrows running down it — visually "
     "rhyming with the dinosaur limb. Beneath all three, a continuous hand-drawn ground line with "
     "small stones and grass tufts. Surrounding the panels like margin notes: a hand-drawn plumb "
     "bob on a string, a small set of stacked blocks, a sketch of an elephant's pillar-like leg, "
     "and three empty caption frames for later text. Crimson is the only saturated accent, used "
     "exclusively on the force arrows. CAMERA (fill all 8 seconds): 0.0-1.0s Tight low angle on "
     "the bent human knee, the crimson stress arrows bunching there. 1.0-4.5s ORBIT — the camera "
     "sweeps 180 degrees around the three subjects in one continuous arc, the human leg, the "
     "sauropod limb and the stone column rotating past each other, their force arrows aligning as "
     "the angle changes. 4.5-6.5s It rises above the sauropod limb and CRANE-DOWNS straight along "
     "the support column axis, PUSHING IN so the straight force arrows run directly at the lens and into the "
     "ground plane. 6.5-8.0s Settle at ground level where the arrows disappear into the earth. No "
     "shake, never locked-off. Push-in subject is the force arrow running down the support column. Mood: "
     "elegant, clarifying. "),

    ("s15_elephant", "VIDEO",
     "Savanna scene at golden hour. An adult elephant and its much smaller calf stand side by side "
     "in three-quarter view, drawn in flat dusty grey with heavy ink contours, wrinkled skin "
     "indicated by short brush hatching, large ears, and visible pillar-like legs. Behind them, a "
     "hand-drawn herd of five more elephants recedes into haze, a flat-topped acacia tree, a "
     "termite mound, tall dry grass drawn as vertical brush flicks, three white egrets, a shallow "
     "watering hole with reflections, scattered rocks, and a low distant escarpment. Overlaid on "
     "each animal like a pinned structural study: a ghosted white outline of its support column, the "
     "adult's dramatically thicker relative to its body, each in its own hand-inked frame. Beside "
     "them, a small hand-drawn growth chart of three stacked silhouettes from calf to adult with "
     "an empty label box. Warm gold light with long soft shadows across the ground. A single "
     "saturated accent: the warm gold rim light on the elephants' backs. CAMERA (fill all 8 "
     "seconds): 0.0-1.0s Low in the dry grass, brush-flick blades filling the foreground, the herd "
     "silhouetted in golden haze beyond. 1.0-4.5s FLY-THROUGH — the camera races forward low "
     "between the herd's legs, pillar limbs sweeping past on both sides, dust and egrets "
     "scattering, emerging in front of the adult and calf. 4.5-6.5s It CRANE-DOWNS onto the "
     "adult's foreleg and PUSHES IN on the ghosted white support column overlay until the support column's thickness "
     "fills the frame, the calf's much thinner support column visible small beside it for contrast. 6.5-8.0s "
     "Hold there, gold rim light sliding along the support column outline. No shake. Do not zoom on the "
     "elephants' faces — the push-in subject is the support column overlay. Mood: warm, grounded, natural "
     "wisdom. "),

    ("s16_whale", "VIDEO",
     "[STYLE LOCK — palette shifts to deep ocean blues while keeping ink-and-gouache texture] "
     "Underwater wide shot in deep blue-teal water with god rays slanting down from a bright "
     "surface. An enormous blue whale glides across the full width of the frame in slate-blue with "
     "a pale mottled belly, throat pleats drawn as long parallel ink lines, small dorsal fin, and "
     "wide flukes mid-downstroke. Around it: a school of hundreds of tiny silver fish splitting "
     "into two streams, three dolphins arcing above, drifting krill drawn as thousands of specks "
     "in a warm haze, floating kelp fronds, suspended plankton motes, a scattering of rising "
     "bubble strings, and a small human diver silhouette near the lower right for scale — almost "
     "invisibly small. On the whale's body, two sets of hand-drawn arrows in contrasting colors: "
     "heavy downward gravity arrows and equally strong upward buoyancy arrows, canceling each "
     "other visibly. Seafloor far below with soft dunes and a shipwreck rib cage half-buried. "
     "Surface shimmer at the top edge. Electric cyan is the single saturated accent, used only on "
     "the buoyancy arrows. CAMERA (fill all 8 seconds): 0.0-1.0s Ahead of the whale's rostrum as "
     "it comes toward the lens out of the blue gloom, krill haze and god rays overhead. 1.0-4.5s "
     "TRACK — the camera flies backward alongside the animal at its own speed, the full body "
     "streaming past, throat pleats and the fluke's downstroke sweeping the frame, the fish school "
     "splitting around the lens. 4.5-6.5s It DIVES beneath the whale and CRANES UP to look at the "
     "pale belly from below, then PUSHES IN where the upward buoyancy arrows meet and cancel the "
     "downward gravity arrows, the arrow pair filling the frame. 6.5-8.0s Hold under the belly, "
     "bubbles rising past, the wreck's rib cage far below. No shake. Push-in subject is the "
     "buoyancy arrow pair. Mood: serene, majestic release. "),

    ("s17_sunset", "VIDEO",
     "A single continuous day-to-night transition in one composition. A 15-meter humanoid titan "
     "stands motionless on a grassy hillside. In the left half of the frame it is bathed in warm "
     "afternoon sun: golden light rims its shoulders, thin sunbeam strokes drawn entering the skin "
     "as small warm arrows, faint steam rising, and its posture upright and faintly alert. Toward "
     "the right half the sky graduates into deep indigo dusk with the sun a low flat disc on the "
     "horizon; the same figure appears slumping, its surface going grey and matte with hairline "
     "cracks spreading like dried clay, steam dying to nothing, and its head bowed. Environmental "
     "detail across the hillside: tall grass drawn as vertical brush flicks bending in wind, a "
     "lone twisted tree, a low stone ruin with a collapsed arch, a flock of birds crossing from "
     "lit side to dark side, three sheep, a winding dirt path, and scattered wildflowers closing "
     "their petals on the dark side. Stars begin as tiny ink dots in the upper right. Warm gold on "
     "the left and deep indigo on the right, meeting in the middle. CAMERA (fill all 8 seconds): "
     "0.0-1.0s Low on the sunlit side, warm gold raking across the grass toward the standing "
     "figure. 1.0-4.5s ORBIT — the camera swings a full 180 degrees around the figure, and as it "
     "travels the sky rolls from gold through amber into deep indigo, the sun sinking, birds "
     "crossing from light into dark, wildflowers folding shut, the figure's surface going grey and "
     "matte behind the moving camera. 4.5-6.5s It arrives on the dark side and PUSHES IN on the "
     "hairline cracks spreading across the stiffening surface like drying clay, until the fissure "
     "network fills the frame. 6.5-8.0s Hold as the last steam wisp dies and stars prick out "
     "above. No shake. Push-in subject is the spreading surface crack. Mood: melancholy, quiet "
     "logic. "),

    ("s18_dawn", "VIDEO",
     "Wide closing shot at dawn. The silhouette of a colossal humanoid figure stands beyond a long "
     "stone wall, backlit by a rising sun that fills the sky with pale gold and soft rose bands, "
     "the figure reduced to a flat dark shape with only thin crimson steam curling from its "
     "shoulders. The wall runs diagonally across the lower third, its stones catching warm rim "
     "light, with three tiny watchtowers, a line of banner poles, and six ant-sized figures "
     "standing on the parapet looking outward. Below the wall: rooftops of a sleeping town with "
     "chimney smoke rising in thin curls, a windmill, a church spire, and orchards in neat rows. "
     "Foreground: tall grass in soft focus at the bottom edge and two birds crossing the frame. "
     "Layered atmospheric haze separates wall, figure, and sky into three clean depth planes. Wide "
     "empty sky area in the upper third deliberately left clear for later end-card overlay. Warm "
     "gold is the single saturated accent. CAMERA (fill all 8 seconds): 0.0-1.0s Low among the "
     "foreground grass behind the parapet, the town rooftops and chimney smoke beyond. 1.0-4.5s "
     "CRANE UP — the camera lifts and flies forward over the wall walk, the watchtowers and banner "
     "poles and the six tiny figures passing beneath it, then continues climbing past the colossal "
     "silhouette's shoulder. 4.5-6.5s It keeps rising into the open dawn sky, the wall and figure "
     "dropping away to the bottom edge of frame, gold and rose bands filling the view. 6.5-8.0s "
     "Settle on the wide empty sky, two birds crossing, the lower third holding the silhouette "
     "small. Upper two-thirds deliberately left clear for the end card. No shake. Mood: resolved, "
     "thoughtful, a little hopeful. "),

    ("s01_b", "VIDEO",
     "Ground level inside the walled town at dawn. A narrow cobbled lane runs between leaning "
     "timber-framed houses with clay-tiled roofs, shuttered windows, hanging laundry lines, a "
     "stone well with a wooden bucket, stacked barrels, a fruit stall under a striped awning, "
     "three chickens, a tethered donkey and a water trough. At the far end of the lane the "
     "colossal stone wall blocks the sky completely. 0-1s: tight on the well and the bucket in the "
     "foreground, the lane receding behind it. 1-4.5s: the camera races forward down the lane at "
     "speed, houses whipping past on both sides, laundry lines flicking overhead, chickens "
     "scattering, and bursts out into the open square at the wall's base where the stonework fills "
     "the entire frame. 4.5-6.5s: it cranes upward along the wall face and pushes in on a single "
     "weathered stone block with olive moss in its mortar joint until that block fills the frame. "
     "6.5-8s: it holds there, a thin shadow sweeping across the stone as something enormous moves "
     "beyond the wall. Continuous forward travel, strong parallax. No people in close-up. Mood: "
     "ordinary morning about to end. "),

    ("s01_c", "VIDEO",
     "Extreme close view of the top edge of a colossal stone wall against a pale cream sky. Four "
     "enormous humanoid fingers with dry cracked skin like old ceramic rest over the parapet, thin "
     "crimson steam curling from the knuckle creases. Along the wall walk below the fingers: iron "
     "braziers, a coiled rope ladder, three banner poles with tattered crimson cloth, stacked "
     "sandbags, a small bell on a bracket and two abandoned helmets on the stones. 0-1s: start "
     "behind the fingers looking along the wall walk into the distance. 1-4.5s: the camera orbits "
     "180 degrees around the nearest finger at speed, the wall walk and its clutter wheeling past "
     "below, the cream sky rotating behind, steam ribbons trailing across the lens. 4.5-6.5s: it "
     "stops in front of the fingertip and pushes in hard on the cracked nail plate until the "
     "fissure network fills the frame. 6.5-8s: it holds, steam drifting. Crimson is the only "
     "saturated accent. Never zoom on a face. Mood: dread at close range. "),

    ("s02_b", "VIDEO",
     "A muddy survey field at dusk. A detached titan forearm the size of a bus lies tipped on "
     "churned earth, pale ochre skin dry and cracked, the sealed end glassy with faint crimson "
     "steam. Around it: two wooden crates, a coil of rope, iron stakes with red pennants, a tipped "
     "bucket, a folding stool, a lantern on a pole, cart ruts filled with rainwater, and boot "
     "prints in the mud. 0-1s: top-down bird's eye directly above the forearm, its silhouette flat "
     "on the churned ground. 1-4.5s: the camera drops vertically out of the top-down view, "
     "rotating as it falls, and levels out at mud height beside the limb, water splashing past the "
     "lens as it arrives. 4.5-6.5s: it tracks along the underside of the forearm and pushes in "
     "where the limb barely presses into the soft mud - the ground almost undisturbed beneath "
     "something enormous. 6.5-8s: it holds on that shallow impression, a single raindrop rippling "
     "a puddle. No people in close-up. Mood: quiet wrongness, weight that isn't there. "),

    ("s02_c", "VIDEO",
     "Interior of an open supply tent at dusk beside a muddy field. On a plank table: a large "
     "brass balance scale with two empty pans, a stack of iron weight discs, a leather ledger, an "
     "inkpot, a folding rule, a lantern, a tin cup, and a rolled canvas. Through the open flap the "
     "detached titan forearm is visible outside, dwarfing the crates around it. 0-1s: low across "
     "the table, weight discs in the foreground, the balance beam level. 1-4.5s: the camera sweeps "
     "in a wide orbit around the balance, the tent poles and the field beyond rotating behind it, "
     "and as it comes round the beam tips sharply upward with a swing. 4.5-6.5s: it dives in on "
     "the pointer needle sitting absurdly low on its arc scale, the dial filling the frame as it "
     "wobbles and settles. 6.5-8s: it holds on the needle, lantern light flickering across the "
     "brass. Push-in subject is the balance needle. Mood: comic disbelief. "),

    ("s03_b", "VIDEO",
     "A candlelit 17th-century desk seen from directly above. Spread across the oak surface: an "
     "open folio showing two hand-drawn support column diagrams, one slender and one grotesquely "
     "thick; loose sketch sheets; a brass compass; dividers; a wooden ruler; an inkwell with two "
     "quills; a sand shaker; a stack of leather books; a guttering candle in a brass holder; a "
     "magnifying lens; and a small terrestrial globe at the frame edge. 0-1s: full top-down over "
     "the whole desk, everything readable at once. 1-4.5s: the camera drops straight down toward "
     "the open folio, rotating as it descends, and levels out just above the page so the two "
     "column drawings run away toward the horizon of the desk. 4.5-6.5s: it pushes in along the "
     "thicker column drawing until the ink hatching fills the frame, candlelight warming one edge "
     "of the paper. 6.5-8s: it holds, a wisp of candle smoke crossing the page. No text, no "
     "letters, no numbers anywhere - the diagrams are pure line drawings. Mood: quiet revelation. "),

    ("s03_c", "VIDEO",
     "A 17th-century study at night, seen from the far corner. Floor-to-ceiling shelves packed "
     "with books and rolled charts, a brass telescope on a tripod at an arched window, a hanging "
     "astrolabe, a globe on a stand, a ladder against the shelves, a fireplace with low embers, a "
     "high-backed chair, and a heavy desk with three lit candles. Deep indigo night sky and stars "
     "beyond the window. 0-1s: wide from the corner, the whole room in one frame, candle glow "
     "pooling at the desk. 1-4.5s: the camera flies forward across the room, past the telescope "
     "and under the hanging astrolabe, banking toward the window, shelves streaking on both sides. "
     "4.5-6.5s: it turns and pushes in through the window glass to the night sky, stars spreading "
     "wide, then settles on the moon low over rooftops. 6.5-8s: it holds on the moon, thin cloud "
     "drifting across. Never zoom on the scholar. Mood: a small room, a large universe. "),

    ("s04_b", "VIDEO",
     "A clean study stage on warm cream paper. A single large cube built from many small unit "
     "blocks stands centre frame, its faces drawn with wobbly ink outlines and flat sand fills. "
     "Beside it, a hand-drawn column of small square tiles represents its surface area, and below, "
     "a stack of round weight discs represents its mass. Study props scattered around: a set "
     "square, dividers, a coiled tape, three drawing pins and four blank framed panels. 0-1s: "
     "tight low angle at the base of the cube, unit blocks receding upward. 1-4.5s: the camera "
     "flies straight through a gap between the unit blocks into the cube's hollow interior, unit "
     "blocks rushing past on all sides, then bursts out of the top face and rises. 4.5-6.5s: from "
     "above it cranes down onto the stack of weight discs and pushes in until the topmost disc "
     "fills the frame, the tile column tiny beside it. 6.5-8s: it holds there. Electric cyan only "
     "on the weight discs. No numbers anywhere. Mood: escalating logic. "),

    ("s04_c", "VIDEO",
     "A clean study stage on warm cream paper. Two hand-drawn creatures stand side by side as "
     "simple ink outlines with translucent sand fill: a small four-legged animal on the left and "
     "the same animal scaled up enormously on the right, its legs now absurdly thick and stumpy. "
     "Beneath each, a hand-ruled ground line. Around them: a plumb bob, a folding rule, a stack of "
     "three weight discs, and blank framed panels. 0-1s: tight on the small creature's slender "
     "leg. 1-4.5s: the camera pulls back fast and arcs right, the giant version rising into frame "
     "and dwarfing the first, its thick legs sliding past the lens as the camera sweeps around "
     "behind it. 4.5-6.5s: it pushes in on the giant's thickened lower leg where the outline "
     "bulges outward, until that swollen contour fills the frame. 6.5-8s: it settles. Never zoom "
     "on a face. Mood: the shape of the problem. "),

    ("s05_b", "VIDEO",
     "A clean study stage on warm cream paper. A tall slender chalky-white support column with an "
     "internal lattice of thin diagonal struts stands centre frame under a large ochre load block. "
     "Beside it a short stout column carries an identical block, untouched. Around them: a plumb "
     "bob, dividers, a set square, a coiled tape, stacked weight discs and blank framed panels. "
     "0-1s: start high above both columns looking straight down at the two ochre blocks. 1-4.5s: "
     "the camera falls vertically between the two columns, rotating as it drops, the lattice of "
     "the tall one sliding past on one side and the smooth surface of the short one on the other, "
     "and levels out at ground height between them. 4.5-6.5s: it pushes in on the base of the tall "
     "column where fine hairline lines have opened in the chalk and pale dust has gathered on the "
     "ground line. 6.5-8s: it holds, dust drifting. Amber and ochre only - no red, nothing that "
     "reads as liquid. No people. Mood: the failure has already happened. "),

    ("s05_c", "VIDEO",
     "A clean study stage on warm cream paper. The tall chalky-white lattice column now leans at a "
     "slight angle under its ochre load block, thin pale lines open along its midsection, chalk "
     "dust settled in a ring on the ground line. The short stout column beside it stands perfectly "
     "straight under an identical block. Study props around the stage: plumb bob, dividers, set "
     "square, coiled tape, weight discs, drawing pins, blank framed panels. 0-1s: tight on the "
     "short column's clean untouched surface. 1-4.5s: the camera tracks sideways at speed across "
     "the stage, sweeping past the props, and arcs up and around the leaning tall column so its "
     "tilt reads against the level ground line. 4.5-6.5s: it pushes in on the widest opening in "
     "the lattice until the thin pale lines and drifting chalk dust fill the frame. 6.5-8s: it "
     "holds. No red anywhere. Mood: quiet inevitability. "),

    ("s06_b", "VIDEO",
     "A dusty parade ground. A hand-inked military tank in olive drab sits on wide continuous "
     "tracks - riveted armour plates, stowage boxes, spare track links, a long barrel and an "
     "antenna - its tracks pressing shallow even grooves into the dirt. Around it: sandbag walls, "
     "three wooden crates, a fuel drum, a leaning signpost with a blank board, tyre ruts, dry "
     "grass tufts and a windsock on a pole. 0-1s: low along the track line, road wheels receding "
     "into the distance. 1-4.5s: the camera races along the length of the tank at ground height, "
     "track links flicking past the lens, then cranes up and over the hull to look down at the two "
     "long grooves the tracks have left in the dirt. 4.5-6.5s: it pushes in on one shallow groove, "
     "the dirt barely disturbed, individual pebbles visible in the tread pattern. 6.5-8s: it holds "
     "there, dust drifting across. Push-in subject is the track groove. Mood: engineered weight, "
     "properly carried. "),

    ("s06_c", "VIDEO",
     "The same dusty parade ground. Two enormous bare humanoid footprints are punched deep into "
     "the dirt, each a dark crater with radiating cracks and thrown clods around its rim, far "
     "deeper than the shallow tank grooves running alongside. Sandbags, crates, a fuel drum, a "
     "windsock and dry grass tufts frame the scene. Tiny figures stand at the far edge for scale. "
     "0-1s: full top-down over both footprints and the tank grooves beside them. 1-4.5s: the "
     "camera drops vertically into one footprint, rotating as it falls, the crater walls rising "
     "past the lens until it reaches the cracked floor of the impression. 4.5-6.5s: it pushes "
     "forward along a radiating crack in the crater floor until the fissure fills the frame, loose "
     "soil trickling into it. 6.5-8s: it holds. Push-in subject is the crater crack. Mood: "
     "undeniable. "),

    ("s07_b", "VIDEO",
     "A hand-drawn explanatory stage on cream paper. A single large humanoid body outline drawn as "
     "a thick ink contour with translucent sand fill fills most of the frame. Inside it, hundreds "
     "of tiny warm-orange heat particles drawn as loose ink circles churn and press outward. Thin "
     "brush arrows try to escape through the skin outline but are far too few and curl back "
     "inward. Around the stage: a mercury thermometer, a small hand fan, a stylised radiator fin "
     "diagram, a cup with steam curls, and blank framed panels. 0-1s: outside the body outline, "
     "the whole figure in frame, particles visible through the fill. 1-4.5s: the camera drives "
     "straight through the ink contour into the interior and flies among the packed orange "
     "particles, which stream past the lens in every direction, growing denser. 4.5-6.5s: it "
     "pushes toward the inner surface of the skin outline where escape arrows are choked and bent "
     "back, until that jammed cluster fills the frame. 6.5-8s: it holds inside the packed mass. "
     "Warm orange only. No people, no faces. Mood: nowhere to go. "),

    ("s07_c", "VIDEO",
     "A hand-drawn explanatory stage on cream paper. A large humanoid body outline seen from "
     "directly above, its skin contour drawn as a closed ink loop. The interior is packed solid "
     "with warm-orange heat particles. A ring of thin brush arrows around the outline shows escape "
     "routes, far too sparse for the volume inside. Beside it, a much smaller outline holds only a "
     "handful of particles with plenty of arrows. Props: thermometer, hand fan, radiator fin "
     "diagram, blank panels. 0-1s: top-down over the small outline, its few particles drifting "
     "calmly. 1-4.5s: the camera sweeps laterally across the stage at speed to the giant outline "
     "and spirals down toward it, the packed orange mass swelling in frame. 4.5-6.5s: it pushes in "
     "on a single escape arrow at the skin line, bent and curling back on itself, until that one "
     "bent arrow fills the frame. 6.5-8s: it holds. Mood: the exit is too small. "),

    ("s08_b", "VIDEO",
     "A colossal humanoid figure stands motionless in an empty stone plaza at dusk, painted as "
     "though seen through a hand-brushed thermal filter: deep violet at the limbs through orange "
     "in the torso to intense white-yellow at the core, all with visible brush texture and ink "
     "contours. Heat shimmer rises as wavering vertical ink lines. The plaza stones beneath are "
     "heat-darkened in a widening ring, seams glowing, a toppled cart, blackened banner poles, a "
     "bell lying on its side. 0-1s: high wide from a rooftop, the figure small in the plaza, "
     "shimmer rising. 1-4.5s: the camera dives from the rooftop straight down toward the plaza, "
     "buildings streaking past, and pulls out of the dive at ground height right at the figure's "
     "feet. 4.5-6.5s: it pushes in on the glowing seam between two paving stones where the heat "
     "has spread, the crack line blazing white-yellow, until it fills the frame. 6.5-8s: it holds, "
     "pale flecks drifting up through the shot. Never zoom on the face. Mood: the ground itself is "
     "cooking. "),

    ("s08_c", "VIDEO",
     "Close view of a colossal figure's shoulder and nape rendered in hand-brushed thermal colours "
     "- violet, orange and intense white - with heavy ink contours and visible brush grain. Thick "
     "crimson steam blasts from vents along the nape in curling ribbon shapes. Behind, a dusk sky "
     "in deep violet with drifting pale flecks and silhouetted rooftops far below. 0-1s: below the "
     "shoulder looking up along the arm, steam ribbons crossing overhead. 1-4.5s: the camera "
     "cranes up the side of the body at speed, the thermal bands sliding from violet through "
     "orange to white as it climbs, and banks around behind the neck. 4.5-6.5s: it charges into "
     "the densest steam vent at the nape until the crimson plume fills the frame entirely. 6.5-8s: "
     "it holds inside the steam, the glowing skin barely visible through it. Push-in subject is "
     "the steam vent. Mood: a body venting itself. "),

    ("s09_b", "VIDEO",
     "Interior of a canvas field research tent, afternoon light through the fabric. A reinforced "
     "wooden trestle table barely bows under a huge pale-ochre limb segment. Dense clutter: glass "
     "specimen jars on a shelf, a brass microscope, coils of rope, leather notebooks, scattered "
     "quills, an overturned inkpot, a hanging lantern, two folding stools, a bucket, a rack of "
     "sample tubes, and a chalkboard covered in blank framed panels. 0-1s: low along the table "
     "top, jars and notebooks in the foreground. 1-4.5s: the camera sweeps in a wide arc around "
     "the trestle table, tent poles and hanging lantern wheeling past, and comes to rest beneath "
     "the table looking up at the barely-bending planks. 4.5-6.5s: it pushes in on a single table "
     "leg where the wood is not even flexing under a load that should have snapped it. 6.5-8s: it "
     "holds on the untroubled joint. Never zoom on a person. Mood: the evidence is in what didn't "
     "happen. "),

    ("s09_c", "VIDEO",
     "A cluttered research tent table seen from directly above. On the planks: a hanging spring "
     "scale with its needle low on the dial, a chalkboard leaning at the edge covered in blank "
     "framed panels, glass jars, a brass microscope, a rack of sample tubes, leather notebooks, "
     "quills, a folding rule and an overturned inkpot with a dark pool. 0-1s: full top-down over "
     "the whole table, everything laid out flat. 1-4.5s: the camera drops vertically toward the "
     "spring scale, rotating as it falls, the table clutter spreading away at the frame edges, and "
     "levels out beside the dial. 4.5-6.5s: it pushes in on the needle resting far lower on the "
     "arc than it should, the graduated marks blank and unlabelled, until the dial face fills the "
     "frame. 6.5-8s: it holds as the needle trembles once and settles. No numbers or letters on "
     "the dial. Mood: quiet impossible reading. "),

    ("s10_b", "VIDEO",
     "Deep inside a porous organic foam structure. Irregular chambers of every size are separated "
     "by thin fibrous walls drawn with wobbly ink outlines and translucent sand fills. Light "
     "filters through the thinnest membranes. Fine strands stretch between chamber walls like the "
     "inside of a sea sponge, and faint warm steam threads through the cavities. 0-1s: inside a "
     "single large chamber, its curved walls surrounding the lens. 1-4.5s: the camera flies "
     "forward through one chamber wall into the next, and the next, and the next, cell walls "
     "bursting past on all sides in a continuous tunnel of openings, the structure opening "
     "endlessly ahead. 4.5-6.5s: it slows and pushes in on one paper-thin membrane backlit from "
     "behind, its fibre network glowing until it fills the frame. 6.5-8s: it drifts there, strands "
     "flexing gently. Electric cyan only on the backlit membrane. Mood: vast interior emptiness. "),

    ("s10_c", "VIDEO",
     "A specimen study page on warm cream paper. Three hand-inked comparison vignettes sit in "
     "their own frames like pinned specimens: a torn slice of bread showing its crumb, a broken "
     "block of white foam showing its bubbles, and a sectional study of porous mineral showing its "
     "lattice. Around them: a magnifying lens, a scalpel, two pins, a specimen slide, a folding "
     "rule and blank label frames left empty. 0-1s: low across the page, the three vignettes "
     "receding in a row. 1-4.5s: the camera flies along the row at speed, each vignette swelling "
     "and passing, then banks up and over to look straight down at the middle one. 4.5-6.5s: it "
     "dives into the foam vignette and pushes through its surface into the bubble structure until "
     "the cell walls fill the frame. 6.5-8s: it holds inside the bubbles. No text on any label - "
     "every frame is blank. Mood: the same trick, everywhere. "),

    ("s11_b", "VIDEO",
     "An ultra-wide comparison tableau on pale cream. Eighteen blue whales in dusty slate-blue "
     "with pale bellies are arranged in three neat stacked rows like museum specimens, each with "
     "fine ink outlines, throat pleats and small pectoral fins. Tiny scale anchors along a ruled "
     "ground line: a row of houses with tiled roofs, three matchstick trees, a church steeple and "
     "a stationary train of four carriages. 0-1s: low at the ground line beside the tiny houses, "
     "the first whale looming beyond them. 1-4.5s: the camera rises fast and flies backward along "
     "the rows, whale after whale sliding beneath it, the arrangement widening until all eighteen "
     "fill the frame at once. 4.5-6.5s: it cranes down to the ground line and pushes in on the "
     "tiny train carriages, dwarfed beneath the nearest whale's fluke. 6.5-8s: it holds there. "
     "Mood: staggering arithmetic. "),

    ("s11_c", "VIDEO",
     "A colossal humanoid silhouette in flat dark ochre stands on a pale cream field, muscle "
     "striations drawn as simple parallel brush strokes, crimson steam venting from shoulders and "
     "jaw. At its feet, a hand-drawn balance scale of enormous proportions with a tilting beam, "
     "and along the ruled ground line a row of tiny houses, three trees and five ant-sized "
     "figures. 0-1s: at ground level beside the tiny houses, the ochre leg rising out of frame. "
     "1-4.5s: the camera cranes straight up the body at speed, striations and venting steam "
     "blurring past, and arcs over the shoulder to look back down at the balance scale far below. "
     "4.5-6.5s: it dives back down and pushes in on the scale's pivot where the beam grinds over. "
     "6.5-8s: it holds on the pivot. Push-in subject is the balance pivot, never the figure. Mood: "
     "the numbers do not balance. "),

    ("s12_b", "VIDEO",
     "A colossal humanoid figure in flat ochre drives a high kick toward a massive stone wall, "
     "muscle strands drawn as brush strokes, thick crimson steam jetting from shoulder vents and "
     "knee. The wall is built of thousands of inked stone blocks with iron ladders, banner poles "
     "and wooden scaffolding against its face. Dust plumes drawn as stippled clouds. 0-1s: tight "
     "low behind the planted foot as the kicking leg loads, steam building at the knee. 1-4.5s: "
     "the camera whips sideways following the leg's arc at extreme speed, the wall rushing into "
     "frame, three long hand-inked speed arcs sweeping behind. 4.5-6.5s: at contact it pushes in "
     "on the knee vent where crimson steam blasts outward in curling ribbons, the plume filling "
     "the frame. 6.5-8s: it holds in the steam. No screen shake. Push-in subject is the steam "
     "vent. Mood: thrust, not mass. "),

    ("s12_c", "VIDEO",
     "The aftermath at the base of a breached stone wall. Hundreds of individually inked stone "
     "blocks of every size lie tumbled across cobbles in a fan of rubble, trailing stippled dust. "
     "Among them: a bent iron ladder, a torn crimson banner half buried, splintered scaffolding "
     "planks, scattered roof tiles and a toppled bell. Two thin concentric ink rings mark where "
     "the shock spread. Beyond, the wall's ragged breach opens onto pale cream sky. 0-1s: full "
     "top-down over the rubble fan, blocks reading as flat shapes. 1-4.5s: the camera drops "
     "vertically into the rubble field, rotating as it falls, tumbled blocks rising past the lens, "
     "and levels out at cobble height weaving between the largest stones. 4.5-6.5s: it pushes in "
     "on the torn crimson banner caught under a block, cloth still settling. 6.5-8s: it holds, "
     "dust drifting down. Crimson only on the banner. Mood: after the impossible. "),

    ("s13_b", "VIDEO",
     "A Cretaceous river valley. A colossal long-necked sauropod stands in shallow braided water, "
     "drawn in flat olive and warm grey with heavy ink contours. Around it: tall horsetail reeds "
     "and cycads, three smaller sauropods drinking, a flock of long-tailed pterosaurs, boulders, "
     "driftwood logs, a mud bank stamped with huge three-toed trackways filling with water, "
     "conifer forest on the far bank and hazy mesas beyond. 0-1s: water level among the reeds, the "
     "animal's leg rising out of frame like a tree trunk. 1-4.5s: the camera skims forward across "
     "the water at speed, weaving between the legs of the herd, spray flicking past, and bursts "
     "out into the open channel before rising sharply. 4.5-6.5s: from above it cranes down onto a "
     "single water-filled footprint in the mud bank and pushes in until the three-toed impression "
     "fills the frame. 6.5-8s: it holds, ripples spreading in the print. Mood: enormous, and "
     "unbothered. "),

    ("s13_c", "VIDEO",
     "A sectional study of a single enormous vertebral block, presented like a pinned specimen on "
     "warm cream paper. The chalky bone-white exterior is cut away to reveal a honeycomb of hollow "
     "internal chambers with paper-thin walls. Beside it a ghosted outline of a bird's internal "
     "frame shows the identical hollow structure. Study props: a hand lens, a measuring caliper, "
     "two pins and blank label frames. 0-1s: tight on the solid outer surface of the block, its "
     "chalky texture filling the frame. 1-4.5s: the camera drives straight through the surface "
     "into the honeycomb and flies among the hollow chambers, thin walls rushing past on every "
     "side like a cave system opening ahead. 4.5-6.5s: it slows and pushes in on one paper-thin "
     "wall where light glows through from behind. 6.5-8s: it drifts there. Electric cyan only "
     "inside the cavities. No labels or text. Mood: emptiness by design. "),

    ("s14_b", "VIDEO",
     "A weathered stone temple colonnade at golden hour. A row of fluted columns with simple "
     "capitals recedes into the distance on a cracked stone platform, olive weeds in the joints, "
     "fallen block fragments, a broken step, and long shadows raking across the stones. Pale cream "
     "sky beyond. 0-1s: at the base of the nearest column looking straight up its flutes to the "
     "capital. 1-4.5s: the camera flies forward down the colonnade at speed, column after column "
     "whipping past on both sides in strong parallax, shadow bars strobing softly across the lens "
     "without flashing. 4.5-6.5s: it stops at the last column and pushes in on where the shaft "
     "meets its base, the load running straight down into the stone. 6.5-8s: it holds there. Mood: "
     "force with nowhere to bend. "),

    ("s14_c", "VIDEO",
     "A comparative study stage on warm cream paper. Three limbs stand side by side as hand-inked "
     "studies: a bent human leg with curved amber arrows bunching at the knee, a straight vertical "
     "sauropod limb with arrows running clean down the bone axis, and a fluted stone column with "
     "the identical straight arrows. A hand-ruled ground line runs beneath all three, with a plumb "
     "bob, stacked blocks and blank framed panels in the margins. 0-1s: tight on the bent knee, "
     "amber arrows crowding at the joint. 1-4.5s: the camera sweeps 180 degrees around all three "
     "subjects in one continuous arc, the three limbs rotating past each other, their arrows "
     "aligning as the angle changes. 4.5-6.5s: it rises above the straight limb and cranes down "
     "along the bone axis so the arrows run directly at the lens and into the ground. 6.5-8s: it "
     "settles where they disappear into the earth. Amber only on the arrows. Mood: elegant, "
     "clarifying. "),

    ("s15_b", "VIDEO",
     "A savanna at golden hour. A herd of elephants moves across dry grass in flat dusty grey with "
     "heavy ink contours, wrinkled skin indicated by short brush hatching. Around them: a "
     "flat-topped acacia, a termite mound, tall grass drawn as vertical brush flicks, three white "
     "egrets, a shallow watering hole with reflections, scattered rocks and a low escarpment in "
     "haze. 0-1s: low in the grass, blades filling the foreground, the herd silhouetted beyond. "
     "1-4.5s: the camera races forward low between the animals, pillar-like legs sweeping past on "
     "both sides, dust and egrets scattering, and emerges ahead of the herd before rising. "
     "4.5-6.5s: from above it cranes down and pushes in on a single broad footprint pressed into "
     "the dust, its cracked pad pattern filling the frame. 6.5-8s: it holds, a grass blade "
     "springing back at the edge. Never zoom on an animal's face. Mood: mass carried well. "),

    ("s15_c", "VIDEO",
     "A study stage on warm cream paper. Two ghosted white limb-bone outlines are pinned side by "
     "side like specimens: a slender one from a young animal and a dramatically thicker one from "
     "an adult, each in its own hand-inked frame with a blank label box beneath. Between them a "
     "small hand-drawn growth chart of three stacked silhouettes. Props: measuring caliper, "
     "folding rule, two pins and blank framed panels. 0-1s: tight on the slender young bone "
     "outline. 1-4.5s: the camera pulls back and arcs across the stage, the thicker adult bone "
     "swinging into frame and dwarfing the first, the growth chart sliding past beneath. 4.5-6.5s: "
     "it pushes in where the adult bone's shaft is at its thickest, the chalky outline filling the "
     "frame. 6.5-8s: it holds. No text in any label box. Mood: slow tuning over ages. "),

    ("s16_b", "VIDEO",
     "Deep blue-teal open ocean with god rays slanting down. An enormous blue whale glides through "
     "mid-water in slate-blue with a pale mottled belly, throat pleats drawn as long parallel ink "
     "lines, flukes mid-stroke. Around it: a school of hundreds of tiny silver fish, three "
     "dolphins arcing above, drifting krill as thousands of specks, floating kelp fronds and "
     "rising bubble strings. 0-1s: far below the whale looking up, its silhouette against the "
     "bright surface. 1-4.5s: the camera rises fast through the water column toward the animal, "
     "krill and bubbles streaming past, the fish school splitting around the lens, and levels out "
     "alongside the flank. 4.5-6.5s: it pushes in on the throat pleats as they expand, the long "
     "parallel lines widening until they fill the frame. 6.5-8s: it holds, light rippling across "
     "the skin. Mood: effortless mass. "),

    ("s16_c", "VIDEO",
     "Beneath an enormous blue whale in deep blue-teal water. The pale mottled belly fills the "
     "upper frame, flukes sweeping slowly at the edge. Two sets of hand-drawn arrows are laid over "
     "the body in contrasting colours: heavy downward arrows and equally strong upward arrows, "
     "cancelling. Far below, a soft dune seafloor with the half-buried rib cage of a wreck. Bubble "
     "strings rise through the shot. 0-1s: at the seafloor looking up, wreck ribs in the "
     "foreground, the whale a shape far above. 1-4.5s: the camera ascends rapidly through the "
     "water toward the belly, bubbles streaming past, the arrow pairs growing in frame as they "
     "come into alignment. 4.5-6.5s: it pushes in where the upward and downward arrows meet and "
     "cancel, that intersection filling the frame. 6.5-8s: it holds there, light shafting past. "
     "Electric cyan only on the upward arrows. Mood: gravity, switched off. "),

    ("s17_b", "VIDEO",
     "A grassy hillside in warm late afternoon. A colossal humanoid figure in flat ochre stands "
     "motionless, golden light raking across its shoulders, thin warm arrows drawn entering the "
     "skin like absorbed sunlight, faint steam rising. Across the hillside: tall grass as vertical "
     "brush flicks bending in wind, a lone twisted tree, a low stone ruin with a collapsed arch, a "
     "winding dirt path, three sheep and scattered wildflowers. 0-1s: low in the grass, blades "
     "filling the foreground, the figure beyond in gold light. 1-4.5s: the camera flies forward up "
     "the hillside through the grass, past the twisted tree and the stone ruin, and cranes up the "
     "figure's side into the low sun. 4.5-6.5s: it pushes in on the shoulder where the warm arrows "
     "enter the skin, the absorbed light concentrating until it fills the frame. 6.5-8s: it holds, "
     "warm light flaring softly at the edge. Never zoom on the face. Mood: quiet feeding. "),

    ("s17_c", "VIDEO",
     "The same hillside after sunset, deep indigo sky with early stars as tiny ink dots. The "
     "colossal figure stands slumped and grey, its surface matte with hairline cracks spreading "
     "like dried clay, no steam left. Across the hillside: grass now still, the twisted tree in "
     "silhouette, the stone ruin dark, three sheep bedded down, wildflowers closed. 0-1s: wide "
     "from the hill path, the figure a dark shape against the indigo sky. 1-4.5s: the camera "
     "sweeps in a long orbit around the figure, stars wheeling behind it, the ruin and the tree "
     "passing in silhouette, arriving close at the shoulder. 4.5-6.5s: it pushes in on the cracked "
     "surface where the hairlines have spread widest, the dry fissure network filling the frame. "
     "6.5-8s: it holds, one last fleck of dust drifting free. Mood: powered down. "),

    ("s18_b", "VIDEO",
     "Dawn over a walled town. A long stone wall runs diagonally across the lower third, its "
     "blocks catching warm rim light, with three tiny watchtowers, a line of banner poles and six "
     "ant-sized figures on the parapet. Below: rooftops with chimney smoke in thin curls, a "
     "windmill, a church spire and orchards in neat rows. The sky fills with pale gold and soft "
     "rose bands. 0-1s: low among the orchard rows, trees receding toward the wall. 1-4.5s: the "
     "camera flies forward over the orchards and the rooftops at speed, chimney smoke streaming "
     "past, and cranes up the wall face to clear the parapet. 4.5-6.5s: it pushes in on a single "
     "banner pole where the cloth lifts in the dawn wind, the fabric filling the frame against the "
     "gold sky. 6.5-8s: it holds there. Warm gold is the only saturated accent. Mood: the morning "
     "after. "),

    ("s18_c", "VIDEO",
     "Wide dawn sky above a distant stone wall. The wall and a colossal humanoid silhouette sit "
     "small along the very bottom edge of the frame, backlit, thin crimson steam curling from the "
     "figure's shoulders. The upper two-thirds is open sky in pale gold and soft rose bands with "
     "three flat stylised clouds and two birds crossing. Layered atmospheric haze separates wall, "
     "figure and sky into clean depth planes. 0-1s: level with the wall walk, the silhouette large "
     "in frame against the sky. 1-4.5s: the camera rises steadily and pulls back, the wall and the "
     "figure shrinking toward the bottom edge as the open sky expands to fill the frame. 4.5-6.5s: "
     "it continues rising into clear sky, the two birds crossing the frame, everything below "
     "reduced to a thin band at the bottom. 6.5-8s: it settles on the open sky, the upper "
     "two-thirds deliberately left clear and empty for an end card. Mood: resolved, a little "
     "hopeful. "),

    ("s04_d", "VIDEO",
     "A clean study stage on warm cream paper. Three hand-inked cubes of increasing size stand in "
     "a row on a ruled ground line, each built from small unit blocks. Beside each, a column of "
     "square tiles for surface area; below each, a stack of round weight discs for mass - the disc "
     "stacks towering far higher than the tile columns by the third cube. A tiny stick-drawn "
     "figure stands at the base of the first. Props: set square, dividers, coiled tape, blank "
     "framed panels. 0-1s: at the ruled ground line beside the smallest cube, the tiny figure in "
     "frame. 1-4.5s: the camera tracks sideways along the row at speed, each cube swelling as it "
     "passes, the weight stacks climbing out of frame while the tile columns barely grow. "
     "4.5-6.5s: it cranes up alongside the tallest disc stack and pushes in on its topmost disc, "
     "the tile column tiny far below. 6.5-8s: it holds. Electric cyan only on the discs. No "
     "numbers anywhere. Mood: the gap made visible. "),

    ("s07_d", "VIDEO",
     "A hand-drawn stage on cream paper. A single giant humanoid outline is packed to bursting "
     "with warm-orange heat particles, its skin contour a closed ink loop. A thin ring of escape "
     "arrows around the outline is far too sparse; several are bent back on themselves. Beside it "
     "a mercury thermometer, its column climbing steadily. Props: hand fan, radiator fin diagram, "
     "cup with steam curls, blank framed panels. 0-1s: tight on the thermometer bulb at the bottom "
     "of its column. 1-4.5s: the camera rises fast alongside the thermometer as the column climbs "
     "with it, then arcs away across the stage toward the packed giant outline, particles churning "
     "inside. 4.5-6.5s: it pushes through the skin contour into the interior and stops among the "
     "densest particles pressing against the inner wall. 6.5-8s: it holds inside the packed mass. "
     "Warm orange only. No people, no faces. Mood: the needle does not stop. "),

    ("s08_d", "VIDEO",
     "An empty stone plaza at dusk seen from high above, painted through a hand-brushed thermal "
     "filter. A colossal figure stands at the centre, its body glowing from violet at the limbs to "
     "intense white at the core. The paving around it is heat-darkened in a widening ring, seams "
     "glowing, with a toppled cart, blackened banner poles, a bell on its side and steaming "
     "puddles. 0-1s: full top-down over the plaza, the figure a bright shape in a dark ring. "
     "1-4.5s: the camera falls vertically toward the plaza, rotating as it drops, the heat ring "
     "spreading across the frame, and levels out at stone height at the ring's edge. 4.5-6.5s: it "
     "pushes forward along a glowing seam between paving stones toward the figure's feet until the "
     "blazing crack line fills the frame. 6.5-8s: it holds, pale flecks drifting up. Never zoom on "
     "the face. Mood: the ground remembers. "),

    ("s10_d", "VIDEO",
     "Deep inside a porous foam structure, the chambers here far larger and more open. Thin "
     "fibrous walls curve away in every direction, backlit so their fibre networks glow. Drifting "
     "spherical voids catch pale light, fine strands stretch between walls, and faint warm steam "
     "threads through the cavities. 0-1s: inside one vast chamber, its curved walls sweeping "
     "around the lens. 1-4.5s: the camera flies a long curving path through the structure, passing "
     "through three successive wall openings, the lattice opening endlessly ahead, light shifting "
     "as it goes. 4.5-6.5s: it slows and pushes in on a junction where four thin walls meet, the "
     "fibre bundle glowing until it fills the frame. 6.5-8s: it drifts there, strands flexing. "
     "Electric cyan only on the glowing junction. Mood: architecture of emptiness. "),

    ("s12_d", "VIDEO",
     "A colossal humanoid figure lands from its kick in a wide cobbled square, ochre and heavy "
     "ink, crimson steam pouring from shoulder vents. Behind it the breached wall gapes, rubble "
     "fanned across the cobbles - hundreds of inked blocks, a bent ladder, torn banners, "
     "splintered planks, roof tiles. Dust hangs in stippled clouds. Two thin ink rings mark the "
     "spread of the shock. 0-1s: low among the rubble looking up at the landing figure through "
     "drifting dust. 1-4.5s: the camera cranes upward and swings in a wide orbit around the "
     "figure, the breach, the rubble fan and the rooftops wheeling past below in strong parallax. "
     "4.5-6.5s: it dives back down and pushes in on a single large stone block rocking to a stop "
     "on the cobbles, dust sliding off its face. 6.5-8s: it holds there. Crimson only on the "
     "steam. Push-in subject is the block, never a person. Mood: the aftermath of speed. "),

    ("s13_d", "VIDEO",
     "A Cretaceous valley at golden hour, wide. A colossal long-necked sauropod stands in profile "
     "in flat olive and warm grey, its neck sweeping across the sky, legs like temple columns "
     "planted straight and vertical. Around it: horsetail reeds, cycads, boulders, driftwood, a "
     "braided river, a flock of pterosaurs, conifer forest and hazy mesas. 0-1s: at ground level "
     "between two of the animal's columnar legs, the body a ceiling overhead. 1-4.5s: the camera "
     "races forward between the legs and out into the open, then cranes up sharply along the flank "
     "and rides the length of the neck toward the head against the gold sky. 4.5-6.5s: it banks "
     "away and pushes in on a single vertical foreleg where it meets the ground, the straight "
     "column of the limb driving into the earth. 6.5-8s: it holds there, dust settling around the "
     "foot. Never zoom on the head. Mood: mass held straight. "),

    ("s16_d", "VIDEO",
     "Open ocean, wide, in deep blue-teal with god rays from a bright surface. An enormous blue "
     "whale glides across the full width of frame in slate-blue, flukes mid-downstroke. Around it: "
     "a school of hundreds of tiny silver fish splitting into two streams, three dolphins arcing, "
     "drifting krill as thousands of specks, kelp fronds, bubble strings, and far below a dune "
     "seafloor with a half-buried wreck rib cage. 0-1s: ahead of the whale as it comes toward the "
     "lens out of the blue gloom. 1-4.5s: the camera flies backward alongside the animal at its "
     "own speed, the full body streaming past, then peels away and rises toward the bright "
     "surface, the whale shrinking below. 4.5-6.5s: it turns at the surface and looks down through "
     "the shafts of light, then pushes in on the rising column of bubbles trailing from the whale "
     "far below. 6.5-8s: it holds on the bubble column. Mood: weightless immensity. "),
]

KIND = {k: t for k, t, _p in SCENES}


def prompt_for(key):
    for k, t, p in SCENES:
        if k == key:
            return f"{p}\n\n{STYLE}"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.keys:
        print(f"{'키':16s} {'종류':6s} 앞머리")
        for k, t, p in SCENES:
            print(f"  {k:16s} {t:6s} {p[:56]}…")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    for k in a.keys:
        p = prompt_for(k)
        if not p:
            print(f"  ★없는 키 {k}"); continue
        f = os.path.join(OUT_DIR, f"{k}.txt")
        open(f, "w", encoding="utf-8").write(p)
        print(f"  {k} -> {f}  ({len(p.split())}단어)")


if __name__ == "__main__":
    main()
