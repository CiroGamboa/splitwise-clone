from typing import Dict, Optional

from domain import Group


class GroupRepository:
    def __init__(self):

    def find_by_id(self, group_id: str) -> Optional[Group]:
        return self._groups.get(group_id)
