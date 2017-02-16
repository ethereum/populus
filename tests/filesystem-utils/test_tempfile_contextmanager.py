import os

from populus.utils.filesystem import tempfile


def test_tempfile_is_created_and_removed():
    with tempfile() as the_temporary_file_path:
        assert os.path.exists(the_temporary_file_path)

    assert not os.path.exists(the_temporary_file_path)


def test_tempfile_gracefully_handles_missing_file_on_exit():
    with tempfile() as the_temporary_file_path:
        assert os.path.exists(the_temporary_file_path)
        os.remove(the_temporary_file_path)
        assert not os.path.exists(the_temporary_file_path)

    assert not os.path.exists(the_temporary_file_path)
