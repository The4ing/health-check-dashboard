from app.main import normalize_url, is_valid_url


def test_normalize_url_adds_scheme():
    assert normalize_url("google.com") == "https://google.com"


def test_normalize_url_strips_trailing_slash():
    assert normalize_url("https://example.com/") == "https://example.com"


def test_is_valid_url_true():
    assert is_valid_url("https://github.com") is True


def test_is_valid_url_false():
    assert is_valid_url("not a url") is False
