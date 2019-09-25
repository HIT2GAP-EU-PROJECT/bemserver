"""File storage manager exceptions."""


class FileStorageManagerError(Exception):
    """Generic file storage manager error."""


class FileStorageSaveError(FileStorageManagerError):
    """An error occured while saving a data stream to a file."""


class FileStorageDeleteError(FileStorageManagerError):
    """An error occured while deleting all file's storage folder content."""


class FileStorageNotCompressedError(FileStorageManagerError):
    """Error when a file is not a compressed archive."""
