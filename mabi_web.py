import streamlit as st
import requests
import urllib.parse
import time

# =========================================================
# 금고(Secrets)에서 꺼내옴
FIXED_API_KEY = st.secrets["my_api_key"]

# [설정 2] 이번 주 물교 6티어 재료 (여기서 직접 수정하면 반영됩니다)
# 형식 -> "아이템이름": 개수,
SHOPPING_LIST = {
    "탈틴 농장 붉은 배 잼": 3,
    "탈틴 농장 자색 원단": 3,
    "탈틴 농장 레드문 귀걸이": 3,
    "탈틴 농장 강화 섬유": 2,
    "탈틴 농장 황혼의 류트": 2,
    "남동판": 2,
    "적철판": 2,
    "월광 여울 이삭빵 박스": 2,
    "루멘 시럽": 2
}
# =========================================================

st.set_page_config(page_title="마비노기 물교&경매장 계산기", layout="wide")
st.title("💰 마비노기 물교 & 경매장 계산기")

# API 호출 함수 (공통 사용)
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
    except:
        pass
    return 0

# ---------------------------------------------------------
# 섹션 1: 고정 목록 (물교 재료)
# ---------------------------------------------------------
st.header("📅 이번 주 물교 6티어 재료")
st.info("코드 상단에서 설정한 고정 리스트입니다.")

# 고정 목록 보여주기 (접었다 폈다 가능)
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
        time.sleep(0.3) # API 보호용 딜레이
        my_bar.progress((idx + 1) / len(SHOPPING_LIST))
    
    my_bar.empty()
    
    # 결과 출력
    col1, col2 = st.columns(2)
    with col1:
        st.metric("총 필요 골드", f"{total_price:,} Gold")
    with col2:
        st.metric("1/N (절반)", f"{int(total_price/2):,} Gold")
    
    st.table(result_data)

st.divider() # 구분선 ========================================

# ---------------------------------------------------------
# 섹션 2: 자유 검색 (장바구니)
# ---------------------------------------------------------
st.header("🔍 개별 품목 검색 (장바구니)")
st.caption("위의 고정 목록 외에 따로 검색하고 싶은 아이템이 있다면 추가하세요.")

# 장바구니 초기화
if 'cart' not in st.session_state:
    st.session_state.cart = []

