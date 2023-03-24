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
            raise DevoClientException(
                "No 'recipe.lookupType.instantPolicy' value is expected for 'historic' 'recipe.lookupType.type' lookup")
        if self.instant is not None and (
                self.type != LookupTypeType.HISTORIC or self.instantPolicy != LookupTypeInstantPolicy.CONST):
            raise DevoClientException(
                "No 'recipe.lookupType.instant' value is expected for 'historic' value at 'recipe.lookupType.type' and"
                " 'const' value at 'recipe.lookupType.instantPolicy' lookup")
        if self.columnName is not None and (
                self.type != LookupTypeType.HISTORIC or self.instantPolicy != LookupTypeInstantPolicy.COLUMN):
            raise DevoClientException(
                "No 'recipe.lookupType.columnName' value is expected for 'historic' value at 'recipe.lookupType.type'"
                " and 'column' value at 'recipe.lookupType.instantPolicy' lookup")


class KeyType(str, Enum):
    FIRST_COLUMN = "first-column"
    ROW_HASH = "row-hash"
    COL_HASH = "col-hash"
    COLUMN = "column"
    SEQ = "seq"


class Key:
    def __init__(self, type: KeyType, columns: List[str] = None, column: str = None):
        self.type = type
        self.columns = columns
        self.column = column
        if self.column is not None and self.type != KeyType.COLUMN:
            raise DevoClientException("'recipe.key.column' value is expected when 'recipe.key.type' value is 'column'")
        if self.columns is not None and self.type != KeyType.COL_HASH:
            raise DevoClientException(
                "'recipe.key.columns' value is expected when 'recipe.key.type' value is 'col-hash'")


class ContributionType(str, Enum):
    ADD = "add"
    DEL = "del"
    COL = "col"


class Contribution:
    def __init__(self, type: ContributionType = ContributionType.ADD, name: str = None):
        self.type = type
        self.name = name
        if self.name is not None and self.type != ContributionType.COL:
            raise DevoClientException(
                "'recipe.contribution.name' value is expected when 'recipe.contribution.type' value is 'col'")


class IndexType(str, Enum):
    ALL = "all"
    NONE = "none"
    BY_NAME = "by-name"


class SecondaryIndexes:
    def __init__(self, type: IndexType = IndexType.NONE, map: List[str] = None):
        self.type = type
        self.map: List[str] = map
        if self.map is not None and self.type != IndexType.BY_NAME:
            raise DevoClientException(
                "'recipe.secondaryIndexes.map' value is expected when 'recipe.secondaryIndexes.type' value is"
                " 'by-name'")


class Recipe:
    def __init__(self, source: Source, recipe_type: RecipeType = RecipeType.ONCE,
                 lookup_type: LookupType = LookupType(), append: bool = False, key: Key = Key(KeyType.SEQ),
                 column_filter: List[str] = None, contribution: Contribution = Contribution(),
                 secondary_indexes: SecondaryIndexes = None,
                 refresh_millis: int = None, start_millis: int = None, requires_date: bool = False):
        self.recipeType: RecipeType = recipe_type
        self.source: Source = source
        self.lookupType: LookupType = lookup_type
        self.append: bool = append
        self.key: Key = key
        self.columnFilter: List[str] = column_filter
        self.contribution: Contribution = contribution
        self.secondary_indexes: SecondaryIndexes = secondary_indexes
        self.refreshMillis: int = refresh_millis
        self.startMillis: int = start_millis
        self.requires_date: bool = requires_date
        if self.refreshMillis is not None and self.recipeType != RecipeType.PERIODIC:
            raise DevoClientException("'refreshMillis' value is expected when 'recipeType' value is 'periodic'")
        if self.startMillis is not None and self.recipeType != RecipeType.PERIODIC:
            raise DevoClientException("'startMillis' value is expected when 'recipeType' value is 'periodic'")


class Lookup:
    def __init__(self, id: Id, recipe: Recipe, notify_status: bool = False,
                 visibility: Visibility = Visibility.CREATOR_ONLY):
        self.id: Id = id
        self.visibility: Visibility = visibility
        self.recipe: Recipe = recipe
        self.notifyStatus: bool = notify_status
