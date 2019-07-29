"""File storage API exceptions."""


class IFCFileAPIError(Exception):
    """Generic IFC file storage API error."""


class FileStorageConfigError(IFCFileAPIError):
    """File storage configuration error."""


class IFCFileBadArchiveError(IFCFileAPIError):
    """Error if an IFC compressed archive contains more than one IFC file."""


class IFCFileImportError(IFCFileAPIError):
    """Error while importing an IFC file."""
