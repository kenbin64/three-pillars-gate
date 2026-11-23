# A small money library. The human's direction: money is always integer cents, never floating point, and a split
# must sum back to the exact total with no cent lost or invented.


def add_cents(a, b):
    total = a + b
    return total


def percent_cents(amount_cents, percent):
    # integer percent of an integer-cent amount, rounded half up, exact integer cents
    result = (amount_cents * percent + 50) // 100
    return result


def split_bill(total_cents, people):
    # Split as evenly as possible. The first `remainder` people pay one extra cent, so the shares sum to the
    # exact total. This remainder handling is the part weak tests miss.
    base = total_cents // people
    remainder = total_cents - base * people
    shares = []
    for i in range(people):
        extra = 1 if i < remainder else 0
        shares.append(base + extra)
    return shares
