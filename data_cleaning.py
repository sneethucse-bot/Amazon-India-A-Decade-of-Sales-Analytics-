import pandas as pd
import numpy as np
import re

def clean_dates(df):
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce', dayfirst=True)
    df['order_year'] = df['order_date'].dt.year
    df['order_month'] = df['order_date'].dt.month
    return df

def clean_price(series):
    series = series.astype(str)
    series = series.replace(['Price on Request','nan'], np.nan)
    series = series.str.replace(r'[₹,]', '', regex=True)
    return pd.to_numeric(series, errors='coerce')

def clean_ratings(series):
    def parse(x):
        if pd.isna(x): return np.nan
        x = str(x)
        if '/' in x:
            return float(x.split('/')[0])
        return float(re.findall(r'\d+\.?\d*', x)[0])
    return series.apply(parse)

def clean_boolean(series):
    return series.map({
        'Yes':True,'No':False,'Y':True,'N':False,
        1:True,0:False,True:True,False:False
    })

def clean_delivery(series):
    series = series.replace({'Same Day':0,'1-2 days':2})
    series = pd.to_numeric(series, errors='coerce')
    return series[(series>=0)&(series<=15)]

def clean_payment(series):
    mapping = {
        'UPI':'UPI','PHONEPE':'UPI','GOOGLEPAY':'UPI',
        'COD':'Cash on Delivery','C.O.D':'Cash on Delivery',
        'CC':'Credit Card','CREDIT_CARD':'Credit Card'
    }
    return series.str.upper().replace(mapping)

def remove_duplicates(df):
    return df.drop_duplicates(
        subset=['customer_id','product_id','order_date','final_amount_inr']
    )

def clean_all(df):
    df = clean_dates(df)
    df['original_price_inr'] = clean_price(df['original_price_inr'])
    df['final_amount_inr'] = clean_price(df['final_amount_inr'])
    df['customer_rating'] = clean_ratings(df['customer_rating'])
    df['is_prime_member'] = clean_boolean(df['is_prime_member'])
    df['is_festival_sale'] = clean_boolean(df['is_festival_sale'])
    df['delivery_days'] = clean_delivery(df['delivery_days'])
    df['payment_method'] = clean_payment(df['payment_method'])
    df = remove_duplicates(df)
    return df