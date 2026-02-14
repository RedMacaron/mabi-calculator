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
    st.table(st.session_state.cart)
    
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
        
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.metric("장바구니 총액", f"{total_cart:,} Gold")
        with c_res2:
            st.metric("1/N (절반)", f"{int(total_cart/2):,} Gold")
            
        st.table(cart_result)

# ---------------------------------------------------------
# 섹션 3: (참고용) 물물교환 재료표 이미지 옮겨적기
# ---------------------------------------------------------
st.divider() # 구분선

st.header("📚 물물교환 6티어 재료 참고표")
st.markdown("""
> **💡 필수 팁** > 6티어는 본인 특화는 자급, 나머지는 경매장 구매 추천!  
> **그랜마 상인 + 알파카 + 임프의 고급 보증서(필수!) >>> 탈틴 or 티르코네일 판매
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
    - 남동석/적철석: **100개**
    - 월광당근: **60개**
    - 여울이삭: **40개**
    - 설련화/루멘: **50개**
    """)

# 맨 아래 구매 목록 강조
st.warning("🛒 **구매 목록 (교역소):** 페라(4/5/6) - 칼리다(5/6) - 오아시스(4/5/6) - 카루(4/5/6)")






