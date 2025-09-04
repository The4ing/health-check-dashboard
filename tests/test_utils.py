# מניח שהקוד שלך ב-app/main.py
from app.main import normalize_url, is_valid_url

def test_normalize_adds_scheme():
    assert normalize_url("example.com") == "https://example.com"

def test_normalize_strips_trailing_slash():
    assert normalize_url("https://example.com/") == "https://example.com"

def test_is_valid_good_urls():
    assert is_valid_url("https://example.com")
    assert is_valid_url("http://example.com")

def test_is_valid_bad_urls():
    assert not is_valid_url("")
    assert not is_valid_url("not-a-url")
