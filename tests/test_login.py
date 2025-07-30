import pytest

# # Mapowanie Testiny External ID
# TESTINY_ID = {
#     "test_valid_login": "TC_LOGIN_001",
#     "test_invalid_login": "TC_LOGIN_002",
#     "test_force_fail": "TC_LOGIN_003"
# }

@pytest.mark.parametrize("username,password", [("admin", "admin123")])
def test_valid_login(username, password):
    """[externalId=TC_LOGIN_001]"""
    assert username == "admin" and password == "admin123"

@pytest.mark.parametrize("password", [("admin", "wrongpass")])
def test_invalid_login(password):
    """[externalId=TC_LOGIN_002]"""
    assert password != "admin123"


@pytest.mark.parametrize("password", [("admin", "wrongpass")])
def test_force_fail(password):
    """[externalId=TC_LOGIN_003]"""
    assert password == "uzipass"

@pytest.mark.parametrize("password", [("admin", "uzipass")])
def test_force_pass(password):
    assert password == "uzipass"
