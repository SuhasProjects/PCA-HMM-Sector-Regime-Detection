
import yfinance as yf
import pandas as pd

def download(tickers_to_download, filename):
    data = yf.download(
        tickers_to_download,
        start='2019-08-27',
        end='2026-08-25',
        auto_adjust=True,
        progress=False
    )['Close']

    # Forward-fill missing prices (only 3 data points)
    before_count = data.isna().sum().sum()
    data = data.ffill()
    after_count = data.isna().sum().sum()

    print(f"Forward-filled {before_count - after_count} missing price points")

    # Calculate daily percentage returns
    returns = data.pct_change().iloc[1:]
    # (handles missing data at the beginning)
    returns = returns.dropna()

    returns.to_csv(filename)

    print(f"Saved {filename}")
    print(f"Shape: {returns.shape}")
    print(f"NaNs remaining: {returns.isna().sum().sum()}")
    print()

#List of all s&p 500 stocks that have been in the index for the past 7 years (to make data cleaner). There are 396 companies included. 
tech = ['AAPL', 'ACN', 'ADBE', 'ADI', 'ADSK', 'AKAM', 'AMAT', 'AMD', 'ANET', 'APH', 'AVGO', 'CDNS', 'CRM', 'CSCO', 'CTSH', 'FFIV', 'FTNT', 'GEN', 'GLW', 'HPE', 'HPQ', 'IBM', 'INTC', 'INTU', 'IT', 'KEYS', 'KLAC', 'LRCX', 'MCHP', 'MSFT', 'MSI', 'MU', 'NTAP', 'NVDA', 'ORCL', 'QCOM', 'ROP', 'SNPS', 'STX', 'SWKS', 'TEL', 'TXN', 'VRSN', 'WDC']
finance = ['AFL', 'AIG', 'AIZ', 'AJG', 'ALL', 'AMP', 'AON', 'AXP', 'BAC', 'BEN', 'BLK', 'BNY', 'BRK-B', 'C', 'CB', 'CBOE', 'CFG', 'CINF', 'CME', 'COF', 'CPAY', 'EG', 'FIS', 'FISV', 'FITB', 'GL', 'GPN', 'GS', 'HBAN', 'HIG', 'ICE', 'IVZ', 'JKHY', 'JPM', 'KEY', 'L', 'MA', 'MCO', 'MET', 'MRSH', 'MS', 'MSCI', 'MTB', 'NDAQ', 'NTRS', 'PFG', 'PGR', 'PNC', 'PRU', 'PYPL', 'RF', 'RJF', 'SCHW', 'SPGI', 'STT', 'SYF', 'TFC', 'TROW', 'TRV', 'USB', 'V', 'WFC', 'WTW']
communication_services = ['CHTR', 'CMCSA', 'DIS', 'FOX', 'FOXA', 'GOOG', 'GOOGL', 'META', 'NFLX', 'NWS', 'NWSA', 'OMC', 'PSKY', 'T', 'TMUS', 'TTWO', 'VZ']
consumer_discretionary = ['AMZN', 'APTV', 'AZO', 'BBY', 'BKNG', 'CCL', 'CMG', 'DHI', 'DRI', 'EBAY', 'EXPE', 'F', 'GM', 'GPC', 'GRMN', 'HAS', 'HD', 'HLT', 'LEN', 'LOW', 'MAR', 'MCD', 'MGM', 'NCLH', 'NKE', 'ORLY', 'PHM', 'RCL', 'RL', 'ROST', 'SBUX', 'TJX', 'TPR', 'TSCO', 'ULTA', 'WYNN', 'YUM']
health_care = ['A', 'ABBV', 'ABT', 'ALGN', 'AMGN', 'BAX', 'BDX', 'BIIB', 'BMY', 'BSX', 'CAH', 'CI', 'CNC', 'COO', 'COR', 'CVS', 'DGX', 'DHR', 'DVA', 'ELV', 'EW', 'GILD', 'HCA', 'HSIC', 'HUM', 'IDXX', 'INCY', 'IQV', 'ISRG', 'JNJ', 'LH', 'LLY', 'MCK', 'MDT', 'MRK', 'MTD', 'PFE', 'REGN', 'RMD', 'RVTY', 'SYK', 'TMO', 'UHS', 'UNH', 'VRTX', 'VTRS', 'WAT', 'ZBH', 'ZTS']
industrials = ['ADP', 'ALLE', 'AME', 'AOS', 'BA', 'BR', 'CAT', 'CHRW', 'CMI', 'CPRT', 'CSX', 'CTAS', 'DAL', 'DE', 'DOV', 'EFX', 'EMR', 'ETN', 'EXPD', 'FAST', 'FDX', 'FTV', 'GD', 'GE', 'GWW', 'HII', 'HON', 'HWM', 'IEX', 'ITW', 'J', 'JBHT', 'JCI', 'LDOS', 'LHX', 'LMT', 'LUV', 'MAS', 'MMM', 'NOC', 'NSC', 'PAYX', 'PCAR', 'PH', 'PNR', 'PWR', 'ROK', 'ROL', 'RSG', 'RTX', 'SNA', 'SWK', 'TDG', 'TT', 'TXT', 'UAL', 'UNP', 'UPS', 'URI', 'VRSK', 'WAB', 'WM', 'XYL']
consumer_staples = ['ADM', 'BF-B', 'CHD', 'CL', 'CLX', 'COST', 'DG', 'DLTR', 'EL', 'GIS', 'HRL', 'HSY', 'KHC', 'KMB', 'KO', 'KR', 'MDLZ', 'MKC', 'MNST', 'MO', 'PEP', 'PG', 'PM', 'SJM', 'STZ', 'SYY', 'TAP', 'TGT', 'TSN', 'WMT']
energy = ['APA', 'BKR', 'COP', 'CVX', 'DVN', 'EOG', 'FANG', 'HAL', 'KMI', 'MPC', 'OKE', 'OXY', 'PSX', 'SLB', 'VLO', 'WMB', 'XOM']
utilities = ['AEE', 'AEP', 'AES', 'ATO', 'AWK', 'CMS', 'CNP', 'D', 'DTE', 'DUK', 'ED', 'EIX', 'ES', 'ETR', 'EVRG', 'EXC', 'FE', 'LNT', 'NEE', 'NI', 'NRG', 'PEG', 'PNW', 'PPL', 'SO', 'SRE', 'WEC', 'XEL']
materials = ['ALB', 'AMCR', 'APD', 'AVY', 'BALL', 'CF', 'CTVA', 'DD', 'DOW', 'ECL', 'FCX', 'IFF', 'IP', 'LIN', 'LYB', 'MLM', 'MOS', 'NEM', 'NUE', 'PKG', 'PPG', 'SHW', 'VMC']
real_estate = ['AMT', 'ARE', 'BXP', 'CBRE', 'CCI', 'DLR', 'DOC', 'EQIX', 'ESS', 'EXR', 'FRT', 'HST', 'IRM', 'KIM', 'MAA', 'O', 'PLD', 'PSA', 'REG', 'SBAC', 'SPG', 'UDR', 'VTR', 'WELL', 'WY']

