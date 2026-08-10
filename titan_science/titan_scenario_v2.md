# 진격의 거인의 과학 — 시나리오 v2 (8분 / 18씬)

> **프로젝트** `titan_science` (CA-002) · **길이** 8분 00초(480초) · **씬** 18개
> **제목(확정안)** 60m 거인은 왜 '스티로폼'보다 가벼워야만 했나 — 물리학이 밝힌 충격적 설계
> **타깃** 15~30세 · 애니 팬 + 과학 호기심층
> **구조** ★**반전 선제시**(Reverse Hook) — 결론을 30초 안에 던지고, 나머지 7분 30초로 그 이유를 파고든다.
>
> ⚠️ **브랜드 금지** — 화면·내레이션·프롬프트 어디에도 특정 교육채널 이름/로고/워터마크를 넣지 않는다.
>    참고한 것은 **연출 문법**(스케일 대비 컷, 크림 배경, 붓펜 외곽선)뿐이다.
> ⚠️ **우하단 Veo 워터마크** — 생성 후 같은 크기 로고로 덮는다. W24R에서 확립한 방식을 그대로 쓴다
>    ([[youtube-studio-editor-ui-changed]] 아님 — `hangeul_birth_vowels/compile_stickman.draw_wm_cover` 참조).

---

## 0. 아트 디렉션 (전 씬 공통 · 프롬프트 접두)

모든 Flow 프롬프트 앞에 **이 블록을 그대로** 붙인다. 씬마다 바꾸지 않는다 — 톤이 흔들리면 8분이 산만해진다.

```
STYLE LOCK:
2D hand-drawn cartoon animation, warm cream paper background (#F7EFDC), thick uneven
hand-inked brush outlines that vary from 3px to 8px in width with slight wobble, flat
gouache color fills with visible watercolor paper grain, soft cel shading with no
gradients on characters, muted earth palette (sand, terracotta, olive, dusty teal)
punched by ONE high-saturation accent per shot (crimson steam / electric cyan diagram),
subtle paper texture over the whole frame, no photorealism, no 3D render look,
no lens flare, no text or letters anywhere in the frame, no logos, no watermarks.
16:9, cinematic composition, generous negative space.
```

**연출 문법 3가지 (레퍼런스 역공학 결과)**
1. **스케일 대비 컷** — 와이드(전신) ↔ 극단 클로즈업(발목·뼈·단면)을 번갈아 친다. 거대함은 '큰 것을 보여줘서'가 아니라 **작은 것 옆에 둬서** 전달된다.
2. **한 컷 한 개념** — 한 화면에 두 개를 설명하지 않는다.
3. **도표는 손그림처럼** — 수식·그래프도 같은 붓펜 선으로. 깔끔한 벡터 UI 금지.

**금지**
- 프레임 안 텍스트/숫자/수식 문자 — 전부 후반 합성으로 올린다(다국어 대응 때문).
- 사실적 유혈·신체 절단 묘사. 거인 부위는 **증기 뿜는 무기물**처럼 처리.

---

## 0-B. 카메라 규격 ★사장님 지시(2026-08-10)

> "전체를 떨거나 번쩍이지 말고, 손 하나 나뭇잎 하나 까딱이는 정도의 미미한 동영상은 하지 마라.
>  다이나믹하게, 지미집 쓴 것처럼. 버티컬 뷰도 줌인도 다이나믹하게.
>  **사람은 줌인하지 말고, 포인트 객체와 주인공이 되는 물체를 줌인**해라."

**8초 3단 구성 — 모든 클립이 지켜야 한다**

| 구간 | 할 일 |
|---|---|
| 0.0~1.0초 | 시작 앵글 제시 |
| 1.0~4.5초 | **대변화** — 카메라가 공간을 가로지르거나, 대상이 폭발적으로 바뀐다 |
| 4.5~8.0초 | 새 앵글에 안착. 다음 컷으로 넘길 여백 |

**쓸 카메라 (지미집 = 크레인 기준)**
- `CRANE UP` 지면에서 30m 위로 솟구치며 상승, 동시에 피사체 쪽으로 기울임
- `CRANE DOWN` 조감에서 지면으로 급강하해 로우앵글로 꽂힘
- `ORBIT` 대상 중심으로 90~180도 궤도 선회
- `VERTICAL TOP-DOWN → GROUND` 완전 탑다운에서 수직으로 떨어져 지면 시점으로 전환
- `PUSH-THROUGH` 물체 표면을 뚫고 내부로 진입 (단면·현미경 진입에 사용)
- `WHIP` 빠른 횡이동 후 급정지 (액션 임팩트에만)

**줌인 대상 규칙**
- ✅ 줌인해도 되는 것 — 뼈 단면, 골절선, 큐브, 저울 바늘, 발자국 크레이터, 폼 기공, 수증기 밸브, 기낭 벌집, 부력 화살표, 굳어가는 균열
- ❌ 줌인 금지 — 사람 얼굴, 인물 상반신, 눈동자 클로즈업

**절대 금지**
- 화면 전체 흔들림(shake), 번쩍임(flash/strobe)
- 손끝·나뭇잎·머리카락만 살짝 움직이는 미세 모션 — **8초를 쓰고 아무 일도 안 일어나는 클립은 만들지 않는다**
- 고정 카메라(locked-off). 도표 씬조차 카메라가 움직인다.


## 0-C. 생성 모델 방침 ★사장님 지시(2026-08-10)

> "이 두 개만 veo quality 쓰고 이후부터는 veo 3.1 lite 만 쓴다. 토큰이 모자랄 거야."

| 대상 | 모델 |
|---|---|
| S5 · S17 (재시도분) | Veo 3.1 **Quality** |
| 그 밖의 전부 | Veo 3.1 **Lite** (기본값) |

`flow_make_titan.py` 의 기본값이 Lite 다. Quality 가 필요할 때만 환경변수로 올린다.
```
python run_titan_one_by_one.py <키>                    # Lite
$env:TITAN_MODEL='Veo 3.1 - Quality'; python ...      # 예외적으로만
```

★모델을 안 고르면 **오류 없이 240초 시간초과**로 실패한다. 진단은 같은 프롬프트를
STILL 한 장으로 만들어 보는 것 — 되면 모델 문제, 안 되면 프롬프트 문제.


## 0-D. 컷 연결 규격 — Last Image Transition ★사장님 지시(2026-08-10)

> "키프레임을 정해서 하나의 그룹을 만들고, 그 그룹 내에서는 **last image transition** 방식으로 가야 한다.
>  연결해야 하고 동질성이 필요한 곳은 전부 이 기법으로 간다."

**왜 바꿨나** — 처음엔 컷마다 장면을 처음부터 묘사해 독립 생성했다. 그러면 컷마다 그림이
새로 그려져 **같은 성벽·같은 손가락이 매번 다르게** 나오고, 매 컷이 와이드로 시작해
클로즈업으로 끝나 이어 붙이면 계속 튄다. S1 세 컷으로 실측 확인했다(폐기).

**새 방식**

```
씬 = 하나의 그룹
  1번컷(키프레임 기반) ──끝프레임──▶ 2번컷 ──끝프레임──▶ 3번컷 ──▶ 4번컷
```

1. 앞 컷의 **마지막 프레임을 뽑아** 다음 컷의 첫 프레임으로 업로드한다
2. 프롬프트에는 **장면을 다시 묘사하지 않는다** — 그림은 이미지가 결정한다
3. 프롬프트는 **이어받는 카메라 동작**만 쓴다 (60~120단어)
4. 컷의 끝은 완결시키지 않고 **다음 컷에 넘길 상태**로 둔다

**모션 프롬프트 뼈대**

