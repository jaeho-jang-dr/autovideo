# Google Flow 수동 제작 가이드 (16씬 · 하나씩)

labs.google/fx/tools/flow 에서 **Frames to Video**(이미지→비디오) 모드로 한 씬씩 만든다.

## 공통 설정 (한 번만)
- 모드: **Frames to Video** (이미지→비디오)
- 모델: **Veo 3.1** (또는 사용 가능한 최신 Veo)
- 화면비: **16:9**(유튜브) 또는 9:16(쇼츠)
- Outputs per prompt: **1**

## 한 씬 처리 순서
1. **Frames to Video** 선택 → 시작 프레임으로 아래 `이미지` 파일 업로드
2. `프롬프트` 텍스트를 입력창에 붙여넣기
3. 생성(▶/화살표) 클릭 → 완료까지 대기
4. 결과 영상 다운로드 (다운로드 폴더에 그대로 둬도 됨 — 나중에 한꺼번에 정리)
5. 다음 씬 반복

> 다운로드한 16개 클립은 마지막에 `python place_clips.py "<다운로드폴더>"` 로
> `assets/videos/scene_1.mp4 ~ scene_16.mp4` 에 순서대로 자동 배치 → `python make_video_hypnosis.py` 로 최종 렌더링.

---

### Scene 1
- 이미지: `assets/images/scene_1.png`
- 프롬프트:
```
The glowing pocket watch swings gently left to right. As it swings, the camera slowly zooms into the spiral pattern, which begins to swirl. The background fades into a deep lavender.
```

### Scene 2
- 이미지: `assets/images/scene_2.png`
- 프롬프트:
```
The magician taps his top hat with the wand. A funny cartoon rabbit pops out of the hat and starts dancing. The camera pans down to show the audience clapping, with colorful confetti floating down.
```

### Scene 3
- 이미지: `assets/images/scene_3.png`
- 프롬프트:
```
The gears inside the head silhouette begin to turn slowly. A bright light bulb in the center of the brain lights up and sparkles. The camera zooms into the light bulb, transitioning the screen to a warm white light.
```

### Scene 4
- 이미지: `assets/images/scene_4.png`
- 프롬프트:
```
Mesmer winks at the camera and waves his wand. The camera pans right as glowing cosmic energy lines flow out from his wand, wrapping around a historical scroll map.
```

### Scene 5
- 이미지: `assets/images/scene_5.png`
- 프롬프트:
```
The glowing energy lines wrap around the patient. The patient smiles and raises both arms in relief. The camera tilts up to show the ceiling decorated with stars and moons.
```

### Scene 6
- 이미지: `assets/images/scene_6.png`
- 프롬프트:
```
The King frowns and points forward. The royal guard steps forward, tapping his halberd on the ground. The camera pans left to reveal a formal document unfurling with a royal seal.
```

### Scene 7
- 이미지: `assets/images/scene_7.png`
- 프롬프트:
```
Benjamin Franklin looks through his magnifying glass, which makes his eye look giant and funny. The other scientists scribble on their pads. The camera zooms in on Franklin's notebook as he draws a big question mark.
```

### Scene 8
- 이미지: `assets/images/scene_8.png`
- 프롬프트:
```
The scientist behind the patient waves his hands dramatically. The blindfolded patient remains perfectly still and yawns. A question mark pops up over the patient's head.
```

### Scene 9
- 이미지: `assets/images/scene_9.png`
- 프롬프트:
```
The scale tips heavily towards the brain side. The bottle of 'Magnetic Fluid' shatters, and small sparkles evaporate. The cartoon brain smiles and winks at the camera.
```

### Scene 10
- 이미지: `assets/images/scene_10.png`
- 프롬프트:
```
The brain's light bulb glows intensely. The camera pans down to show a patient swallowing a simple white sugar pill, instantly transforming their facial expression from sick to energetic and happy.
```

### Scene 11
- 이미지: `assets/images/scene_11.png`
- 프롬프트:
```
The metallic object in Braid's hand begins to shine with concentric rings of light. The patient's eyes show rotating spirals, and the camera zooms in closely on one eye.
```

### Scene 12
- 이미지: `assets/images/scene_12.png`
- 프롬프트:
```
The glowing lines pulse rapidly. The background darkens, and the frontal lobe of the brain goes dim while the focus center glows brightly with a warm golden light.
```

### Scene 13
- 이미지: `assets/images/scene_13.png`
- 프롬프트:
```
The colorful brain on the monitor spins in 3D. The therapist in the background gestures, and the camera pans closer to the monitor as specific regions of the brain glow and shift color.
```

### Scene 14
- 이미지: `assets/images/scene_14.png`
- 프롬프트:
```
The bright red region on the brain map slowly dissolves into a peaceful cool blue color. Tiny cartoon shield icons appear around the blue area, deflecting tiny red lightning bolts representing pain.
```

### Scene 15
- 이미지: `assets/images/scene_15.png`
- 프롬프트:
```
The patient on the bed closes their eyes and takes a deep, peaceful breath. A small green leaf sprouts from the patient's hand, representing healing. The camera slowly pans out to show the whole room in a warm, comforting light.
```

### Scene 16
- 이미지: `assets/images/scene_16.png`
- 프롬프트:
```
The person gently blows on the glowing spark. The spark rises into the air, multiplying into dozens of tiny glowing stars that light up the giant brain silhouette in the background sky, creating a beautiful constellation effect.
```
