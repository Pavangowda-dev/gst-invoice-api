from app.gstin import checksum_character, has_valid_checksum, has_valid_format
from tests.sample_data import BUYER_GSTIN, SAMPLE_GSTIN


def test_real_gstin_passes_both_checks():
    assert has_valid_format("27AAPFU0939F1ZV")
    assert has_valid_checksum("27AAPFU0939F1ZV")


def test_sample_gstins_are_valid():
    for gstin in (SAMPLE_GSTIN, BUYER_GSTIN):
        assert has_valid_format(gstin)
        assert has_valid_checksum(gstin)


def test_wrong_check_digit_is_caught():
    assert has_valid_format("27AAPFU0939F1ZX")
    assert not has_valid_checksum("27AAPFU0939F1ZX")


def test_changed_character_is_caught():
    assert not has_valid_checksum("27AAPFU0938F1ZV")


def test_bad_format_is_caught():
    assert not has_valid_format("12345")
    assert not has_valid_format("27aapfu0939f1zv")
    assert not has_valid_format("27AAPFU0939F1AV")


def test_checksum_character():
    assert checksum_character("27AAPFU0939F1Z") == "V"