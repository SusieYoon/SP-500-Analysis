# analysis.py
import yfinance as yf
import pandas as pd
from datetime import datetime

# =========================
# 1. 설정
# =========================
UNIVERSE = "SP500"   # 나중에 NASDAQ100 등으로 확장 가능
TOP_N = 30

TODAY = datetime.now().strftime("%Y-%m-%d")

# =========================
# 2. 종목 리스트 불러오기
# =========================
def get_universe():
    # S&P500 티커 리스트 (간단 버전)
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    return table[0]["Symbol"].tolist()

# =========================
# 3. 데이터 다운로드
# =========================
def load_price_data(tickers):
    data = yf.download(
        tickers,
        period="3mo",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        threads=True
    )
    return data

# =========================
# 4. 지표 계산
# =========================
def compute_indicators(df):
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()
    df["VOL_MA20"] = df["Volume"].rolling(20).mean()
    df["RET"] = df["Close"].pct_change() * 100
    return df

# =========================
# 5. 필터 + 점수화
# =========================
def score_stock(df):
    score = 0

    if df["RET"].iloc[-1] > 3:
        score += 1
    if df["Volume"].iloc[-1] > 1.5 * df["VOL_MA20"].iloc[-1]:
        score += 1
    if df["MA20"].iloc[-1] > df["MA60"].iloc[-1]:
        score += 1
    if df["Close"].iloc[-1] > df["MA20"].iloc[-1]:
        score += 1

    return score

# =========================
# 6. 메인 로직
# =========================
def main():
    tickers = get_universe()
    raw = load_price_data(tickers)

    results = []

    for ticker in tickers:
        try:
            df = raw[ticker].dropna()
            df = compute_indicators(df)

            score = score_stock(df)
            ret = df["RET"].iloc[-1]

            results.append({
                "Ticker": ticker,
                "Return(%)": round(ret, 2),
                "Score": score,
                "Volume": int(df["Volume"].iloc[-1])
            })

        except Exception:
            continue

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(
        ["Score", "Return(%)"],
        ascending=False
    ).head(TOP_N)

    # =========================
    # 7. 저장
    # =========================
    result_df.to_csv(f"top30_{TODAY}.csv", index=False)

    summary = {
        "date": TODAY,
        "avg_return": round(result_df["Return(%)"].mean(), 2),
        "avg_score": round(result_df["Score"].mean(), 2),
        "count": len(result_df)
    }

    with open(f"summary_{TODAY}.txt", "w") as f:
        f.write(str(summary))

    print("✅ Daily analysis complete")

if __name__ == "__main__":
    main()
