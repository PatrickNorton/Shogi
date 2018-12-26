class NotPromotableException(Exception):
    pass


class PromotedException(Exception):
    pass


class DemotedException(Exception):
    pass


class IllegalMove(Exception):
    pass

class PlayerExit(Exception):
    pass


class OtherMove(Exception):
    pass


class OtherInput(Exception):
    pass