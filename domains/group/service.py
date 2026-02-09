import uuid

from domain import User, Group
from domains.group.repository import GroupRepository


class GroupService:
    def __init__(self, group_repo: GroupRepository):
        self._repo = group_repo

    def create_group(self, name: str, currency: str, creator: User) -> Group:
        group_id = str(uuid.uuid4())
        group = Group(id=group_id, name=name, currency=currency)
        group.add_member(creator)
        self._repo.save(group)
        return group

    def invite_to_group(self, group_id: str, user: User) -> Group:
        group = self._get_group_or_raise(group_id)
        group.add_member(user)
        self._repo.save(group)
        return group

    def drop_out_from_group(self, group_id: str, user: User) -> Group:
        group = self._get_group_or_raise(group_id)

        if group.has_unsettled_debts(user):
            raise ValueError(f"User '{user.name}' has unsettled debts.")

        group.remove_member(user)
        self._repo.save(group)
        return group

    def _get_group_or_raise(self, group_id: str) -> Group:
        group = self._repo.find_by_id(group_id)
        if group is None:
            raise ValueError(f"Group with id '{group_id}' not found.")
        return group