```
Continue directly from this exact frame. Keep the drawing style, colours, line work and
every object precisely as they are - do not redraw, do not restyle, do not change the
palette. No text anywhere. The only thing that changes is the camera and <움직이는 것>.

0-1s: <이 화면 그대로에서 출발>
1-4.5s: <카메라 대이동 — 크레인/궤도/관통/낙하>
4.5-8s: <다음 컷에 넘길 자리에 안착>

Continuous camera travel, strong parallax, no static framing, no screen shake, no
flashing. Never zoom on a face.
```

**적용 범위** — 한 씬 안의 2·3·4번 컷 전부. 씬과 씬 사이는 장면이 바뀌므로 적용하지 않는다.

---

## 1. 씬 구성표

| # | 파트 | 초 | 누적 | 한 줄 |
|---|---|---|---|---|
| S1 | 반전 선제시 | 22 | 0:22 | 60m 거인이 성벽을 내려다본다 |
| S2 | 반전 선제시 | 24 | 0:46 | 잘린 팔이 종이처럼 튕긴다 — "이건 스티로폼보다 가볍다" |
| S3 | 스케일의 저주 | 26 | 1:12 | 1638년, 갈릴레오가 이미 계산해 둔 것 |
| S4 | 스케일의 저주 | 28 | 1:40 | 10배 커지면 면적 100배, 무게 1,000배 |
| S5 | 스케일의 저주 | 30 | 2:10 | 첫 걸음에 허벅지뼈가 부서진다 |
| S6 | 스케일의 저주 | 26 | 2:36 | 48톤 — 전차 한 대를 다리 둘로 |
| S7 | 열역학 지옥 | 28 | 3:04 | 열은 부피로 늘고 방출은 면적으로만 |
| S8 | 열역학 지옥 | 30 | 3:34 | 걷기 전에 스스로 익는다 |
| S9 | 작가의 답 | 26 | 4:00 | 한지 조에가 거인 팔을 걷어찬다 |
| S10 | 작가의 답 | 30 | 4:30 | 현미경 속 — 구멍투성이 유기 폼 |
| S11 | 작가의 답 | 26 | 4:56 | 고래 18마리 부피에 무게는 몇 톤 |
| S12 | 작가의 답 | 32 | 5:28 | 가벼워서 더 빠르고, 빨라서 더 파괴적 |
| S13 | 현실의 거인 | 28 | 5:56 | 80톤 공룡의 뼈는 비어 있었다 |
| S14 | 현실의 거인 | 26 | 6:22 | 다리를 신전 기둥처럼 세운다 |
| S15 | 현실의 거인 | 26 | 6:48 | 코끼리는 자랄수록 뼈가 굵어진다 |
| S16 | 현실의 거인 | 28 | 7:16 | 190톤 대왕고래 — 바다가 중력을 끊는다 |
| S17 | 마무리 | 24 | 7:40 | 햇빛으로 움직이고 밤엔 굳는 이유 |
| S18 | 마무리 | 20 | 8:00 | 물리학과 상상력이 만나는 자리 |

---

## 2. 씬별 상세

---

### S1 — 성벽 위의 그림자 (0:00~0:22 · 22초 · 3클립)

**KO** 높이 50미터의 성벽. 100년 동안 단 한 번도 뚫린 적이 없었습니다. 그런데 그날, 성벽 너머로 손가락이 올라왔습니다. 사람의 손 모양을 한, 폭이 4미터짜리 손가락이.

**EN** A wall fifty meters high. For a hundred years, nothing had ever breached it — not an army, not a siege, not once. And then one morning, fingers appeared over the top. Human-shaped fingers, cracked and steaming, each one four meters wide.

**CAMERA** `CRANE UP` — 개미 시점 지면에서 출발해 성벽 면을 타고 50m 수직 상승, 정상에서 손가락과 눈높이가 맞는 순간 급정지. 줌인 대상은 **손가락 관절의 갈라진 피부**(사람 얼굴 아님).

**FLOW PROMPT**
```
[STYLE LOCK]
Extreme low-angle shot from ground level of a colossal 50-meter-tall dry-stone
defensive wall filling the right two-thirds of the frame. The wall is built from
thousands of individually inked irregular stone blocks in sand and warm grey tones,
with dark mortar lines, patches of olive moss creeping up the lower courses, three
rusted iron ladders bolted to the face, a row of small square watch-slits near the
top, and two tattered crimson banners hanging limp. At the base: a cobbled street
with a wooden handcart tipped over, scattered clay pots, a spilled basket of apples,
a stray dog frozen mid-bark, and seven tiny townspeople rendered as simple silhouettes
looking upward — they are barely 1/40th the wall's height to sell the scale. Above the
wall rim, four enormous humanoid fingers with cracked steaming skin curl over the
edge, thin crimson steam wisps rising from the knuckles into a pale cream sky with
three flat stylized clouds and a flock of tiny birds scattering.

CAMERA (fill all 8 seconds):
0.0-1.0s  Ant-level on the cobbles, lens nearly touching the ground, the wall rearing up
          and running out of frame at the top.
1.0-4.5s  AGGRESSIVE CRANE UP — the camera launches vertically up the wall face at speed,
          stone courses streaking past, ladders and watch-slits whipping down out of frame,
          the town below shrinking to a toy model.
4.5-6.5s  Arrive level with the wall rim, TILT to meet the four colossal fingers, then
          PUSH IN hard on the cracked steaming skin of one knuckle until the fissures
          fill the frame.
6.5-8.0s  Settle there, steam drifting across the lens.
No camera shake, no strobe, no micro-motion-only shots. Never zoom on human figures —
the only push-in target is the knuckle skin. Mood: dread, vertigo, held breath.
```

---

### S2 — 튕기는 팔 (0:22~0:46 · 24초 · 3클립)

**KO** 그런데 이상한 일이 벌어집니다. 이 거대한 팔을 잘라내면, 툭 차는 것만으로 종이 상자처럼 튀어 오릅니다. 60미터짜리 괴물이, 스티로폼보다 가볍습니다. 오늘 이야기는 여기서 시작합니다. 왜 이 거인은 **가벼워야만 했을까요?**

**EN** But here's the strange part, and it's the part almost nobody talks about. Cut off one of those massive arms, and a single kick sends it bouncing across the mud like an empty cardboard box. A sixty-meter monster, lighter than styrofoam. That's where today's story starts — not with how terrifying this creature is, but with a question. Why did this giant *have* to be light?

**CAMERA** `ORBIT → CRANE UP` — 팔 주위를 90도 선회하다 발차기 임팩트에 맞춰 급상승, 튕겨 오르는 **거인 팔**을 따라 붙는다. 사람 얼굴 줌인 없음.

**FLOW PROMPT**
```
[STYLE LOCK]
Medium shot in a muddy field at dusk. A severed titan forearm the size of a bus lies
on churned earth — pale ochre skin with a dry cracked surface like old ceramic, deep
ink outlines, faint crimson steam curling off the cut end which is sealed and glassy,
not bloody. A small scientist figure in a tan field coat, goggles pushed up into messy
brown ponytail hair, leather boots and a satchel, plants one foot and kicks the huge
forearm; the arm tips up weightlessly at a comic angle, one end lifting off the ground,
motion arcs drawn as three thin hand-inked speed lines. Surrounding clutter to sell the
scene: two wooden supply crates, a coil of rope, three iron stakes with red pennants
marking a survey grid, a tipped bucket, a folding stool with a clipboard on it, a lantern
on a pole, and four uniformed onlookers in the mid-distance with jaws dropped. Puddles
reflect the cream sky. One high-saturation crimson accent on the pennants and steam.
CAMERA (fill all 8 seconds):
0.0-1.0s  Low three-quarter view along the length of the severed forearm, mud in the
          foreground, the scientist's boot entering frame edge.
1.0-4.5s  ORBIT — the camera swings 90 degrees around the forearm at speed while the kick
          lands; at the moment of contact it CRANES UP and RISES with the tumbling limb,
          the field, crates and survey pennants wheeling away below.
4.5-6.5s  PUSH IN on the huge forearm itself as it hangs weightless at the top of its arc,
          filling the frame, steam trailing off the sealed cut end.
6.5-8.0s  Fall back with it toward the mud and settle.
No shake, no strobe. Do not zoom on the scientist's face — the push-in subject is the
floating forearm. Mood: absurd, delightful surprise.
```

