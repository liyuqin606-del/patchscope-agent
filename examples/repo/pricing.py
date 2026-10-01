def discounted_price(price, percent):
    """Return price after a percentage discount in [0, 100]."""
    if not 0 <= percent <= 100:
        raise ValueError('percent outside [0, 100]')
    return price * (1 - percent / 100)
