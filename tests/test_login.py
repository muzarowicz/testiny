import pytest


@pytest.mark.parametrize("username,password", [("admin", "admin123")])
def test_valid_login(username, password):
    """[testinyId=TC-40]"""
    assert username == "admin" and password == "admin123"

@pytest.mark.parametrize("password", ["wrongpass"])
def test_invalid_login(password):
    """[testinyId=TC-41]"""
    assert password != "admin123"


@pytest.mark.parametrize("password", ["wrongpass"])
def test_force_fail(password):
    """[testinyId=TC-42]"""
    assert password == "uzipass"

@pytest.mark.parametrize("password", ["uzipass"])
def test_force_pass(password):
    assert password == "uzipass"
