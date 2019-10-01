"""File storage manager."""

from pathlib import Path
import shutil
import zipfile

from .exceptions import (
    FileStorageManagerError, FileStorageSaveError, FileStorageDeleteError,
    FileStorageNotCompressedError)


# TODO: auto extract compressed files?


class FileStorageMgr():
    """File storage manager allows to manipulate entries
    (`FileStorageEntry` instances) in a storage folder."""

    def __init__(self, dir_path):
        """
        :param Path|str dir_path: Main file storage folder.
        """
        self.dir_path = Path(dir_path)

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'dir_path="{self.dir_path}"'
            ')'.format(self=self))

    def add(self, file_id, file_name, data_stream):
        """Save a data stream to a file in its storage folder entry
        (data stream will be closed after use).

        :param UUID file_id: File storage entry's ID (entry folder name).
        :param str file_name: File's name (as saved on disk).
        :param file-like object data_stream: Data stream to write in file.
        :returns FileStorageEntry: The file storage entry created.
        """
        fs_entry = FileStorageEntry(self.dir_path, file_id)
        fs_entry.save(file_name, data_stream)
        return fs_entry

    def get(self, file_id):
        """Get a file storage entry using its unique `file_id`.

        :param UUID file_id: File storage entry's ID (entry folder name).
        :returns FileStorageEntry: The file storage entry found.
        """
        fs_entry = FileStorageEntry(self.dir_path, file_id)
        if fs_entry.is_empty():
            raise FileNotFoundError()
        return fs_entry

    def delete(self, file_id, *, ignore_errors=False):
        """Clear a file storage folder by removing all his files
        (including extracted files from compressed archive).

        :param UUID file_id: File storage entry's ID (entry folder name).
        :param bool ignore_errors: If True no exception raised (default False).
        :raises FileNotFoundError: File's storage folder entry does not exist.
        :raises FileStorageDeleteError:
            Error while deleting file's storage folder entry.
        """
        try:
            fs_entry = self.get(file_id)
            fs_entry.delete(ignore_errors=ignore_errors)
        except FileNotFoundError as exc:
            if not ignore_errors:
                raise exc

    def get_all(self):
        """Get all file storage entries.

        :returns [FileStorageEntry]: List of all storage folder entries.
        """
        fs_entries = []
        for item_path in self.dir_path.iterdir():
            if item_path.is_dir():
                fs_entries.append(self.get(item_path.name))
        return fs_entries

    def list_file_paths(self, *, include_extracted=False):
        """List all files from all storage folder entries.

        :param bool include_extracted:
            If True, also reads 'extract' folder (default False).
        :returns [Path]: List of all file paths in entry storage.
        """
        file_paths = []
        for fs_entry in self.get_all():
            file_paths.extend(
                fs_entry.list_file_paths(include_extracted=include_extracted))
        return file_paths


