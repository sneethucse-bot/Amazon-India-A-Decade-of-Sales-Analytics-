import pandas as pd

def rfm_features(df):
    snapshot = df['order_date'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (snapshot - x.max()).days,
        'transaction_id':'count',
        'final_amount_inr':'sum'
    })
    rfm.columns = ['Recency','Frequency','Monetary']
    return rfm