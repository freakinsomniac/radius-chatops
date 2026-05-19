class RadiusException(Exception):
    pass


class DatabaseError(RadiusException):
    pass


class UserNotFound(DatabaseError):
    pass


class DuplicateUser(DatabaseError):
    pass


class GroupNotFound(DatabaseError):
    pass


class NASNotFound(DatabaseError):
    pass


class OperationError(RadiusException):
    pass


class PoolNotInitialized(OperationError):
    pass
