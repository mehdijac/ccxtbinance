def max_margin(data):
    """
    MAX MARGIN :
    This function calculates the max of absolute margin of [high - low,high - previous close, low-previous close] prices for a set of prices
    It returns an array 
    """
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    mx_margin = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return mx_margin

def ma_max_margin(data,last_period):
    """
    MOVING AVERAGE OF MAX MARGINS :
    This function calculates the average of margins over the last_period
    It returns an array of moving averages
    """
    data['mx_margin'] = max_margin(data)
    ma = data['mx_margin'].rolling(last_period).mean()

    return ma

def average_high_low(df):
    """
    This function returns the average of high and low price
    """
    hl2=(df['high'] + df['low']) / 2

    return  hl2



def In_trend(df, last_period=7, weight_ma_margion=3):
    """
    This functions identify momentums, if the price is crossing the upper band or the lower band
    """

    hl2 = average_high_low(df)
    df['ma_margin'] = ma_max_margin(df, last_period)
    df['upperband'] = hl2 + (weight_ma_margion * df['ma_margin'])
    df['lowerband'] = hl2 - (weight_ma_margion * df['ma_margin'])
    
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]
        
    return df