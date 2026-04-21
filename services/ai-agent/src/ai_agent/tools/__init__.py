from .search_hotels import SEARCH_HOTELS_SCHEMA, execute_search_hotels
from .get_hotel_details import GET_HOTEL_DETAILS_SCHEMA, execute_get_hotel_details

TOOLS = [SEARCH_HOTELS_SCHEMA, GET_HOTEL_DETAILS_SCHEMA]

TOOL_HANDLERS = {
    "search_hotels": execute_search_hotels,
    "get_hotel_details": execute_get_hotel_details,
}

__all__ = ["TOOLS", "TOOL_HANDLERS"]
