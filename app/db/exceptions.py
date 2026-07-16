class DatabaseError(Exception):
    pass


class ItemAlreadyInCartError(Exception):
    pass


class ItemNotInCartError(Exception):
    pass


class EmptyCartError(Exception):
    pass


class NonExistingItemError(Exception):
    pass


class OrderAccessDeniedError(Exception):
    pass
