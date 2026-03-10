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
# 금고(Secrets)에서 꺼내옴
FIXED_API_KEY = st.secrets["my_api_key"]

# [설정 2] 이번 주 물교 6티어 재료 (여기서 직접 수정하면 반영됩니다)
# 형식 -> "아이템이름": 개수,
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
    "적철석", "신비한 깃털", "루멘 플랜트", "힐웬 광정", "실리엔 응축핵", 
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
        "탈틴 농장 일반 마법 거
