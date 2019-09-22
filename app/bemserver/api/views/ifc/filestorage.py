"""File storage management."""

from flask import current_app

from bemserver.database.filestorage.filestore import FileStorageMgr

from .exceptions import FileStorageConfigError


# TODO: do this at init time?
# TODO: check at init that storage path exists and is writable?

def get_filestorage_manager():
    """Return file storage manager according to application configuration."""

    app_config = current_app.config

    # Instantiate file storage manager
    try:
        storage_dir = app_config['FILE_STORAGE_DIR']
    except KeyError:
        raise FileStorageConfigError(
            "Missing file storage directory in configuration.")

    return FileStorageMgr(storage_dir)