# 입력 폼
with st.form("add_item_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        input_name = st.text_input("아이템 이름")
    with c2:
        input_count = st.number_input("수량", min_value=1, value=1)
    with c3:
        submitted = st.form_submit_button("추가 ➕")
        
    if submitted and input_name:
        st.session_state.cart.append({"name": input_name, "count": input_count})
        st.success(f"추가됨: {input_name}")

# 장바구니 목록 및 검색 버튼
if st.session_state.cart:
    st.write(f"현재 담긴 품목: {len(st.session_state.cart)}개")
    
    # 개별 아이템 삭제 기능
    for i, item in enumerate(st.session_state.cart):
        col_name, col_count, col_btn = st.columns([3, 1, 1])
        with col_name:
            st.write(item['name'])
        with col_count:
            st.write(f"{item['count']}개")
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
        
        # 절반 표기 제거
        st.metric("장바구니 총액", f"{total_cart:,} Gold")
            
        st.table(cart_result)

# ---------------------------------------------------------
# 섹션 3: (참고용) 물물교환 재료표 이미지 옮겨적기
# ---------------------------------------------------------
st.divider() # 구분선

st.header("📚 물물교환 6티어 재료 참고표")
st.markdown("""
> **💡 필수 팁** > 6티어는 본인 특화는 자급, 나머지는 경매장 구매 추천!  
> **그랜마 상인 + 알파카 + 임프의 고급 보증서(필수!) >>> 탈틴 or 티르코네일 판매**   
> **탈농템은 완제 해금 해놓고 배,석영,거미줄,재스민 위주로 에너지 다써서 단축시키고 수확만! 그 이상은 시간아까움** 
""")

# 3개의 기둥(Column)으로 나누어 표처럼 배치
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
    
    # ---------------------------------------------------------
    # 여기에 표를 넣으면 col1(왼쪽 기둥)의 맨 아래에 쏙 들어갑니다
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
    - 탈틴 농장 붉은 배 잼: **3개**
    - 탈틴 농장 자색 원단: **3개**
    - 탈틴 농장 레드문 귀걸이: **3개**
    - 탈틴 농장 강화 섬유: **2개**
    - 탈틴 농장 황혼의 류트: **2개**
    - 남동판: **2개**
    - 적철판: **2개**
    - 월광 여울 이삭빵 박스: **2개**
    - 루멘 시럽: **2개**
""")

# ---------------------------------------------------------
# 섹션 4: 아르바이트 보상 목록 (맨 아래 추가)
# ---------------------------------------------------------
st.divider() # 굵은 구분선

st.subheader("🕊️ 아르바이트 보상 받기 목록")

# 여기는 컬럼(col) 없이 넓게 씁니다
st.markdown("""
- **관청:** 잡보 아무거나
- **식료품:** 낙지
- **의류점:** **튼튼한 고리** (1순위) / 물교용 방직 재료 (2순위)
- **힐러:** 생명력 500 포션
- **서점:** 마법의 깃털펜
""")

# ---------------------------------------------------------
# 섹션 5: 납품 퀘스트 계산기
# ---------------------------------------------------------
st.divider()
st.header("📦 생활 협회 납품 퀘스트 계산기")
st.caption("진행하려는 퀘스트를 체크한 후 계산하기를 누르면, 필요한 총 재료를 합산하여 경매장 최저가를 검색합니다.")

# 납품 퀘스트 데이터 정리
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

# 퀘스트 목록을 2개의 열로 나누어 배치 전 설정
quest_names = list(DELIVERY_QUESTS.keys())
half_idx = len(quest_names) // 2 + 1

# 체크박스 상태 관리를 위한 세션 초기화
for q_name in quest_names:
    if f"chk_{q_name}" not in st.session_state:
        st.session_state[f"chk_{q_name}"] = False

# 전체 선택 및 해제 버튼 배치
col_btn1, col_btn2, _ = st.columns([1, 1, 6])
with col_btn1:
    if st.button("전체 선택", use_container_width=True, type="primary"):
        for q_name in quest_names:
            st.session_state[f"chk_{q_name}"] = True
with col_btn2:
    if st.button("전체 해제", use_container_width=True):
        for q_name in quest_names:
            st.session_state[f"chk_{q_name}"] = False

selected_quests = []

# 퀘스트 목록을 2개의 열로 나누어 배치
col_q1, col_q2 = st.columns(2)

# 왼쪽 열 체크박스
with col_q1:
    for q_name in quest_names[:half_idx]:
        q_info = DELIVERY_QUESTS[q_name]
        label = f"{q_name} (납품 {q_info['limit']}회 / 코인 {q_info['coin']})"
        if st.checkbox(label, key=f"chk_{q_name}"):
            selected_quests.append(q_name)
            
        mat_str = ", ".join([f"{k} {v}개" for k, v in q_info['materials'].items()])
        st.caption(f"└ {mat_str}")
        st.write("") 

# 오른쪽 열 체크박스
with col_q2:
    for q_name in quest_names[half_idx:]:
        q_info = DELIVERY_QUESTS[q_name]
        label = f"{q_name} (납품 {q_info['limit']}회 / 코인 {q_info['coin']})"
        if st.checkbox(label, key=f"chk_{q_name}"):
            selected_quests.append(q_name)
            
        mat_str = ", ".join([f"{k} {v}개" for k, v in q_info['materials'].items()])
        st.caption(f"└ {mat_str}")
        st.write("")

if st.button("체크된 납품 퀘스트 견적 확인하기 🚀", type="primary"):
    if not selected_quests:
        st.warning("선택된 퀘스트가 없습니다. 위에서 퀘스트를 하나 이상 체크해주세요!")
    else:
        # 체크된 퀘스트의 재료 합산 및 코인 계산 로직
        aggregated_materials = {}
        total_coins = 0
        
        for q_name in selected_quests:
            q_data = DELIVERY_QUESTS[q_name]
            limit = q_data['limit']
            
            # 획득 코인 합산 (1회당 코인 * 납품가능횟수)
            total_coins += (q_data['coin'] * limit)
            
            # 재료 수량 합산
            for mat_name, mat_count in q_data['materials'].items():
                req_qty = mat_count * limit
                if mat_name in aggregated_materials:
                    aggregated_materials[mat_name] += req_qty
                else:
                    aggregated_materials[mat_name] = req_qty

        # 합산된 재료들로 경매장 API 검색 진행
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
            
            time.sleep(0.3) # API 보호용 딜레이
            progress_bar.progress((idx + 1) / len(aggregated_materials))
            
        progress_bar.empty()
        
        # 결과 출력
        st.success(f"💰 총 획득 예상 생활 협회 코인: **{total_coins:,}개**")
        st.metric("총 예상 구매 비용", f"{quest_total_price:,} Gold")
        st.table(quest_result)



























