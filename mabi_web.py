import streamlit as st
import requests
import urllib.parse
import time
import pandas as pd
import gspread
import json
import plotly.express as px
import base64
import os
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# =========================================================
# 설정 및 변수 선언
# =========================================================
FIXED_API_KEY = st.secrets["my_api_key"]

SHOPPING_LIST = {
    "탈틴 농장 블랙베리 주스": 3,
    "탈틴 농장 퓨어 블러썸 머리핀": 3,
    "탈틴 농장 방수 원단": 3,
    "탈틴 농장 이브닝 드레스": 2,
    "탈틴 농장 별무늬 샐러드": 2,
    "남동판": 2,
    "희귀 버섯 볶음 박스": 2,
    "월광 여울 이삭빵 박스": 2,
    "루멘 시럽": 2
}

SPECIAL_ITEMS = [
    "노랑망태버섯", "설련화", "브리움 우유", "카넬리안", "여울 이삭",
    "아벤츄린", "밀키쿼츠", "남동석", "악마의 손가락", "산딸기",
    "적철석", "신비한 깃털", "루멘 플랜트", "힐웬 광정", "실리엔 응축액",
    "월광 당근", "백연석", "마력 심재핵", "빛나는 양털"
]

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
@st.cache_data(ttl=300)
def get_all_quest_prices(key):
    """납품 퀘스트 전체 재료 시세를 한 번에 조회 (5분 캐시)"""
    all_materials = set()
    for q_data in DELIVERY_QUESTS.values():
        all_materials.update(q_data['materials'].keys())

    price_map = {}
    for mat in all_materials:
        url = f"https://open.api.nexon.com/mabinogi/v1/auction/list?item_name={urllib.parse.quote(mat)}"
        headers = {"x-nxopen-api-key": key, "accept": "application/json"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                items = res.json().get('auction_item', [])
                if items:
                    items.sort(key=lambda x: x['auction_price_per_unit'])
                    price_map[mat] = items[0]['auction_price_per_unit']
                else:
                    price_map[mat] = 0
        except:
            price_map[mat] = 0
        time.sleep(0.3)
    return price_map

@st.cache_data(ttl=60)
def get_price(item_name, key):
    url = f"https://open.api.nexon.com/mabinogi/v1/auction/list?item_name={urllib.parse.quote(item_name)}"
    headers = {"x-nxopen-api-key": key, "accept": "application/json"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            items = data.get('auction_item', [])
            if items:
                items.sort(key=lambda x: x['auction_price_per_unit'])
                return items[0]['auction_price_per_unit']
    except: pass
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

@st.cache_data(ttl=60)
def load_sheet_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = json.loads(st.secrets["google_credentials"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Mabi_DB").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.set_index('시간')
        return df
    except Exception as e:
        st.error(f"구글 시트 연동 오류: {e}")
        return pd.DataFrame()

# =========================================================
# ★ 섹션 0: 납품 손익 분석 (최상단)
# =========================================================
st.header("🏆 납품 퀘스트 손익 분석 (시즌 말 탈농 가격 하락 대비)")

with st.expander("ℹ️ 계산 방식 안내", expanded=False):
    st.markdown(f"""
    - **재료비**: 각 퀘스트 납품 1회에 필요한 재료를 경매장 최저가로 구매 시 총 비용 (limit 횟수 × 재료비 합산)
    - **보상 기대값**: 납품 1회당 보상 아이템 1개를 랜덤으로 받는다고 가정, 아래 5종 동일 확률 적용
    - **손익** = 총 보상 기대값 − 총 재료비 (양수면 이득 🟢, 음수면 손해 🔴)
    
    | 보상 아이템 | 상점 판매가 |
    |---|---|
    | 탈틴 농장 업그레이드 벽돌 | 10,000 G |
    | 탈틴 농장 업그레이드 철판 | 20,000 G |
    | 탈틴 농장 업그레이드 도료 | 30,000 G |
    | 탈틴 농장 업그레이드 유리 | 40,000 G |
    | 탈틴 협회 열쇠 | 25,000 G |
    
    > **보상 기대값 (1회 평균)**: {REWARD_EXPECTED_VALUE:,.0f} G
    
    ⚠️ *보상 확률이 동일하지 않을 수 있으며, 퀘스트별 보상 풀이 다를 수 있습니다. 데이터 연구 후 수정 예정.*
    """)

# 캐시된 시세 자동 조회 (5분 TTL — 만료 시 다음 로드에서 자동 갱신)
with st.spinner("납품 재료 경매장 시세 조회 중... (약 20초, 이후 5분간 캐시)"):
    price_map = get_all_quest_prices(FIXED_API_KEY)
fetched_at = datetime.now().strftime('%H:%M:%S')

# 퀘스트별 손익 계산
roi_rows = []
for q_name, q_data in DELIVERY_QUESTS.items():
    limit = q_data['limit']
    cost_per_run = sum(price_map.get(mat, 0) * cnt for mat, cnt in q_data['materials'].items())
    total_cost = cost_per_run * limit
    total_reward = REWARD_EXPECTED_VALUE * limit
    profit = total_reward - total_cost
    missing = [m for m in q_data['materials'] if price_map.get(m, 0) == 0]
    roi_rows.append({
        "q_name": q_name,
        "limit": limit,
        "cost_per_run": cost_per_run,
        "total_cost": total_cost,
        "total_reward": total_reward,
        "profit": profit,
        "missing": missing,
    })

roi_rows.sort(key=lambda x: x["profit"], reverse=True)

# 요약 메트릭
profitable = sum(1 for r in roi_rows if r["profit"] > 0)
m1, m2, m3, m4 = st.columns(4)
m1.metric("이득 퀘스트", f"{profitable}개")
m2.metric("손해 퀘스트", f"{len(roi_rows) - profitable}개")
m3.metric("보상 1회 기대값", f"{REWARD_EXPECTED_VALUE:,.0f} G")
m4.metric("시세 갱신", fetched_at)

# 손익 표 — pandas DataFrame으로 렌더링
df_roi = pd.DataFrame([
    {
        "퀘스트명": r["q_name"] + (" ⚠️" if r["missing"] else ""),
        "납품 횟수": r["limit"],
        "1회 재료비": r["cost_per_run"],
        "총 재료비": r["total_cost"],
        "총 보상 기대값": int(r["total_reward"]),
        "손익": int(r["profit"]),
    }
    for r in roi_rows
])

def color_profit(val):
    if val > 0:
        return "color: #00ffc8; font-weight: bold;"
    elif val < 0:
        return "color: #ff6b6b; font-weight: bold;"
    return "color: #ffd166; font-weight: bold;"

def fmt_gold(val):
    return f"{val:+,.0f} G" if isinstance(val, (int, float)) else val

df_display = df_roi.copy()
df_display["1회 재료비"] = df_display["1회 재료비"].apply(lambda v: f"{v:,.0f} G")
df_display["총 재료비"] = df_display["총 재료비"].apply(lambda v: f"{v:,.0f} G")
df_display["총 보상 기대값"] = df_display["총 보상 기대값"].apply(lambda v: f"{v:,.0f} G")
df_display["손익"] = df_display["손익"].apply(lambda v: f"🟢 {v:+,.0f} G" if v > 0 else (f"🔴 {v:+,.0f} G" if v < 0 else f"⚪ {v:+,.0f} G"))
df_display["납품 횟수"] = df_display["납품 횟수"].apply(lambda v: f"{v}회")

st.table(df_display.reset_index(drop=True))

col_refresh, col_cap = st.columns([1, 6])
with col_refresh:
    if st.button("🔄 지금 새로고침", key="btn_roi_refresh"):
        st.cache_data.clear()
        st.rerun()
with col_cap:
    st.caption(f"※ 경매장 최저가 기준 | 보상 기대값 = {REWARD_EXPECTED_VALUE:,.0f} G × 납품 횟수 | 조회: {fetched_at} | 5분마다 자동 갱신")

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
        time.sleep(0.3)
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
            time.sleep(0.3)
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
        - 탈틴 농장 블랙베리 주스: **3개**
        - 탈틴 농장 퓨어 블러썸 머리핀: **3개**
        - 탈틴 농장 방수 원단: **3개**
        - 탈틴 농장 이브닝 드레스: **2개**
        - 탈틴 농장 별무늬 샐러드: **2개**
        - 남동판: **2개**
        - 희귀 버섯 볶음 박스: **2개**
        - 월광 여울 이삭빵 박스: **2개**
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
        - 탈틴 농장 블랙베리 주스: **3개**
        - 탈틴 농장 퓨어 블러썸 머리핀: **3개**
        - 탈틴 농장 방수 원단: **3개**
        - 탈틴 농장 이브닝 드레스: **2개**
        - 탈틴 농장 별무늬 샐러드: **2개** """)

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
# 섹션 5: 탈틴 농장 시세 현황 및 1주 그래프
# =========================================================
st.divider()
st.header("📈 탈틴 농장 실시간 시세 및 1주 그래프")
df_history = load_sheet_data()

if not df_history.empty:
    latest_data = df_history.iloc[-1]
    st.write("### 💡 현재 최신 경매장 시세")

    st.subheader("기본 생산품")
    cols_basic = st.columns(3)
    for idx, item in enumerate(CATEGORIES["기본 생산품"]):
        with cols_basic[idx % 3]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)

    st.divider()
    st.subheader("가공품")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**풍요로운 마법의 솥**")
        for item in CATEGORIES["풍요로운 마법의 솥"]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)
        st.write("")
        st.markdown("**반짝이는 마법의 솥**")
        for item in CATEGORIES["반짝이는 마법의 솥"]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)
    with col2:
        st.markdown("**부드러운 마법의 솥**")
        for item in CATEGORIES["부드러운 마법의 솥"]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)
        st.write("")
        st.markdown("**섬세한 마법의 솥**")
        for item in CATEGORIES["섬세한 마법의 솥"]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)

    st.divider()
    st.write("### 📊 농장 작물 시세 변동 추이")
    farm_items = [col for col in df_history.columns if col not in SPECIAL_ITEMS and col != "시간"]
    selected_farm = st.multiselect("그래프에서 확인할 아이템을 선택하세요", farm_items, default=farm_items[:2], key="farm_multiselect_unique")

    if selected_farm:
        df_history.index = pd.to_datetime(df_history.index)
        fig_farm = px.line(df_history[selected_farm], template="plotly_dark")
        fig_farm.update_layout(xaxis=dict(tickformat="%Y-%m-%d\n%H:%M", tickangle=0), yaxis_title="가격(G)", yaxis_tickformat=",", legend_title_text="농장 아이템", hovermode="x unified")
        st.plotly_chart(fig_farm, use_container_width=True, key="farm_chart_id")

# =========================================================
# 섹션 6: 특화 채집 시즌 실시간 현황 및 그래프
# =========================================================
st.divider()
st.header("💎 특화 채집 시즌 실시간 현황")

if not df_history.empty:
    latest_data = df_history.iloc[-1]
    st.write("### 💰 특화 채집 최저가 요약")
    cols_spec = st.columns(4)
    for i, item_name in enumerate(SPECIAL_ITEMS):
        if item_name in latest_data:
            price = latest_data[item_name]
            with cols_spec[i % 4]: display_item_with_local_image(item_name, price)

    st.divider()
    available_special = [item for item in SPECIAL_ITEMS if item in df_history.columns]
    if available_special:
        st.write("### 📈 특화 채집 시세 변동 추이")
        selected_special = st.multiselect("확인할 특화 아이템을 선택하세요", available_special, default=available_special[:3], key="special_multiselect_unique")
        if selected_special:
            df_history.index = pd.to_datetime(df_history.index)
            fig_special = px.line(df_history[selected_special], template="plotly_dark")
            fig_special.update_layout(xaxis=dict(tickformat="%Y-%m-%d\n%H:%M", tickangle=0), yaxis_title="가격(G)", yaxis_tickformat=",", legend_title_text="특화 아이템", hovermode="x unified")
            st.plotly_chart(fig_special, use_container_width=True, key="special_chart_id")

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
            time.sleep(0.3)
            progress_bar.progress((idx + 1) / len(aggregated_materials))
        progress_bar.empty()

        st.metric("총 예상 구매 비용", f"{quest_total_price:,} Gold")
        st.table(quest_result)

st.caption("Data based on NEXON Open API")
