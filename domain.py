from typing import Set, List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass(frozen=True)
class User:
    name: str

    @staticmethod
    def create(name: str) -> "User":
        return User(name=name)


@dataclass
class Expense:
    amount: float
    payer: User
    debtors: Set[User]

    @staticmethod
    def create(amount: float, payer: User, debtors: Set[User]) -> "Expense":
        if not len(debtors):
            raise ValueError("No debtors. Nobody needs to return money then?")
        return Expense(amount=amount, payer=payer, debtors=debtors)


@dataclass
class Group:
    id: str
    name: str
    currency: str
    members: Set[User] = field(default_factory=set)
    expenses: List[Expense] = field(default_factory=list)

    def add_member(self, user: User):
        self.members.add(user)

    def remove_member(self, user: User):
        self.members.remove(user)

    def add_expense(self, expense: Expense):
        if not expense.debtors.issubset(self.members):
            raise ValueError("All debtors must be group members.")
        self.expenses.append(expense)

    def remove_debtor_from_expense(self, expense_index: int, user: User):
        expense = self.expenses[expense_index]
        expense.debtors = expense.debtors - {user}

    def calculate_debt_matrix(self) -> Dict[Tuple[User, User], float]:
        raw_debts = {}

        for expense in self.expenses:
            share = expense.amount / len(expense.debtors)
            for debtor in expense.debtors:
                if debtor == expense.payer:
                    continue
                key = (debtor, expense.payer)
                raw_debts[key] = raw_debts.get(key, 0.0) + share

        netted = {}
        processed = set()

        for (debtor, creditor), amount in raw_debts.items():
            pair = frozenset({debtor, creditor})
            if pair in processed:
                continue
            processed.add(pair)

            reverse_amount = raw_debts.get((creditor, debtor), 0.0)
            net = amount - reverse_amount

            if net > 0:
                netted[(debtor, creditor)] = round(net, 2)
            elif net < 0:
                netted[(creditor, debtor)] = round(-net, 2)

        return netted

    def settle_up(self) -> List[Tuple[User, User, float]]:
        debt_matrix = self.calculate_debt_matrix()
        balances = {}

        for (debtor, creditor), amount in debt_matrix.items():
            balances[debtor] = balances.get(debtor, 0.0) - amount
            balances[creditor] = balances.get(creditor, 0.0) + amount

        debtors_list = []
        creditors_list = []
        for user, balance in balances.items():
            if balance < -0.005:
                debtors_list.append([user, -balance])
            elif balance > 0.005:
                creditors_list.append([user, balance])

        debtors_list.sort(key=lambda x: x[1], reverse=True)
        creditors_list.sort(key=lambda x: x[1], reverse=True)

        settlements = []
        i, j = 0, 0
        while i < len(debtors_list) and j < len(creditors_list):
            debtor, debt_amount = debtors_list[i]
            creditor, credit_amount = creditors_list[j]

            transfer = round(min(debt_amount, credit_amount), 2)
            if transfer > 0:
                settlements.append((debtor, creditor, transfer))

            debtors_list[i][1] = round(debt_amount - transfer, 2)
            creditors_list[j][1] = round(credit_amount - transfer, 2)

            if debtors_list[i][1] < 0.005:
                i += 1
            if creditors_list[j][1] < 0.005:
                j += 1

        return settlements

    def has_unsettled_debts(self, user: User) -> bool:
        debt_matrix = self.calculate_debt_matrix()
        for (debtor, creditor), amount in debt_matrix.items():
            if (debtor == user or creditor == user) and amount > 0.005:
                return True
        return False
