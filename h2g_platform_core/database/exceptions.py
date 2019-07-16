"""Models exceptions"""


class ItemError(Exception):
    """Generic item exception"""


class ItemNotFoundError(ItemError):
    """Item not found error"""


class ItemSaveError(ItemError):
    """Item save error"""


class ItemDeleteError(ItemError):
    """Item delete error"""


class IntegrityError(Exception):
    """The dataset is not as expected"""