class FileStorageEntry():
    """A storage folder entry class."""

    EXTRACTED_DIR = '_extracted'

    def __init__(self, base_dir_path, file_id):
        """
        :param Path|str dir_path: Main file storage folder.
        :param UUID file_id: File storage entry ID
            (it is used as unique folder path).
        """
        if file_id is None:
            raise ValueError('Invalid file_id.')
        self.file_id = file_id
        self.base_dir_path = Path(base_dir_path)
        self.entry_dir_path = self.base_dir_path / str(self.file_id)
        self.extracted_dir_path = self.entry_dir_path / self.EXTRACTED_DIR

        self._file_name = None

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'base_dir_path="{self.base_dir_path}"'
            ', file_id="{self.file_id}"'
            ', entry_dir_path="{self.entry_dir_path}"'
            ', file_name="{self.file_name}"'
            ', file_path="{self.file_path}"'
            ', extracted_dir_path="{self.extracted_dir_path}"'
            ')'.format(self=self))

    def _get_file_name(self):
        """An entry in storage folder can only contain one file (at root level).
        Here, the purpose is to get its name automatically by reading the
        entry folder.

        ..Note:
            If file is a compressed archive, entry folder can also contain
            an 'extract' folder with all extracted files from the archive.
            In this function, this extraction folder is ignored.

        :returns str: The name of the unique file found or `None`.
        :raises FileNotFoundError: File's storage folder does not exist.
        :raises FileStorageManagerError:
            The root level of a file's storage folder must contain one file.
        """
        if not self.entry_dir_path.exists():
            return None
        file_names = [
            file_path.name for file_path in self.entry_dir_path.iterdir()
            if file_path.is_file()]
        # root level of an entry storage folder must only contain ONE file
        if len(file_names) != 1:
            raise FileStorageManagerError()
        return file_names[0]

    @property
    def file_name(self):
        """Get the file name of current storage folder entry.

        :returns str: File's name.
        """
        if self._file_name is None:
            self._file_name = self._get_file_name()
        return self._file_name

    @property
    def file_path(self):
        """Get the file path of current storage folder entry.

        :returns Path: File's path.
        """
        return self.entry_dir_path / (self.file_name or '')

    @property
    def extracted_file_paths(self):
        """Get all extracted file paths from current storage folder entry.

        :returns [Path]: List of all extracted file paths.
        """
        def _list_file_paths(dir_path, deep=True):
            file_paths = []
            for item_path in dir_path.iterdir():
                if item_path.is_dir() and deep:
                    file_paths.extend(_list_file_paths(item_path, deep=deep))
                elif item_path.is_file():
                    file_paths.append(item_path)
            return file_paths

        extracted_file_paths = []
        if self.extracted_dir_path.exists():
            for extracted_item_path in self.extracted_dir_path.iterdir():
                if extracted_item_path.is_dir():
                    extracted_file_paths.extend(
                        _list_file_paths(extracted_item_path))
                elif extracted_item_path.is_file():
                    extracted_file_paths.append(extracted_item_path)
        return extracted_file_paths

    def is_empty(self):
        """Is current entry storage folder containing a file?

        :returns bool: False if entry storage folder contains a file.
        """
        return not self.file_path.exists() or not self.file_path.is_file()

    def is_compressed(self):
        """Is the file in current entry storage folder a compressed archive?

        :returns bool: True if file is a compressd archive, else False.
        """
        return zipfile.is_zipfile(str(self.file_path))

    def save(self, file_name, data_stream):
        """Save a data stream to a file in its storage folder entry
        (data stream will be closed after use).

        :param str file_name: File's name (as saved on disk).
        :param file-like object data_stream: Data stream to write in file.
        :returns Path: The storage path of saved file.
        :raises ValueError: Invalid input data stream.
        :raises FileExistsError: File already exists in storage folder.
        :raises FileStorageSaveError: Error while saving data stream to a file.
        """
        if self.file_name == file_name:
            raise FileExistsError(file_name)
        try:
            self._file_name = file_name
            # save data stream in a file on disk
            if not self.file_path.parent.exists():
                self.file_path.parent.mkdir()
            buffer_size = 16384
            data_stream.seek(0)
            with open(str(self.file_path), 'wb') as cur_file:
                shutil.copyfileobj(data_stream, cur_file, buffer_size)
        except (ValueError, shutil.Error) as exc:
            # on errors, clean storage folder (transaction-like)
            self.delete(ignore_errors=True)
            raise FileStorageSaveError(exc)
        finally:
            data_stream.close()
        return self.file_path

    def delete(self, *, ignore_errors=False):
        """Clear a file storage folder by removing all his files
        (including extracted files from compressed archive).

        :param bool ignore_errors: If True raises no exception (default False).
        :raises FileStorageDeleteError:
            Error while deleting file's storage folder.
        """
        try:
            shutil.rmtree(
                str(self.entry_dir_path), ignore_errors=ignore_errors)
        except shutil.Error as exc:
            if not ignore_errors:
                raise FileStorageDeleteError(exc)

    def list_file_paths(self, *, include_extracted=False):
        """List all files from current entry storage.

        :param bool include_extracted:
            If True, also reads 'extracted' folder (default False).
        :returns [Path]: List of all file paths in entry storage.
        """
        file_paths = []
        if not self.is_empty():
            file_paths = [self.file_path]
            if include_extracted and self.extracted_dir_path.exists():
                file_paths.extend([
                    x for x in self.extracted_dir_path.iterdir()
                    if x.is_file()])
        return file_paths

    def extract(self, *, pwd=None):
        """Extract files from a compressed archive.

        :param str pwd: Password used for encrypted files, optional.
        :returns [Path]: The storage path(s) of uncompressed archive content.
        :raises FileStorageNotCompressedError:
            File is not a compressed archive (gz...).
        """
        if not self.is_compressed():
            raise FileStorageNotCompressedError()

        extracted_file_paths = []
        if not self.extracted_dir_path.exists():
            self.extracted_dir_path.mkdir()
            with zipfile.ZipFile(str(self.file_path), 'r') as zipped_file:
                for z_file_name in zipped_file.namelist():
                    extracted_file_path = zipped_file.extract(
                        z_file_name, path=str(self.extracted_dir_path),
                        pwd=pwd)
                    extracted_file_paths.append(Path(extracted_file_path))
        else:
            extracted_file_paths = self.extracted_file_paths

        return extracted_file_paths
