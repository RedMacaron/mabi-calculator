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

# 이번 주 물교 6티어 재료 설정
SHOPPING_LIST = {
    "탈틴 농장 달콤 케이크": 3,
    "탈틴 농장 천연 고무": 3,
    "탈틴 농장 레드문 귀걸이": 3,
    "탈틴 농장 새벽의 활": 2,
    "탈틴 농장 미드나잇 펄 페인트": 2,
    "백연판": 2,
    "적철판": 2,
    "희귀 버섯 볶음 박스": 4
}

# 특화 채집 아이템 리스트 (NameError 방지를 위해 상단 배치)
SPECIAL_ITEMS = [
    "노랑망태버섯", "설련화", "브리움 우유", "카넬리안", "여울 이삭", 
    "아벤츄린", "밀키쿼츠", "남동석", "악마의 손가락", "산딸기", 
    "적철석", "신비한 깃털", "루멘 플랜트", "힐웬 광정", "실리엔 응축액", 
    "월광 당근", "백연석", "마력 심재핵", "빛나는 양털"
]

# 아이템 분류 데이터
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

# 납품 퀘스트 데이터
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
# 페이지 설정 및 CSS
# =========================================================
st.set_page_config(page_title="마비노기 물교&경매장 계산기", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #1a1c24; }
    .stApp p, .stApp span, .stApp label, .stApp li { color: #ffffff !important; font-weight: 500; }
    div[data-testid="stJson"], div[data-testid="stJson"] pre { background-color: #262730 !important; color: #ffffff !important; }
    .stTable { background-color: #262730 !important; }
    div[data-testid="stMetricValue"] { color: #00ffc8 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💰 마비노기 물교 & 경매장 계산기")

# =========================================================
# 헬퍼 함수
# =========================================================
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

# 아이템 정보와 로컬 이미지를 나란히 렌더링해주는 함수 (복구됨)
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
# 섹션 1-4: 기존 계산기 및 참고표 기능
# =========================================================
st.header("📅 이번 주 물교 6티어 재료")
with st.expander("📋 목록 확인하기 (클릭)", expanded=True):
    st.write(SHOPPING_LIST)

if st.button("6티어 재료 견적 확인하기 🚀", type="primary"):
    total_price = 0
    result_data = []
    my_bar = st.progress(0, text="시세 조회 중...")
    for idx, (name, count) in enumerate(SHOPPING_LIST.items()):
        price = get_price(name, FIXED_API_KEY)
        subtotal = price * count
        total_price += subtotal
        result_data.append({"아이템": name, "최저가": f"{price:,} G", "수량": f"{count}개", "합계": f"{subtotal:,} G"})
        time.sleep(0.3)
        my_bar.progress((idx + 1) / len(SHOPPING_LIST))
    my_bar.empty()
    col1, col2 = st.columns(2)
    with col1: st.metric("총 필요 골드", f"{total_price:,} Gold")
    with col2: st.metric("1/N (절반)", f"{int(total_price/2):,} Gold")
    st.table(result_data)

st.divider()
st.header("🔍 개별 품목 검색 (장바구니)")
if 'cart' not in st.session_state: st.session_state.cart = []
with st.form("add_item_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1: input_name = st.text_input("아이템 이름")
    with c2: input_count = st.number_input("수량", min_value=1, value=1)
    with c3: submitted = st.form_submit_button("추가 ➕")
    if submitted and input_name: st.session_state.cart.append({"name": input_name, "count": input_count})

if st.session_state.cart:
    for i, item in enumerate(st.session_state.cart):
        col_n, col_c, col_b = st.columns([3, 1, 1])
        with col_n: st.write(item['name'])
        with col_c: st.write(f"{item['count']}개")
        with col_b: 
            if st.button("삭제", key=f"del_cart_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

st.divider()
st.header("📚 물물교환 6티어 재료 참고표")
col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    st.markdown("### 🧪 포션 & 목공\n- 생명력 500: 14개\n- 정령 리큐르: 7개\n- 최장/특장: 각 9개")
with col_t2:
    st.markdown("### 🧵 방직 & 공학\n- 고옷/최옷: 28/35개\n- 뮤턴트: 3개\n- 스핀 기어: 7개")
with col_t3:
    st.markdown("### 💎 제련 & 기타\n- 은판: 14개\n- 마법 깃털펜: 15개\n- 펫 놀이세트: 3개")

# =========================================================
# 섹션 5: 탈틴 농장 실시간 시세 및 1주 그래프 (중복 통합됨)
# =========================================================
st.divider()
st.header("📈 탈틴 농장 실시간 시세 및 1주 그래프")
df_history = load_sheet_data()

if not df_history.empty:
    latest_data = df_history.iloc[-1]
    st.write("### 💡 현재 최신 경매장 시세")
    
    # 1. 기본 생산품 파트 (3열 배치)
    st.subheader("기본 생산품")
    cols_basic = st.columns(3)
    for idx, item in enumerate(CATEGORIES["기본 생산품"]):
        with cols_basic[idx % 3]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)
    
    st.divider()
    
    # 2. 가공품 파트 (2열 분할 후 각각 솥 배치)
    st.subheader("가공품")
    ca1, ca2 = st.columns(2)
    
    with ca1:
        st.markdown("**풍요로운 마법의 솥**")
        for item in CATEGORIES["풍요로운 마법의 솥"]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)
            
        st.write("") 
        
        st.markdown("**반짝이는 마법의 솥**")
        for item in CATEGORIES["반짝이는 마법의 솥"]:
            price = latest_data.get(item, 0)
            display_item_with_local_image(item, price)
            
    with ca2:
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
    
    # 3. 농장 아이템 전용 그래프
    st.write("### 📊 농장 작물 시세 변동 추이")
    
    farm_items = [col for col in df_history.columns if col not in SPECIAL_ITEMS and col != "시간"]
    selected_farm = st.multiselect("그래프에서 확인할 농장 아이템을 선택하세요", farm_items, default=farm_items[:2], key="ms_farm")
    
    if selected_farm:
        df_history.index = pd.to_datetime(df_history.index)
        fig_f = px.line(df_history[selected_farm], template="plotly_dark")
        fig_f.update_layout(
            xaxis=dict(tickformat="%Y-%m-%d\n%H:%M", tickangle=0), 
            yaxis_title="가격(G)",
            yaxis_tickformat=",", 
            legend_title_text="농장 아이템",
            hovermode="x unified"
        )
        st.plotly_chart(fig_f, use_container_width=True, key="chart_farm")

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
            with cols_spec[i % 4]: 
                display_item_with_local_image(item_name, price)

    st.divider()
    
    available_special = [item for item in SPECIAL_ITEMS if item in df_history.columns]
    
    if available_special:
        st.write("### 📈 특화 채집 시세 변동 추이")
        sel_spec = st.multiselect("확인할 특화 아이템을 선택하세요", available_special, default=available_special[:3], key="ms_spec")
        
        if sel_spec:
            fig_s = px.line(df_history[sel_spec], template="plotly_dark")
            fig_s.update_layout(
                xaxis=dict(tickformat="%Y-%m-%d\n%H:%M", tickangle=0), 
                yaxis_title="가격(G)",
                yaxis_tickformat=",", 
                legend_title_text="특화 아이템",
                hovermode="x unified"
            )
            st.plotly_chart(fig_s, use_container_width=True, key="chart_spec")

# =========================================================
# 섹션 7: 생활 협회 납품 퀘스트 계산기
# =========================================================
st.divider()
st.header("📦 생활 협회 납품 퀘스트 계산기")
st.caption("진행하려는 퀘스트를 체크한 후 계산하기를 누르면, 필요한 총 재료를 합산하여 경매장 최저가를 검색합니다.")

# 세션 상태 초기화 (고유 키 부여)
for q_name in DELIVERY_QUESTS.keys():
    if f"chk_{q_name}" not in st.session_state: 
        st.session_state[f"chk_{q_name}"] = False

col_q1, col_q2 = st.columns(2)
q_names = list(DELIVERY_QUESTS.keys())
h_idx = len(q_names) // 2 + 1

# 왼쪽 열
with col_q1:
    for name in q_names[:h_idx]:
        with st.container(border=True):
            st.checkbox(f"{name}", key=f"chk_{name}")

# 오른쪽 열
with col_q2:
    for name in q_names[h_idx:]:
        with st.container(border=True):
            st.checkbox(f"{name}", key=f"chk_{name}")

if st.button("납품 견적 확인하기 🚀", type="primary", key="btn_quest_calc"):
    selected_quests = [name for name in q_names if st.session_state.get(f"chk_{name}")]
    if not selected_quests:
        st.warning("선택된 퀘스트가 없습니다. 위에서 퀘스트를 하나 이상 체크해주세요!")
    else:
        aggregated_materials = {}
        total_coins = 0
        
        for q_name in selected_quests:
            q_data = DELIVERY_QUESTS[q_name]
            limit = q_data['limit']
            total_coins += (q_data['coin'] * limit)
            
            for mat_name, mat_count in q_data['materials'].items():
                req_qty = mat_count * limit
                aggregated_materials[mat_name] = aggregated_materials.get(mat_name, 0) + req_qty

        quest_total_price = 0
        quest_result = []
        progress_bar = st.progress(0, text="경매장 시세 조회 중...")
        
        for idx, (item_name, count) in enumerate(aggregated_materials.items()):
            price = get_price(item_name, FIXED_API_KEY)
            subtotal = price * count
            quest_total_price += subtotal
            
            quest_result.append({
                "재료명": item_name,
                "최저가": f"{price:,} G" if price > 0 else "매물 없음",
                "필요 수량": f"{count}개",
                "합계": f"{subtotal:,} G"
            })
            time.sleep(0.3)
            progress_bar.progress((idx + 1) / len(aggregated_materials))
            
        progress_bar.empty()
        st.success(f"💰 총 획득 예상 생활 협회 코인: **{total_coins:,}개**")
        st.metric("총 예상 구매 비용", f"{quest_total_price:,} Gold")
        st.table(quest_result)
