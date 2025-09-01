import pytest


@pytest.mark.testiny_id("TC-4")
@pytest.mark.parametrize("username,password", [("admin", "admin123")])
def test_valid_login(username, password):
    assert username == "admin" and password == "admin123"

@pytest.mark.testiny_id("TC-5")
@pytest.mark.parametrize("password", ["wrongpass"])
def test_invalid_login(password):
    assert password != "admin123"


@pytest.mark.testiny_id("TC-6")
@pytest.mark.parametrize("password", ["wrongpass"])
def test_force_fail(password):
    assert password == "uzipass"

@pytest.mark.testiny_id("TC-7")
@pytest.mark.parametrize("password", ["uzipasss"])
def test_force_pass(password):
    assert password == "uzipasss"

@pytest.mark.testiny_id("TC-8")
def test_example_test():
    assert 1 == 1