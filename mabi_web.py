import streamlit as st
import requests
import urllib.parse
import time
import pandas as pd
import base64
import os
from datetime import datetime

# =========================================================
# 설정 및 변수 선언
# =========================================================
FIXED_API_KEY = st.secrets["my_api_key"]

SHOPPING_LIST = {
    "탈틴 농장 달콤 케이크": 3,
    "탈틴 농장 레드문 귀걸이": 3,
    "탈틴 농장 천연 고무": 3,
    "탈틴 농장 재스민 향수": 2,
    "탈틴 농장 장식용 크리스탈 검": 2,
    "남동판": 2,
    "백연판": 2,
    "산딸기 크림 소스 박스": 2,
    "루멘 시럽": 2
}

CATEGORIES = {
    "기본 생산품": [
        "탈틴 농장 일반 블랙베리", "탈틴 농장 고급 블랙베리", "탈틴 농장 최고급 블랙베리",
        "탈틴 농장 일반 오크라", "탈틴 농장 고급 오크라", "탈틴 농장 최고급 오크라",
        "탈틴 농장 일반 재스민", "탈틴 농장 고급 재스민", "탈틴 농장 최고급 재스민",
        "탈틴 농장 일반 붉은 배", "탈틴 농장 고급 붉은 배", "탈틴 농장 최고급 붉은 배",
        "탈틴 농장 일반 고무", "탈틴 농장 고급 고무", "탈틴 농장 최고급 고무",
        "탈틴 농장 일반 마법 거미줄", "탈틴 농장 고급 마법 거미줄", "탈틴 농장 최고급 마법 거미줄",
        "탈틴 농장 일반 석영", "탈틴 농장 고급 석영", "탈틴 농장 최고급 석영"
    ],
    "풍요로운 마법의 솥": [
        "탈틴 농장 블랙베리 주스", "탈틴 농장 달콤 케이크", "탈틴 농장 붉은 배 잼",
        "탈틴 농장 별무늬 샐러드", "탈틴 농장 재스민 향수"
    ],
    "부드러운 마법의 솥": [
        "탈틴 농장 자색 원단", "탈틴 농장 꽃무늬 원피스", "탈틴 농장 방수 원단",
        "탈틴 농장 강화 섬유", "탈틴 농장 이브닝 드레스"
    ],
    "반짝이는 마법의 솥": [
        "탈틴 농장 레드문 귀걸이", "탈틴 농장 퓨어 블러썸 머리핀", "탈틴 농장 석영 파우더",
        "탈틴 농장 미드나잇 펄 페인트", "탈틴 농장 장식용 크리스탈 검"
    ],
    "섬세한 마법의 솥": [
        "탈틴 농장 강력 접착제", "탈틴 농장 천연 고무", "탈틴 농장 누름꽃 공예 함",
        "탈틴 농장 황혼의 류트", "탈틴 농장 새벽의 활"
    ]
}

