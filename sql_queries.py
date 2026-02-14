def revenue_by_year():
    return """
    SELECT order_year, SUM(final_amount_inr) revenue
    FROM transactions
    GROUP BY order_year
    ORDER BY order_year
    """

def top_categories():
    return """
    SELECT category, SUM(final_amount_inr) revenue
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY category
    ORDER BY revenue DESC
    """