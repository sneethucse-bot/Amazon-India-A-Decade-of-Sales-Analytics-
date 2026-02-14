import matplotlib.pyplot as plt
import seaborn as sns

def revenue_trend(df):
    yearly = df.groupby('order_year')['final_amount_inr'].sum()
    plt.figure(figsize=(10,4))
    sns.lineplot(x=yearly.index, y=yearly.values)
    plt.title("Revenue Trend 2015–2025")
    plt.show()

def payment_trend(df):
    pivot = df.pivot_table(values='final_amount_inr',
                           index='order_year',
                           columns='payment_method',
                           aggfunc='sum')
    pivot.plot.area(figsize=(10,5))
    plt.show()

def category_performance(df):
    cat = df.groupby('category')['final_amount_inr'].sum().sort_values()
    cat.plot(kind='barh', figsize=(8,6))
    plt.show()