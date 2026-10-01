def discounted_price(price, percent):
    # Deliberate semantic bug: parses successfully but applies the wrong formula.
    return price * percent / 100