---

### S3 — 1638년의 예언 (0:46~1:12 · 26초 · 3클립)

**KO** 사실 이 답은 만화가 나오기 삼백팔십 년 전에 이미 나와 있었습니다. 1638년, 갈릴레오 갈릴레이. 그는 마지막 책에서 이렇게 썼습니다. "거인은 존재할 수 없다. 자기 무게에 스스로 무너지기 때문이다."

**EN** The answer was written three hundred and eighty years before the manga ever existed. The year is 1638. Galileo Galilei, old and going blind, publishes his final book. And buried in it is a warning about giants: they cannot exist. Scale a body up far enough, he wrote, and it will collapse under its own weight.

**CAMERA** `PUSH-THROUGH → CRANE DOWN` — 창밖 밤하늘에서 서재 안으로 돌진해 들어와 책상 위로 급강하, **펼쳐진 뼈 도해**로 꽂힌다.

**FLOW PROMPT**
```
[STYLE LOCK]
Interior of a 17th-century study at night, warm candlelight. An elderly scholar with a
long white beard, small round spectacles, dark scholar's robe and skullcap sits at a
heavy oak desk, quill in hand, leaning over an open folio. On the desk, densely arranged:
an open book showing two hand-drawn bone diagrams side by side (one small, one grotesquely
thick), a brass candlestick with three lit candles and dripping wax, an hourglass, a pair
of brass dividers, a wooden ruler, a stack of five leather-bound books, a rolled parchment
tied with twine, an inkwell with two spare quills, a small terrestrial globe on a stand,
and a scattering of loose sketch papers. Behind him: floor-to-ceiling shelves crammed with
books and rolled charts, a brass telescope on a tripod aimed at a small arched window
showing a deep indigo night sky with stars, and a hanging astrolabe. Dust motes drift in
the candle glow. Warm amber is the single saturated accent against the cream palette.
CAMERA (fill all 8 seconds):
0.0-1.0s  Outside the arched window at night, stars and rooftops, the warm candlelit study
          glowing through the glass.
1.0-4.5s  PUSH-THROUGH — the camera flies in through the window frame into the room,
          sweeping past the telescope and the hanging astrolabe, shelves of books
          streaking by on both sides.
4.5-6.5s  CRANE DOWN hard onto the desk surface and PUSH IN on the open folio until the two
          hand-drawn bone diagrams fill the frame, candle flames flaring at the edges.
6.5-8.0s  Hold on the diagram, dust motes drifting through the light.
No shake. Do not zoom on the scholar's face — the push-in subject is the bone diagram.
Mood: quiet, weighty revelation.
```

---

### S4 — 제곱과 세제곱 (1:12~1:40 · 28초 · 4클립)

**KO** 원리는 단순합니다. 키가 두 배가 되면 뼈의 단면적은 네 배가 됩니다. 그런데 몸무게는 여덟 배가 됩니다. 열 배로 키우면? 뼈는 백 배 튼튼해지지만, 몸은 천 배 무거워집니다. 힘은 제곱으로, 무게는 세제곱으로 늘어납니다. 이 격차가 벌어질수록, 몸은 자기 자신을 감당하지 못합니다.

**EN** The logic is simple enough to do on your fingers. Double the height, and the bone's cross-section — the part that actually carries the load — grows four times. But the body's weight grows eight times. Now scale it ten times. The bone gets a hundred times stronger, while the body gets a thousand times heavier. Strength scales with the square. Weight scales with the cube. And the wider that gap grows, the less a body can carry itself.

**CAMERA** `FLY-THROUGH` — 큐브 사이를 통과하며 후퇴, 마지막에 **무게추 더미**로 급강하 줌인. 고정 카메라 아님.

**FLOW PROMPT**
```
[STYLE LOCK]
Clean diagram stage on cream paper. Three hand-inked cubes of increasing size stand in a
row on a simple ruled ground line: a small cube, a medium cube, and a large cube, each
drawn with wobbly brush outlines and flat sand-colored fills with visible paper grain.
Each cube is stacked internally from tiny unit blocks so the viewer can count the volume
growth. Beside each cube, a hand-drawn column of small square tiles represents its
cross-sectional area, and below each, a hand-drawn stack of round weights represents its
mass — the weight stacks grow dramatically faster than the tile columns. A tiny stick-drawn
human figure stands at the base of the first cube for scale and looks progressively more
dwarfed. Additional hand-drawn props scattered around the stage: a wooden set square, a
pair of dividers, a coiled measuring tape, and three loose sketch sheets pinned at the
corners. Everything rendered like an illustrator's ink-and-gouache notebook page, never
like clean vector UI. Electric cyan is the single saturated accent used only on the
weight stacks.

CAMERA (fill all 8 seconds):
0.0-1.0s  Tight on the smallest cube, the tiny stick figure beside it, low angle.
1.0-4.5s  FLY-THROUGH — the camera pulls backward fast, threading between the cubes as
          each one erupts to its next size in a hard stepped beat; the unit blocks stack
          up and the weight piles slam down, the frame widening violently to keep up.
4.5-6.5s  Arrive at a high three-quarter angle, then CRANE DOWN and PUSH IN on the tallest
          stack of round weights until it fills the frame and dwarfs the tile column
          beside it.
6.5-8.0s  Settle, the stick figure now a speck at the bottom edge.
No shake, no strobe, never a locked-off frame. Push-in subject is the weight stack.
Mood: crisp, escalating, satisfying logic.
```

---

### S5 — 첫 걸음 (1:40~2:10 · 30초 · 4클립)

**KO** 15미터짜리 거인이 사람과 같은 밀도라면 어떻게 될까요. 한 발을 내딛는 순간, 허벅지뼈에 걸리는 압력이 뼈가 견딜 수 있는 한계를 넘어섭니다. 걷는 게 아닙니다. 무너지는 겁니다. 유전학자 홀데인은 이걸 한 문장으로 정리했습니다. "크기마다 알맞은 형태가 따로 있다."

**EN** So what happens to a fifteen-meter titan built at human density? Watch the first step. The instant its weight shifts onto one leg, the stress inside that thigh bone climbs past the limit that bone can physically survive. It isn't walking anymore. It's collapsing. The geneticist J.B.S. Haldane summed this up in a single line that has never been improved on: for every size, there is a fitting form.

**CAMERA** `CRANE DOWN → PUSH-THROUGH` — 거인 어깨 높이에서 다리를 따라 급강하한 뒤 피부를 뚫고 뼈 속으로 진입, **골절선**을 정면으로 본다.

**FLOW PROMPT**
```
[STYLE LOCK]
Split-feel composition. Left two-thirds: a 15-meter humanoid titan mid-stride on a
cobbled plaza, drawn in flat ochre with heavy ink contours, muscles indicated by simple
brush strokes, faint crimson steam at the shoulders, expression blank and unsettling.
Right third: the same leg shown as a hand-inked anatomical cutaway — the femur drawn in
chalky bone-white with visible internal trabecular lattice, and a cluster of short
crimson stress lines radiating from the bone's midshaft where a jagged fracture is
beginning to spider outward. Ground details for scale and clutter: cracked paving stones
radiating fracture lines from the footfall, a toppled market stall with striped awning,
scattered cabbages and clay jars, a broken cart wheel, two fleeing citizens rendered
tiny, a startled cat, and a plume of dust drawn as soft stippled clouds. Crimson is the
only saturated accent, used exclusively on the stress lines.

CAMERA (fill all 8 seconds):
0.0-1.0s  High angle at the titan's shoulder height, the plaza and market stalls far below.
1.0-4.5s  CRANE DOWN — the camera plunges vertically alongside the titan's body as the leg
          swings through the stride, paving stones rushing up, the toppled stall and
          fleeing citizens whipping past the edges of frame.
4.5-6.5s  PUSH-THROUGH — at the thigh the camera drives straight through the skin surface
          into the anatomical cutaway and stops nose-to-nose with the femur as the jagged
          fracture spiders outward, crimson stress lines snapping open toward the lens.
6.5-8.0s  Hold on the splitting bone, dust sifting down through the frame.
No shake. Do not zoom on any human or the titan's face — the push-in subject is the
fracturing femur. Mood: brutal physics, inevitability.
```

