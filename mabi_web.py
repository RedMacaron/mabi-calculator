import streamlit as st
import requests
import urllib.parse
import time

# =========================================================
# [설정 1] 본인의 넥슨 API 키를 입력하세요 (따옴표 필수)
FIXED_API_KEY = "test_e120ab983233c28b080ec9820192d670e9d4ba97f7d9a3fe0246b29642035136efe8d04e6d233bd35cf2fabdeb93fb0d"

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