DELIVERY_QUESTS = {
    "두갈드 아일 목수의 주문": {"limit": 7, "coin": 330, "materials": {"탈틴 농장 일반 블랙베리": 1, "탈틴 농장 자색 원단": 2, "탈틴 농장 붉은 배 잼": 2}},
    "슬리아브 퀼린 광부의 주문": {"limit": 7, "coin": 240, "materials": {"탈틴 농장 일반 오크라": 1, "탈틴 농장 강력 접착제": 2, "탈틴 농장 방수 원단": 2}},
    "레자르 양조장 관리인의 주문": {"limit": 7, "coin": 250, "materials": {"탈틴 농장 일반 재스민": 2, "탈틴 농장 레드문 귀걸이": 2, "탈틴 농장 달콤 케이크": 1}},
    "탈틴 괴짜 연금술사의 주문": {"limit": 7, "coin": 230, "materials": {"탈틴 농장 일반 붉은 배": 1, "탈틴 농장 블랙베리 주스": 1, "탈틴 농장 석영 파우더": 1}},
    "케안 항구 선원의 주문": {"limit": 7, "coin": 320, "materials": {"탈틴 농장 일반 고무": 2, "탈틴 농장 천연 고무": 1, "탈틴 농장 별무늬 샐러드": 1}},
    "센마이 상점가 점원의 주문": {"limit": 7, "coin": 400, "materials": {"탈틴 농장 일반 마법 거미줄": 2, "탈틴 농장 꽃무늬 원피스": 1, "탈틴 농장 누름꽃 공예 함": 1}},
    "반호르 시계 장인의 주문": {"limit": 7, "coin": 300, "materials": {"탈틴 농장 일반 석영": 2, "탈틴 농장 퓨어 블러썸 머리핀": 1, "탈틴 농장 강화 섬유": 1}},
    "이멘 마하 인테리어 전문가의 주문": {"limit": 5, "coin": 320, "materials": {"탈틴 농장 자색 원단": 1, "탈틴 농장 미드나잇 펄 페인트": 2, "탈틴 농장 방수 원단": 1}},
    "음유시인 캠프 방랑자의 주문": {"limit": 5, "coin": 700, "materials": {"탈틴 농장 퓨어 블러썸 머리핀": 2, "탈틴 농장 황혼의 류트": 1, "탈틴 농장 석영 파우더": 1}},
    "던바튼 주민의 주문": {"limit": 5, "coin": 270, "materials": {"탈틴 농장 레드문 귀걸이": 1, "탈틴 농장 새벽의 활": 1, "탈틴 농장 누름꽃 공예 함": 1}},
    "오스나 사일 산지기의 주문": {"limit": 5, "coin": 330, "materials": {"탈틴 농장 달콤 케이크": 1, "탈틴 농장 이브닝 드레스": 2, "탈틴 농장 붉은 배 잼": 2}},
    "티르코네일 보부상의 주문": {"limit": 5, "coin": 400, "materials": {"탈틴 농장 강력 접착제": 2, "탈틴 농장 장식용 크리스탈 검": 1, "탈틴 농장 천연 고무": 2}},
    "카브 항구 의상 디자이너의 주문": {"limit": 5, "coin": 650, "materials": {"탈틴 농장 블랙베리 주스": 2, "탈틴 농장 재스민 향수": 1, "탈틴 농장 꽃무늬 원피스": 1}},
    "케안 항구 무역 사무원의 주문": {"limit": 5, "coin": 840, "materials": {"탈틴 농장 별무늬 샐러드": 2, "탈틴 농장 새벽의 활": 2, "탈틴 농장 이브닝 드레스": 2}},
    "아브네아 상점가 점원의 주문": {"limit": 5, "coin": 320, "materials": {"탈틴 농장 강화 섬유": 2, "탈틴 농장 장식용 크리스탈 검": 2, "탈틴 농장 황혼의 류트": 2}},
    "타라 '큰손'의 주문": {"limit": 5, "coin": 538, "materials": {"탈틴 농장 이브닝 드레스": 2, "탈틴 농장 미드나잇 펄 페인트": 2, "탈틴 농장 재스민 향수": 2}},
    "라흐 왕성 시종의 주문": {"limit": 5, "coin": 640, "materials": {"탈틴 농장 재스민 향수": 2, "탈틴 농장 장식용 크리스탈 검": 2, "탈틴 농장 새벽의 활": 2}}
}

# =========================================================
# 납품 보상 아이템 상점 판매가 (골드 기준, 확정값)
# 나중에 퀘스트별 보상 풀이 다를 때 여기서 수정하세요
# =========================================================
REWARD_ITEMS = {
    "탈틴 농장 업그레이드 벽돌": 10000,
    "탈틴 농장 업그레이드 철판": 20000,
    "탈틴 농장 업그레이드 도료": 30000,
    "탈틴 농장 업그레이드 유리": 40000,
    "탈틴 협회 열쇠": 25000,
}
# 보상 기대값 = 전체 보상 아이템 평균 (동일 확률 가정)
REWARD_EXPECTED_VALUE = sum(REWARD_ITEMS.values()) / len(REWARD_ITEMS)  # 25,000 G