---

### S6 — 48톤 (2:10~2:36 · 26초 · 3클립)

**KO** 숫자로 보면 더 분명합니다. 15미터 거인의 몸무게는 약 48톤. 주력 전차 한 대와 같습니다. 전차는 무한궤도로 무게를 땅에 넓게 펴서 버팁니다. 거인에게는 발바닥 두 개뿐입니다.

**EN** And the numbers only make it worse. A fifteen-meter titan at human density weighs about forty-eight tons — the same as a main battle tank. But look at how a tank carries that load. Two long tracks, spreading the weight across meters of ground. The titan has two footprints. That's the entire contact patch.

**CAMERA** `TOP-DOWN → VERTICAL DROP` — 완전 조감에서 수직 낙하해 지면 시점으로, **발자국 크레이터**를 궤도 자국과 나란히 놓고 줌인.

**FLOW PROMPT**
```
[STYLE LOCK]
Wide comparison shot on a dusty parade ground. On the left, a hand-inked military tank
in olive drab with wide continuous tracks, riveted armor plates, a long barrel, stowage
boxes, spare track links on the hull, and an antenna — its tracks pressing shallow even
grooves into the dirt. On the right, the bare lower legs and feet of a colossal humanoid
figure in pale ochre, the two soles pressing deep dark craters into the same ground with
radiating cracks and sprays of dirt clods. Between them, a small hand-drawn balance scale
tipping, with a stack of round weights on one pan. Environmental clutter: sandbag walls,
three wooden ammunition crates, a fuel drum, a leaning signpost, tire ruts, tufts of dry
grass, a windsock on a pole, and four tiny soldier silhouettes for scale standing near
the tank's tracks. Dusty haze in the background with a low cream horizon. Single
saturated accent: a crimson stripe on the windsock.

CAMERA (fill all 8 seconds):
0.0-1.0s  Full TOP-DOWN bird's eye over the parade ground: the tank and the two colossal
          feet read as flat shapes on the dirt, sandbags and crates arranged around them.
1.0-4.5s  VERTICAL DROP — the camera falls straight down out of the top-down view, rotating
          as it goes, and levels out at ground height between the tank tracks and the
          titan's soles; dust kicks past the lens as it arrives.
4.5-6.5s  Track sideways at ground level and PUSH IN on the deep cratered footprint, its
          radiating cracks and thrown clods filling the frame, the tank's shallow track
          groove visible small in the background for contrast.
6.5-8.0s  Hold, dirt still trickling into the crater.
No shake. Push-in subject is the footprint crater. Mood: concrete, undeniable.
```

---

### S7 — 표면적의 배신 (2:36~3:04 · 28초 · 4클립)

**KO** 그런데 뼈보다 먼저 무너지는 게 있습니다. 체온입니다. 몸이 열을 만드는 건 부피입니다. 세제곱으로 늘어납니다. 몸이 열을 버리는 건 피부, 즉 면적입니다. 제곱으로만 늘어납니다. 커질수록 만드는 열은 폭증하는데, 버릴 통로는 상대적으로 좁아집니다.

**EN** But something fails before the bones ever do. Body heat. Heat is produced by volume, by every cell in the body burning fuel — and volume scales with the cube. Heat escapes through skin, through surface area — and that scales only with the square. So the bigger you get, the more heat you make, and the narrower the exit becomes. The furnace grows. The chimney doesn't.

**CAMERA** `ORBIT → PUSH-THROUGH` — 두 몸 사이를 180도 선회하다 거인 몸통 안으로 뚫고 들어가 **갇힌 열 입자 덩어리**로 줌인.

**FLOW PROMPT**
```
[STYLE LOCK]
Hand-drawn explanatory stage on cream paper. Two simplified humanoid body outlines stand
side by side, drawn only as thick ink contours with translucent sand fill: a small one on
the left, a giant one on the right. Inside each body, dozens of tiny round heat particles
in warm orange are drawn as loose ink circles — the small body holds a handful, the giant
body is densely packed to bursting. Short arrows drawn as thin brush strokes escape
through the skin outline, but far too few on the giant. Around the giant, the escaping
arrows are choked and curl back inward. Supporting hand-drawn props on the stage: a
mercury thermometer with a rising column, a small hand fan, a stylized radiator fin
diagram, a cup with steam curls, and three annotation frames left deliberately empty for
later text overlay. Ground shadow drawn as a single soft brush smear. Warm orange is the
only saturated accent.

CAMERA (fill all 8 seconds):
0.0-1.0s  Tight on the small body outline, its few heat particles drifting calmly.
1.0-4.5s  ORBIT — the camera swings 180 degrees around behind both figures and back, and as
          it comes around the giant body it RUSHES toward it while heat particles multiply
          explosively inside, escape arrows choking and curling back at the skin line.
4.5-6.5s  PUSH-THROUGH the giant's outline into its interior and PUSH IN on the densest
          knot of trapped orange particles churning against the inner wall.
6.5-8.0s  Hold inside the packed mass, particles jostling with nowhere to go.
No shake, no strobe, never locked-off. Push-in subject is the trapped particle mass.
Mood: mounting pressure, claustrophobia.
```

---

### S8 — 스스로 익는다 (3:04~3:34 · 30초 · 4클립)

**KO** 계산 결과는 잔인합니다. 인간과 같은 대사율을 가진 15미터 거인의 몸속 온도는 섭씨 200도를 넘어섭니다. 단백질이 응고되는 온도의 세 배입니다. 이 거인은 적을 만나기 전에, 자기가 만든 열에 익어버립니다. 걷다가 뼈가 부러지거나, 서 있다가 삶아지거나. 물리학은 두 가지 죽음만 허락했습니다.

**EN** Run the numbers and the result is merciless. A fifteen-meter titan with a human metabolic rate would drive its internal temperature past two hundred degrees Celsius — roughly three times the point where the proteins in a body cook solid. It would never reach an enemy. It would never even finish crossing the field. It would cook, standing there, in heat of its own making. Snap your bones walking, or boil standing still. Physics offered exactly two deaths, and no third option.

**CAMERA** `CRANE UP` — 발밑에서 거인 몸을 타고 30m 수직 상승, 목덜미 **수증기 분출 밸브**로 돌진 줌인. 눈동자 클로즈업은 쓰지 않는다(사람 줌인 금지).

