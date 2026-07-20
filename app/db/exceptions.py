class DatabaseError(Exception):
    pass


class ItemNotFoundError(Exception):
    pass


class ItemAlreadyInCartError(Exception):
    pass


class ItemNotInCartError(Exception):
    pass


class EmptyCartError(Exception):
    pass


class NonExistingItemError(Exception):
    pass


class OrderNotFoundError(Exception):
    pass


class UsernameAlreadyTakenError(Exception):
    pass
