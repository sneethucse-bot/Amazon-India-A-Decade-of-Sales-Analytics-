def executive_kpis(df):
    return {
        "Total Revenue": df.final_amount_inr.sum(),
        "Active Customers": df.customer_id.nunique(),
        "AOV": df.final_amount_inr.mean(),
        "Prime %": df.is_prime_member.mean()*100
    }