**FLOW PROMPT**
```
[STYLE LOCK — but shift palette to thermal]
Full-body shot of a 15-meter humanoid titan standing in an empty stone plaza at dusk,
rendered as if seen through a hand-painted thermal imaging filter: the body glows in
layered bands of deep violet at the extremities through orange in the torso to searing
white-yellow at the core, all painted with visible brush texture and ink contours rather
than digital gradients. Heat shimmer drawn as wavering vertical ink lines rising off the
shoulders and skull. Thick crimson steam pours from the nape and the mouth. The stone
plaza beneath is scorched in a widening ring, with paving stones cracked and glowing at
the seams, small fires on a toppled wooden cart, blackened banner poles, a melted iron
bell lying on its side, and puddles boiling into steam. Background: silhouetted rooftops
and a dark violet sky with ash flakes drifting. In the final beat, cut to an extreme
close-up of the titan's eye — the iris a boiling white-hot disc with tiny steam curls at
CAMERA (fill all 8 seconds):
0.0-1.0s  Ground level between the titan's scorched feet, cracked glowing paving stones
          filling the foreground, the body towering away into heat shimmer.
1.0-4.5s  CRANE UP — the camera rockets vertically up the front of the body, thermal bands
          sliding from violet through orange to searing white as it climbs, heat-shimmer
          lines and ash flakes streaming past the lens.
4.5-6.5s  At shoulder height it BANKS around to the nape and CHARGES IN on the steam vents
          there, thick crimson jets blasting toward the camera until they fill the frame.
6.5-8.0s  Hold in the steam, the glowing cracked skin barely visible through it.
No shake, no strobe. Do not zoom on the face or eye — the push-in subject is the nape
steam vent. Mood: horrifying, beautiful.
```

---

### S9 — "이상하게 가볍다" (3:34~4:00 · 26초 · 3클립)

**KO** 그런데 원작자는 이 문제를 몰랐던 게 아닙니다. 알고 있었고, 답을 준비해 뒀습니다. 작중에서 연구자 한지 조에는 거인의 잘린 부위를 조사하다가 소리칩니다. "이상해. 너무 가벼워!" 이 한 마디가 모든 물리 문제를 한 번에 풀어냅니다.

**EN** But the author knew about every bit of this. He knew — and he had an answer ready long before anyone asked the question. In the story, a researcher is examining a severed titan limb, expecting tons of dead weight, and instead shouts a single line: *it's strange — it's far too light!* That one sentence, thrown away in a panel, quietly solves every physics problem we just watched pile up.

**CAMERA** `CRANE DOWN → PUSH IN` — 텐트 천장에서 급강하해 표본 팔을 스쳐 지나가고, **저울 바늘**로 돌진 줌인. 연구자 얼굴은 줌인하지 않는다.

**FLOW PROMPT**
```
[STYLE LOCK]
Interior of a canvas field research tent, afternoon light glowing through the fabric.
A scientist with messy brown hair tied back, round goggles pushed onto the forehead, a
stained tan work coat with rolled sleeves, and ink-smudged hands stands wide-eyed with
both arms thrown up in astonishment. In front of her, a huge pale-ochre titan forearm
segment rests on a reinforced wooden trestle table that is barely bowing under it —
visibly, absurdly, not enough. Dense supporting detail: a large hanging spring scale
whose needle sits shockingly low, a chalkboard covered in hand-drawn anatomical sketches
and blank annotation boxes, glass specimen jars on a shelf, a brass microscope, coils of
rope, a stack of leather notebooks, scattered quills and an overturned inkpot, a lantern
hanging from the ridge pole, two folding stools, a bucket of water, a rack of sample
tubes, and a canvas flap tied open showing a sliver of muddy camp outside with two
uniformed figures. Faint crimson steam still curls from the specimen. Crimson is the
single saturated accent.

CAMERA (fill all 8 seconds):
0.0-1.0s  High under the tent ridge pole looking down, the whole cluttered workspace and
          the huge specimen laid out below.
1.0-4.5s  CRANE DOWN — the camera drops fast through the tent volume, skimming over the
          specimen forearm along its length, the trestle table, jars, microscope and
          notebooks sweeping past underneath.
4.5-6.5s  It banks up and CHARGES IN on the hanging spring scale, the needle sitting
          absurdly low, the dial filling the frame as it swings and settles.
6.5-8.0s  Hold on the needle, the scientist's raised arms visible only as blurred shapes
          at the frame edge.
No shake. Do not zoom on her face — the push-in subject is the scale dial and needle.
Mood: eureka, comic disbelief.
```

---

### S10 — 구멍투성이 몸 (4:00~4:30 · 30초 · 4클립)

**KO** 거인의 몸을 현미경으로 들여다보면 답이 보입니다. 근육이 빽빽하게 들어찬 게 아니라, 무수한 공기 방울로 채워진 다공성 구조입니다. 스티로폼, 식빵, 그리고 뼛속 해면골이 쓰는 것과 같은 방식입니다. 부피는 그대로 두고 밀도만 덜어내는 것. 자연이 이미 수억 년 전에 찾아낸 해법입니다.

**EN** Put titan tissue under a microscope and the answer is right there. It isn't packed solid with muscle at all — it's a porous structure, riddled with air pockets, walls thin as paper. It's the same trick used by styrofoam. By a loaf of bread. And by the spongy bone sitting inside your own skeleton right now. Keep the volume, delete the density. Nature worked this out hundreds of millions of years ago.

**CAMERA** `PUSH-THROUGH ×3` — 피부를 뚫고 폼 내부로 관통 비행, 기공 사이를 유영하며 **기공 벽**을 통과해 더 깊이 들어간다.

**FLOW PROMPT**
```
[STYLE LOCK]
A three-stage magnification journey rendered as hand-inked illustration. Foreground
layer: a patch of pale ochre titan skin with dry ceramic-like cracks. Middle layer: the
same patch magnified into a lattice of irregular chambers separated by thin fibrous
walls, drawn with wobbly brush outlines and translucent sand fills, hundreds of round and
polygonal air pockets of varying size. Deep layer: inside the foam, drifting spherical
voids catch pale light, thin strands stretch between chamber walls like the inside of a
sea sponge, and faint warm steam wisps thread through the cavities. Beside the main
journey, three small hand-drawn comparison vignettes are arranged like specimens pinned
on a notebook page: a torn slice of bread showing its crumb, a broken block of white foam
showing its bubbles, and a cutaway of spongy bone showing its trabecular lattice — each
in its own hand-inked frame with an empty label box beneath for later text. Scattered
notebook props: a magnifying lens, a scalpel, two pins, a specimen slide. Electric cyan
is the single saturated accent, used only on the deepest cavity highlights.

CAMERA (fill all 8 seconds):
0.0-1.0s  Grazing angle skimming across the dry cracked skin surface, the pinned specimen
          vignettes and notebook props sliding past in the periphery.
1.0-4.5s  PUSH-THROUGH — the camera drives into a crack in the skin and keeps going,
          bursting through the first chamber wall into the foam lattice, then through a
          second wall deeper in, cell walls rushing past on all sides like flying through
          a cave system at speed.
4.5-6.5s  In the deepest layer it BANKS between drifting spherical voids and PUSHES IN on
          a single thin fibrous chamber wall until its fibers fill the frame, light
          glowing through from behind.
6.5-8.0s  Drift there, strands flexing, warm steam threading between the cavities.
No shake, no strobe, continuous forward flight — never a static frame. Push-in subject is
the pore wall. Mood: wondrous, scientific intimacy.
```

---

### S11 — 고래 열여덟 마리 (4:30~4:56 · 26초 · 3클립)

**KO** 규모를 실감해 봅시다. 60미터 초대형 거인의 부피는 대왕고래 열여덟 마리와 맞먹습니다. 인간과 같은 밀도였다면 몸무게가 수천 톤이어야 합니다. 그런데 작중에서 이 거인은 성벽 위에 올라서고, 걸어 다니고, 발차기를 합니다. 밀도를 덜어냈다는 뜻입니다. 그것도 아주 많이.

**EN** Let's feel the scale for a second. A sixty-meter colossal titan has roughly the volume of eighteen blue whales stacked together. At human density, that is thousands of tons — a number that simply cannot stand on legs. And yet in the story, this thing climbs onto a wall. It walks. It kicks. Which tells you the density was cut. And cut drastically.

**CAMERA** `FLY-OVER → CRANE UP` — 고래 18마리 위를 낮게 활공해 거인 발치까지 간 뒤 몸을 타고 수직 상승, 마지막에 **저울 빔**으로 급강하 줌인.

