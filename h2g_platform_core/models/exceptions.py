"""Model exceptions"""


class OccupantUnknownElectronicFamilyError(Exception):
    """Unknow electronics family error for occupant profile"""


class TreeNodeAlreadyHasParentError(Exception):
    """Tree node already has a parent."""
