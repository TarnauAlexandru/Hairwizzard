import strand_core


def test_package_exposes_version() -> None:
    assert strand_core.__version__ == "0.1.0"
