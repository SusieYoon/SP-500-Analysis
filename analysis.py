import pandas as pd
import yfinance as yf
import datetime
import numpy as np

today = datetime.datetime.now().strftime("%Y-%m-%d")

# 예시 S&P500 상위 30개 종목
sp500_symbols = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA",
    "TSLA","BRK-B","META","JPM","JNJ",
    "V","PG","UNH","HD","MA",
    "DIS","BAC","VZ","ADBE","CMCSA",
    "NFLX","KO","PEP","INTC","T",
    "CSCO","XOM","PFE","ABBV","CRM"
]

results = []

for symbol in sp500_symbols:
    try:
        # 데이터 다운로드 (최근 35일)
        data = yf.download(symbol, period="35d", progress=False)
        if data.empty or len(data) < 2:
            print(f"[Warning] Not enough data for {symbol}, skipping.")
            continue

        # 1) 단기 상승률
        try:
            pct_change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        except IndexError:
            pct_change = 0

        # 2) 변동성 (최근 30일 표준편차)
        volatility = data['Close'][-30:].pct_change().std() * 100 if len(data) >= 30 else 0

        # 3) 거래량 비율 (오늘 vs 최근 5일 평균)
        avg_vol5 = data['Volume'][-6:-1].mean() if len(data) >= 6 else 1
        vol_ratio = data['Volume'].iloc[-1] / avg_vol5

        # 4) 모멘텀 (최근 5일 수익률 합)
        momentum = data['Close'].pct_change()[-5:].sum() * 100 if len(data) >= 5 else 0

        # 종합 점수
        score = pct_change*0.4 + momentum*0.3 + vol_ratio*0.2 - volatility*0.1

        results.append((symbol, score, pct_change, momentum, vol_ratio, volatility))

    except Exception as e:
        print(f"[Error] Processing {symbol}: {e}")
        continue

# 점수 내림차순 top30
results.sort(key=lambda x: x[1], reverse=True)
top_results = results[:30]

# CSV 생성
columns = ["Symbol","Score","PctChange(%)","Momentum(%)","VolumeRatio","Volatility(%)"]
df_top = pd.DataFrame(top_results, columns=columns)
csv_file = f"top30_{today}.csv"
df_top.to_csv(csv_file, index=False)

# summary.txt 생성
summary_file = f"summary_{today}.txt"
with open(summary_file, "w") as f:
    f.write("Top 30 S&P500 Stocks by Composite Score\n")
    f.write("="*60 + "\n")
    for row in top_results:
        f.write(f"{row[0]} | Score: {row[1]:.2f} | Change: {row[2]:.2f}% | Momentum: {row[3]:.2f}% | VolRatio: {row[4]:.2f} | Volatility: {row[5]:.2f}%\n")

print(f"Enhanced Analysis complete. Files: {csv_file}, {summary_file}")
