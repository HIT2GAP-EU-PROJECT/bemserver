"""Security manager exceptions."""


class SecurityManagerError(Exception):
    """Generic security manager exception."""


class UserAccountAlreadyExistError(SecurityManagerError):
    """User account uid already exists."""
