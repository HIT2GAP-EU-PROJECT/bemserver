"""Data model for IFC file."""

from .thing import Thing


class IFCFile(Thing):
    """IFC file description."""

    ALLOWED_IFC_FILE_EXTENSIONS = ('.ifc', '.zip', '.ifczip',)

    def __init__(
            self, original_file_name, file_name, description=None, **kwargs):
        super().__init__(**kwargs)
        self.original_file_name = original_file_name
        self.file_name = file_name
        self.description = description
