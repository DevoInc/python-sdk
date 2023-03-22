from enum import Enum


class Id:
    def __init__(self, creator: str, name: str):
        self.creator: str = creator
        self.name: str = name

class Visibility(str, Enum):
    CREATOR_ONLY = "creator-only"
    ALL_SUBDOMAINS = "all-subdomains"

class Recipe:
    pass

class Lookup:
    def __init__(self, id: Id, recipe: Recipe, notify_status: bool = False, visibility: Visibility = Visibility.CREATOR_ONLY):
        self.id: Id = id
        self.visibility: Visibility = visibility
        self. recipe: Recipe = recipe
        self.notify_status: bool = notify_status
