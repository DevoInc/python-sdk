from enum import Enum
from typing import List

from devo.api.exception import DevoClientException


class Id:
    def __init__(self, creator: str, name: str):
        self.creator: str = creator
        self.name: str = name


class Visibility(str, Enum):
    CREATOR_ONLY = "creator-only"
    ALL_SUBDOMAINS = "all-subdomains"


class RecipeType(str, Enum):
    ONCE = "once"
    PERIODIC = "periodic"


class Source:
    def __init__(self, query: str):
        self.query: str = query


class LookupTypeType(str, Enum):
    NORMAL = "normal"
    HISTORIC = "historic"


class LookupTypeInstantPolicy(str, Enum):
    NATURAL = "natural"
    CONST = "const"
    COLUMN = "column"


class LookupType:
    def __init__(self, type: LookupTypeType = LookupTypeType.NORMAL, instant_policy: LookupTypeInstantPolicy = None,
                 instant: int = None, column_name: str = None):
        self.type = type
        self.instantPolicy = instant_policy
        self.instant = instant
        self.columnName = column_name
        if self.instantPolicy is not None and self.type != LookupTypeType.HISTORIC:
            raise DevoClientException("No 'recipe.lookupType.instantPolicy' value is expected for 'historic' 'recipe.lookupType.type' lookup")
        if self.instant is not None and (self.type != LookupTypeType.HISTORIC or self.instantPolicy != LookupTypeInstantPolicy.CONST):
            raise DevoClientException("No 'recipe.lookupType.instant' value is expected for 'historic' value at 'recipe.lookupType.type' and 'const' value at 'recipe.lookupType.instantPolicy' lookup")
        if self.columnName is not None and (self.type != LookupTypeType.HISTORIC or self.instantPolicy != LookupTypeInstantPolicy.COLUMN):
            raise DevoClientException("No 'recipe.lookupType.columnName' value is expected for 'historic' value at 'recipe.lookupType.type' and 'column' value at 'recipe.lookupType.instantPolicy' lookup")


class Recipe:
    def __init__(self, recipe_type: RecipeType, source: Source, lookup_type: LookupType = LookupType(), append: bool = False, key: Key,
                 column_filter: List[ColumnFilter], contribution: Contribution, secondary_indexes: SecondaryIndexes,
                 refresh_millis: int, start_millis: int, requires_date: bool = False):
        self.recipe_type: RecipeType = recipe_type
        self.source: Source = source
        self.lookup_type: LookupType = lookup_type
        self.append: bool = append
        self.key: Key = key
        self.columnFilter: List[ColumnFilter] = column_filter
        self.contribution: Contribution = contribution
        self.secondary_indexes: SecondaryIndexes = secondary_indexes
        self.refresh_millis: int = refresh_millis
        self.start_millis: int = start_millis
        self.requires_date: bool = requires_date


class Lookup:
    def __init__(self, id: Id, recipe: Recipe, notify_status: bool = False,
                 visibility: Visibility = Visibility.CREATOR_ONLY):
        self.id: Id = id
        self.visibility: Visibility = visibility
        self.recipe: Recipe = recipe
        self.notifyStatus: bool = notify_status
