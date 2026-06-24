export interface GrammarSection {
  id: string;
  title_ko: string;
  title_en: string;
  intro_ko: string;
  intro_en: string;
  items: {
    name_ko: string;
    name_en: string;
    details_ko: string;
    details_en: string;
    ipa?: string;
    tip_ko?: string;
    tip_en?: string;
    visual_highlight?: string; // 'throat' | 'lips' | 'tongue' | 'teeth' | 'palate'
    sound_play?: string; // 소리 재생을 위한 자모
  }[];
}

export const grammarData: GrammarSection[] = [
  {
    id: "principles",
    title_ko: "창제 원리 (Creative Principles)",
    title_en: "Principles of Creation",
    intro_ko: "한글은 발음 기관의 모양과 동양 철학의 삼재(하늘, 땅, 사람)를 본떠 만들어진 세계 역사상 가장 과학적이고 체계적인 자질 문자(Featural Alphabet)입니다.",
    intro_en: "Hangeul is a featural alphabet, designed after the shapes of the vocal organs and Eastern philosophy (Heaven, Earth, Human), making it highly scientific and intuitive.",
    items: [
      {
        name_ko: "자음: 발음 기관의 상형 (Consonants)",
        name_en: "Consonants: Vocal Organ Mimicry",
        details_ko: "기본 자음 5자(ㄱ, ㄴ, ㅁ, ㅅ, ㅇ)는 소리를 낼 때 발음 기관(혀, 입술, 이, 목구멍)의 모양을 본떠 만들어졌습니다. 글자의 모양이 소리의 물리적 성격을 그대로 반영합니다.",
        details_en: "The 5 basic consonants (ㄱ, ㄴ, ㅁ, ㅅ, ㅇ) mimic the shape of the tongue, lips, teeth, and throat during pronunciation. Visual shapes directly match physical sounds.",
        tip_ko: "ㄱ(혀뿌리가 목을 막는 모양), ㄴ(혀끝이 윗잇몸에 닿는 모양), ㅁ(입 모양), ㅅ(이 모양), ㅇ(목구멍 모양)",
        tip_en: "ㄱ (tongue root blocking throat), ㄴ (tongue tip touching gums), ㅁ (lip frame), ㅅ (tooth contour), ㅇ (circular throat passage)",
        sound_play: "ㄱ"
      },
      {
        name_ko: "모음: 천·지·인 삼재 (Vowels)",
        name_en: "Vowels: Heaven, Earth, Human",
        details_ko: "기본 모음 3자(ㆍ, ㅡ, ㅣ)는 동양 철학의 삼재(하늘, 땅, 사람)를 상징합니다. 하늘의 둥근 모양(ㆍ), 땅의 평평한 모양(ㅡ), 서 있는 사람의 모양(ㅣ)을 조합하여 모든 모음을 확장합니다.",
        details_en: "The 3 basic vowels (ㆍ, ㅡ, ㅣ) represent the three cosmic elements: Heaven (round dot ㆍ), Earth (flat line ㅡ), and Human (standing line ㅣ). All vowels expand from combinations of these.",
        tip_ko: "ㆍ(하늘) + ㅡ(땅) = ㅗ/ㅜ, ㆍ(하늘) + ㅣ(사람) = ㅏ/ㅓ 로 확장됩니다.",
        tip_en: "Combining ㆍ(Heaven) with ㅡ(Earth) yields ㅗ/ㅜ, and with ㅣ(Human) yields ㅏ/ㅓ.",
        sound_play: "ㅏ"
      },
      {
        name_ko: "가획의 원리 (Adding Strokes)",
        name_en: "Stroke Addition Rule",
        details_ko: "한글 자음은 소리가 세짐에 따라 기본 자형에 획을 더하여 거센 소리를 만듭니다. 이를 통해 글자의 시각적 복잡도만으로 소리의 성격을 유추할 수 있습니다.",
        details_en: "Strokes are added to basic consonants as sounds become stronger/aspirated. Learners can easily gauge sound intensity just by looking at the stroke count.",
        tip_ko: "ㄱ(약함) ➡️ ㅋ(거셈), ㄴ(약함) ➡️ ㄷ(가획) ➡️ ㅌ(거셈), ㅁ ➡️ ㅂ ➡️ ㅍ, ㅅ ➡️ ㅈ ➡️ ㅊ, ㅇ ➡️ ㅎ",
        tip_en: "ㄱ (soft) ➡️ ㅋ (stronger/puff), ㄴ (soft) ➡️ ㄷ (add stroke) ➡️ ㅌ (stronger/puff), ㅁ ➡️ ㅂ ➡️ ㅍ, ㅅ ➡️ ㅈ ➡️ ㅊ, ㅇ ➡️ ㅎ",
        sound_play: "ㅋ"
      }
    ]
  },
  {
    id: "consonants",
    title_ko: "자음 조음법 (Consonants)",
    title_en: "Consonant Articulation",
    intro_ko: "한국어 자음은 숨의 거세기와 긴장도에 따라 3단계로 정교하게 분류되며, 발음할 때 공기가 지나가는 구강의 물리적 위치에 따라 다르게 작동합니다.",
    intro_en: "Korean consonants feature a unique three-way distinction based on breath strength and muscle tension, and operate according to specific anatomical oral zones.",
    items: [
      {
        name_ko: "평음 / Plain (ㄱ, ㄷ, ㅂ, ㅅ, ㅈ)",
        name_en: "Plain Consonants (ㄱ, ㄷ, ㅂ, ㅅ, ㅈ)",
        details_ko: "숨을 편안하게 내보내며 부드럽게 내는 소리입니다. 영어권 화자에게는 단어 첫머리에서는 무성음(k, t, p)에 가깝게, 모음 사이에서는 유성음(g, d, b)으로 부드럽게 인식됩니다.",
        details_en: "Produced with gentle, relaxed breath release. English speakers perceive them as unvoiced (k, t, p) at the start of words, and voiced (g, d, b) between vowels.",
        ipa: "[k], [t], [p], [s], [tɕ]",
        tip_ko: "발음 꿀팁: 거울을 보며 입안에 긴장을 풀고 편안한 호흡으로 소리 냅니다.",
        tip_en: "Tip: Keep your mouth relaxed and release sound with standard, comfortable breath flow.",
        visual_highlight: "palate",
        sound_play: "가"
      },
      {
        name_ko: "격음 / Aspirated (ㅋ, ㅌ, ㅍ, ㅊ, ㅎ)",
        name_en: "Aspirated Consonants (ㅋ, ㅌ, ㅍ, ㅊ, ㅎ)",
        details_ko: "공기를 허파에서부터 거세고 빠르게 불어내며 발음하는 소리입니다. 입 앞에 종이나 손바닥을 대고 발음할 때 강한 공기 바람이 손바닥을 탁 치는 느낌이 나야 정확합니다.",
        details_en: "Produced with a strong, rapid puff of air. If you place a tissue or hand in front of your mouth, it should blow or hit your palm with noticeable force.",
        ipa: "[kʰ], [tʰ], [pʰ], [tɕʰ], [h]",
        tip_ko: "종이 테스트: '카!'라고 말할 때 입 앞의 휴지가 확 펄럭여야 합니다.",
        tip_en: "Tissue Test: Say 'Ka!' and verify that a paper sheet in front of your lips flutters strongly.",
        visual_highlight: "tongue",
        sound_play: "카"
      },
      {
        name_ko: "경음 / Tense (ㄲ, ㄸ, ㅃ, ㅆ, ㅉ)",
        name_en: "Tense Consonants (ㄲ, ㄸ, ㅃ, ㅆ, ㅉ)",
        details_ko: "공기를 밖으로 거의 내뿜지 않고, 목구멍 근육(성대)을 꽉 조여 단단하고 팽팽하게 내는 소리입니다. 영어 sky의 'k'나 spy의 'p' 발음 시 s 뒤에 오는 맑고 강한 무기음과 유사합니다.",
        details_en: "Produced by tensing the vocal cords without releasing air. Similar to the crisp, unaspirated 'k' in 'sky' or 'p' in 'spy' (after the 's').",
        ipa: "[k’], [t’], [p’], [s’], [tɕ’]",
        tip_ko: "발음 꿀팁: 숨을 참듯이 목에 꽉 힘을 준 채 공기 방출 없이 또렷하게 끊어 칩니다.",
        tip_en: "Tip: Tense your throat as if briefly holding your breath, then release a sharp, crisp sound without air.",
        visual_highlight: "throat",
        sound_play: "까"
      },
      {
        name_ko: "조음 기관별 소리 구분 (Articulation Zones)",
        name_en: "Anatomical Zones (Where Sound Forms)",
        details_ko: "자음은 구강 구도에 따라 발음 부위가 다릅니다: 어금닛소리(ㄱ/ㅋ-혀뿌리로 목구멍 폐쇄), 혓소리(ㄴ/ㄷ-혀끝이 윗잇몸에 접촉), 입술소리(ㅁ/ㅂ-양순 밀착), 잇소리(ㅅ/ㅈ-치조/경구개 마찰), 목소리(ㅎ-성문 마찰).",
        details_en: "Korean classifies consonants by oral touchpoints: Velar (ㄱ/ㅋ - tongue root blocks soft palate), Alveolar (ㄴ/ㄷ - tongue tip touches gum ridge), Bilabial (ㅁ/ㅂ - two lips seal), Dental/Palatal (ㅅ/ㅈ - friction at teeth/palate), Glottal (ㅎ - friction in throat).",
        tip_ko: "혀의 위치를 머릿속으로 그리며 의식적으로 혀끝이나 입술을 부착해 봅니다.",
        tip_en: "Visualize your tongue position: feel your tongue tip hit your gum ridge for ㄴ, or your lips seal for ㅁ.",
        visual_highlight: "tongue",
        sound_play: "라"
      }
    ]
  },
  {
    id: "vowels",
    title_ko: "모음과 개구도 (Vowels)",
    title_en: "Vowel Lip/Aperture Hacks",
    intro_ko: "외국인들이 가장 구별하기 힘들어하는 한국어 모음의 미세한 차이를 입술의 둥글림(원순/평순)과 입을 여는 크기(개구도)를 통해 공식으로 해결합니다.",
    intro_en: "Master tricky Korean vowels using simple visual formulas based on lip rounding (round vs. flat) and mouth opening size (aperture).",
    items: [
      {
        name_ko: "으 [ɯ] vs 이 [i] (입술 찢기)",
        name_en: "으 [ɯ] vs 이 [i] (The Horizontal Stretch)",
        details_ko: "영어에 없는 '으'는 윗니와 아랫니를 거의 닫고 입술을 양옆으로 길게 찢으면서 목구멍 쪽에서 자연스럽게 공기를 냅니다 (미소 모양). '이'는 혀 앞부분을 입천장 쪽으로 더 바짝 대서 날카롭게 냅니다.",
        details_en: "'으' has no English equivalent. Spread your lips wide horizontally (like a smile), bring teeth close, and release breath. For '이', push your tongue further forward for a sharp, high tone (like 'ee' in 'meet').",
        ipa: "[ɯ] / [i]",
        tip_ko: "으 공식: 입을 옆으로 찢고 '으-' 하고 웃으며 소리 냅니다.",
        tip_en: "Formula: Smile wide, pull lips back, keep teeth nearly closed, and say 'eu'.",
        visual_highlight: "lips",
        sound_play: "으"
      },
      {
        name_ko: "어 [ʌ] vs 오 [o] (입 크기와 모양)",
        name_en: "어 [ʌ] vs 오 [o] (Vertical Open vs. Circular Round)",
        details_ko: "'어'는 입술을 동그랗게 하지 않고 턱을 아래로 크게 벌려 손가락 두 개 높이로 소리 냅니다. 반면 '오'는 턱을 거의 벌리지 않고 입술 주변 근육을 둥글게 모아서 앞으로 동그랗게 쏩니다.",
        details_en: "For '어', open your jaw wide vertically (flat, unrounded lips, about two fingers tall). For '오', keep your jaw mostly closed and round your lips into a tight, circular circle ('O' shape).",
        ipa: "[ʌ] / [o]",
        tip_ko: "입 크기 공식: '어' = 턱 내리기 / '오' = 입술 똥그랗게 오므리기.",
        tip_en: "Formula: '어' = drop jaw vertically / '오' = purse lips into a circular whistle shape.",
        visual_highlight: "lips",
        sound_play: "어"
      },
      {
        name_ko: "우 [u] vs 오 [o] (돌출의 강도)",
        name_en: "우 [u] vs 오 [o] (Protrusion vs. Rounding)",
        details_ko: "'오'는 원을 그려 오므린다면, '우'는 입술 근육을 닭똥집 모양처럼 앞 방향으로 최대한 쭉 내밀면서 혀 뒷부분을 높이 올려 발음하는 고모음입니다.",
        details_en: "While '오' is rounded, '우' requires pushing your lips forward as far as possible (like a kiss or pout) while raising the back of your tongue (like 'oo' in 'boot').",
        ipa: "[u] / [o]",
        tip_ko: "우 공식: 입술을 오리 입처럼 앞으로 뾰족하게 내밀어 소리 냅니다.",
        tip_en: "Formula: Pout your lips forward intensely for '우', keep them rounded for '오'.",
        visual_highlight: "lips",
        sound_play: "우"
      },
      {
        name_ko: "에 [e] vs 애 [ɛ] (턱의 높이)",
        name_en: "에 [e] vs 애 [ɛ] (The Jaw Drop)",
        details_ko: "현대 한국어 화자들도 발음상 구별이 희미해졌으나 원칙적으로 '에'는 입을 가볍게 열고(새끼손가락 두께), '애'는 아랫턱을 아래로 더 뚝 떨어뜨려 입을 더 크게 벌리고 발음합니다.",
        details_en: "Though merging in modern speech, '에' is pronounced with a mid jaw drop (one finger height), whereas '애' requires dropping your jaw significantly lower (two fingers height).",
        ipa: "[e] / [ɛ]",
        tip_ko: "애 공식: '에'보다 턱을 아래로 한 칸 더 뚝 떨어뜨려 벌립니다.",
        tip_en: "Formula: '에' = normal mid-open / '애' = drop your lower jaw one notch further down.",
        visual_highlight: "tongue",
        sound_play: "에"
      },
      {
        name_ko: "이중모음 활주 (Semivowel Glides)",
        name_en: "Diphthong Gliding Mechanics",
        details_ko: "이중모음(ㅘ, ㅝ, ㅛ, ㅠ 등)은 하나의 정지된 소리가 아닙니다. 첫 반모음(w 또는 y)의 조음 상태에서 주모음으로 부드럽고 매끄럽게 미끄러지듯 이동(Gliding)하며 소리 내야 합니다.",
        details_en: "Diphthongs (ㅘ, ㅝ, ㅛ, ㅠ) are motion-based. You must start at a semivowel ('w' or 'y') posture and slide smoothly (glide) into the primary vowel (e.g. for ㅘ, slide from 'u' to 'a').",
        tip_ko: "ㅘ 공식: '우' 입모양에서 빠르게 턱을 열며 '아'로 슬라이딩! '우-아' ➡️ '와'.",
        tip_en: "Formula: Make a quick 'oo' shape and instantly slide into 'ah'! 'oo-ah' ➡️ 'wah'.",
        visual_highlight: "lips",
        sound_play: "와"
      }
    ]
  },
  {
    id: "rules",
    title_ko: "음운 변동 규칙 (Sound Rules)",
    title_en: "Connected Speech Rules",
    intro_ko: "한국어는 글자 그대로 발음되지 않는 경우가 많습니다. 문맥 속에서 혀의 움직임을 편하게 만들기 위해 발생하는 연음 법칙과 받침 중화 메커니즘을 배웁니다.",
    intro_en: "Korean is often not spoken exactly as written. Study the liaison (linking) and final-consonant neutralization rules that make pronunciation smooth and effortless.",
    items: [
      {
        name_ko: "연음 법칙 (Liaison / Linking)",
        name_en: "Liaison: The Slide-Over Rule",
        details_ko: "받침 뒤에 모음(이응'ㅇ'으로 시작하는 글자)이 오면, 받침 소리가 빈 초성 자리로 미끄러져 들어가 발음됩니다. 예: 음악은 표기대로가 아닌 [으막]으로, 한국어는 [한구거]로 부드럽게 흘려 읽습니다.",
        details_en: "When a batchim is followed by a vowel (syllables starting with silent 'ㅇ'), the batchim sound slides over to fill the silent slot. E.g. 음악 is spoken as [으막] (eu-mak), and 한국어 as [한구거] (han-gu-geo).",
        tip_ko: "연음 가이드: '음-악'이 아니라 받침 'ㅁ'이 넘어가 '으-막'으로 발음합니다.",
        tip_en: "Rule of thumb: Don't pause between blocks. Let the final consonant flow into the next block.",
        sound_play: "음악"
      },
      {
        name_ko: "받침 중화 (Batchim Neutralization)",
        name_en: "Neutralization: The 7 Representative Sounds",
        details_ko: "받침 자리에는 수많은 자음이 쓰일 수 있지만, 단어 끝이나 자음 앞에서는 입을 완전히 닫아 기류를 차단하는 7개의 대표 자음소[ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ] 중 하나로 닫혀서 발음됩니다.",
        details_en: "Although many consonants are written in the batchim position, they converge into just 7 representative closed sounds [ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ] at the end of words or before other consonants.",
        tip_ko: "ㄷ 대표음: ㅅ, ㅆ, ㅈ, ㅊ, ㄷ, ㅌ, ㅎ 받침은 모두 [낟]처럼 대표음 'ㄷ'으로 수렴 발음됩니다. 예: 낫, 낮, 낯, 낱 ➡️ 모두 발음은 [낟].",
        tip_en: "ㄷ converging: batchims ㅅ, ㅆ, ㅈ, ㅊ, ㄷ, ㅌ, ㅎ are all pronounced as representative closed 'ㄷ'. E.g. 낫, 낮, 낯, 낱 ➡️ all spoken as [낟] (nad).",
        sound_play: "꽃"
      }
    ]
  },
  {
    id: "stroke",
    title_ko: "한글 획순 대원칙 (Writing)",
    title_en: "Stroke Order Master Rules",
    intro_ko: "올바른 필순(Stroke Order)을 지키는 것은 예쁜 손글씨의 비결일 뿐만 아니라 글자의 형태가 뭉개지는 것을 방지하여 읽기 쉽게 만들어 줍니다.",
    intro_en: "Writing Hangeul in the correct order is the secret to clean handwriting and ensures that the letter components stay clear and legible.",
    items: [
      {
        name_ko: "기본 2대 원칙 (Left to Right / Top to Bottom)",
        name_en: "The 2 Core Rules",
        details_ko: "한글 쓰기의 핵심은 '왼쪽에서 오른쪽으로', '위에서 아래로' 그어 나가는 것입니다. 모음과 자음 모두 이 대원칙을 기반으로 움직입니다.",
        details_en: "Always draw strokes from Left to Right and from Top to Bottom. Both consonants and vowels follow this universal rule.",
        tip_ko: "가로 획은 항상 왼쪽 ➡️ 오른쪽 / 세로 획은 항상 위 ➡️ 아래로 그립니다.",
        tip_en: "Horizontal lines go Left ➡️ Right. Vertical lines go Top ➡️ Bottom.",
        sound_play: "한글"
      },
      {
        name_ko: "미음(ㅁ)과 리을(ㄹ)의 정밀 획순",
        name_en: "Writing 'ㅁ' (M) and 'ㄹ' (R) Correctly",
        details_ko: "'ㅁ'은 원 안 그리기 대신 3획으로 끊어 씁니다(세로선 ➡️ ㄱ모양 꺾쇠 ➡️ 바닥 가로선). 'ㄹ'은 한 번에 꼬아 쓰지 않고 ㄷ자 모양을 3단계로 쪼개어 정밀하게 조립하듯 씁니다.",
        details_en: "'ㅁ' is written in 3 separate strokes (vertical line ➡️ right-angle hook ➡️ bottom bar). 'ㄹ' is written in 3 steps (top hook ➡️ middle horizontal bar ➡️ bottom hook) to preserve structural balance.",
        tip_ko: "ㅁ = 3획 / ㄹ = 3획으로 정밀하게 조각 내어 씁니다.",
        tip_en: "ㅁ = 3 strokes / ㄹ = 3 strokes. Avoid drawing them in a single connected swoop.",
        sound_play: "라"
      }
    ]
  }
];
