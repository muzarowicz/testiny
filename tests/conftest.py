import pytest


def pytest_configure(config: pytest.Config) -> None:
    # Register custom markers to avoid Pytest warnings
    config.addinivalue_line("markers", "testiny_id(id): Link this test to a Testiny manual test case externalId")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # Propagate testiny_id marker into JUnit properties as externalId for Testiny CLI
    for item in items:
        marker = item.get_closest_marker("testiny_id")
        if marker and marker.args:
            external_id = str(marker.args[0])
            # user_properties are serialized to JUnit <properties>
            item.user_properties.append(("externalId", external_id))

