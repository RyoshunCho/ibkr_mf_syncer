import yfinance as yf

def get_latest_fx_rate(from_currency='USD', to_currency='JPY'):
    currency_pair = f'{from_currency}{to_currency}=X'
    # USD/JPYのデータを取得
    fx_ticker = yf.Ticker(currency_pair)
    # 履歴データを取得
    fx_rate_history = fx_ticker.history(period='1d')
    # 最新の為替レートを取得
    latest_fx_rate = fx_rate_history['Close'].iloc[-1]
    return latest_fx_rate

def add_value_jpy(df, calculation_column_name, additonal_column_name):
    if 'fx_rate_to_JPY' not in df.columns:
            # dfにFXレートを追加
            df['fx_rate_to_JPY'] = df.apply(lambda x: float(1) if x['currency'] == 'JPY' else float(get_latest_fx_rate(x['currency'])), axis=1)
    # dfにValue_JPY列を追加し、円転換した値を代入
    df[additonal_column_name] = df.apply(lambda x: float(x[calculation_column_name]) * x['fx_rate_to_JPY'], axis=1)
    #dfのValue_JPY列を整数型に変換
    df[additonal_column_name] = df[additonal_column_name].astype(int)
    #print(df)
    return df