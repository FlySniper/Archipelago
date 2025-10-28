from NetUtils import NetworkItem

POLL_OPTION_TYPE_ITEM = "ITEM"
POLL_OPTION_TYPE_DEATHLINK = "DEATHLINK"

class PollOption:
    def __init__(self, name: str, item_reference: NetworkItem | None, location: int | None, poll_option_type: str):
        self.name = name
        self.item_reference = item_reference
        self.location = location
        self.poll_option_type = poll_option_type