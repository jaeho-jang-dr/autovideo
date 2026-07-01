#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_details.py — Generate detailed tourist information for 168 Korean scenic places.
Produces web/src/data/korea_places_details.json with high-quality descriptions, directions, links, and images.
"""
import os
import json
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "web", "src", "data")
OUT_FILE = os.path.join(OUT_DIR, "korea_places_details.json")
# Category translation helper for Unsplash queries
CAT_KEYWORDS = {
    "궁궐·역사": "palace,temple,historic",
    "강·공원": "river,park",
    "쇼핑·먹거리": "shopping,streetmarket",
    "산·자연": "mountain,nature",
    "섬·해변": "beach,island",
    "온천·레저": "resort,leisure",
    "박물관·미술관": "museum,artgallery",
    "default": "korean,touristspot"
}

# Image URL mapper by place name or category keywords
def get_image_url(name_en, category):
    kw = CAT_KEYWORDS.get(category, CAT_KEYWORDS["default"])
    # We combine the category keyword and "south korea" to retrieve a highly relevant Korean aesthetic photo
    query_str = f"{kw},south korea"
    return f"https://images.unsplash.com/featured/800x600/?{urllib.parse.quote(query_str)}"

# Ground truth custom high-quality mapping for top/prominent places
# Using 100% free and permanent Wikimedia Commons direct links
SPECIAL_DETAILS = {
    1: { # Han River
        "description_en": "The Han River flows through the heart of Seoul, offering a massive waterfront oasis. Parks along the river are famous for cycling, picnics with convenience-store instant ramen, and late-night fried chicken deliveries (Chimaek). It also hosts the annual spectacular Seoul International Fireworks Festival.",
        "description_ko": "서울의 중심을 가로지르는 한강은 넓은 수변 오아시스를 제공합니다. 한강공원은 자전거 타기, 편의점 즉석 라면 피크닉, 돗자리에 앉아 즐기는 치맥 배달 문화로 매우 유명하며, 매년 화려한 서울 세계 불꽃 축제가 개최되는 무대이기도 합니다.",
        "directions_en": "Subway Line 5 Yeouinaru Station, Exit 2 or 3 (Directly leads to Yeouido Hangang Park).",
        "directions_ko": "지하철 5호선 여의나루역 2번 또는 3번 출구 (여의도 한강공원으로 바로 연결).",
        "official_link": "https://hangang.seoul.go.kr/",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Seongsu_Bridge_at_Night_2020.jpg/800px-Seongsu_Bridge_at_Night_2020.jpg"
    },
    2: { # Gyeongbokgung Palace
        "description_en": "Built in 1395, Gyeongbokgung Palace is the largest and most iconic of the Five Grand Palaces built by the Joseon Dynasty. It served as the main royal palace, housing the kings and the government. Visitors frequently wear traditional Hanbok to experience the historic atmosphere and get free admission.",
        "description_ko": "1395년에 건립된 경복궁은 조선 왕조가 세운 5대 궁궐 중 가장 크고 대표적인 법궁입니다. 왕과 조정이 머물며 정사를 돌보던 역사적 중심지이며, 방문객들이 전통 한복을 입고 역사적인 분위기를 직접 체험하며 무료 입장 혜택을 즐기는 곳입니다.",
        "directions_en": "Subway Line 3 Gyeongbokgung Station, Exit 5 (Direct connection to the palace yard).",
        "directions_ko": "지하철 3호선 경복궁역 5번 출구 (궁궐 앞마당으로 직접 연결됨).",
        "official_link": "https://royal.cha.go.kr/GJB/html/HtmlPage.do?pg=/gjb/01/gjb01_01_01.jsp&mn=GD_01_01",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Gyeongbokgung-palace-Seoul-Korea.jpg/800px-Gyeongbokgung-palace-Seoul-Korea.jpg"
    },
    3: { # Myeongdong
        "description_en": "Myeongdong is Seoul's primary shopping district, beloved by tourists for its vibrant beauty shops, international fashion boutiques, and street food carts. The carts offer delicacies like grilled cheese skewers, hotteok, and egg bread, making it a culinary adventure.",
        "description_ko": "명동은 서울의 대표적인 쇼핑가로, 다채로운 뷰티 브랜드 숍, 글로벌 패션 매장, 그리고 맛있는 길거리 음식 리어카들로 외국인 관광객들에게 사랑받고 있습니다. 치즈 구이 꼬치, 호떡, 계란빵 등 다채로운 미식을 탐방할 수 있는 허브입니다.",
        "directions_en": "Subway Line 4 Myeongdong Station, Exit 5, 6, 7, or 8.",
        "directions_ko": "지하철 4호선 명동역 5, 6, 7, 8번 출구.",
        "official_link": "https://www.myeongdong.org/",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Myeong-dong_Shopping_Street_2016.jpg/800px-Myeong-dong_Shopping_Street_2016.jpg"
    },
    4: { # Namsan Seoul Tower
        "description_en": "Perched on Mt. Namsan in central Seoul, this landmark tower offers panoramic 360-degree views of the capital city. The observation decks, romantic love padlocks on the fence, and the cable car ride up the mountain make it a top destination for couples and tourists.",
        "description_ko": "서울 중심부 남산 꼭대기에 솟아 있는 랜드마크 타워로, 서울 전역을 360도 각도로 한눈에 조망할 수 있습니다. 전망대와 함께 사랑의 자물쇠를 매다는 야외 펜스, 그리고 하늘을 나는 남산 케이블카 탑승 체험으로 연인들과 관광객들의 필수 코스입니다.",
        "directions_en": "Take Namsan Sunhwan Shuttle Bus No. 01 from Myeongdong Station or Chungmuro Station, or ride the Namsan Cable Car.",
        "directions_ko": "명동역 또는 충무로역에서 남산순환버스 01번 탑승, 혹은 남산 케이블카 탑승 이용.",
        "official_link": "https://www.seoultower.co.kr/",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Seoul_Tower_by_USAG_Humphreys.jpg/800px-Seoul_Tower_by_USAG_Humphreys.jpg"
    },
    5: { # Bukchon Hanok Village
        "description_en": "Nestled between Gyeongbokgung and Changdeokgung, Bukchon is home to hundreds of traditional Korean houses (hanok) dating back to the Joseon Dynasty. It is a quiet residential neighborhood where visitors stroll through narrow scenic stone alleys while respecting residents' privacy.",
        "description_ko": "경복궁과 창덕궁 사이에 자리 잡은 북촌은 조선시대부터 이어져 온 전통 한옥 수백 채가 보존된 주거 지역입니다. 고즈넉한 돌담길과 좁은 골목길을 한복을 입고 거닐 수 있으며, 거주민들의 프라이버시를 존중하며 산책을 즐기는 예절이 필요합니다.",
        "directions_en": "Subway Line 3 Anguk Station, Exit 2. Walk straight for about 10 minutes.",
        "directions_ko": "지하철 3호선 안국역 2번 출구에서 북쪽 방향으로 도보 약 10분.",
        "official_link": "https://hanok.seoul.go.kr/",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Bukchon_Hanok_Village.jpg/800px-Bukchon_Hanok_Village.jpg"
    },
    8: { # Gwangjang Market
        "description_en": "As one of Korea's oldest traditional markets, Gwangjang is world-famous for its central food alley. Food stalls serve freshly fried bindaetteok (mung-bean pancakes), mayak gimbap (addictive mini seaweed rolls), and fresh yukhoe (beef tartare) under glowing market signs.",
        "description_ko": "한국에서 가장 오래된 전통시장 중 하나인 광장시장은 먹자골목으로 전 세계에 널리 알려졌습니다. 갓 부쳐낸 노릇노릇한 빈대떡, 한 번 먹으면 멈출 수 없는 마약김밥, 신선한 육회 등을 포장마차 감성의 빨간 간이의자에 앉아 활기차게 맛볼 수 있습니다.",
        "directions_en": "Subway Line 1 Jongno 5-ga Station, Exit 7 or 8.",
        "directions_ko": "지하철 1호선 종로5가역 7번 또는 8번 출구 바로 앞.",
        "official_link": "http://www.kwangjangmarket.co.kr/",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Gwangjang_Market_Street_Food_2017.jpg/800px-Gwangjang_Market_Street_Food_2017.jpg"
    },
    12: { # Seongsan Ilchulbong
        "description_en": "Seongsan Ilchulbong, also called Sunrise Peak, is an archetypal tuff cone formed by hydrovolcanic eruptions off Jeju Island. Designated a UNESCO World Natural Heritage site, climbing to its massive crater rim rewards hikers with a breathtaking ocean sunrise.",
        "description_ko": "일출봉으로 불리는 성산일출봉은 제주도 해안에서 수중 화산 분출로 형성된 전형적인 응회구입니다. 유네스코 세계자연유산으로 등재되어 있으며, 거대한 사발 모양의 분화구 정상에 오르면 탁 트인 제주 바다 위로 장엄하게 떠오르는 일출을 감상할 수 있습니다.",
        "directions_en": "From Jeju Intercity Bus Terminal, take Bus No. 111 or 112 directly to Seongsan Ilchulbong Bus Stop.",
        "directions_ko": "제주 시외버스터미널에서 111번 또는 112번 급행버스를 탑승하고 성산일출봉 정류장에서 하차.",
        "official_link": "https://www.jeju.go.kr/jeju/cultural/heritage/natural.htm",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Seongsan_Ilchulbong_Jeju.jpg/800px-Seongsan_Ilchulbong_Jeju.jpg"
    },
    41: { # Haeundae Beach
        "description_en": "Haeundae is Korea's most famous beach, featuring a wide 1.5km sandy coastline backed by futuristic skyscrapers. Known for its summer festivals, vibrant nightlife, and luxury ocean-view hotels, it is the ultimate resort destination in Busan.",
        "description_ko": "해운대해수욕장은 1.5km에 달하는 넓은 백사장과 미래적인 초고층 마천루들이 어우러진 한국 최고의 해변입니다. 다채로운 여름 축제와 버스킹, 화려한 밤문화, 오션뷰 호텔들로 휴양과 축제를 한 번에 즐길 수 있는 부산의 상징입니다.",
        "directions_en": "Busan Subway Line 2 Haeundae Station, Exit 3 or 5. Walk straight for 5 minutes.",
        "directions_ko": "부산 지하철 2호선 해운대역 3번 또는 5번 출구에서 해변 방향으로 도보 5분.",
        "official_link": "https://www.haeundae.go.kr/tour/index.do",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Haeundae_Beach_Busan_2015.jpg/800px-Haeundae_Beach_Busan_2015.jpg"
    }
}

def generate():
    # We will import list P from make_korea_places.py to ensure numbers match perfectly.
    import sys
    sys.path.insert(0, ROOT)
    try:
        import make_korea_places
        places_data = make_korea_places.P
    except Exception as e:
        print(f"Could not load make_korea_places: {e}")
        return

    print(f"Generating details for {len(places_data)} places...")
    
    details_db = {}
    
    for idx, item in enumerate(places_data):
        no = idx + 1
        name_ko, name_en, region_ko, category, leisure_ko, why_ko, why_en, motif = item
        
        region_en = make_korea_places.REGION_EN.get(region_ko, "Korea")
        
        # 1. Fallback Info Generation based on details
        # Ensure we have standard descriptions for all 168 places
        desc_en = f"Discover {name_en}, a popular {category} spot in {region_en}, South Korea. Famed for '{leisure_ko}', it offers visitors a delightful experience: {why_en}"
        desc_ko = f"{region_ko}에 위치한 인기 {category} 명소 {name_ko}입니다. '{leisure_ko}' 활동으로 널리 알려져 있으며, 다음과 같은 매력을 선사합니다: {why_ko}"
        
        # Smart Directions generator
        if region_ko == "서울":
            dir_en = f"Take Seoul Subway to near {name_en} in {region_ko}. Please check local navigation apps (Naver/Kakao Maps) for the optimal route."
            dir_ko = f"서울 지하철을 이용하여 {name_ko} 인근 역에서 하차하세요. 최적의 경로를 위해 네이버/카카오 지도 앱 확인을 권장합니다."
            if "궁" in name_ko:
                dir_en = f"Take Subway to near {name_en}. (e.g. Line 3 or 5 for palace cluster)."
                dir_ko = f"인근 지하철역에서 하차하여 도보로 이동 가능합니다. (고궁 지구는 지하철 3, 5호선 편리)."
        elif region_ko == "부산":
            dir_en = f"Take Busan Subway or city bus to {name_en}. Check Naver/Kakao maps for exact line transfers."
            dir_ko = f"부산 도시철도 및 시내버스를 이용해 편리하게 찾아갈 수 있습니다. 상세 경로는 지도 앱을 참고하세요."
        elif region_ko == "제주":
            dir_en = f"From Jeju Airport, ride a rental car or take a Jeju express/trunk bus heading to {name_en}."
            dir_ko = f"제주국제공항에서 렌터카를 대여하거나, {name_ko} 방향 시외/급행버스를 탑승하세요."
        else:
            dir_en = f"Access via express bus or regional trains to {region_en}. Renting a car or taking a taxi is recommended."
            dir_ko = f"{region_ko} 지역 버스터미널 또는 열차역에서 하차 후 대중교통이나 택시, 렌터카로 이동을 권장합니다."
            
        # Map Link
        encoded_query = urllib.parse.quote(f"{name_en}, {region_en}, South Korea")
        map_link = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
        
        # Official Website Link
        official_link = "https://english.visitkorea.or.kr"
        
        # Image URL
        image_url = get_image_url(name_en, category)
        
        # Match Special Details by comparing Name_en or Number
        # Note: Gyeongbokgung is no 2 in make_korea_places.py and Han River is no 1, let's match by name_en instead of no
        matched_sd = None
        for k, sd in SPECIAL_DETAILS.items():
            # If the index is matching or if the name matches
            if k == no:
                matched_sd = sd
                break
        
        # Let's also do a name-based match for safety
        for k, sd in SPECIAL_DETAILS.items():
            if k == 2 and "gyeongbokgung" in name_en.lower():
                matched_sd = sd
            elif k == 1 and "han river" in name_en.lower():
                matched_sd = sd
            elif k == 3 and "myeongdong" in name_en.lower() and "night" not in name_en.lower():
                matched_sd = sd
            elif k == 4 and "namsan seoul tower" in name_en.lower():
                matched_sd = sd
            elif k == 5 and "bukchon hanok" in name_en.lower():
                matched_sd = sd
            elif k == 8 and "gwangjang" in name_en.lower():
                matched_sd = sd
            elif k == 12 and "seongsan ilchulbong" in name_en.lower():
                matched_sd = sd
            elif k == 41 and "haeundae beach" in name_en.lower():
                matched_sd = sd

        if matched_sd:
            desc_en = matched_sd.get("description_en", desc_en)
            desc_ko = matched_sd.get("description_ko", desc_ko)
            dir_en = matched_sd.get("directions_en", dir_en)
            dir_ko = matched_sd.get("directions_ko", dir_ko)
            map_link = matched_sd.get("map_link", map_link)
            official_link = matched_sd.get("official_link", official_link)
            image_url = matched_sd.get("image_url", image_url)
            
        details_db[str(no)] = {
            "no": no,
            "description_en": desc_en,
            "description_ko": desc_ko,
            "directions_en": dir_en,
            "directions_ko": dir_ko,
            "map_link": map_link,
            "official_link": official_link,
            "image_url": image_url
        }
        
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(details_db, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated {len(details_db)} items to {OUT_FILE}")

if __name__ == "__main__":
    generate()
