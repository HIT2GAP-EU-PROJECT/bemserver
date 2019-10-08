"""Tests on 'database' file storage manager."""

import pytest

from bemserver.database.filestorage.filestore import (
    FileStorageMgr, FileStorageEntry)

from tests import TestCoreDatabase
from tests.utils import uuid_gen


class TestFileStorageManager(TestCoreDatabase):
    """Tests for file storage manager."""

    def test_filestorage_manager(self, tmpdir):
        """Tests on file storage manager."""

        fs_mgr = FileStorageMgr(str(tmpdir))
        assert fs_mgr.dir_path == tmpdir

    def test_filestorage_manager_entry(self, tmpdir, ifc_file_data_stream):
        """Tests on file storage manager functions."""

        fs_mgr = FileStorageMgr(str(tmpdir))
        file_id = uuid_gen()
        file_name, data_stream = ifc_file_data_stream

        # `file_id` entry does not exists yet
        with pytest.raises(FileNotFoundError):
            fs_mgr.get(file_id)

        # create an entry
        fs_entry = fs_mgr.add(file_id, file_name, data_stream)
        assert isinstance(fs_entry, FileStorageEntry)
        assert fs_entry.file_id == file_id
        assert fs_entry.file_name == file_name
        assert fs_entry.base_dir_path == tmpdir
        assert fs_entry.entry_dir_path == tmpdir / str(file_id)
        assert fs_entry.file_path == tmpdir / str(file_id) / file_name
        assert not fs_entry.is_empty()
        assert not fs_entry.is_compressed()

        # create the entry again
        with pytest.raises(FileExistsError):
            fs_mgr.add(file_id, file_name, data_stream)

        # get the entry
        fs_entry = fs_mgr.get(file_id)
        assert fs_entry.file_name == file_name

        # delete the entry
        # `fs_entry.delete()` is also available
        fs_mgr.delete(file_id)

        # file storage entry has been removed
        with pytest.raises(FileNotFoundError):
            fs_mgr.get(file_id)

    def test_filestorage_manager_entry_extract(
            self, tmpdir, ifc_multi_zip_file_data):
        """Tests on file storage manager extract function."""

        fs_mgr = FileStorageMgr(str(tmpdir))
        file_id = uuid_gen()
        file_name, data_stream = ifc_multi_zip_file_data

        # save the entry
        fs_entry = fs_mgr.add(file_id, file_name, data_stream)
        assert not fs_entry.is_empty()
        assert fs_entry.is_compressed()

        # archive is not extracted yet
        assert len(fs_entry.extracted_file_paths) == 0

        # extract archive
        extracted_file_paths = fs_entry.extract()
        assert len(extracted_file_paths) == 2
        for extracted_file_path in extracted_file_paths:
            assert extracted_file_path.parent == (
                tmpdir / str(file_id) / fs_entry.EXTRACTED_DIR)

        # archive is now extracted
        assert len(fs_entry.extracted_file_paths) == 2

        # extract archive again
        extracted_file_paths = fs_entry.extract()
        assert len(extracted_file_paths) == 2
        for extracted_file_path in extracted_file_paths:
            assert extracted_file_path.parent == (
                tmpdir / str(file_id) / fs_entry.EXTRACTED_DIR)

        # list entry files
        entry_file_paths = fs_entry.list_file_paths()
        assert len(entry_file_paths) == 1
        assert entry_file_paths[0] == fs_entry.file_path
        entry_file_paths = fs_entry.list_file_paths(include_extracted=True)
        assert len(entry_file_paths) == 3

        # delete
        fs_entry.delete()

        # file storage entry has been removed
        with pytest.raises(FileNotFoundError):
            fs_mgr.get(file_id)

    def test_filestorage_manager_list(
            self, tmpdir, ifc_file_data_stream, ifc_zip_file_data):
        """Tests on file storage manager list function."""

        fs_mgr = FileStorageMgr(str(tmpdir))
        file_id_1 = uuid_gen()
        file_name_1, data_stream_1 = ifc_file_data_stream
        file_id_2 = uuid_gen()
        file_name_2, data_stream_2 = ifc_zip_file_data

        # create entries
        fs_entry_1 = fs_mgr.add(file_id_1, file_name_1, data_stream_1)
        fs_entry_2 = fs_mgr.add(file_id_2, file_name_2, data_stream_2)
        fs_entry_2.extract()

        # list all files (even exrtacted from compressed archives)
        file_paths = fs_mgr.list_file_paths(include_extracted=True)
        assert len(file_paths) == 3
        assert fs_entry_1.file_path in file_paths
        assert fs_entry_2.file_path in file_paths
        for extracted_file_path_2 in fs_entry_2.extracted_file_paths:
            assert extracted_file_path_2 in file_paths

        # list all 'root' files (not including the extracted from archives)
        file_paths = fs_mgr.list_file_paths()
        assert len(file_paths) == 2
        assert fs_entry_1.file_path in file_paths
        assert fs_entry_2.file_path in file_paths

    def test_filestorage_manager_errors(self, tmpdir):
        """Tests on file storage manager errors."""

        fs_mgr = FileStorageMgr(str(tmpdir))

        with pytest.raises(FileNotFoundError):
            fs_mgr.get('not_found_dir')
