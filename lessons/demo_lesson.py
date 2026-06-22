# -*- coding: utf-8 -*-
"""레슨 엔진 데모 — 한글 "안녕하세요" 교육(외국인용). 벤치마크 기법 시연.
씬 스펙(데이터)만 바꾸면 새 레슨이 됨. 출력: lessons/_demo_lesson.mp4
"""
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import lesson_engine as E
A=E.ACCENT
ZG="home_vocab/zollanyeo_pointing.png"; ZC="home_vocab/zollanyeo_cheering.png"

SCENES=[
 # 1. 타이틀 — 단어 팝 + 스포트라이트 + 프리젠터 슬라이드 인
 {"dur":3.2,"sub":"오늘의 한글 — 안녕하세요","els":[
   {"type":"text","text":"오늘의 한글","size":68,"color":(120,120,145),"pos":(540,340),"in":"slide_d","t_in":0.1},
   {"type":"spotlight","pos":(500,720),"r":320,"t_in":0.5,"strength":0.5},
   {"type":"text","text":"안녕하세요","size":150,"color":(40,40,62),"pos":(500,720),"in":"pop","t_in":0.6},
   {"type":"presenter","img":ZG,"h":760,"flip":True,"pos":(870,1330),"bob":7,"in":"slide_l","t_in":0.3},
 ]},
 # 2. 뜻 — 밑줄 + 의미 콜아웃 슬라이드 + 체크
 {"dur":3.0,"sub":"뜻은 Hello / Hi 예요","els":[
   {"type":"text","text":"안녕하세요","size":140,"color":(40,40,62),"pos":(540,560),"in":"fade","t_in":0.0},
   {"type":"underline","pos":(540,675),"width":640,"color":A,"t_in":0.5,"in_dur":0.6},
   {"type":"text","text":"= Hello !","size":98,"color":(36,150,170),"pos":(540,860),"in":"slide_r","t_in":1.0},
   {"type":"check","pos":(840,855),"size":72,"t_in":1.6},
 ]},
 # 3. 분해 — 번호배지 ①② + 슬라이드 + 보충설명
 {"dur":3.4,"sub":"두 부분: 안녕 + 하세요","els":[
   {"type":"badge","num":"1","pos":(330,540),"in":"pop","t_in":0.2},
   {"type":"text","text":"안녕","size":132,"color":(40,40,62),"pos":(500,540),"in":"slide_d","t_in":0.4},
   {"type":"badge","num":"2","pos":(330,810),"in":"pop","t_in":0.9},
   {"type":"text","text":"하세요","size":132,"color":(40,40,62),"pos":(540,810),"in":"slide_d","t_in":1.1},
   {"type":"text","text":"안녕=평안   ·   하세요=높임말","size":46,"color":(120,120,145),"pos":(540,1070),"in":"fade","t_in":1.7},
 ]},
 # 4. 사용 — 프리젠터 + 타이핑 콜아웃 + 체크
 {"dur":3.2,"sub":"이렇게 인사해요!","els":[
   {"type":"presenter","img":ZC,"h":840,"flip":False,"pos":(290,1320),"bob":9,"in":"slide_r","t_in":0.1},
   {"type":"spotlight","pos":(660,640),"r":300,"t_in":0.5,"strength":0.45},
   {"type":"text","text":"안녕하세요!","size":118,"color":(40,40,62),"pos":(660,640),"in":"type","in_dur":1.3,"t_in":0.6},
   {"type":"check","pos":(660,830),"size":84,"t_in":2.2},
 ]},
 # 5. 마무리 — 단어 팝 + 영어 + 체크
 {"dur":2.6,"sub":"참 쉽죠? 다음에 또 배워요!","els":[
   {"type":"text","text":"안녕하세요","size":150,"color":(40,40,62),"pos":(540,700),"in":"pop","t_in":0.1},
   {"type":"text","text":"Hello!","size":82,"color":(36,150,170),"pos":(540,880),"in":"fade","t_in":0.7},
   {"type":"check","pos":(540,1040),"size":92,"t_in":1.1},
 ]},
]

if __name__=="__main__":
    E.render(SCENES, os.path.join(os.path.dirname(__file__),"_demo_lesson.mp4"), bgkind="pastel")
