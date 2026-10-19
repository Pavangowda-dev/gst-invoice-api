from decimal import Decimal

from app.formatting import amount_in_words, format_inr


def test_format_inr_small_numbers():
    assert format_inr(Decimal("0")) == "0.00"
    assert format_inr(Decimal("999")) == "999.00"


def test_format_inr_uses_indian_grouping():
    assert format_inr(Decimal("59000")) == "59,000.00"
    assert format_inr(Decimal("100000")) == "1,00,000.00"
    assert format_inr(Decimal("1234567.5")) == "12,34,567.50"


def test_format_inr_negative_amount():
    assert format_inr(Decimal("-0.01")) == "-0.01"


def test_amount_in_words_simple():
    assert amount_in_words(Decimal("59000")) == "Rupees Fifty Nine Thousand Only"
    assert amount_in_words(Decimal("118")) == "Rupees One Hundred Eighteen Only"


def test_amount_in_words_lakh_and_crore():
    assert amount_in_words(Decimal("125000")) == "Rupees One Lakh Twenty Five Thousand Only"
    assert amount_in_words(Decimal("12345678")) == (
        "Rupees One Crore Twenty Three Lakh Forty Five Thousand "
        "Six Hundred Seventy Eight Only"
    )


def test_amount_in_words_with_paise():
    assert amount_in_words(Decimal("100.50")) == "Rupees One Hundred and Fifty Paise Only"


def test_amount_in_words_zero():
    assert amount_in_words(Decimal("0")) == "Rupees Zero Only"