# =========================================================
# 페이지 설정 및 CSS
# =========================================================
st.set_page_config(page_title="마비노기 물교&경매장 계산기", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #1a1c24; }
    .stApp p, .stApp span, .stApp label, .stApp li { color: #ffffff !important; font-weight: 500; }
    div[data-testid="stJson"], div[data-testid="stJson"] pre { background-color: #262730 !important; color: #ffffff !important; border-radius: 5px; }
    .stTable { background-color: #262730 !important; }
    .stTable th { background-color: #31333f !important; color: #ffffff !important; font-weight: bold; }
    .stTable td { color: #e0e0e0 !important; border-bottom: 1px solid #3f404d !important; }
    div[data-testid="stExpander"] { background-color: #2d303d !important; border: 1px solid #4a4d5e !important; border-radius: 8px; }
    div[data-testid="stExpander"] .streamlit-expanderHeader { color: #ffffff !important; background-color: transparent !important; }
    div[data-testid="stExpander"] .streamlit-expanderContent { background-color: #262730 !important; color: #ffffff !important; }
    input { color: #ffffff !important; background-color: #3f404d !important; }
    div[data-testid="stMetricValue"] { color: #00ffc8 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #2d303d !important; border: 1px solid #4a4d5e !important; }
    /* 손익 표 강조 스타일 */
    .profit-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .profit-table th { background-color: #31333f; color: #ffffff; padding: 8px 12px; text-align: left; border-bottom: 2px solid #4a4d5e; }
    .profit-table td { padding: 7px 12px; border-bottom: 1px solid #3a3d4d; color: #e0e0e0; }
    .profit-table tr:hover td { background-color: #2d303d; }
    .badge-profit { background-color: #1a4a3a; color: #00ffc8; padding: 3px 10px; border-radius: 10px; font-weight: bold; font-size: 12px; }
    .badge-loss { background-color: #4a1a1a; color: #ff6b6b; padding: 3px 10px; border-radius: 10px; font-weight: bold; font-size: 12px; }
    .badge-neutral { background-color: #3a3a1a; color: #ffd166; padding: 3px 10px; border-radius: 10px; font-weight: bold; font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💰 마비노기 물교 & 경매장 계산기")

# =========================================================
# 헬퍼 함수
# =========================================================
@st.cache_data(ttl=60)
def fetch_all_prices(key):
    # 납품 재료 + 탈농 아이템 전체를 한 번에 조회 (10분 캐시)
    item_set = set()
    for q_data in DELIVERY_QUESTS.values():
        item_set.update(q_data['materials'].keys())
    for cat_items in CATEGORIES.values():
        item_set.update(cat_items)

    price_map = {}
    for item in item_set:
        url = f'https://open.api.nexon.com/mabinogi/v1/auction/list?item_name={urllib.parse.quote(item)}'
        headers = {'x-nxopen-api-key': key, 'accept': 'application/json'}
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 429:
                time.sleep(3)
                res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                items_data = res.json().get('auction_item', [])
                if items_data:
                    items_data.sort(key=lambda x: x['auction_price_per_unit'])
                    price_map[item] = items_data[0]['auction_price_per_unit']
                else:
                    price_map[item] = 0
        except:
            price_map[item] = 0
        time.sleep(0.05)
    return price_map

# 장바구니 단건 조회용
@st.cache_data(ttl=60)
def get_price(item_name, key):
    url = f'https://open.api.nexon.com/mabinogi/v1/auction/list?item_name={urllib.parse.quote(item_name)}'
    headers = {'x-nxopen-api-key': key, 'accept': 'application/json'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            items = res.json().get('auction_item', [])
            if items:
                items.sort(key=lambda x: x['auction_price_per_unit'])
                return items[0]['auction_price_per_unit']
    except:
        pass
    return 0

def display_item_with_local_image(item_name, price):
    image_path = f"images/{item_name}.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            img_src = f"data:image/png;base64,{encoded_string}"
    else:
        img_src = "https://via.placeholder.com/30"

    html_code = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; padding: 8px 12px; border-radius: 8px; background-color: rgba(150, 150, 150, 0.1);">
        <div style="display: flex; align-items: center;">
            <img src="{img_src}" style="width: 28px; height: 28px; margin-right: 12px; background-color: transparent;">
            <span style="font-size: 14px;">{item_name}</span>
        </div>
        <strong style="font-size: 15px;">{int(price):,} G</strong>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# =========================================================
# ★ 섹션 0: 납품 손익 분석 (최상단)
# =========================================================
st.header("🏆 납품 퀘스트 손익 분석 (시즌 말 탈농 가격 하락 대비)")

# 퀘스트별 보상 개수 범위 정의
# 1번 사진 (보상 1~3개): 케안 항구 무역 사무원, 아브네아 상점가 점원, 타라 큰손, 라흐 왕성 시종
# 2번 사진 + 카브 항구 의상 디자이너 (보상 1~2개): 이멘 마하, 음유시인 캠프, 던바튼, 오스나 사일, 티르코네일, 카브 항구
# 나머지 7회짜리: 보상 1개 고정
# 퀘스트별 (열쇠 개수 범위, 업그레이드 템 개수 범위) 정의
# 7회짜리: 둘 다 1개 고정
# 1번사진 4개: 둘 다 1~3개
# 2번사진+카브항구: 둘 다 1~2개
REWARD_COUNT_RANGE = {
    # (열쇠 범위, 업그레이드 템 범위)
    "케안 항구 무역 사무원의 주문":    ([1,2,3], [1,2,3]),
    "아브네아 상점가 점원의 주문":     ([1,2,3], [1,2,3]),
    "타라 '큰손'의 주문":             ([1,2,3], [1,2,3]),
    "라흐 왕성 시종의 주문":           ([1,2,3], [1,2,3]),
    "이멘 마하 인테리어 전문가의 주문": ([1,2],   [1,2]),
    "음유시인 캠프 방랑자의 주문":     ([1,2],   [1,2]),
    "던바튼 주민의 주문":              ([1,2],   [1,2]),
    "오스나 사일 산지기의 주문":       ([1,2],   [1,2]),
    "티르코네일 보부상의 주문":        ([1,2],   [1,2]),
    "카브 항구 의상 디자이너의 주문":  ([1,2],   [1,2]),
}
# 7회짜리는 정의 없으면 (1개 고정, 1개 고정) 처리

with st.expander("ℹ️ 계산 방식 안내", expanded=False):
    st.markdown(f"""
    - **재료비**: 납품 1회 재료를 경매장 최저가로 구매 시 비용 × 납품 횟수
    - **보상 기대값**: 납품 1회당 아래 5종 중 랜덤 1개 (동일 확률 가정), 1회 평균 **{REWARD_EXPECTED_VALUE:,.0f} G**
    - 퀘스트별로 보상 개수(1~3개)가 다르므로 각 행 드롭다운으로 경우의 수 선택 가능
    - **손익** = 총 보상 기대값 − 총 재료비

    | 보상 아이템 | 상점 판매가 |
    |---|---|
    | 탈틴 농장 업그레이드 벽돌 | 10,000 G |
    | 탈틴 농장 업그레이드 철판 | 20,000 G |
    | 탈틴 농장 업그레이드 도료 | 30,000 G |
    | 탈틴 농장 업그레이드 유리 | 40,000 G |
    | 탈틴 협회 열쇠 | 25,000 G |
    """)

# 시세 자동 조회 (5분 캐시)
with st.spinner("납품 재료 경매장 시세 조회 중... (최초 1회, 이후 10분간 캐시)"):
    price_map = fetch_all_prices(FIXED_API_KEY)
fetched_at = datetime.now().strftime('%H:%M:%S')

# 갱신 버튼 + 조회 시각
col_refresh, col_cap = st.columns([1, 6])
with col_refresh:
    if st.button("🔄 지금 새로고침", key="btn_roi_refresh"):
        st.cache_data.clear()
        st.rerun()
with col_cap:
    st.caption(f"경매장 최저가 기준 | 조회: {fetched_at} | 10분마다 자동 갱신")

st.divider()

# 퀘스트별 손익 — 헤더 + expander 슬라이더 시뮬레이터

KEY_VALUE = 25000
UPGRADE_ITEMS = {
    "벽돌": 10000,
    "철판": 20000,
    "도료": 30000,
    "유리": 40000,
}

def profit_badge(p):
    if p > 0:   return f"🟢 +{p:,} G"
    elif p < 0: return f"🔴 {p:,} G"
    else:       return f"⚪ 0 G"

def profit_color(p):
    if p > 0:   return "#00ffc8"
    elif p < 0: return "#ff6b6b"
    else:       return "#ffd166"

for q_name, q_data in DELIVERY_QUESTS.items():
    limit = q_data['limit']
    cost_per_run = int(sum(price_map.get(mat, 0) * cnt for mat, cnt in q_data['materials'].items()))
    missing = [m.replace("탈틴 농장 ", "") for m in q_data['materials'] if price_map.get(m, 0) == 0]
    key_range, upg_range = REWARD_COUNT_RANGE.get(q_name, ([1], [1]))
    is_fixed = len(key_range) == 1 and len(upg_range) == 1

    with st.container(border=True):
        # 헤더
        c1, c2, c3, c4 = st.columns([4, 1, 2, 2])
        with c1:
            st.markdown(f"**{q_name}**")
            if missing:
                st.caption(f"⚠️ 매물없음: {', '.join(missing)}")
        with c2:
            st.caption("납품 횟수")
            st.markdown(f"**{limit}회**")
        with c3:
            st.caption("1회 재료비")
            st.markdown(f"**{cost_per_run:,} G**")
        with c4:
            st.caption("보상 범위")
            if is_fixed:
                st.markdown("**열쇠·업템 각 1개 고정**")
            else:
                st.markdown(f"**열쇠 {key_range[0]} ~ {key_range[-1]}개 / 업템 {upg_range[0]} ~ {upg_range[-1]}개**")

        # 시뮬레이터 expander
        with st.expander("🎲 보상 시뮬레이터", expanded=False):
            s1, s2, s3 = st.columns([1, 2, 1])

            with s1:
                st.caption("🗝️ 열쇠 개수")
                if is_fixed:
                    sel_key = 1
                    st.markdown("**1개 고정**")
                else:
                    sel_key = st.radio(
                        "열쇠 개수",
                        options=key_range,
                        horizontal=True,
                        key=f"key_radio_{q_name}",
                        label_visibility="collapsed",
                        format_func=lambda x: f"{x}개"
                    )

            with s2:
                st.caption("🧱 업그레이드 템 종류")
                sel_upg_name = st.radio(
                    "업템 종류",
                    options=list(UPGRADE_ITEMS.keys()),
                    horizontal=True,
                    key=f"upg_type_{q_name}",
                    label_visibility="collapsed",
                    format_func=lambda x: f"{x} ({UPGRADE_ITEMS[x]//10000}만G)"
                )
                st.caption("🔢 업그레이드 템 개수")
                if is_fixed:
                    sel_upg_cnt = 1
                    st.markdown("**1개 고정**")
                else:
                    sel_upg_cnt = st.radio(
                        "업템 개수",
                        options=upg_range,
                        horizontal=True,
                        key=f"upg_radio_{q_name}",
                        label_visibility="collapsed",
                        format_func=lambda x: f"{x}개"
                    )

            # 결과 계산
            reward_val = KEY_VALUE * sel_key + UPGRADE_ITEMS[sel_upg_name] * sel_upg_cnt
            profit_val = reward_val - cost_per_run
            color = profit_color(profit_val)

            with s3:
                st.caption("📊 결과")
                st.markdown(f"재료비 **{cost_per_run:,} G**")
                st.markdown(f"보상 합계 **{reward_val:,} G**")
                st.markdown(
                    f"<div style='font-size:18px; font-weight:bold; color:{color};'>{profit_badge(profit_val)}</div>",
                    unsafe_allow_html=True
                )

st.caption("※ 열쇠 1개 = 25,000 G | 업그레이드 템 가격: 벽돌 1만 / 철판 2만 / 도료 3만 / 유리 4만 | 1회 납품 기준")

st.divider()

# =========================================================
# 섹션 1: 고정 목록 (물교 재료)
# =========================================================
st.header("📅 이번 주 물교 6티어 재료")
st.info("코드 상단에서 설정한 고정 리스트입니다.")

with st.expander("📋 목록 확인하기 (클릭)", expanded=True):
    st.write(SHOPPING_LIST)

if st.button("6티어 재료 견적 확인하기 🚀", type="primary"):
    if "여기에" in FIXED_API_KEY or len(FIXED_API_KEY) < 10:
         st.error("코드 상단에 API 키를 먼저 입력해주세요!")
         st.stop()

    total_price = 0
    result_data = []
    my_bar = st.progress(0, text="시세 조회 중...")

    for idx, (name, count) in enumerate(SHOPPING_LIST.items()):
        price = get_price(name, FIXED_API_KEY)
        subtotal = price * count
        total_price += subtotal
        result_data.append({
            "아이템": name,
            "최저가": f"{price:,} G" if price > 0 else "매물없음",
            "수량": f"{count}개",
            "합계": f"{subtotal:,} G"
        })
        time.sleep(0.05)
        my_bar.progress((idx + 1) / len(SHOPPING_LIST))

    my_bar.empty()

    col1, col2 = st.columns(2)
    with col1: st.metric("총 필요 골드", f"{total_price:,} Gold")
    with col2: st.metric("1/N (절반)", f"{int(total_price/2):,} Gold")

    st.table(result_data)

st.divider()

# =========================================================
# 섹션 2: 자유 검색 (장바구니)
# =========================================================
st.header("🔍 개별 품목 검색 (장바구니)")
st.caption("위의 고정 목록 외에 따로 검색하고 싶은 아이템이 있다면 추가하세요.")

if 'cart' not in st.session_state:
    st.session_state.cart = []

with st.form("add_item_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: input_name = st.text_input("아이템 이름")
    with c2: input_count = st.number_input("수량", min_value=1, value=1)
    with c3: submitted = st.form_submit_button("추가 ➕")

    if submitted and input_name:
        st.session_state.cart.append({"name": input_name, "count": input_count})
        st.success(f"추가됨: {input_name}")

if st.session_state.cart:
    st.write(f"현재 담긴 품목: {len(st.session_state.cart)}개")
    for i, item in enumerate(st.session_state.cart):
        col_name, col_count, col_btn = st.columns([3, 1, 1])
        with col_name: st.write(item['name'])
        with col_count: st.write(f"{item['count']}개")
        with col_btn:
            if st.button("삭제", key=f"del_cart_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
    st.divider()
    if st.button("목록 비우기 🗑️"):
        st.session_state.cart = []
        st.rerun()

    if st.button("장바구니 견적 확인하기 🔎"):
        total_cart = 0
        cart_result = []
        bar2 = st.progress(0, text="검색 중...")
        for idx, item in enumerate(st.session_state.cart):
            p = get_price(item['name'], FIXED_API_KEY)
            sub = p * item['count']
            total_cart += sub
            cart_result.append({
                "아이템": item['name'],
                "최저가": f"{p:,} G" if p > 0 else "매물없음",
                "수량": f"{item['count']}개",
                "합계": f"{sub:,} G"
            })
            time.sleep(0.05)
            bar2.progress((idx + 1) / len(st.session_state.cart))
        bar2.empty()
        st.metric("장바구니 총액", f"{total_cart:,} Gold")
        st.table(cart_result)

st.divider()

# =========================================================
# 섹션 3: 물물교환 참고표
# =========================================================
st.header("📚 물물교환 재료 참고표")
st.markdown("""
> **💡 필수 팁** > 6티어는 본인 특화는 자급, 나머지는 경매장 구매 추천!  
> **그랜마 상인 + 윌리엄or교역파트너 부유선(6티어탈농만루트),알파카(6티어원루트) + 임프의 고급 보증서(필수!) >>> 탈틴 or 티르코네일 판매**""")

tab2, tab1 = st.tabs(["🛠️ 6티어 탈농만 루트", "📚 기존 표준 루트"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🧪 포션 & 목공")
        st.markdown("""
        **[포션]**
        - 생명력 500 포션: **14개**
        - 정령의 리큐르: **7개**
        
        **[목공]**
        - 최고급 나무장작: **9개**
        - 특급 나무장작: **9개**
        - 중급 나무장작: **35개**
        
        **[핸디크래프트]**
        - 건초더미: **9개**
        - 독묻은 와이번 볼트: **9개**
        """)
        st.markdown("""
        🛒 **교역소별 구매 목록 및 수량(구매순서는 페라 > 칼리다 > 오아시스 > 카루)**
     
        | 교역소 | 4T | 5T | 6T |
        | :---: | :---: | :---: | :---: |
        | **페라** | 7개 | 3개 | 2개 |
        | **칼리다** | - | 3개 | 2개 |
        | **오아시스** | 7개 | 3개 | 2개 |
        | **카루** | 7개 | 3개 | **3개** |
       """)
    with col2:
        st.markdown("### 🧵 방직 & 공학")
        st.markdown("""
        **[방직]**
        - 고급 옷감: **28개**
        - 최고급 옷감: **35개**
        - 튼튼한 고리: **3개**
        - 고급 실크: **28개**

        **[매직 크래프트]**
        - 마력이 깃든 나무장작: **15개**
        - 뮤턴트: **3개**

        **[힐웬 공학]**
        - 에너지 증폭 장치: **6개**
        - 스핀 기어: **7개**
        """)
    with col3:
        st.markdown("### 💎 제련 & 기타")
        st.markdown("""
        **[제련]**
        - 은판: **14개**
        - 미스릴 대못: **9개**

        **[기타]**
        - 반짝이 종이: **35개**
        - 마법의 깃털펜: **15개**
        - 조화의 코스모스 퍼퓸: **6개**
        - 펫 놀이세트: **3개**

        **[희귀 재료]**
        - 탈틴 농장 달콤 케이크: **3개**
        - 탈틴 농장 레드문 귀걸이: **3개**
        - 탈틴 농장 천연 고무: **3개**
        - 탈틴 농장 재스민 향수: **2개**
        - 탈틴 농장 장식용 크리스탈 검: **2개**
        - 남동판: **2개**
        - 백연판: **2개**
        - 산딸기 크림 소스 박스: **2개**
        - 루멘 시럽: **2개** """)

with tab2:
    col1_c, col2_c, col3_c = st.columns(3)
    with col1_c:
        st.markdown("### 🧪 포션 & 목공")
        st.markdown("""
        **[포션]**
        - 생명력 500 포션: **14개**
        - 정령의 리큐르: **7개**
        
        **[목공]**
        - 최고급 나무장작: **9개**
        - 특급 나무장작: **9개**
        - 중급 나무장작: **35개**
        
        **[핸디크래프트]**
        - 건초더미: **9개**
        - 독묻은 와이번 볼트: **9개**
        """)
        st.markdown("""
        🛒 **교역소별 구매 목록 및 수량**<br>
        🛒 **윌리엄or교역파트너 + 부유선**<br>
        (구매순서는 페라 > 칼리다 > 오아시스 > 카루)
     
        | 교역소 | 4T | 5T | 6T |
        | :---: | :---: | :---: | :---: |
        | **페라** | 7개 | 3개 | - |
        | **칼리다** | 7개 | 3개 | - |
        | **오아시스** | 7개 | 3개 | 2개 |
        | **카루** | 7개 | 3개 | **3개** |
       """, unsafe_allow_html=True)
    with col2_c:
        st.markdown("### 🧵 방직 & 공학")
        st.markdown("""
        **[방직]**
        - 고급 옷감: **28개**
        - 최고급 옷감: **35개**
        - 튼튼한 고리: **3개**
        - 고급 실크: **28개**
        - 고급 가죽 끈: **35개**

        **[매직 크래프트]**
        - 마력이 깃든 나무장작: **15개**
        - 뮤턴트: **3개**

        **[힐웬 공학]**
        - 에너지 증폭 장치: **6개**
        - 스핀 기어: **7개**
        - 에메랄드 퓨즈: **7개**
        """)
    with col3_c:
        st.markdown("### 💎 제련 & 기타")
        st.markdown("""
        **[제련]**
        - 은판: **14개**
        - 미스릴 대못: **9개**

        **[기타]**
        - 반짝이 종이: **35개**
        - 마법의 깃털펜: **15개**
        - 조화의 코스모스 퍼퓸: **6개**
        - 펫 놀이세트: **3개**
        - 인조 잔디: **7개**

        **[희귀 재료]**
        - 탈틴 농장 달콤 케이크: **3개**
        - 탈틴 농장 레드문 귀걸이: **3개**
        - 탈틴 농장 천연 고무: **3개**
        - 탈틴 농장 재스민 향수: **2개**
        - 탈틴 농장 장식용 크리스탈 검: **2개**
        - 남동판: **2개**
        - 백연판: **2개**
        - 산딸기 크림 소스 박스: **2개**
        - 루멘 시럽: **2개** """)

st.divider()

# =========================================================
# 섹션 4: 아르바이트 보상 목록
# =========================================================
st.subheader("🕊️ 아르바이트 보상 받기 목록")
st.markdown("""
- **관청:** 잡보 아무거나
- **식료품:** 낙지
- **의류점:** **튼튼한 고리** (1순위) / 물교용 방직 재료 (2순위)
- **힐러:** 생명력 500 포션
- **서점:** 마법의 깃털펜
""")

# =========================================================
# 섹션 5: 탈틴 농장 실시간 시세
# =========================================================
st.divider()
st.header("📈 탈틴 농장 실시간 시세")

with st.spinner("탈틴 농장 시세 불러오는 중... (캐시 유효 시 즉시)"):
    farm_price_map = fetch_all_prices(FIXED_API_KEY)
farm_fetched_at = datetime.now().strftime('%H:%M:%S')

col_farm_refresh, col_farm_cap = st.columns([1, 6])
with col_farm_refresh:
    if st.button("🔄 새로고침", key="btn_farm_refresh"):
        st.cache_data.clear()
        st.rerun()
with col_farm_cap:
    st.caption(f"경매장 최저가 기준 | 조회: {farm_fetched_at} | 10분마다 자동 갱신")

st.subheader("기본 생산품")
cols_basic = st.columns(3)
for idx, item in enumerate(CATEGORIES["기본 생산품"]):
    with cols_basic[idx % 3]:
        display_item_with_local_image(item, farm_price_map.get(item, 0))

st.divider()
st.subheader("가공품")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**풍요로운 마법의 솥**")
    for item in CATEGORIES["풍요로운 마법의 솥"]:
        display_item_with_local_image(item, farm_price_map.get(item, 0))
    st.write("")
    st.markdown("**반짝이는 마법의 솥**")
    for item in CATEGORIES["반짝이는 마법의 솥"]:
        display_item_with_local_image(item, farm_price_map.get(item, 0))
with col2:
    st.markdown("**부드러운 마법의 솥**")
    for item in CATEGORIES["부드러운 마법의 솥"]:
        display_item_with_local_image(item, farm_price_map.get(item, 0))
    st.write("")
    st.markdown("**섬세한 마법의 솥**")
    for item in CATEGORIES["섬세한 마법의 솥"]:
        display_item_with_local_image(item, farm_price_map.get(item, 0))

# =========================================================
# 섹션 7: 생활 협회 납품 퀘스트 계산기
# =========================================================
st.divider()
st.header("📦 생활 협회 납품 퀘스트 계산기")
st.caption("진행하려는 퀘스트를 체크한 후 계산하기를 누르면, 필요한 총 재료를 합산하여 경매장 최저가를 검색합니다.")

quest_names = list(DELIVERY_QUESTS.keys())
half_idx = len(quest_names) // 2 + 1

for q_name in quest_names:
    if f"chk_{q_name}" not in st.session_state: st.session_state[f"chk_{q_name}"] = False

col_btn1, col_btn2, _ = st.columns([1, 1, 6])
with col_btn1:
    if st.button("전체 선택", use_container_width=True, type="primary"):
        for q_name in quest_names: st.session_state[f"chk_{q_name}"] = True
with col_btn2:
    if st.button("전체 해제", use_container_width=True):
        for q_name in quest_names: st.session_state[f"chk_{q_name}"] = False

selected_quests = []
col_q1, col_q2 = st.columns(2)

with col_q1:
    for q_name in quest_names[:half_idx]:
        with st.container(border=True):
            q_info = DELIVERY_QUESTS[q_name]
            label = f"{q_name} (납품 {q_info['limit']}회)"
            if st.checkbox(label, key=f"chk_{q_name}"): selected_quests.append(q_name)
            tags_html = ""
            for k, v in q_info['materials'].items():
                short_name = k.replace("탈틴 농장 ", "")
                tags_html += f"<span style='display:inline-block; background-color:rgba(150,150,150,0.1); padding:4px 10px; border-radius:12px; font-size:12px; margin-right:6px; margin-top:4px; border: 1px solid rgba(150,150,150,0.2); color:gray;'>{short_name} <b>{v}</b>개</span>"
            st.markdown(f"<div style='margin-left: 28px; margin-bottom: 4px;'>{tags_html}</div>", unsafe_allow_html=True)

with col_q2:
    for q_name in quest_names[half_idx:]:
        with st.container(border=True):
            q_info = DELIVERY_QUESTS[q_name]
            label = f"{q_name} (납품 {q_info['limit']}회)"
            if st.checkbox(label, key=f"chk_{q_name}"): selected_quests.append(q_name)
            tags_html = ""
            for k, v in q_info['materials'].items():
                short_name = k.replace("탈틴 농장 ", "")
                tags_html += f"<span style='display:inline-block; background-color:rgba(150,150,150,0.1); padding:4px 10px; border-radius:12px; font-size:12px; margin-right:6px; margin-top:4px; border: 1px solid rgba(150,150,150,0.2); color:gray;'>{short_name} <b>{v}</b>개</span>"
            st.markdown(f"<div style='margin-left: 28px; margin-bottom: 4px;'>{tags_html}</div>", unsafe_allow_html=True)

st.divider()

multiplier = st.number_input("계산할 배수 (예: 3배 구매 진행 시 3 입력)", min_value=1, value=1, step=1)

if st.button("체크된 납품 퀘스트 견적 확인하기 🚀", type="primary", key="btn_quest_calc"):
    if not selected_quests: st.warning("선택된 퀘스트가 없습니다. 위에서 퀘스트를 하나 이상 체크해주세요!")
    else:
        aggregated_materials = {}
        for q_name in selected_quests:
            q_data = DELIVERY_QUESTS[q_name]
            limit = q_data['limit']
            for mat_name, mat_count in q_data['materials'].items():
                req_qty = mat_count * limit * multiplier
                if mat_name in aggregated_materials: aggregated_materials[mat_name] += req_qty
                else: aggregated_materials[mat_name] = req_qty

        quest_total_price = 0
        quest_result = []
        progress_bar = st.progress(0, text="경매장 시세 조회 중...")
        for idx, (item_name, count) in enumerate(aggregated_materials.items()):
            price = get_price(item_name, FIXED_API_KEY)
            subtotal = price * count
            quest_total_price += subtotal
            quest_result.append({"재료명": item_name, "최저가": f"{price:,} G" if price > 0 else "매물 없음", "필요 수량": f"{count}개", "합계": f"{subtotal:,} G"})
            time.sleep(0.05)
            progress_bar.progress((idx + 1) / len(aggregated_materials))
        progress_bar.empty()

        st.metric("총 예상 구매 비용", f"{quest_total_price:,} Gold")
        st.table(quest_result)

st.caption("Data based on NEXON Open API")