**FLOW PROMPT**
```
[STYLE LOCK]
Ultra-wide comparison tableau on a pale cream field with a simple ruled ground line. On
the right, the full standing silhouette of a 60-meter colossal humanoid figure rendered
in flat dark ochre with exposed muscle striations drawn as simple parallel brush strokes,
crimson steam venting from the shoulders and jaw, towering to the top of the frame. On
the left, eighteen blue whales drawn in dusty slate-blue with pale bellies, arranged in
three neat stacked rows of six like museum specimens, each with fine ink outlines,
throat pleats, and small pectoral fins. Between the two groups, a hand-drawn balance
scale of enormous proportions, its beam tilting. Scale anchors placed along the ground
line: a row of tiny houses with tiled roofs, three matchstick trees, a small church
steeple, five ant-sized human figures, and a stationary train of four carriages — all
dwarfed. Faint horizontal haze bands recede into the distance. Crimson steam is the
single saturated accent.

CAMERA (fill all 8 seconds):
0.0-1.0s  Low over the first row of whales, their flukes and pleated throats sliding
          beneath the lens.
1.0-4.5s  FLY-OVER — the camera races low across all eighteen whales, row after row
          streaking past below, then hits the colossal figure's ankle and CRANES UP the
          full height of its body, muscle striations and venting steam blurring past.
4.5-6.5s  At the top it whips around and CRANE-DOWNS onto the giant balance scale,
          PUSHING IN on the tilting beam and its pivot as it groans over.
6.5-8.0s  Hold on the beam, the tiny houses and train visible far below as specks.
No shake, never locked-off. Push-in subject is the balance beam. Mood: staggering scale.
```

---

### S12 — 가벼워서 강하다 (4:56~5:28 · 32초 · 4클립)

**KO** 여기서 반전이 한 번 더 뒤집힙니다. 가벼우면 약할까요? 파괴력을 결정하는 건 운동에너지입니다. 질량 곱하기 속도의 제곱, 나누기 이. 질량이 절반이 되어도 속도가 두 배가 되면 파괴력은 두 배가 됩니다. 게다가 거인의 몸속에는 섭씨 350도 고압 수증기가 차 있습니다. 가벼운 몸을 순간적으로 밀어내는 추진 장치입니다. 가벼워서 약한 게 아니라, 가벼워서 빠르고, 빨라서 성벽을 부숩니다.

**EN** And here the twist flips one more time. Because light doesn't mean weak. Destructive power isn't mass — it's kinetic energy. Mass, times velocity squared, over two. Halve the mass but double the speed, and the damage doubles with it. On top of that, the titan's body is filled with pressurized steam at three hundred and fifty degrees — a thruster built into a lightweight frame. So it isn't weak because it's light. It's fast because it's light. And the wall breaks because it's fast.

**CAMERA** `WHIP → 임팩트 홀드 → CRANE DOWN` — 발차기 궤적을 따라 급속 횡이동, 임팩트에서 0.3초 정지 후 **부서지는 돌덩이** 사이로 하강하며 줌인.

**FLOW PROMPT**
```
[STYLE LOCK]
Dynamic action shot. A colossal humanoid figure in flat ochre with visible muscle-strand
brushwork drives a high kick into the upper section of a massive stone wall. The moment
of impact: the wall's stone blocks burst outward in a fan of dozens of individually inked
tumbling chunks of every size, trailing dust plumes drawn as stippled clouds, with three
long hand-inked speed arcs sweeping behind the leg. Thick crimson steam jets explosively
from the figure's shoulder vents, knee, and the nape of the neck, drawn as curling ribbon
shapes. Debris detail: shattered masonry, a snapped iron ladder cartwheeling, a torn
crimson banner spiraling, splintered wooden scaffolding planks, a bent bell, and a cloud
of roof tiles. In the lower foreground, tiny silhouetted figures on rooftops brace against
the shockwave, and birds scatter in every direction. Shockwave rendered as two concentric
thin ink rings. Background: pale cream sky going hazy with dust. Crimson is the single
saturated accent, on the steam and the banner.

CAMERA (fill all 8 seconds):
0.0-1.0s  Low behind the colossal figure's planted foot as the kicking leg begins to load,
          steam building at the knee vent.
1.0-3.5s  WHIP — the camera slams sideways following the leg's arc at extreme speed, the
          wall rushing into frame, motion arcs streaking.
3.5-4.0s  HARD FREEZE on the impact frame: stone bursting, shockwave rings snapping out.
4.0-6.5s  Time resumes and the camera CRANES DOWN through the exploding debris field,
          weaving between tumbling masonry chunks, then PUSHES IN on one large spinning
          stone block turning end over end toward the lens.
6.5-8.0s  Follow it down as it slams into the rubble and dust swallows the frame.
No screen shake, no strobe. Push-in subject is the tumbling stone block, never a person.
Mood: explosive, exhilarating.
```

---

### S13 — 비어 있는 뼈 (5:28~5:56 · 28초 · 4클립)

**KO** 이건 만화만의 발명이 아닙니다. 현실에도 같은 문제를 푼 거인들이 있습니다. 아르헨티노사우루스. 몸길이 35미터, 몸무게 80톤. 이 공룡의 뼈를 잘라 보면 속이 비어 있습니다. 새처럼 뼛속에 공기주머니를 넣어 무게를 덜어냈습니다. 부피는 유지하고 밀도만 줄인 것. 거인과 정확히 같은 해법입니다.

**EN** And none of this is a fictional invention. Real giants solved the identical problem. Argentinosaurus — thirty-five meters long, eighty tons of animal. Cut its bones open and you find them hollow. Like a bird, it packed air sacs deep into its skeleton to shed weight it didn't need. Keep the volume, cut the density. That is, precisely and exactly, the titan's solution.

**CAMERA** `CRANE UP → PUSH-THROUGH` — 공룡 다리 옆에서 등을 타고 목까지 상승한 뒤 척추뼈를 뚫고 들어가 **벌집 기낭 구조**로 줌인.

**FLOW PROMPT**
```
[STYLE LOCK]
A colossal long-necked sauropod dinosaur stands in a Cretaceous river valley, drawn in
flat olive and warm grey with heavy ink contours, its neck sweeping across the top of the
frame and tail exiting the right edge. Environmental density: tall horsetail reeds and
cycads in the foreground, three smaller sauropods drinking at a shallow braided river,
a flock of long-tailed pterosaurs, scattered boulders, driftwood logs, a mud bank with
trackways of huge three-toed footprints filling with water, low conifer forest on the far
bank, and layered hazy mesas on the horizon. Inset into the composition like a pinned
notebook study: an enlarged cutaway of a single vertebra revealing a honeycomb of hollow
internal chambers with paper-thin bony walls, drawn in chalky bone-white with wobbly ink
outlines, plus a small ghosted silhouette of a bird's skeleton beside it showing the same
hollow structure. Extra study props around the inset: a hand lens, a bone caliper, two
pins, and an empty label frame. Dusty teal sky with three flat clouds. Electric cyan is
the single saturated accent, used only inside the bone cavities.

CAMERA (fill all 8 seconds):
0.0-1.0s  Ground level beside one colossal pillar leg, horsetail reeds brushing the lens,
          the body vanishing upward out of frame.
1.0-4.5s  CRANE UP — the camera climbs the flank and RIDES ALONG the spine toward the neck
          at speed, the river valley, drinking sauropods and pterosaur flock wheeling away
          below, the neck sweeping ahead like a highway.
4.5-6.5s  Over a single vertebra it PUSHES THROUGH the bone surface into the cutaway and
          slows inside the honeycomb of hollow chambers, paper-thin bony walls glowing
          around the lens.
6.5-8.0s  Drift deeper between the air cells and settle.
No shake. Push-in subject is the vertebra's internal honeycomb. Mood: awe with scientific
curiosity.
```