sectors = {
    'tech': tech,
    'finance': finance,
    'communication_services': communication_services,
    'consumer_discretionary': consumer_discretionary,
    'health_care': health_care,
    'industrials': industrials,
    'consumer_staples': consumer_staples,
    'energy': energy,
    'utilities': utilities,
    'materials': materials,
    'real_estate': real_estate
}

all_tickers = []

for sector_name, sector_tickers in sectors.items():

    all_tickers.extend(sector_tickers)

    download(
        sector_tickers,
        f"data/{sector_name}_data.csv"
    )


# Download the entire market
download(
    all_tickers,
    "data/market_data.csv"
)

import yfinance as yf
import pandas as pd

#List of all s&p 500 stocks that have been in the index for the past 7 years (to make data cleaner). There are 396 companies included. 
tech = ['AAPL', 'ACN', 'ADBE', 'ADI', 'ADSK', 'AKAM', 'AMAT', 'AMD', 'ANET', 'APH', 'AVGO', 'CDNS', 'CRM', 'CSCO', 'CTSH', 'FFIV', 'FTNT', 'GEN', 'GLW', 'HPE', 'HPQ', 'IBM', 'INTC', 'INTU', 'IT', 'KEYS', 'KLAC', 'LRCX', 'MCHP', 'MSFT', 'MSI', 'MU', 'NTAP', 'NVDA', 'ORCL', 'QCOM', 'ROP', 'SNPS', 'STX', 'SWKS', 'TEL', 'TXN', 'VRSN', 'WDC']
finance = ['AFL', 'AIG', 'AIZ', 'AJG', 'ALL', 'AMP', 'AON', 'AXP', 'BAC', 'BEN', 'BLK', 'BNY', 'BRK-B', 'C', 'CB', 'CBOE', 'CFG', 'CINF', 'CME', 'COF', 'CPAY', 'EG', 'FIS', 'FISV', 'FITB', 'GL', 'GPN', 'GS', 'HBAN', 'HIG', 'ICE', 'IVZ', 'JKHY', 'JPM', 'KEY', 'L', 'MA', 'MCO', 'MET', 'MRSH', 'MS', 'MSCI', 'MTB', 'NDAQ', 'NTRS', 'PFG', 'PGR', 'PNC', 'PRU', 'PYPL', 'RF', 'RJF', 'SCHW', 'SPGI', 'STT', 'SYF', 'TFC', 'TROW', 'TRV', 'USB', 'V', 'WFC', 'WTW']
communication_services = ['CHTR', 'CMCSA', 'DIS', 'FOX', 'FOXA', 'GOOG', 'GOOGL', 'META', 'NFLX', 'NWS', 'NWSA', 'OMC', 'PSKY', 'T', 'TMUS', 'TTWO', 'VZ']
consumer_discretionary = ['AMZN', 'APTV', 'AZO', 'BBY', 'BKNG', 'CCL', 'CMG', 'DHI', 'DRI', 'EBAY', 'EXPE', 'F', 'GM', 'GPC', 'GRMN', 'HAS', 'HD', 'HLT', 'LEN', 'LOW', 'MAR', 'MCD', 'MGM', 'NCLH', 'NKE', 'ORLY', 'PHM', 'RCL', 'RL', 'ROST', 'SBUX', 'TJX', 'TPR', 'TSCO', 'ULTA', 'WYNN', 'YUM']
health_care = ['A', 'ABBV', 'ABT', 'ALGN', 'AMGN', 'BAX', 'BDX', 'BIIB', 'BMY', 'BSX', 'CAH', 'CI', 'CNC', 'COO', 'COR', 'CVS', 'DGX', 'DHR', 'DVA', 'ELV', 'EW', 'GILD', 'HCA', 'HSIC', 'HUM', 'IDXX', 'INCY', 'IQV', 'ISRG', 'JNJ', 'LH', 'LLY', 'MCK', 'MDT', 'MRK', 'MTD', 'PFE', 'REGN', 'RMD', 'RVTY', 'SYK', 'TMO', 'UHS', 'UNH', 'VRTX', 'VTRS', 'WAT', 'ZBH', 'ZTS']
industrials = ['ADP', 'ALLE', 'AME', 'AOS', 'BA', 'BR', 'CAT', 'CHRW', 'CMI', 'CPRT', 'CSX', 'CTAS', 'DAL', 'DE', 'DOV', 'EFX', 'EMR', 'ETN', 'EXPD', 'FAST', 'FDX', 'FTV', 'GD', 'GE', 'GWW', 'HII', 'HON', 'HWM', 'IEX', 'ITW', 'J', 'JBHT', 'JCI', 'LDOS', 'LHX', 'LMT', 'LUV', 'MAS', 'MMM', 'NOC', 'NSC', 'PAYX', 'PCAR', 'PH', 'PNR', 'PWR', 'ROK', 'ROL', 'RSG', 'RTX', 'SNA', 'SWK', 'TDG', 'TT', 'TXT', 'UAL', 'UNP', 'UPS', 'URI', 'VRSK', 'WAB', 'WM', 'XYL']
consumer_staples = ['ADM', 'BF-B', 'CHD', 'CL', 'CLX', 'COST', 'DG', 'DLTR', 'EL', 'GIS', 'HRL', 'HSY', 'KHC', 'KMB', 'KO', 'KR', 'MDLZ', 'MKC', 'MNST', 'MO', 'PEP', 'PG', 'PM', 'SJM', 'STZ', 'SYY', 'TAP', 'TGT', 'TSN', 'WMT']
energy = ['APA', 'BKR', 'COP', 'CVX', 'DVN', 'EOG', 'FANG', 'HAL', 'KMI', 'MPC', 'OKE', 'OXY', 'PSX', 'SLB', 'VLO', 'WMB', 'XOM']
utilities = ['AEE', 'AEP', 'AES', 'ATO', 'AWK', 'CMS', 'CNP', 'D', 'DTE', 'DUK', 'ED', 'EIX', 'ES', 'ETR', 'EVRG', 'EXC', 'FE', 'LNT', 'NEE', 'NI', 'NRG', 'PEG', 'PNW', 'PPL', 'SO', 'SRE', 'WEC', 'XEL']
materials = ['ALB', 'AMCR', 'APD', 'AVY', 'BALL', 'CF', 'CTVA', 'DD', 'DOW', 'ECL', 'FCX', 'IFF', 'IP', 'LIN', 'LYB', 'MLM', 'MOS', 'NEM', 'NUE', 'PKG', 'PPG', 'SHW', 'VMC']
real_estate = ['AMT', 'ARE', 'BXP', 'CBRE', 'CCI', 'DLR', 'DOC', 'EQIX', 'ESS', 'EXR', 'FRT', 'HST', 'IRM', 'KIM', 'MAA', 'O', 'PLD', 'PSA', 'REG', 'SBAC', 'SPG', 'UDR', 'VTR', 'WELL', 'WY']

all_tickers = tech + finance + communication_services + consumer_discretionary + health_care + industrials + consumer_staples + energy + utilities + materials + real_estate

def download(tickers_to_download, filename):
    data = yf.download(tickers_to_download, start='2019-08-27', end='2026-08-25', auto_adjust=True)['Close']

    # Forward-fill missing prices (assumes price stayed flat on any gap day) Only fills in 3 data points out of 700k+, so has no meaningful impact on data, and only makes for clean data
    before_count = data.isna().sum().sum()
    data = data.ffill()
    after_count = data.isna().sum().sum()
    print(f"Forward-filled {before_count - after_count} missing price points")

    returns = data.pct_change().iloc[1:]
    returns.to_csv(filename)
    print(returns.shape)
    print(returns.isna().sum().sum(), "total NaNs remaining")

download(all_tickers, "data/market_data.csv")

