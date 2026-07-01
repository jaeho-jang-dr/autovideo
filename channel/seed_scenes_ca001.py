#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CA-001 "피터팬은 왜 늙지 않을까?" 에피소드의 씬 데이터를 content.db에 시드한다.
"""
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.db")

CA_001_SCENES = [
    (1,
     "네버랜드에서 영원히 어린아이로 살아가는 소년 피터팬. 만약 현대 의학의 돋보기로 그의 몸을 관찰한다면 어떤 비밀이 숨겨져 있을까요?",
     "Peter Pan, the boy who lives forever as a child in Neverland. If we were to observe his body through the magnifying glass of modern medicine, what secrets would be revealed?",
     "Minimalist flat pastel illustration of Peter Pan flying in the night sky over London, cozy warm colors, rough ink outlines, starry background. No watermark, no text, no letters, no signatures.",
     ":: slow motion Peter Pan slowly glides from top-right to bottom-left, camera panning slowly"),
    
    (2,
     "사람이 성장하려면 뼈 양 끝에 위치한 연골 조직인 '성장판', 즉 골단판이 세포분열을 하며 뼈를 늘려가야 합니다.",
     "For a human to grow, the epiphyseal plates—commonly known as growth plates—located at the ends of bones must divide cells to lengthen the skeleton.",
     "Minimalist flat pastel illustration of a child's leg bone, highlighting the glowing growth plate cartilage at the ends, clean cross-section, beige and coral colors. No watermark, no text, no letters, no signatures.",
     ":: slow motion growth plate cartilage glowing with pulsing warm orange light, camera slowly zooming in"),
    
    (3,
     "성장판 속 연골세포들이 활발하게 분열하고 뼈로 변해가면서 키가 자라지만, 사춘기가 지나 성호르몬이 분비되면 성장판은 완전히 단단한 뼈로 바뀌어 닫히게 됩니다.",
     "As chondrocytes inside the growth plate actively divide and calcify into bone, we grow taller; but after puberty, sex hormones cause these plates to completely ossify and close.",
     "Minimalist flat pastel illustration showing chondrocytes dividing and then turning into solid bone, arrows pointing to the transition, clean vector art. No watermark, no text, no letters, no signatures.",
     ":: slow motion tiny cell spheres dividing rapidly, then freezing and solidifying into a dense bone pattern"),
    
    (4,
     "피터팬이 영원히 자라지 않는 상태라면, 그의 성장판은 닫히지 않고 계속 연골 상태로 남아있거나, 혹은 분열이 멈춘 상태일 것입니다.",
     "If Peter Pan never grows up, his growth plates must either remain open as cartilage forever, or their cell division has completely frozen in place.",
     "Minimalist flat pastel illustration of Peter Pan's knee joint with open, glowing growth plates, surrounded by small frozen clock gears, cozy warm cream palette. No watermark, no text, no letters, no signatures.",
     ":: slow motion glowing growth plate remains perfectly still while tiny clock gears in the background spin backwards, camera rotating slowly"),
    
    (5,
     "이 과정을 조절하는 핵심 물질은 뇌하수체에서 분비되는 '성장호르몬'입니다. 뼈의 성장을 촉진하고 간에서 성장인자를 만들어내죠.",
     "The key regulator of this process is the \"growth hormone\" secreted by the pituitary gland, which stimulates bone growth and produces growth factors in the liver.",
     "Minimalist flat pastel illustration of the brain's pituitary gland releasing glowing hormone particles that flow down towards a simplified liver, medical art style. No watermark, no text, no letters, no signatures.",
     ":: slow motion glowing gold particles flow down from the brain to the liver, liver lighting up in response"),
    
    (6,
     "만약 성장호르몬이 전혀 분비되지 않는 '뇌하수체 왜소증' 상태라면 피터팬처럼 어린아이의 체구를 유지할 수 있습니다.",
     "If one has \"pituitary dwarfism\"—a condition where no growth hormone is secreted—they can maintain a child-like stature just like Peter Pan.",
     "Minimalist flat pastel illustration comparing a normal adult silhouette with a child-sized adult silhouette, simple clinical scale in background. No watermark, no text, no letters, no signatures.",
     ":: slow motion child-sized silhouette stays still while the scale balance swings gently, camera panning right"),
    
    (7,
     "하지만 단순히 키만 작을 뿐 아니라, 2차 성징이 나타나지 않고 피부가 일찍 노화하거나 심혈관 질환에 취약해지는 심각한 의학적 문제를 동반합니다.",
     "However, this condition is not just about being short; it brings serious medical challenges like lack of secondary sexual characteristics, early skin aging, and cardiovascular issues.",
     "Minimalist flat pastel illustration of a heart with glowing arterial lines and a dry, cracked leaf pattern overlay, soft coral and charcoal colors. No watermark, no text, no letters, no signatures.",
     ":: slow motion heart beating slowly, arterial lines pulsing with electric-like red light, camera zooming out slowly"),
    
    (8,
     "또 다른 가능성은 갑상선 호르몬 결핍입니다. 뼈와 지능 발달을 모두 지연시켜 육체와 정신이 모두 어린 상태에 머물게 만들죠.",
     "Another possibility is thyroid hormone deficiency, which delays both bone and intellectual development, keeping both body and mind in an infantile state.",
     "Minimalist flat pastel illustration of a thyroid gland on a throat silhouette, with a glowing brain and a stylized hourglass that is stuck. No watermark, no text, no letters, no signatures.",
     ":: slow motion hourglass sand frozen in the middle, brain pulsing slowly with dim blue light, camera rotating slowly"),
    
    (9,
     "이처럼 네버랜드의 마법이 아니라 실제 의학 세계에서 '영원한 어린이'로 남는다는 것은 몸의 조화와 균형이 완전히 붕괴된 병리적 상태를 의미합니다.",
     "Thus, in the real medical world, remaining an \"eternal child\" without Neverland's magic means a pathological state where body harmony and balance have completely collapsed.",
     "Minimalist flat pastel illustration of a stone tower collapsing, with a human body skeleton outline fading in, symbolizing the loss of balance. No watermark, no text, no letters, no signatures.",
     ":: slow motion stone blocks crumbling and sliding down, revealing the glowing bone skeleton behind it, camera tilting down"),
    
    (10,
     "성장이 멈추는 것은 슬픈 일이 아니라, 우리 몸이 무한한 성장의 부하를 견디지 못하고 성숙과 안정의 단계로 들어서는 치유와 생존의 메커니즘입니다.",
     "Stopping growth is not a tragedy, but a mechanism of healing and survival, allowing the body to enter a stage of maturity and stability rather than bearing the strain of infinite growth.",
     "Minimalist flat pastel illustration of a tiny green sprout growing out of a solid stone crack, then stabilizing under a warm sun, cozy sage green palette. No watermark, no text, no letters, no signatures.",
     ":: slow motion green sprout growing out of the crack and its leaves unfurl under a warm glowing sun, camera zooming out"),
    
    (11,
     "피터팬이 모험을 즐기며 늙지 않는 동안, 사실 그의 뼈와 장기는 끊임없이 균형을 유지하기 위해 투쟁하고 있었던 것입니다.",
     "While Peter Pan enjoyed his adventures without aging, his bones and organs were actually struggling constantly to maintain their internal balance.",
     "Minimalist flat pastel illustration of a balance scale with a glowing heart on one side and a feather on the other, balanced in the air, soft warm background. No watermark, no text, no letters, no signatures.",
     ":: slow motion scale sways gently back and forth in a balanced state, camera panning up slowly"),
    
    (12,
     "결국 늙고 성장하는 것은 잃어버리는 과정이 아니라, 비로소 완전한 균형과 안정을 찾아가는 건강한 생명의 섭리인 셈입니다.",
     "In the end, aging and growing are not processes of loss, but a healthy law of life that finally finds complete balance and stability.",
     "Minimalist flat pastel illustration of a mature person looking at their own hands, hands glowing with warm gold lines, cozy warm cream and green palette. No watermark, no text, no letters, no signatures.",
     ":: slow motion person raises hands slowly, gold lines on the hands glowing warmly, camera zooming out slowly")
]

def estimate_duration(text_kr):
    return max(5.0, round(len(text_kr) / 7.0, 1))

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    
    code = "CA-001"
    cur.execute("DELETE FROM scenes WHERE episode=?", (code,))
    
    total = 0.0
    for seq, kr, en, img_p, veo_p in CA_001_SCENES:
        dur = estimate_duration(kr)
        total += dur
        cur.execute(
            "INSERT INTO scenes(episode, seq, script_kr, script_en, image_prompt, veo_prompt, duration_sec) "
            "VALUES (?,?,?,?,?,?,?)",
            (code, seq, kr, en, img_p, veo_p, dur)
        )
    
    cur.execute(
        "UPDATE episodes SET status='scripted', runtime_sec=? WHERE code=?",
        (int(round(total)), code)
    )
    conn.commit()
    conn.close()
    
    print(f"[OK] Seeded {len(CA_001_SCENES)} scenes into content.db for {code}.")
    print(f"Total estimated runtime: {total}s")

if __name__ == "__main__":
    main()
