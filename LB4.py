from abc import ABC, abstractmethod
from typing import Dict, List

class CustomError(BaseException):
    pass

class InsufficientFundsError(CustomError):
    pass

class InvalidTransactionTypeError(CustomError):
    pass

class FinancialOperation(ABC):
    @abstractmethod
    def execute(self):
        pass

class Account:
    accounts: Dict[int, 'Account'] = {}

    def __init__(self, account_id: int, account_name: str, balance: float, currency: str):
        self.account_id = account_id
        self.account_name = account_name
        self.balance = balance
        self.currency = currency
        Account.accounts[account_id] = self

    def deposit(self, amount: float):
        self.balance += amount
        print(f"Счет '{self.account_name}' пополнен на {amount}. Новый баланс: {self.balance} {self.currency}")

    def withdraw(self, amount: float):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Со счета '{self.account_name}' снято {amount}. Новый баланс: {self.balance} {self.currency}")
        else:
            raise InsufficientFundsError("Недостаточно средств на счете.")

    def get_balance(self):
        return self.balance

    @staticmethod
    def find_account(account_id: int) -> 'Account':
        if account_id in Account.accounts:
            return Account.accounts[account_id]
        else:
            raise ValueError(f"Счет с ID {account_id} не найден.")

    def __add__(self, other: 'Account') -> float:
        return self.balance + other.balance

    def __gt__(self, other: 'Account') -> bool:
        return self.balance > other.balance

    def __str__(self):
        return f"Счет {self.account_name} (ID: {self.account_id}), Баланс: {self.balance} {self.currency}"

    def __repr__(self):
        return f"Account({self.account_id}, '{self.account_name}', {self.balance}, '{self.currency}')"

class Transaction(FinancialOperation):
    def __init__(self, transaction_id: int, account: Account, transaction_type: str, amount: float, description: str):
        self.transaction_id = transaction_id
        self.account = account
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description

    def execute(self):
        try:
            if self.transaction_type == "доход":
                self.account.deposit(self.amount)
            elif self.transaction_type == "расход":
                self.account.withdraw(self.amount)
            else:
                raise InvalidTransactionTypeError("Неверный тип транзакции.")
        except CustomError as e:
            print(f"Ошибка при выполнении транзакции: {e}")
        finally:
            print(f"Транзакция {self.transaction_id} завершена.")

class Tax:
    def __init__(self, tax_name: str, rate: float):
        self.tax_name = tax_name
        self.rate = rate

    def calculate_tax(self, income: float) -> float:
        tax_amount = income * self.rate
        print(f"Налог '{self.tax_name}' рассчитан: {tax_amount}")
        return tax_amount

class Report:
    def __init__(self, report_id: int, report_type: str, content: str):
        self.report_id = report_id
        self.report_type = report_type
        self.content = content

    def generate_report(self):
        print(f"Отчет '{self.report_type}' сгенерирован: {self.content}")

class AccountManager:
    def __init__(self):
        self.accounts = []

    def add_account(self, account: Account):
        self.accounts.append(account)

    def find_max_balance_account(self):
        if not self.accounts:
            raise ValueError("Список счетов пуст.")
        return max(self.accounts, key=lambda acc: acc.get_balance())

class BaseAccount:
    def __init__(self, account_id: int, account_name: str):
        self._account_id = account_id
        self.account_name = account_name

    def display_info(self):
        print(f"Базовый счет: {self.account_name} (ID: {self._account_id})")

class DerivedAccount(BaseAccount):
    def __init__(self, account_id: int, account_name: str, balance: float):
        super().__init__(account_id, account_name)
        self.balance = balance

    def display_info(self):
        if self.balance > 0:
            super().display_info()
            print(f"Баланс: {self.balance}")
        else:
            print("Баланс отрицательный или нулевой.")

if __name__ == "__main__":
    try:
        account1 = Account(1, "Основной счет", 1000, "RUB")
        account2 = Account(2, "Дополнительный счет", 500, "RUB")

        print("\n--- Управление транзакциями ---")
        transaction_type = input("Введите тип транзакции (доход/расход): ").strip().lower()
        while transaction_type not in ["доход", "расход"]:
            print("Неверный тип транзакции. Введите 'доход' или 'расход'.")
            transaction_type = input("Введите тип транзакции (доход/расход): ").strip().lower()

        amount = float(input("Введите сумму транзакции: "))
        description = input("Введите описание транзакции: ")

        transaction1 = Transaction(1, account1, transaction_type, amount, description)
        transaction1.execute()

        print("\n--- Расчет налога ---")
        tax_name = input("Введите название налога: ")
        tax_rate = float(input("Введите ставку налога (например, 0.2 для 20%): "))
        income = float(input("Введите доход для расчета налога: "))

        tax1 = Tax(tax_name, tax_rate)
        tax_amount = tax1.calculate_tax(income)

        if account1.get_balance() >= tax_amount:
            account1.withdraw(tax_amount)
            print(f"Налог '{tax_name}' уплачен.")
        else:
            print("Недостаточно средств для уплаты налога.")

        print("\n--- Все счета ---")
        for acc_id, acc in Account.accounts.items():
            print(acc)

        print("\n--- Перегрузка операторов ---")
        print(f"Суммарный баланс счетов: {account1 + account2}")
        print(f"Счет 1 больше счета 2: {account1 > account2}")

        report1 = Report(1, "Баланс", f"Баланс счета '{account1.account_name}': {account1.get_balance()} {account1.currency}")
        report1.generate_report()

        account_manager = AccountManager()
        account_manager.add_account(account1)
        account_manager.add_account(account2)
        max_balance_account = account_manager.find_max_balance_account()
        print(f"\nСчет с максимальным балансом: {max_balance_account}")

        derived_account = DerivedAccount(3, "Производный счет", 200)
        derived_account.display_info()

    except CustomError as e:
        print(f"Пользовательская ошибка: {e}")
    except ValueError as e:
        print(f"Ошибка: {e}")
    finally:
        print("Программа завершена.")