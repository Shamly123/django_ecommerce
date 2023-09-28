def calculate_cart_total(cart_items):
    total = sum(item.sub_total() for item in cart_items)  # Note the parentheses
    return total
