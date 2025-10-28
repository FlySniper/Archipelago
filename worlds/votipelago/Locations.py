from typing import Dict

location_table: Dict[str, int | None] = {f"Option Number {loc_id}": loc_id for loc_id in range(1, 1001)}
location_table["Votipelago Victory Location"] = None