---

### S14 — 신전의 기둥 (5:56~6:22 · 26초 · 3클립)

**KO** 무게를 덜어내는 것만으로는 부족합니다. 남은 무게를 어떻게 받치느냐도 문제입니다. 거대 공룡의 다리는 구부러져 있지 않습니다. 신전 기둥처럼 곧게 수직으로 서 있습니다. 다리가 굽으면 관절에 휘는 힘이 걸리지만, 곧게 세우면 힘이 뼈를 따라 그대로 땅으로 흘러갑니다. 코끼리 다리가 기둥처럼 생긴 것도 같은 이유입니다.

**EN** But shedding weight is only half the job. You still have to hold up whatever is left. So look at a giant dinosaur's legs. They don't bend. They stand straight and vertical, like temple columns. A bent leg loads the joint with bending stress, and bending is what breaks bone. A straight one channels the force cleanly down the shaft and into the ground. It's the same reason an elephant's leg looks like a pillar instead of a spring.

**CAMERA** `ORBIT → CRANE DOWN` — 세 다리(사람·공룡·기둥)를 180도 선회하며 훑고, 마지막에 **곧게 뻗은 뼈 축의 힘 화살표**로 수직 하강 줌인.

**FLOW PROMPT**
```
[STYLE LOCK]
Three-panel comparative composition on cream paper, each panel divided by a thin
hand-inked border. Left panel: a human leg in mid-stride, drawn as an ink contour with
the knee clearly bent, and a set of curved crimson stress arrows bunching at the knee
joint. Center panel: a massive sauropod hind limb, drawn in flat olive-grey, standing
perfectly straight and vertical like a tree trunk, with straight crimson force arrows
running cleanly down the bone axis into the ground. Right panel: a weathered stone temple
column with fluting and a simple capital, cracked at the base, with the identical straight
arrows running down it — visually rhyming with the dinosaur limb. Beneath all three, a
continuous hand-drawn ground line with small stones and grass tufts. Surrounding the
panels like margin notes: a hand-drawn plumb bob on a string, a small set of stacked
blocks, a sketch of an elephant's pillar-like leg, and three empty caption frames for
later text. Crimson is the only saturated accent, used exclusively on the force arrows.
CAMERA (fill all 8 seconds):
0.0-1.0s  Tight low angle on the bent human knee, the crimson stress arrows bunching there.
1.0-4.5s  ORBIT — the camera sweeps 180 degrees around the three subjects in one continuous
          arc, the human leg, the sauropod limb and the stone column rotating past each
          other, their force arrows aligning as the angle changes.
4.5-6.5s  It rises above the sauropod limb and CRANE-DOWNS straight along the bone axis,
          PUSHING IN so the straight force arrows run directly at the lens and into the
          ground plane.
6.5-8.0s  Settle at ground level where the arrows disappear into the earth.
No shake, never locked-off. Push-in subject is the force arrow running down the bone.
Mood: elegant, clarifying.
```

---

### S15 — 자랄수록 굵어진다 (6:22~6:48 · 26초 · 3클립)

**KO** 코끼리는 한 걸음 더 나아갔습니다. 새끼 코끼리와 어른 코끼리의 다리뼈를 비교하면, 어른 쪽이 몸 크기에 비해 훨씬 더 굵습니다. 몸이 커지는 속도보다 뼈가 굵어지는 속도를 더 빠르게 맞춘 겁니다. 생물은 이걸 수백만 년에 걸쳐 조금씩 조정했습니다. 만화 속 거인에게는 그 시간이 없었습니다. 그래서 작가는 밀도를 택했습니다.

**EN** Elephants went one step further than that. Compare a calf's leg bone to an adult's, and the adult's is disproportionately thicker for its body size — not just bigger, but bigger than it should be. Bone thickness was tuned to outpace body growth. Living things adjusted this dial slowly, over millions of years of trial and error. A fictional titan had no such time. So its author reached for density instead.

**CAMERA** `FLY-THROUGH → CRANE DOWN` — 코끼리 무리 사이를 낮게 통과한 뒤 어른 코끼리 **앞다리 뼈 오버레이**로 급강하 줌인. 코끼리 얼굴은 줌인하지 않는다.

**FLOW PROMPT**
```
[STYLE LOCK]
Savanna scene at golden hour. An adult elephant and its much smaller calf stand side by
side in three-quarter view, drawn in flat dusty grey with heavy ink contours, wrinkled
skin indicated by short brush hatching, large ears, and visible pillar-like legs. Behind
them, a hand-drawn herd of five more elephants recedes into haze, a flat-topped acacia
tree, a termite mound, tall dry grass drawn as vertical brush flicks, three white egrets,
a shallow watering hole with reflections, scattered rocks, and a low distant escarpment.
Overlaid on each animal like a pinned anatomical study: a ghosted white outline of its
femur, the adult's dramatically thicker relative to its body, each in its own hand-inked
frame. Beside them, a small hand-drawn growth chart of three stacked silhouettes from
calf to adult with an empty label box. Warm gold light with long soft shadows across the
ground. A single saturated accent: the warm gold rim light on the elephants' backs.
CAMERA (fill all 8 seconds):
0.0-1.0s  Low in the dry grass, brush-flick blades filling the foreground, the herd
          silhouetted in golden haze beyond.
1.0-4.5s  FLY-THROUGH — the camera races forward low between the herd's legs, pillar limbs
          sweeping past on both sides, dust and egrets scattering, emerging in front of the
          adult and calf.
4.5-6.5s  It CRANE-DOWNS onto the adult's foreleg and PUSHES IN on the ghosted white femur
          overlay until the bone's thickness fills the frame, the calf's much thinner bone
          visible small beside it for contrast.
6.5-8.0s  Hold there, gold rim light sliding along the bone outline.
No shake. Do not zoom on the elephants' faces — the push-in subject is the femur overlay.
Mood: warm, grounded, natural wisdom.
```

---

### S16 — 바다가 중력을 끊는다 (6:48~7:16 · 28초 · 4클립)

**KO** 그리고 지구 역사상 가장 무거운 동물. 대왕고래, 190톤입니다. 이 몸으로 어떻게 움직일까요? 답은 바다입니다. 물속에서는 부력이 중력을 거의 완전히 상쇄합니다. 대왕고래는 다리로 몸을 받칠 필요가 아예 없습니다. 스케일의 저주를 이긴 게 아니라, 저주가 걸리지 않는 곳으로 옮겨간 겁니다. 만약 거인이 바다에 살았다면, 물리학은 아무 불평도 하지 않았을 겁니다.

**EN** And then there's the heaviest animal in the history of this planet — the blue whale, one hundred and ninety tons. How does something that heavy move at all? The ocean. Underwater, buoyancy cancels gravity almost completely, and a blue whale never has to hold itself up on legs for a single second of its life. It didn't beat the curse of scale. It moved somewhere the curse doesn't apply. Put a titan in the sea, and physics wouldn't complain at all.

**CAMERA** `TRACK → CRANE DOWN` — 고래와 나란히 유영하다 몸 아래로 급강하해 배를 올려다보고, **부력 화살표**로 줌인.

