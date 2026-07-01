import os
import sys
from playwright.sync_api import sync_playwright

# Content structured into exactly 15 pages
PAGES_HTML = [
    # Page 1: Cover
    """
    <div class="page cover-page">
        <div class="brand">SORI HANGEUL · 소리 한글</div>
        <div class="title-wrap">
            <h1>한글 교육 종합 가이드북</h1>
            <h2>Week 1: 한글의 탄생과 단모음</h2>
        </div>
        <div class="meta">
            <p><strong>대상:</strong> 외국인 성인 및 어린이 학습자</p>
            <p><strong>단계:</strong> 초급 (Beginner Level 1)</p>
            <p><strong>발행:</strong> 소리한글 교육 개발부</p>
        </div>
        <div class="decoration">🇰🇷</div>
    </div>
    """,
    # Page 2: Table of Contents
    """
    <div class="page toc-page">
        <h3>목차 (Table of Contents)</h3>
        <ul class="toc-list">
            <li><span>1. 한글의 창제 원리와 독창성</span> <span>Page 3</span></li>
            <li><span>  1.1. 자음의 상형 원리 (ㄱ, ㄴ, ㅁ, ㅅ, ㅇ)</span> <span>Page 4</span></li>
            <li><span>  1.2. 모음의 천지인 원리 (·, ㅡ, ㅣ)</span> <span>Page 5</span></li>
            <li><span>  1.3. 가획의 원리 (소리의 세기와 확장)</span> <span>Page 6</span></li>
            <li><span>2. 외국인을 위한 조음(발음) 지도법</span> <span>Page 7</span></li>
            <li><span>  2.1. 자음 삼분법 (평음 / 격음 / 경음)</span> <span>Page 8</span></li>
            <li><span>  2.2. 모음 조음 구별 (으 / 어 / 오 / 우)</span> <span>Page 9</span></li>
            <li><span>3. 한글의 결합 구조와 쓰기 규칙</span> <span>Page 10</span></li>
            <li><span>  3.1. 받침(종성)과 대표 7음</span> <span>Page 11</span></li>
            <li><span>  3.2. 획순(Stroke Order) 대원칙</span> <span>Page 12</span></li>
            <li><span>4. 단답형 연습 문제</span> <span>Page 13</span></li>
            <li><span>5. 심화 에세이 및 토론 주제</span> <span>Page 14</span></li>
            <li><span>6. 용어 사전 (Glossary) & 교육 리소스</span> <span>Page 15</span></li>
        </ul>
    </div>
    """,
    # Page 3: Section 1 Intro
    """
    <div class="page">
        <h3>1. 한글의 창제 원리와 독창성</h3>
        <p class="lead">한글(Hangul)은 세계 문자 역사에서 독보적인 위치를 차지하고 있습니다. 대부분의 전통 문자가 오랜 세월에 걸쳐 서서히 변형되며 형성된 것과 달리, 한글은 창제자와 창제 연도(1443년 창제, 1446년 반포)가 명확히 밝혀진 유일한 문자입니다.</p>
        
        <div class="info-box">
            <h4>자질 문자 (Featural Alphabet)</h4>
            <p>한글은 현대 언어학에서 '자질 문자'로 분류됩니다. 이는 단순히 자음과 모음을 나열하는 것을 넘어, 글자의 모양 자체가 소리를 내는 발음 기관의 움직임과 철학적 요소를 시각적으로 대변하는 고도의 논리적 체계임을 의미합니다.</p>
        </div>
        
        <p>세종대왕은 글을 읽지 못해 법을 몰라 억울한 일을 당하는 백성들을 위해 이 문자를 만들었습니다. "백성을 가르치는 바른 소리"라는 뜻의 '훈민정음(訓民正음)'은 지혜로운 자는 하루 아침에, 어리석은 자도 열흘이면 배울 수 있는 혁신적인 문자였습니다.</p>
    </div>
    """,
    # Page 4: Section 1.1 Consonants
    """
    <div class="page">
        <h3>1.1. 자음의 상형 원리 (상형의 원리)</h3>
        <p>한글의 기본 자음 5자(ㄱ, ㄴ, ㅁ, ㅅ, ㅇ)는 소리를 낼 때 발음 기관(혀, 입술, 이, 목구멍)의 모양을 본떠 만들어졌습니다. 이는 소리의 물리적 조음 위치와 글자의 모양을 일치시킨 과학적 결과입니다.</p>
        
        <table class="styled-table">
            <thead>
                <tr>
                    <th>기본 자음</th>
                    <th>조음 기관 분류</th>
                    <th>상형의 구체적 원리</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>ㄱ</strong></td>
                    <td>아음 (Velar)</td>
                    <td>혀뿌리가 목구멍을 막는 모양 (혀의 뒷부분이 입천장 뒤쪽에 닿음)</td>
                </tr>
                <tr>
                    <td><strong>ㄴ</strong></td>
                    <td>설음 (Alveolar)</td>
                    <td>혀끝이 윗잇몸에 닿는 모양 (혀끝이 윗니 뒤쪽에 닿는 형상)</td>
                </tr>
                <tr>
                    <td><strong>ㅁ</strong></td>
                    <td>순음 (Bilabial)</td>
                    <td>입술의 모양 (네모난 입 모양을 상형)</td>
                </tr>
                <tr>
                    <td><strong>ㅅ</strong></td>
                    <td>치음 (Dental)</td>
                    <td>이의 모양 (뾰족한 치아의 형상)</td>
                </tr>
                <tr>
                    <td><strong>ㅇ</strong></td>
                    <td>후음 (Glottal)</td>
                    <td>목구멍의 모양 (둥근 목구멍 구멍을 상형)</td>
                </tr>
            </tbody>
        </table>
        
        <p>이 기본 5자를 바탕으로 획을 더하거나 글자를 겹쳐 써서 나머지 14개의 자음(총 19개 자음)이 확장되는 논리적 구조를 취하고 있습니다.</p>
    </div>
    """,
    # Page 5: Section 1.2 Vowels
    """
    <div class="page">
        <h3>1.2. 모음의 천지인(天地人) 원리</h3>
        <p>한글 모음은 동양 철학의 우주관인 삼재(三才), 즉 하늘(天), 땅(地), 사람(人)의 모양을 본떠 만들어졌습니다. 우주의 조화와 인간의 중심적 위치를 글자 속에 녹여낸 디자인적 독창성을 보여줍니다.</p>
        
        <div class="philosophical-cards">
            <div class="card">
                <div class="sym">•</div>
                <div class="name">하늘 (아래아)</div>
                <p>둥근 하늘의 모양을 본떠 동그란 점으로 표현했습니다. (현대 국어에서는 짧은 가로 또는 세로 획으로 변형되어 사용)</p>
            </div>
            <div class="card">
                <div class="sym">ㅡ</div>
                <div class="name">땅 (으)</div>
                <p>평평하게 펼쳐진 땅의 모양을 상징하는 수평선으로 설계되었습니다.</p>
            </div>
            <div class="card">
                <div class="sym">ㅣ</div>
                <div class="name">사람 (이)</div>
                <p>서 있는 사람의 모양을 상징하는 수직선으로 설계되었습니다.</p>
            </div>
        </div>
        
        <p>이 기본 세 요소를 조합하여 첫 번째 파생 모음인 초출자(ㅏ, ㅓ, ㅗ, ㅜ)와 두 번째 파생 모음인 재출자(ㅑ, ㅕ, ㅛ, ㅠ)를 확장해 나가는 단순하면서도 강력한 기하학적 원리를 지니고 있습니다.</p>
    </div>
    """,
    # Page 6: Section 1.3 Addition of strokes
    """
    <div class="page">
        <h3>1.3. 가획(加劃)의 원리: 소리의 세기와 확장</h3>
        <p>한글은 소리의 강도가 세짐에 따라 글자에 획을 더해 나가는 '가획의 원리'를 취하고 있습니다. 글자의 외관만 보고도 해당 글자가 어떤 성격의 소리를 내는지 직관적으로 알 수 있는 독보적인 장점입니다.</p>
        
        <div class="stroke-tree">
            <div class="row">
                <span class="base">ㄱ (Plain)</span> ➡️ <span class="added">ㅋ (Aspirated / 거센소리)</span>
            </div>
            <div class="row">
                <span class="base">ㄴ (Plain)</span> ➡️ <span class="added">ㄷ (Plain / 가획)</span> ➡️ <span class="added">ㅌ (Aspirated / 거센소리)</span>
            </div>
            <div class="row">
                <span class="base">ㅁ (Plain)</span> ➡️ <span class="added">ㅂ (Plain / 가획)</span> ➡️ <span class="added">ㅍ (Aspirated / 거센소리)</span>
            </div>
            <div class="row">
                <span class="base">ㅅ (Plain)</span> ➡️ <span class="added">ㅈ (Plain / 가획)</span> ➡️ <span class="added">ㅊ (Aspirated / 거센소리)</span>
            </div>
            <div class="row">
                <span class="base">ㅇ (Plain)</span> ➡️ <span class="added">ㆆ (예소리)</span> ➡️ <span class="added">ㅎ (Aspirated / 거센소리)</span>
            </div>
        </div>
        
        <p class="highlight">이러한 가획 원리는 한글이 단순한 암기 대상이 아니라 구조적 대칭성과 논리성을 갖춘 완벽한 과학적 발명품임을 증명하는 핵심 원리입니다.</p>
    </div>
    """,
    # Page 7: Section 2 Pronunciation
    """
    <div class="page">
        <h3>2. 외국인을 위한 조음(발음) 지도법</h3>
        <p>외국인 학습자, 특히 영어권 학습자가 한글을 배울 때 겪는 가장 큰 장벽은 자음과 모음의 조음 방식 차이입니다. 한국어 특유의 기압(Aspiration)과 성대 긴장도(Tension)를 인지하지 못하면 부자연스럽거나 완전히 틀린 발음을 구사하게 됩니다.</p>
        
        <div class="info-box accent-box">
            <h4>한국어 조음 지도의 핵심 전략</h4>
            <p>단순히 원어민의 소리를 듣고 따라 하는 방식을 넘어, 발음할 때의 구체적인 <strong>입모양(Mouth Shape)</strong>, <strong>턱의 위치(Jaw Position)</strong>, 그리고 <strong>공기의 흐름(Airflow)</strong>을 시각적으로 인지시키고 훈련하는 것이 효과적입니다.</p>
        </div>
        
        <p>이를 위해 '소리한글'은 음성 학습에 최적화된 시각 자료와 3D 입 모양 가이드 및 오디오 플레이백 시스템을 활용해 지도합니다. 다음 페이지부터 자음과 모음의 정밀 발음법을 학습합니다.</p>
    </div>
    """,
    # Page 8: Section 2.1 Consonant Distinction
    """
    <div class="page">
        <h3>2.1. 자음 삼분법 (평음 / 격음 / 경음)</h3>
        <p>영어권에는 유성음/무성음(voiced/voiceless)의 2단계 대립만 존재하지만, 한국어 자음은 '평음-격음-경음'의 3단계 대립 구조를 지니고 있습니다. 이를 명확히 시각화하여 가르쳐야 합니다.</p>
        
        <table class="styled-table font-dense">
            <thead>
                <tr>
                    <th>소리 분류</th>
                    <th>특징</th>
                    <th>자음 예시</th>
                    <th>외국인 인지 및 지도 꿀팁</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>평음 (Plain)</strong></td>
                    <td>부드럽고 약한 숨을 내보내며 발음</td>
                    <td>ㄱ, ㄷ, ㅂ, ㅅ, ㅈ</td>
                    <td>영어의 'g, d, b'와 'k, t, p'의 중간음으로 인식됩니다. 단어 첫머리에서는 다소 무성음화된다는 점을 인지시킵니다.</td>
                </tr>
                <tr>
                    <td><strong>격음 (Aspirated)</strong></td>
                    <td>강한 바람을 거세게 뿜어냄</td>
                    <td>ㅋ, ㅌ, ㅍ, ㅊ, ㅎ</td>
                    <td>입 앞에 손바닥이나 얇은 종이를 대고 발음할 때 <strong>"바람이 세게 뿜어져 나와 손바닥을 치는 느낌"</strong>을 직접 느끼도록 훈련합니다.</td>
                </tr>
                <tr>
                    <td><strong>경음 (Tense)</strong></td>
                    <td>성대를 꽉 조여 단단하게 소리 냄</td>
                    <td>ㄲ, ㄸ, ㅃ, ㅆ, ㅉ</td>
                    <td>공기를 밖으로 거의 뿜지 않고 목 안쪽 성대에 힘을 주는 방식입니다. 영어의 'sky'에서 s 뒤에 발음되는 'k' 소리와 유사함을 활용합니다.</td>
                </tr>
            </tbody>
        </table>
        
        <p class="exercise-note">연습: '방-팡-빵', '개-캐-깨', '달-탈-딸'을 발음하며 손바닥으로 공기 흐름의 차이를 느껴보세요.</p>
    </div>
    """,
    # Page 9: Section 2.2 Vowel Distinction
    """
    <div class="page">
        <h3>2.2. 모음 조음 구별 (으 / 어 / 오 / 우)</h3>
        <p>외국인들이 가장 발음하기 헷갈려하고 실수하기 쉬운 단모음들의 혀 위치와 입술 모양 특징입니다.</p>
        
        <div class="vowel-guides">
            <div class="vg-item">
                <span class="v-letter">으 [ɯ]</span>
                <p>영어권 학습자에게 가장 낯선 모음입니다. 턱을 가볍게 닫고 <strong>"억지 미소를 짓는 느낌"</strong>으로 입술을 양옆으로 길게 찢은 상태에서 목구멍 안쪽에서 소리를 내도록 유도합니다.</p>
            </div>
            
            <div class="vg-item">
                <span class="v-letter">어 [ʌ] vs 오 [o]</span>
                <p><strong>어:</strong> 입을 아래로 크게 벌리고 턱을 아래로 떨어뜨립니다. 입술은 동그랗게 모으지 않습니다 (평순 모음).<br>
                <strong>오:</strong> 입술을 튀어나오게 동그랗게 모아야 합니다. 빨대를 문 것처럼 좁은 동그라미를 그립니다 (원순 모음).</p>
            </div>
            
            <div class="vg-item">
                <span class="v-letter">우 [u] vs 오 [o]</span>
                <p><strong>우:</strong> 입술을 가장 작고 동그랗게 오므려 앞으로 쭉 내밀면서 발음합니다.<br>
                <strong>오:</strong> 우보다 입을 턱 아래로 살짝 더 내린 상태의 조금 더 큰 동그라미 입 모양을 유지합니다.</p>
            </div>
        </div>
    </div>
    """,
    # Page 10: Section 3 Syllable Structure
    """
    <div class="page">
        <h3>3. 한글의 결합 구조와 쓰기 규칙</h3>
        <p>한글은 알파벳처럼 자소들을 일렬로 나열하는 풀어쓰기 대신, 자음과 모음을 결합하여 하나의 사각형 음절 블록을 만드는 <strong>'모아쓰기(Syllabic Block)'</strong> 방식을 택합니다. 이는 한글의 시각적 가독성과 정보 압축성을 높여주는 핵심 구조입니다.</p>
        
        <div class="block-diagrams">
            <div class="diag">
                <div class="d-title">가로 결합형 (ㅣ계열 모음)</div>
                <div class="d-grid horizontal">
                    <div class="box">초성 (자음)</div>
                    <div class="box">중성 (모음)</div>
                </div>
                <p>예: 가, 나, 다, 라</p>
            </div>
            <div class="diag">
                <div class="d-title">세로 결합형 (ㅡ계열 모음)</div>
                <div class="d-grid vertical">
                    <div class="box">초성 (자음)</div>
                    <div class="box">중성 (모음)</div>
                </div>
                <p>예: 고, 노, 두, 루</p>
            </div>
        </div>
        
        <p>학습을 지도할 때는 자음의 오른쪽 혹은 아래쪽에 모음 획의 수직/수평 형태에 따라 위치가 결정된다는 대원칙을 직관적으로 이해할 수 있도록 컬러 코딩이나 블록 조구를 적극 활용하는 것이 좋습니다.</p>
    </div>
    """,
    # Page 11: Section 3.1 Batchim
    """
    <div class="page">
        <h3>3.1. 받침(종성)과 대표 7음 규칙</h3>
        <p>음절 블록의 바닥(가장 아래쪽)에 위치하는 자음을 **'받침(종성, Final Consonant)'**이라고 부릅니다. 한글의 모든 자음(ㄲ, ㄸ, ㅃ, ㅉ 제외)이 받침 자리에 올 수 있지만, 발음될 때는 단 <strong>7개의 대표 소리</strong>로만 실현됩니다.</p>
        
        <table class="styled-table font-dense">
            <thead>
                <tr>
                    <th>대표 받침 소리</th>
                    <th>실제 표기 받침 자음</th>
                    <th>발음 예시 및 음성 실현</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>[ㄱ]</strong></td>
                    <td>ㄱ, ㅋ, ㄲ, ㄳ, ㄺ</td>
                    <td>책 [책], 부엌 [부억], 밖 [박], 닭 [닥]</td>
                </tr>
                <tr>
                    <td><strong>[ㄴ]</strong></td>
                    <td>ㄴ, ㄵ, ㄶ</td>
                    <td>문 [문], 앉다 [안따], 많다 [만타]</td>
                </tr>
                <tr>
                    <td><strong>[ㄷ]</strong></td>
                    <td>ㄷ, ㅅ, ㅈ, ㅊ, ㅌ, ㅎ, ㅆ</td>
                    <td>듣다 [듣따], 옷 [옏/옫], 낮 [낟], 꽃 [꼳], 밑 [믿]</td>
                </tr>
                <tr>
                    <td><strong>[ㄹ]</strong></td>
                    <td>ㄹ, ㄼ, ㄽ, ㄾ, ㅀ</td>
                    <td>물 [물], 여덟 [여덜], 넓다 [널따]</td>
                </tr>
                <tr>
                    <td><strong>[ㅁ]</strong></td>
                    <td>ㅁ, ㄻ</td>
                    <td>엄마 [엄마], 삶 [삼]</td>
                </tr>
                <tr>
                    <td><strong>[ㅂ]</strong></td>
                    <td>ㅂ, ㅍ, ㅄ, ㄿ</td>
                    <td>밥 [밥], 앞 [압], 값 [갑]</td>
                </tr>
                <tr>
                    <td><strong>[ㅇ]</strong></td>
                    <td>ㅇ</td>
                    <td>공 [공], 강 [강]</td>
                </tr>
            </tbody>
        </table>
        
        <p class="highlight">주의: 받침 자음 뒤에 모음으로 시작하는 형태소가 오면 연음 현상(Liaison)이 일어나 제소리값으로 발음됩니다. (예: 옷이 [오시])</p>
    </div>
    """,
    # Page 12: Section 3.2 Stroke Order
    """
    <div class="page">
        <h3>3.2. 획순(Stroke Order) 대원칙</h3>
        <p>외국인 학습자들이 한글을 독학할 때 가장 흔히 무시하는 것이 획순입니다. 획순을 무시하고 그림을 그리듯이 쓰면 글씨체가 뭉개지고 가독성이 떨어져 알아볼 수 없게 됩니다. 올바른 필순 지도는 가독성과 쓰는 속도를 비약적으로 증대시킵니다.</p>
        
        <div class="info-box">
            <h4>한글 쓰기 2대 대원칙</h4>
            <p><strong>원칙 1. 왼쪽에서 오른쪽으로 (Left to Right)</strong>: 모든 수평 획과 배치는 좌측에서 우측으로 써 나갑니다.<br>
            <strong>원칙 2. 위에서 아래로 (Top to Bottom)</strong>: 모든 수직 획과 배치는 상단에서 하단으로 내립니다.</p>
        </div>
        
        <div class="stroke-example">
            <p><strong>'ㅁ(미음)'의 올바른 3획 획순:</strong></p>
            <ol>
                <li>1획: 왼쪽 수직선을 위에서 아래로 내립니다.</li>
                <li>2획: 기억(ㄱ) 형태의 기역자 획을 왼쪽 위에서 시작하여 오른쪽으로 간 뒤 아래로 내립니다.</li>
                <li>3획: 아래 밑변 수평선을 왼쪽에서 오른쪽으로 이어 닫아줍니다.</li>
            </ol>
        </div>
    </div>
    """,
    # Page 13: Section 4 Quiz
    """
    <div class="page">
        <h3>4. 단답형 연습 문제</h3>
        <p>본 장은 1주차 학습 성취도를 점검하기 위한 연습 문제입니다. 질문을 읽고 정답을 적어보세요.</p>
        
        <div class="qa-item">
            <p class="q"><strong>문항 1.</strong> 한글 모음의 창제 원리가 되는 동양 철학적 세 요소(천·지·인)는 각각 현실에서 어떤 기하학적 형태(점/수평선/수직선 등)로 상형되었습니까?</p>
            <p class="a"><strong>정답 및 해설:</strong> 하늘(·)은 둥근 점, 땅(ㅡ)은 평평한 수평선, 사람(ㅣ)은 서 있는 수직선으로 상형되었습니다.</p>
        </div>
        
        <div class="qa-item">
            <p class="q"><strong>문항 2.</strong> '어 [ʌ]'와 '오 [o]'를 발음할 때의 입술 모양(둥글림 여부)과 턱의 위치 차이를 서술하시오.</p>
            <p class="a"><strong>정답 및 해설:</strong> '어'는 입술을 평평하게(평순) 한 채 턱을 아래로 크게 내리며, '오'는 입술을 동그랗게 모으고(원순) 턱을 덜 내립니다.</p>
        </div>
        
        <div class="qa-item">
            <p class="q"><strong>문항 3.</strong> '값'이라는 단어의 받침 발음은 대표 7음 중 어떤 소리로 실현됩니까?</p>
            <p class="a"><strong>정답 및 해설:</strong> [ㅂ]으로 실현됩니다. '값'의 ㅂㅅ 겹받침 중 대표음 [ㅂ]만 발음되어 [갑]이 됩니다.</p>
        </div>
    </div>
    """,
    # Page 14: Section 5 Essay
    """
    <div class="page">
        <h3>5. 심화 에세이 및 토론 주제</h3>
        <p>아래 논제들은 한글의 언어학적 특성과 철학적 배경을 더 깊이 통찰하기 위한 심화 에세이 주제입니다.</p>
        
        <div class="essay-topic">
            <h4>[주제 1] 자질 문자로서의 직관성과 정보 처리 효율성</h4>
            <p>한글의 '가획의 원리'와 '상형의 원리'는 형태와 음성학적 기능이 일치하는 뛰어난 특징을 갖습니다. 이러한 자질 문자적 성격이 외국인 학습자가 한글을 배울 때 다른 음소 문자(예: 로마자 알파벳)와 비교하여 어떤 인지적 편리함을 주는지 구체적인 사례를 들어 분석하시오.</p>
        </div>
        
        <div class="essay-topic">
            <h4>[주제 2] 모음 조화의 대칭성과 시각 디자인 연동</h4>
            <p>한국어 모음 조화 규칙(양성 모음과 음성 모음의 결합 원리)은 소리의 조화를 넘어 동양의 음양사상을 투영하고 있습니다. 이 규칙을 외국인 아동 학습자에게 설명할 때 색상의 따뜻함과 차가움(Color Temperature)을 융합한 시각 디자인 교구(예: 빨간 블록과 파란 블록)가 교수학습 도구로서 어떠한 효용을 가질 수 있을지 서술하시오.</p>
        </div>
    </div>
    """,
    # Page 15: Section 6 Glossary
    """
    <div class="page">
        <h3>6. 용어 사전 (Glossary) & 교육 리소스</h3>
        <ul class="glossary-list">
            <li><strong>모아쓰기 (Syllabic Block Assembly):</strong> 자음과 모음을 일렬로 나열하지 않고, 사각형 음절 단위로 묶어 쓰는 표기 방식.</li>
            <li><strong>자질 문자 (Featural Alphabet):</strong> 개별 음소뿐만 아니라 유기적 발음 자질(거센소리, 된소리 등)이 자소의 획수와 모양에 직접 일치되어 나타나는 문자 체계.</li>
            <li><strong>연음 (Liaison/Linking):</strong> 앞 음절의 받침 자음이 모음으로 시작하는 뒤 음절의 첫소리 자리에 이어져 발음되는 음운 현상.</li>
            <li><strong>천지인 (Cheon-Ji-In):</strong> 하늘, 땅, 사람을 뜻하며 한글 기본 모음 3자의 철학적 창제 배경이 됨.</li>
        </ul>
        
        <div class="resources-box">
            <h4>학습 추천 공식 웹사이트</h4>
            <ul>
                <li>국립국어원 한국어교수학습샘터 (https://kcenter.korean.go.kr)</li>
                <li>누리 세종학당 온라인 학습 플랫폼 (https://www.sejonghakdang.org)</li>
                <li>소리한글 교육 개발 센터 (https://drjayed.com/curriculum)</li>
            </ul>
        </div>
    </div>
    """
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>소리한글 교육 종합 가이드북 - Week 1</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #d3c4a9;
            font-family: 'Noto Sans KR', 'Inter', sans-serif;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        /* 15 pages configuration */
        .page {
            width: 210mm;
            height: 297mm;
            box-sizing: border-box;
            padding: 22mm 20mm;
            background-color: #F5F5F0;
            color: #1C1813;
            position: relative;
            page-break-after: always;
            border-bottom: 1px dashed rgba(28, 24, 19, 0.15); /* preview guide line */
        }
        
        @media print {
            body {
                background: none;
            }
            .page {
                border-bottom: none;
                page-break-after: always;
                width: 210mm;
                height: 297mm;
            }
        }
        
        /* Premium Header and Footer */
        .page::before {
            content: "SORI HANGEUL STUDY GUIDE · WEEK 1";
            position: absolute;
            top: 10mm;
            left: 20mm;
            font-size: 8pt;
            font-weight: 600;
            color: #8C7F6A;
            letter-spacing: 0.1em;
        }
        .page::after {
            content: "Page " counter(page-counter);
            position: absolute;
            bottom: 10mm;
            right: 20mm;
            font-size: 8pt;
            font-weight: 600;
            color: #8C7F6A;
        }
        .page {
            counter-increment: page-counter;
        }
        
        /* Custom elements stylings */
        h1, h2, h3, h4 {
            margin-top: 0;
            color: #1C1813;
            font-family: 'Outfit', 'Noto Sans KR', sans-serif;
        }
        
        h3 {
            font-size: 18pt;
            font-weight: 800;
            border-bottom: 2px solid #b5852a;
            padding-bottom: 6px;
            margin-bottom: 16px;
            letter-spacing: -0.01em;
        }
        
        p {
            font-size: 10.5pt;
            line-height: 1.7;
            color: #3C352D;
            margin-bottom: 14px;
            word-break: keep-all;
        }
        
        .lead {
            font-size: 12pt;
            font-weight: 500;
            color: #1C1813;
            line-height: 1.6;
        }
        
        .info-box {
            background-color: rgba(181, 133, 42, 0.08);
            border-left: 4px solid #b5852a;
            padding: 12px 18px;
            border-radius: 4px;
            margin: 18px 0;
        }
        .info-box h4 {
            margin: 0 0 6px 0;
            font-size: 11pt;
            font-weight: 700;
            color: #b5852a;
        }
        .info-box p {
            margin: 0;
            font-size: 9.5pt;
            line-height: 1.6;
        }
        
        .accent-box {
            background-color: rgba(47, 109, 59, 0.08);
            border-left-color: #2f6d3b;
        }
        .accent-box h4 {
            color: #2f6d3b;
        }
        
        .highlight {
            font-weight: 700;
            color: #b5852a;
        }
        
        /* Table */
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 9.5pt;
            text-align: left;
        }
        .styled-table th {
            background-color: #e9e5d9;
            color: #1C1813;
            font-weight: 700;
            padding: 10px 12px;
            border-bottom: 2px solid rgba(28, 24, 19, 0.15);
        }
        .styled-table td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(28, 24, 19, 0.10);
            line-height: 1.5;
        }
        .font-dense td, .font-dense th {
            padding: 8px 10px;
            font-size: 9pt;
        }
        
        /* Cover design */
        .cover-page {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            text-align: center;
            padding: 40mm 20mm;
        }
        .cover-page::before, .cover-page::after {
            display: none; /* Hide header/footer on cover */
        }
        .brand {
            font-family: 'Outfit', sans-serif;
            font-size: 14pt;
            font-weight: 800;
            letter-spacing: 0.2em;
            color: #b5852a;
            border: 2px solid #b5852a;
            padding: 6px 20px;
            border-radius: 2px;
        }
        .title-wrap {
            margin: 30mm 0;
        }
        .cover-page h1 {
            font-size: 28pt;
            font-weight: 800;
            margin-bottom: 10px;
            letter-spacing: -0.02em;
            line-height: 1.3;
        }
        .cover-page h2 {
            font-size: 16pt;
            font-weight: 500;
            color: #8C7F6A;
        }
        .meta {
            font-size: 10.5pt;
            color: #5B5142;
            line-height: 1.8;
        }
        .meta p {
            margin: 4px 0;
        }
        .decoration {
            font-size: 40pt;
            margin-top: 15mm;
            opacity: 0.85;
        }
        
        /* TOC */
        .toc-page {
            padding-top: 30mm;
        }
        .toc-list {
            list-style: none;
            padding: 0;
            margin: 20mm 0 0 0;
        }
        .toc-list li {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            font-size: 11pt;
            margin-bottom: 14px;
            font-weight: 500;
        }
        .toc-list li::after {
            content: " ";
            flex-grow: 1;
            border-bottom: 1px dotted rgba(28, 24, 19, 0.3);
            margin: 0 10px;
        }
        .toc-list li span:last-child {
            font-weight: 700;
            color: #b5852a;
            flex-shrink: 0;
        }
        
        /* Section specific styles */
        .philosophical-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin: 20px 0;
        }
        .philosophical-cards .card {
            background-color: #fffdf7;
            border: 1px solid rgba(28, 24, 19, 0.1);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(60, 48, 30, 0.04);
        }
        .philosophical-cards .sym {
            font-size: 32pt;
            color: #b5852a;
            font-weight: 800;
            margin-bottom: 8px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .philosophical-cards .name {
            font-weight: 700;
            font-size: 10pt;
            margin-bottom: 10px;
        }
        .philosophical-cards p {
            font-size: 8.5pt;
            line-height: 1.5;
            color: #5B5142;
            margin: 0;
        }
        
        .stroke-tree {
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #fffdf7;
            border: 1px solid var(--c-line);
            border-radius: 8px;
            padding: 16px 20px;
            margin: 20px 0;
        }
        .stroke-tree .row {
            font-size: 11pt;
            font-weight: 600;
        }
        .stroke-tree .base {
            color: #3C352D;
            background: rgba(28, 24, 19, 0.05);
            padding: 4px 8px;
            border-radius: 4px;
        }
        .stroke-tree .added {
            color: #b5852a;
            background: rgba(181, 133, 42, 0.08);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 700;
        }
        
        .vowel-guides {
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-top: 10mm;
        }
        .vg-item {
            background-color: #fffdf7;
            border: 1px solid rgba(28, 24, 19, 0.08);
            padding: 16px;
            border-radius: 8px;
            position: relative;
        }
        .vg-item::before {
            content: " ";
            position: absolute;
            left: 0;
            top: 15px;
            bottom: 15px;
            width: 4px;
            background-color: #b5852a;
            border-radius: 0 4px 4px 0;
        }
        .v-letter {
            font-size: 13pt;
            font-weight: 800;
            color: #b5852a;
            display: block;
            margin-bottom: 6px;
        }
        .vg-item p {
            margin: 0;
            font-size: 9.5pt;
        }
        
        .block-diagrams {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .diag {
            background: #fffdf7;
            border: 1px solid rgba(28,24,19,0.1);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }
        .d-title {
            font-size: 10pt;
            font-weight: 700;
            margin-bottom: 14px;
            color: #b5852a;
        }
        .d-grid {
            display: grid;
            gap: 8px;
            width: 120px;
            margin: 0 auto 12px;
        }
        .d-grid.horizontal {
            grid-template-columns: 1fr 1fr;
            height: 60px;
        }
        .d-grid.vertical {
            grid-template-rows: 1fr 1fr;
            height: 120px;
            width: 60px;
        }
        .d-grid .box {
            border: 2px solid #1C1813;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 9pt;
            font-weight: 700;
            border-radius: 4px;
            background: #F5F5F0;
        }
        .diag p {
            font-size: 9pt;
            margin: 0;
            color: #8C7F6A;
        }
        
        .stroke-example ol {
            padding-left: 20px;
            margin: 10px 0 0 0;
        }
        .stroke-example li {
            font-size: 10pt;
            line-height: 1.6;
            color: #3C352D;
            margin-bottom: 6px;
        }
        
        .qa-item {
            background: #fffdf7;
            border: 1px solid rgba(28,24,19,0.1);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .qa-item .q {
            font-weight: 700;
            margin-bottom: 8px;
            color: #1C1813;
        }
        .qa-item .a {
            margin: 0;
            font-size: 9.5pt;
            color: #2f6d3b;
        }
        
        .essay-topic {
            background: #fffdf7;
            border: 1px solid rgba(181, 133, 42, 0.15);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 18px;
        }
        .essay-topic h4 {
            margin: 0 0 8px 0;
            color: #b5852a;
            font-size: 11pt;
            font-weight: 700;
        }
        .essay-topic p {
            margin: 0;
            font-size: 9.5pt;
            line-height: 1.6;
        }
        
        .glossary-list {
            list-style: none;
            padding: 0;
            margin: 15px 0 0 0;
        }
        .glossary-list li {
            font-size: 9.5pt;
            line-height: 1.6;
            margin-bottom: 12px;
            padding-left: 12px;
            position: relative;
        }
        .glossary-list li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: #b5852a;
            font-weight: 700;
        }
        .glossary-list strong {
            color: #b5852a;
        }
        .resources-box {
            background: rgba(181, 133, 42, 0.06);
            border: 1px dashed #b5852a;
            border-radius: 8px;
            padding: 16px;
            margin-top: 15mm;
        }
        .resources-box h4 {
            margin: 0 0 8px 0;
            font-size: 11pt;
        }
        .resources-box ul {
            padding-left: 20px;
            margin: 0;
        }
        .resources-box li {
            font-size: 9.5pt;
            line-height: 1.6;
            margin-bottom: 6px;
            color: #5B5142;
        }
        
    </style>
</head>
<body>
    <div class="book-container">
        {pages}
    </div>
</body>
</html>
"""

def generate():
    print("Generating HTML content for 15 pages...")
    # Assemble page items
    pages_html_str = "\\n".join(PAGES_HTML)
    full_html = HTML_TEMPLATE.replace("{pages}", pages_html_str)
    
    # Save to temp file
    temp_html_path = "scratch/temp_pdf_layout.html"
    os.makedirs("scratch", exist_ok=True)
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Saved temp HTML to {temp_html_path}")
    
    # Render using Playwright to web/public/docs/hangeul_week_1_guide.pdf
    pdf_out_dir = "web/public/docs"
    os.makedirs(pdf_out_dir, exist_ok=True)
    pdf_out_path = os.path.join(pdf_out_dir, "hangeul_week_1_guide.pdf")
    
    print("Starting Playwright to compile PDF...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Load local HTML file
        abs_html_path = os.path.abspath(temp_html_path)
        page.goto(f"file:///{abs_html_path}")
        
        # Print to PDF using A4, exact sizing
        page.pdf(
            path=pdf_out_path,
            format="A4",
            print_background=True,
            margin={
                "top": "0",
                "bottom": "0",
                "left": "0",
                "right": "0"
            }
        )
        browser.close()
        
    print(f"Successfully generated 15-page PDF at: {pdf_out_path}")

if __name__ == "__main__":
    generate()
