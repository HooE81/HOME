import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 금액 및 거래량 변환 함수
def format_number(x):
    if x >= 100000000: return f"{x / 100000000:.1f}억 주"
    elif x >= 1000000: return f"{x / 1000000:.0f}백만 주"
    return f"{x:,} 주"

def format_currency(x):
    if x >= 1000000000000: return f"{x / 1000000000000:.1f}조 원"
    elif x >= 100000000: return f"{x / 100000000:.0f}억 원"
    return f"{x:,} 원"

@st.cache_data(ttl=3600)
def get_stock_list():
    # KOSPI와 KOSDAQ 데이터만 수집
    df_kospi = fdr.StockListing('KOSPI')
    df_kosdaq = fdr.StockListing('KOSDAQ')
    
    # 두 시장 합치기
    df = pd.concat([df_kospi, df_kosdaq], ignore_index=True)
    
    # 거래대금 계산 (데이터가 없는 경우 0 처리)
    df['Close'] = df['Close'].fillna(0)
    df['Volume'] = df['Volume'].fillna(0)
    df['거래대금'] = df['Close'] * df['Volume']
    
    return df.rename(columns={
        'Name': '종목명',
        'Code': '종목코드',
        'Close': '현재가',
        'Marcap': '시가총액',
        'ChagesRatio': '등락률',
        'Volume': '거래량'
    })

st.set_page_config(page_title="KOSPI/KOSDAQ 분석기", layout="wide")
st.title('📈 KOSPI & KOSDAQ 급등 종목 분석기')

stocks = get_stock_list()

# 사이드바 설정
st.sidebar.header("조회 조건")
상승률기준 = st.sidebar.slider("상승률 필터 (%)", 0, 30, 15)
최소거래대금 = st.sidebar.slider("최소 거래대금 (억 원)", 0, 1000, 100) * 100000000

if st.sidebar.button("분석 실행"):
    with st.spinner('데이터 처리 중...'):
        df = stocks.sort_values(by='등락률', ascending=False)
        결과 = df[(df['등락률'] >= 상승률기준) & (df['거래대금'] >= 최소거래대금)]
        
        # 출력용 데이터 변환
        표출용 = 결과.copy()
        표출용['현재가'] = 표출용['현재가'].apply(lambda x: f"{x:,} 원")
        표출용['시가총액'] = 표출용['시가총액'].apply(format_currency)
        표출용['거래량'] = 표출용['거래량'].apply(format_number)
        표출용['거래대금'] = 표출용['거래대금'].apply(format_currency)
        
        st.subheader(f"검색 결과 (총 {len(결과)}개 종목)")
        if not 결과.empty:
            st.dataframe(표출용[['종목명', '종목코드', '현재가', '시가총액', '등락률', '거래량', '거래대금']], use_container_width=True)
        else:
            st.write("해당 조건에 맞는 종목이 없습니다.")