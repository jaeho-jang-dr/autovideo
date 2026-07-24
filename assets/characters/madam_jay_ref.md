# 마담제이(Madam J) — 정확 외형 레퍼런스 (포즈 생성용 고정 스크립트)

> **레퍼런스 이미지**: `assets/characters/cutouts/madam_jay_base_front.png`
> 모든 새 포즈는 이 외형과 **똑같아야** 한다(머리·옷·체형·신발·비율 고정, 포즈만 변화). agy 프롬프트에 이 스크립트를 그대로 넣는다.

## 외형 스크립트 (영문 — agy/nano-banana용)
A simple flat cartoon woman, thick soft black outline, storybook style, cream/off-white skin, minimalist.
- **Face**: two small dot eyes, a tiny short nose line, a gentle small smile. No blush.
- **Hair**: dark warm brown, tied up in a **round top bun (updo)**, center part, with one **slightly wavy loose strand** framing each side of the face.
- **Top**: a **soft coral / salmon-pink V-neck teacher vest**, a **small chest pocket on the left with a pen/pencil sticking out**, a **ribbed knit band hem** at the bottom of the vest, white inner top. (A tiny "선생님" label low-right on the vest — keep small; overlay with PIL later if garbled.)
- **Bottom**: a **plain white A-line knee-length skirt**.
- **Limbs**: thin simple line arms/legs, **cream rounded mitten hands**, bare legs.
- **Shoes**: **cream/white rounded slip-on shoes**.
- **Proportions**: large head, small torso, thin stick limbs (flat cartoon), head ≈ 1/3 of height.

## 한글 요약
연한 코랄 V넥 선생님 조끼(가슴 펜주머니+니트 밑단) · 흰 A라인 치마 · 진갈색 탑번 쪽머리(양옆 잔머리) · 크림색 슬립온 · 가는 스틱 팔다리 · 굵은 검정 외곽선 플랫카툰.

## W11 방향/합성 규칙
- **오른쪽(식당 방향)을 향한** 포즈 위주(왼편 배치, 오른쪽에 식당 배경). 손 뻗기·가리키기는 오른손.
- **앉은 포즈는 의자 없이**(의자는 배경 드로잉) — 무릎 굽혀 앉은 자세만, 오른쪽 향함.
- 흰 배경 + 캐릭터만(그림자·소품 없음) → 투명 컷아웃.

## 기존 포즈 재사용 가능(assets/graphics/poses/, assets/characters/)
base_front · base_side · walk_left · walk_right · point_left · point_right · presenting · raising_hand(부르기) · waving · cheering · clapping · greeting · greeting_r20 · thinking · holding_book · sitting(★의자포함-교체필요) · sitting_r20(★의자여부확인)

## W11 신규 생성 필요(의자 없는·식당 동작, 오른쪽 향함)
sit_plain(의자없이 앉기) · sitting_menu(앉아 메뉴판 보기) · hold_menu(메뉴판 들기) · lean_table(몸 기울여 살피기) · call_staff(손 들어 부르기) · receive(두 손 받기) · chopsticks(젓가락질) · taste(맛보기) · thumbs_up(엄지척) · fan_mouth(입 부채질-매움) · drink_water(물 마시기) · sip(국물) · size_gesture(양 손짓) · pat_belly(배 두드리기) · point_menu(앉아 메뉴 가리키기) · pay_card(카드 내밀기) · receive_receipt(영수증 받기) · stand_up(일어서기) · count_1 · count_2
