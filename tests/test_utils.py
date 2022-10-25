import pytest

from AlbertoX3 import utils, errors


__all__ = ()


def test_get_bool():
    assert utils.get_bool(True) is True
    assert utils.get_bool(1) is True
    assert utils.get_bool("true") is True
    assert utils.get_bool("T") is True
    assert utils.get_bool("YeS") is True
    assert utils.get_bool("y") is True
    assert utils.get_bool("1") is True

    assert utils.get_bool(False) is False
    assert utils.get_bool(-1) is False
    assert utils.get_bool(0) is False
    assert utils.get_bool("false") is False
    assert utils.get_bool("F") is False
    assert utils.get_bool("nO") is False
    assert utils.get_bool("n") is False
    assert utils.get_bool("-1") is False
    assert utils.get_bool("0") is False

    assert pytest.raises(errors.UnrecognisedBooleanError, lambda: utils.get_bool(object))
    assert pytest.raises(errors.UnrecognisedBooleanError, lambda: utils.get_bool(object()))
    assert pytest.raises(errors.UnrecognisedBooleanError, lambda: utils.get_bool(None))
    assert pytest.raises(errors.UnrecognisedBooleanError, lambda: utils.get_bool(-2))


def test_id_regex():
    match = utils._ID_REGEX.match
    assert match("123456") is None  # len: 6
    assert match("1234567") is not None  # len: 7
    assert match("12345678901234567890") is not None  # len: 20
    assert match("123456789012345678901") is None  # len: 21
    assert match("013374269") is None
    assert match("13374269").group(1) == "13374269"


def test_mention_regex():
    match = utils._MENTION_REGEX.match
    assert match("<@123456>") is None  # len: 6
    assert match("<@1234567>") is not None  # len: 7
    assert match("<@12345678901234567890>") is not None  # len: 20
    assert match("<@123456789012345678901>") is None  # len: 21
    assert match("<@013374269>") is None
    assert match("<@13374269>").group(1) == "13374269"

    assert match("<@!123456>") is None  # len: 6
    assert match("<@!1234567>") is not None  # len: 7
    assert match("<@!12345678901234567890>") is not None  # len: 20
    assert match("<@!123456789012345678901>") is None  # len: 21
    assert match("<@!013374269>") is None
    assert match("<@!13374269>").group(1) == "13374269"

    assert match("@13374269") is None
    assert match("<13374269>") is None


def test_name_regex():
    match = utils._NAME_REGEX.match
    assert match("x#1337") is None  # len: 1
    assert match("hi#1337") is not None  # len: 2
    assert match("a name without to many chars!!!!#1234") is not None  # len: 32
    assert match("a name with to many characters!!!#1234") is None  # len: 33

    assert match("creative sausage#123") is None  # len: 3
    assert match("creative sausage#1234") is not None  # len: 4
    assert match("creative sausage#12345") is None  # len: 5

    assert match("AlbertUnruh#3643").group(1) == "AlbertUnruh"
    assert match("AlbertUnruh#3643").group(2) == "3643"

    assert match("𝖈𝖗𝖊𝖆𝖙𝖎𝖛𝖊 𝖘𝖆𝖚𝖘𝖆𝖌𝖊#1234").group(1) is not None
    assert match("𝕔𝕣𝕖𝕒𝕥𝕚𝕧𝕖 𝕤𝕒𝕦𝕤𝕒𝕘𝕖#1234").group(1) is not None


def test_get_language():
    assert pytest.raises(errors.DeveloperArgumentError, lambda: utils.get_language())
    assert pytest.raises(errors.DeveloperArgumentError, lambda: utils.get_language(guild=0, user=0))