**FLOW PROMPT**
```
[STYLE LOCK — palette shifts to deep ocean blues while keeping ink-and-gouache texture]
Underwater wide shot in deep blue-teal water with god rays slanting down from a bright
surface. An enormous blue whale glides across the full width of the frame in slate-blue
with a pale mottled belly, throat pleats drawn as long parallel ink lines, small dorsal
fin, and wide flukes mid-downstroke. Around it: a school of hundreds of tiny silver fish
splitting into two streams, three dolphins arcing above, drifting krill drawn as thousands
of specks in a warm haze, floating kelp fronds, suspended plankton motes, a scattering of
rising bubble strings, and a small human diver silhouette near the lower right for scale —
almost invisibly small. On the whale's body, two sets of hand-drawn arrows in contrasting
colors: heavy downward gravity arrows and equally strong upward buoyancy arrows, canceling
each other visibly. Seafloor far below with soft dunes and a shipwreck rib cage half-buried.
Surface shimmer at the top edge. Electric cyan is the single saturated accent, used only on
the buoyancy arrows.

CAMERA (fill all 8 seconds):
0.0-1.0s  Ahead of the whale's rostrum as it comes toward the lens out of the blue gloom,
          krill haze and god rays overhead.
1.0-4.5s  TRACK — the camera flies backward alongside the animal at its own speed, the full
          body streaming past, throat pleats and the fluke's downstroke sweeping the frame,
          the fish school splitting around the lens.
4.5-6.5s  It DIVES beneath the whale and CRANES UP to look at the pale belly from below,
          then PUSHES IN where the upward buoyancy arrows meet and cancel the downward
          gravity arrows, the arrow pair filling the frame.
6.5-8.0s  Hold under the belly, bubbles rising past, the wreck's rib cage far below.
No shake. Push-in subject is the buoyancy arrow pair. Mood: serene, majestic release.
```

---

### S17 — 햇빛으로 움직이는 몸 (7:16~7:40 · 24초 · 3클립)

**KO** 마지막 조각이 남았습니다. 작중 거인은 음식을 먹지 않습니다. 햇빛에서 에너지를 얻고, 해가 지면 활동을 멈춥니다. 이 설정 역시 우연이 아닙니다. 음식을 태워 에너지를 만들면 반드시 열이 나옵니다. 앞에서 본 그 열 문제입니다. 대사를 태양광으로 돌리고 밤에 꺼버리면, 몸이 스스로 익는 문제가 사라집니다.

**EN** One piece is still missing. In the story, titans don't eat. They draw their energy from sunlight, and when the sun goes down, they simply stop. That isn't a coincidence either. Burning food for energy always produces heat — the exact problem we just watched kill them twice over. Switch the metabolism to sunlight, power the whole thing down at night, and the self-cooking problem quietly disappears.

**CAMERA** `ORBIT → PUSH IN` — 거인을 중심으로 180도 선회하는 동안 낮이 밤으로 넘어가고, 마지막에 **굳어가는 표면 균열**로 줌인.

**FLOW PROMPT**
```
[STYLE LOCK]
A single continuous day-to-night transition in one composition. A 15-meter humanoid
titan stands motionless on a grassy hillside. In the left half of the frame it is bathed
in warm afternoon sun: golden light rims its shoulders, thin sunbeam strokes drawn
entering the skin as small warm arrows, faint steam rising, and its posture upright and
faintly alert. Toward the right half the sky graduates into deep indigo dusk with the sun
a low flat disc on the horizon; the same figure appears slumping, its surface going grey
and matte with hairline cracks spreading like dried clay, steam dying to nothing, and its
head bowed. Environmental detail across the hillside: tall grass drawn as vertical brush
flicks bending in wind, a lone twisted tree, a low stone ruin with a collapsed arch, a
flock of birds crossing from lit side to dark side, three sheep, a winding dirt path, and
scattered wildflowers closing their petals on the dark side. Stars begin as tiny ink dots
in the upper right. Warm gold on the left and deep indigo on the right, meeting in the
middle.

CAMERA (fill all 8 seconds):
0.0-1.0s  Low on the sunlit side, warm gold raking across the grass toward the standing
          figure.
1.0-4.5s  ORBIT — the camera swings a full 180 degrees around the figure, and as it travels
          the sky rolls from gold through amber into deep indigo, the sun sinking, birds
          crossing from light into dark, wildflowers folding shut, the figure's surface
          going grey and matte behind the moving camera.
4.5-6.5s  It arrives on the dark side and PUSHES IN on the hairline cracks spreading across
          the stiffening surface like drying clay, until the fissure network fills the frame.
6.5-8.0s  Hold as the last steam wisp dies and stars prick out above.
No shake. Push-in subject is the spreading surface crack. Mood: melancholy, quiet logic.
```

---

### S18 — 만든 사람의 계산 (7:40~8:00 · 20초 · 3클립)

**KO** 그러니까 거인이 가벼운 건 대충 만든 설정이 아닙니다. 뼈가 부서지는 문제, 몸이 익는 문제, 성벽을 부술 파괴력. 이 세 가지를 한꺼번에 푸는 유일한 답이 바로 '가벼운 몸'이었습니다. 좋은 상상은 물리 법칙을 무시하지 않습니다. 물리 법칙을 알고 나서, 그 사이로 길을 냅니다.

**EN** So the titan's lightness was never a lazy shortcut. Bones that shatter under load. A body that cooks itself. And enough force to bring down a fifty-meter wall. One single answer solves all three at once: make it light. Good imagination doesn't ignore the laws of physics. It learns them first — and then goes looking for the gap to walk through.

**CAMERA** `CRANE UP` — 성벽 위를 스치며 거인 실루엣을 지나 하늘로 크게 솟구쳐, 상단 여백에서 멈춘다(엔드카드 자리).

**FLOW PROMPT**
```
[STYLE LOCK]
Wide closing shot at dawn. The silhouette of a colossal humanoid figure stands beyond a
long stone wall, backlit by a rising sun that fills the sky with pale gold and soft rose
bands, the figure reduced to a flat dark shape with only thin crimson steam curling from
its shoulders. The wall runs diagonally across the lower third, its stones catching warm
rim light, with three tiny watchtowers, a line of banner poles, and six ant-sized figures
standing on the parapet looking outward. Below the wall: rooftops of a sleeping town with
chimney smoke rising in thin curls, a windmill, a church spire, and orchards in neat rows.
Foreground: tall grass in soft focus at the bottom edge and two birds crossing the frame.
Layered atmospheric haze separates wall, figure, and sky into three clean depth planes.
Wide empty sky area in the upper third deliberately left clear for later end-card overlay.
Warm gold is the single saturated accent.

CAMERA (fill all 8 seconds):
0.0-1.0s  Low among the foreground grass behind the parapet, the town rooftops and chimney
          smoke beyond.
1.0-4.5s  CRANE UP — the camera lifts and flies forward over the wall walk, the watchtowers
          and banner poles and the six tiny figures passing beneath it, then continues
          climbing past the colossal silhouette's shoulder.
4.5-6.5s  It keeps rising into the open dawn sky, the wall and figure dropping away to the
          bottom edge of frame, gold and rose bands filling the view.
6.5-8.0s  Settle on the wide empty sky, two birds crossing, the lower third holding the
          silhouette small. Upper two-thirds deliberately left clear for the end card.
No shake. Mood: resolved, thoughtful, a little hopeful.
```

---

## 3. 제작 수치

| 항목 | 값 |
|---|---|
| 총 길이 | 480초 (8:00) |
| 씬 | 18 |
| Flow 8초 클립 | **62클립** (씬당 3~4) |
| 나레이션 한국어 | 약 2,850자 |
| 나레이션 영어 | 약 1,180단어 (분당 148단어) |
| TTS | 초안 edge-tts → 최종 Azure (KO 선희 / EN Emma), 1.1배속 |
| 자막 | 5개국어 KO/EN/JA/ZH-Hans/ES-419, 소프트(번인 금지) |

## 4. 다음 단계

1. 사장님 시나리오 승인
2. 조감독에게 **Flow 키프레임 생성 지시** — S1부터 순서대로, 씬당 대표 키프레임 1장씩 먼저 18장
3. 키프레임 18장 검수 → 통과분만 8초 클립으로 확장
4. TTS·자막·합성은 기존 파이프라인 재사용
5. 우하단 Veo 워터마크 → 동일 크기 로고 덮개 (W24R 방식)
