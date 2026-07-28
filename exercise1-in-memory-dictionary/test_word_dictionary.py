import logging

import pytest

from word_dictionary import WordDictionary


@pytest.fixture
def wd() -> WordDictionary:
    """每個測試一個全新實例，天然隔離。"""
    return WordDictionary()


# --- Part A：Exact Match ---------------------------------------------------------

def test_contains_returns_true_for_exact_word(wd):
    wd.setup(["cat", "car", "bar"])
    assert wd.contains("cat") is True


def test_contains_returns_false_for_prefix_that_is_not_a_word(wd):
    # "ca" 是 cat/car 的前綴，但不是存過的完整字
    wd.setup(["cat", "car", "bar"])
    assert wd.contains("ca") is False


def test_contains_returns_false_for_absent_word(wd):
    wd.setup(["cat", "car", "bar"])
    assert wd.contains("bat") is False


def test_prefix_word_and_longer_word_coexist(wd):
    # car 是 card 的前綴：兩者都要命中，"ca" 仍不是字
    wd.setup(["car", "card"])
    assert wd.contains("car") is True
    assert wd.contains("card") is True
    assert wd.contains("ca") is False


# --- Exact Match 是 case-sensitive（原樣存、精確比對） -----------------------------

def test_setup_preserves_case_and_matches_exactly(wd):
    wd.setup(["Cat"])
    assert wd.contains("Cat") is True     # 原樣存大寫
    assert wd.contains("cat") is False    # 小寫搜不到


def test_contains_is_case_sensitive(wd):
    wd.setup(["cat"])
    assert wd.contains("cat") is True
    assert wd.contains("CAT") is False


# --- 字元驗證：全形/空格/數字/符號 一律擋掉 --------------------------------------

def test_fullwidth_word_is_rejected_on_setup(wd):
    wd.setup(["ｃａｔ"])  # 全形，不是英文字母
    assert wd.contains("cat") is False  # 沒被存進去


def test_fullwidth_query_returns_false(wd):
    wd.setup(["cat"])
    assert wd.contains("ｃａｔ") is False


def test_word_with_space_is_rejected(wd):
    wd.setup(["ca t"])
    assert wd.contains("ca t") is False


def test_empty_string_is_rejected(wd):
    # 空字串不可被當成字（否則會誤標 root）
    wd.setup([""])
    assert wd.contains("") is False


def test_word_with_digits_or_symbols_is_rejected(wd):
    wd.setup(["a1", "c@t"])
    assert wd.contains("a1") is False
    assert wd.contains("c@t") is False


# --- 題目假設：重複、取代 ------------------------------------------------------

def test_duplicates_do_not_change_result(wd):
    wd.setup(["cat", "cat", "car"])
    assert wd.contains("cat") is True
    assert wd.contains("car") is True


def test_setup_replaces_previous_contents(wd):
    wd.setup(["apple"])
    wd.setup(["banana"])
    assert wd.contains("apple") is False  # 舊的被取代
    assert wd.contains("banana") is True


# --- 防護：type check → TypeError --------------------------------------------------

@pytest.mark.parametrize("bad", ["cat", 123, None, ("cat",)])
def test_setup_rejects_non_list(wd, bad):
    with pytest.raises(TypeError):
        wd.setup(bad)


def test_setup_rejects_non_str_element(wd):
    with pytest.raises(TypeError):
        wd.setup(["cat", 123])


@pytest.mark.parametrize("bad", [123, None, ["cat"]])
def test_contains_rejects_non_str(wd, bad):
    wd.setup(["cat"])
    with pytest.raises(TypeError):
        wd.contains(bad)


def test_setup_is_atomic_on_type_error(wd):
    # setup 中途型別錯 raise 時，舊字典必須原封不動
    wd.setup(["keep"])
    with pytest.raises(TypeError):
        wd.setup(["new", 123])  # 走到 123 才 raise
    assert wd.contains("keep") is True  # 舊內容還在
    assert wd.contains("new") is False  # 失敗的 setup 完全沒生效


# --- logging：跳過的字會記 warning ---------------------------------------------

def test_skipped_invalid_word_emits_warning(wd, caplog):
    with caplog.at_level(logging.WARNING):
        wd.setup(["cat", "Ｘ"])  # 全形 X 會被跳過
    assert any("skipped" in r.message for r in caplog.records)


# --- End Part A：Exact Match ---------------------------------------------------------
