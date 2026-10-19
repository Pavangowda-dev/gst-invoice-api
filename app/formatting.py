from decimal import Decimal

ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen",
]

TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety",
]


def format_inr(amount):
    """Format a Decimal the Indian way, e.g. 1234567.5 -> 12,34,567.50"""
    sign = "-" if amount < 0 else ""
    whole, paise = f"{abs(amount):.2f}".split(".")

    if len(whole) > 3:
        last_three = whole[-3:]
        rest = whole[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        whole = ",".join(groups + [last_three])

    return f"{sign}{whole}.{paise}"


def below_hundred(n):
    if n < 20:
        return ONES[n]
    tens, ones = divmod(n, 10)
    if ones:
        return f"{TENS[tens]} {ONES[ones]}"
    return TENS[tens]


def below_thousand(n):
    hundreds, rest = divmod(n, 100)
    parts = []
    if hundreds:
        parts.append(f"{ONES[hundreds]} Hundred")
    if rest:
        parts.append(below_hundred(rest))
    return " ".join(parts)


def number_to_words(n):
    """Whole number to words using the Indian system (lakh, crore)."""
    if n == 0:
        return "Zero"

    parts = []
    for value, name in ((10_000_000, "Crore"), (100_000, "Lakh"), (1_000, "Thousand")):
        count, n = divmod(n, value)
        if count:
            parts.append(f"{number_to_words(count)} {name}")
    if n:
        parts.append(below_thousand(n))

    return " ".join(parts)


def amount_in_words(amount):
    amount = amount.quantize(Decimal("0.01"))
    rupees = int(amount)
    paise = int((amount - rupees) * 100)

    words = f"Rupees {number_to_words(rupees)}"
    if paise:
        words += f" and {number_to_words(paise)} Paise"
    return words + " Only"