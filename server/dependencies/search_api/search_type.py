from enum import Enum


class SearchType(Enum):
    POSTCODE = "postcode"
    UPRN = "uprn"
    USRN = "usrn"
    TEXT = "text"
    TITLE = "title"
