import pandas as pd
import yfinance as yf
import datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")

# 예시 S&P 500 상위 30개 종목
sp500_symbols = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA",
    "TSLA","BRK-B","META","JPM","JNJ",
    "V","PG","UNH","HD","MA",
    "DIS","BAC","VZ","ADBE","CMCSA",
    "NFLX","KO","PEP","INTC","T",
    "CSCO","XOM","PFE","ABBV","CRM"
]

top_stocks = []

# 데이터 다운로드 + 예외 처리
for symbol in sp500_symbols:
    try:
        data = yf.download(symbol, period="2d", progress=False)
        if data.empty:
            print(f"No data for {symbol}, skipping.")
            continue
        close_price = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else close_price
        pct_change = ((close_price - prev_close) / prev_close) * 100
        top_stocks.append((symbol, pct_change))
    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# 내림차순 정렬
top_stocks.sort(key=lambda x: x[1], reverse=True)

# CSV 저장
top_df = pd.DataFrame(top_stocks, columns=["Symbol", "PctChange"])
top_csv_file = f"top30_{today}.csv"
top_df.to_csv(top_csv_file, index=False)

# summary.txt 생성
summary_file = f"summary_{today}.txt"
with open(summary_file, "w") as f:
    f.write("Top 30 S&P500 Stocks by Daily Change (%)\n")
    f.write("="*40 + "\n")
    for symbol, pct in top_stocks:
        f.write(f"{symbol}: {pct:.2f}%\n")

print(f"Analysis complete. Files generated: {top_csv_file}, {summary_file}")
