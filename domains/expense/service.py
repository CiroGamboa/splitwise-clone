from typing import Dict, List, Optional, Set, Tuple

from domain import User, Expense
from domains.group.repository import GroupRepository


class ExpenseService:
    def __init__(self, group_repo: GroupRepository):
        self._repo = group_repo

    def create_expense(
        self,
        group_id: str,
        amount: float,
        payer: User,
        debtors: Optional[Set[User]] = None,
    ) -> Expense:
        group = self._get_group_or_raise(group_id)

        if debtors is None:
            debtors = set(group.members)

        expense = Expense.create(amount=amount, payer=payer, debtors=debtors)
        group.add_expense(expense)
        self._repo.save(group)
        return expense

    def calculate_debts(self, group_id: str) -> Dict[Tuple[User, User], float]:
        group = self._get_group_or_raise(group_id)
        return group.calculate_debt_matrix()

    def get_settlement_plan(self, group_id: str) -> List[Tuple[User, User, float]]:
        group = self._get_group_or_raise(group_id)
        return group.settle_up()

    def settle_up(
        self, group_id: str, payer: User, payee: User, amount: float
    ) -> Expense:
        group = self._get_group_or_raise(group_id)

        debt_matrix = group.calculate_debt_matrix()
        current_debt = debt_matrix.get((payer, payee), 0.0)

        if current_debt < 0.005:
            raise ValueError(f"'{payer.name}' does not owe '{payee.name}' anything.")

        if amount > current_debt + 0.005:
            raise ValueError(
                f"Settlement amount {amount} exceeds debt of {current_debt}."
            )

        settlement = Expense.create(amount=amount, payer=payer, debtors={payee})
        group.add_expense(settlement)
        self._repo.save(group)
        return settlement

    def drop_out_from_expense(
        self, group_id: str, expense_index: int, user: User
    ) -> Expense:
        group = self._get_group_or_raise(group_id)
        group.remove_debtor_from_expense(expense_index, user)
        self._repo.save(group)
        return group.expenses[expense_index]

    def _get_group_or_raise(self, group_id: str):
        group = self._repo.find_by_id(group_id)
        if group is None:
            raise ValueError(f"Group with id '{group_id}' not found.")
        return group
