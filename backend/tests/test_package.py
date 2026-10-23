import app
import strand_core


def test_backend_can_import_core() -> None:
    assert app.__doc__ is not None
    assert strand_core.__version__
