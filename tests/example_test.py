"""Example test."""
import pytest


@pytest.mark.timeout(1)  # type: ignore
def test_example() -> None:
    """Test this timeout."""
    assert True
