from ..type_aliases import TCSContext
from ...levels import SHORT_NAME_TO_LEVEL_AREA
from ...locations import LEVEL_COMMON_LOCATIONS, LOCATION_NAME_TO_ID


class TrueJediAndMinikitChecker:
    remaining_true_jedi_checks: list[str]
    remaining_minikit_checks: dict[str, list[tuple[int, str]]]

    def __init__(self):
        self.remaining_true_jedi_checks = list(LEVEL_COMMON_LOCATIONS.keys())
        self.remaining_minikit_checks = {
            name: list(enumerate(data["Minikits"], start=1)) for name, data in LEVEL_COMMON_LOCATIONS.items()
        }

    async def check_true_jedi_and_minikits(self, ctx: TCSContext, new_location_checks: list[int]):
        # todo: More smartly read only as many bytes as necessary. So only 1 byte when either the True Jedi is complete
        #  or all Minikits have been collected.
        cached_bytes: dict[str, tuple[int, int]] = {}

        def get_bytes_for_short_name(short_name: str):
            if short_name in cached_bytes:
                return cached_bytes[short_name]
            else:
                # True Jedi seems to be at the 4th byte (maybe it is the 3rd because they both get activated?), Minikit
                # count is at the 6th byte. To reduce memory reads, both are retrieved simultaneously.
                read_bytes = ctx.read_bytes(SHORT_NAME_TO_LEVEL_AREA[short_name].address + 3, 3)
                true_jedi_byte = read_bytes[0]
                minikit_count_byte = read_bytes[2]
                new_bytes = (true_jedi_byte, minikit_count_byte)
                cached_bytes[short_name] = new_bytes
                return new_bytes

        updated_remaining_true_jedi_checks: list[str] = []
        for shortname in self.remaining_true_jedi_checks:
            location_name = LEVEL_COMMON_LOCATIONS[shortname]["True Jedi"]
            location_id = LOCATION_NAME_TO_ID[location_name]
            if location_id in ctx.checked_locations:
                continue
            true_jedi = get_bytes_for_short_name(shortname)[0]
            if true_jedi:
                new_location_checks.append(location_id)
            updated_remaining_true_jedi_checks.append(shortname)
        self.remaining_true_jedi_checks = updated_remaining_true_jedi_checks

        updated_remaining_minikit_checks: dict[str, list[tuple[int, str]]] = {}
        for shortname, remaining_minikits in self.remaining_minikit_checks.items():
            not_checked_minikit_checks: list[int] = []
            updated_remaining_minikits: list[tuple[int, str]] = []
            for count, location_name in remaining_minikits:
                location_id = LOCATION_NAME_TO_ID[location_name]
                if location_id not in ctx.checked_locations:
                    not_checked_minikit_checks.append(location_id)
                    updated_remaining_minikits.append((count, location_name))
            if updated_remaining_minikits:
                updated_remaining_minikit_checks[shortname] = updated_remaining_minikits

                minikit_count = get_bytes_for_short_name(shortname)[1]
                zipped = zip(updated_remaining_minikits, not_checked_minikit_checks, strict=True)
                for (count, _name), location_id in zipped:
                    if minikit_count >= count:
                        new_location_checks.append(location_id)
        self.remaining_minikit_checks = updated_remaining_minikit_checks
