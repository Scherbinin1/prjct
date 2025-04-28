from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class CustomError(Exception):

    def __init__(self, message: str = "Произошла ошибка в финансовой операции"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class InsufficientFundsError(CustomError):

    def __init__(self, current_balance: float, requested_amount: float):
        message = (f"Недостаточно средств. Текущий баланс: {current_balance}, "
                   f"попытка снять: {requested_amount}")
        super().__init__(message)
        self.current_balance = current_balance
        self.requested_amount = requested_amount


class InvalidTransactionTypeError(CustomError):

    def __init__(self, transaction_type: str, allowed_types: List[str]):
        message = (f"Недопустимый тип транзакции: '{transaction_type}'. "
                   f"Допустимые типы: {', '.join(allowed_types)}")
        super().__init__(message)
        self.transaction_type = transaction_type
        self.allowed_types = allowed_types


class FinancialOperation(ABC):

    @abstractmethod
    def execute(self) -> bool:
        raise NotImplementedError("Метод execute должен быть реализован в подклассе")


class Account:
    accounts: Dict[int, 'Account'] = {}

    def __init__(self, account_id: int, account_name: str, balance: float, currency: str):
        self.account_id = account_id
        self.account_name = account_name
        self.balance = balance
        self.currency = currency
        self.transaction_history: List[Dict] = []
        Account.accounts[account_id] = self

    def deposit(self, amount: float, description: str = "") -> None:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")

        self.balance += amount
        self._record_transaction("deposit", amount, description)
        print(f"Счет '{self.account_name}' пополнен на {amount}. Новый баланс: {self.balance} {self.currency}")

    def withdraw(self, amount: float, description: str = "") -> None:
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")

        if self.balance < amount:
            raise InsufficientFundsError(self.balance, amount)

        self.balance -= amount
        self._record_transaction("withdrawal", amount, description)
        print(f"Со счета '{self.account_name}' снято {amount}. Новый баланс: {self.balance} {self.currency}")

    def _record_transaction(self, operation_type: str, amount: float, description: str) -> None:
        transaction = {
            'date': datetime.now(),
            'type': operation_type,
            'amount': amount,
            'description': description,
            'balance_after': self.balance
        }
        self.transaction_history.append(transaction)

    def get_balance(self) -> float:
        return self.balance

    def get_transaction_history(self) -> List[Dict]:
        return self.transaction_history

    @staticmethod
    def find_account(account_id: int) -> 'Account':
        account = Account.accounts.get(account_id)
        if account is None:
            raise ValueError(f"Счет с ID {account_id} не найден")
        return account

    def __add__(self, other: 'Account') -> float:
        if not isinstance(other, Account):
            raise TypeError("Можно складывать только объекты Account")
        return self.balance + other.balance

    def __gt__(self, other: 'Account') -> bool:
        if not isinstance(other, Account):
            raise TypeError("Можно сравнивать только объекты Account")
        return self.balance > other.balance

    def __str__(self) -> str:
        return f"Счет {self.account_name} (ID: {self.account_id}), Баланс: {self.balance} {self.currency}"

    def __repr__(self) -> str:
        return f"Account(account_id={self.account_id}, account_name='{self.account_name}', " \
               f"balance={self.balance}, currency='{self.currency}')"


class Transaction(FinancialOperation):
    VALID_TYPES = ["income", "expense"]

    def __init__(self, transaction_id: int, account: Account,
                 transaction_type: str, amount: float, description: str = ""):
        self.transaction_id = transaction_id
        self.account = account
        self.transaction_type = transaction_type.lower()
        self.amount = amount
        self.description = description
        self.executed = False
        self.success = False

    def execute(self) -> bool:
        try:
            if self.transaction_type not in self.VALID_TYPES:
                raise InvalidTransactionTypeError(self.transaction_type, self.VALID_TYPES)

            if self.transaction_type == "income":
                self.account.deposit(self.amount, self.description)
            elif self.transaction_type == "expense":
                self.account.withdraw(self.amount, self.description)

            self.success = True
            return True

        except CustomError as e:
            print(f"Ошибка при выполнении транзакции {self.transaction_id}: {e}")
            self.success = False
            return False
        finally:
            self.executed = True
            print(f"Транзакция {self.transaction_id} {'успешно выполнена' if self.success else 'завершена с ошибкой'}")

    def __str__(self) -> str:
        status = "выполнена" if self.executed else "ожидает выполнения"
        result = "успешно" if self.success else "с ошибкой" if self.executed else "неизвестно"
        return (f"Транзакция ID: {self.transaction_id}, Тип: {self.transaction_type}, "
                f"Сумма: {self.amount}, Статус: {status}, Результат: {result}")


class Tax:

    def __init__(self, tax_name: str, rate: float):
        if not 0 <= rate <= 1:
            raise ValueError("Налоговая ставка должна быть между 0 и 1")
        self.tax_name = tax_name
        self.rate = rate

    def calculate_tax(self, income: float) -> float:
        if income < 0:
            raise ValueError("Доход не может быть отрицательным")
        tax_amount = income * self.rate
        print(f"Налог '{self.tax_name}' рассчитан: {tax_amount:.2f}")
        return tax_amount

    def apply_tax(self, account: Account, income: float) -> bool:
        try:
            tax_amount = self.calculate_tax(income)
            account.withdraw(tax_amount, f"Уплата налога {self.tax_name}")
            return True
        except CustomError as e:
            print(f"Ошибка при уплате налога: {e}")
            return False


class Report:

    def __init__(self, report_id: int, report_type: str, content: str):
        self.report_id = report_id
        self.report_type = report_type
        self.content = content
        self.generated_at = datetime.now()

    def generate_report(self) -> str:
        report = (f"Отчет #{self.report_id}\n"
                  f"Тип: {self.report_type}\n"
                  f"Дата: {self.generated_at}\n"
                  f"Содержание:\n{self.content}")
        print(report)
        return report

    def save_to_file(self, filename: str) -> bool:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.generate_report())
            return True
        except IOError as e:
            print(f"Ошибка при сохранении отчета: {e}")
            return False


class AccountManager:

    def __init__(self):
        self.accounts: List[Account] = []

    def add_account(self, account: Account) -> None:
        if not isinstance(account, Account):
            raise TypeError("Можно добавлять только объекты Account")
        self.accounts.append(account)

    def find_account_by_id(self, account_id: int) -> Optional[Account]:
        for account in self.accounts:
            if account.account_id == account_id:
                return account
        return None

    def find_max_balance_account(self) -> Account:
        if not self.accounts:
            raise ValueError("Нет счетов для поиска")
        return max(self.accounts, key=lambda acc: acc.get_balance())

    def get_total_balance(self) -> float:
        return sum(account.get_balance() for account in self.accounts)

    def transfer(self, from_account_id: int, to_account_id: int, amount: float) -> bool:
        from_account = self.find_account_by_id(from_account_id)
        to_account = self.find_account_by_id(to_account_id)

        if not from_account or not to_account:
            print("Один из счетов не найден")
            return False

        try:
            from_account.withdraw(amount, f"Перевод на счет {to_account_id}")
            to_account.deposit(amount, f"Перевод со счета {from_account_id}")
            return True
        except CustomError as e:
            print(f"Ошибка перевода: {e}")
            return False


class BaseAccount:

    def __init__(self, account_id: int, account_name: str):
        self._account_id = account_id
        self.account_name = account_name

    def display_info(self) -> None:
        print(f"Базовый счет: {self.account_name} (ID: {self._account_id})")

    @property
    def account_id(self) -> int:
        return self._account_id


class DerivedAccount(BaseAccount):

    def __init__(self, account_id: int, account_name: str, balance: float):
        super().__init__(account_id, account_name)
        self.balance = balance

    def display_info(self) -> None:
        if self.balance > 0:
            super().display_info()
            print(f"Баланс: {self.balance:.2f}")
        else:
            print("Внимание: баланс отрицательный или нулевой.")

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount
        print(f"Счет {self.account_name} пополнен на {amount:.2f}. Новый баланс: {self.balance:.2f}")


if __name__ == "__main__":
    try:
        account1 = Account(1, "Основной счет", 1000, "RUB")
        account2 = Account(2, "Дополнительный счет", 500, "RUB")

        print("\n--- Демонстрация транзакций ---")
        transaction1 = Transaction(1, account1, "income", 300, "Зарплата")
        transaction1.execute()

        transaction2 = Transaction(2, account1, "expense", 200, "Покупка продуктов")
        transaction2.execute()

        print("\n--- Демонстрация работы налога ---")
        income_tax = Tax("НДФЛ", 0.13)
        tax_amount = income_tax.calculate_tax(1000)
        income_tax.apply_tax(account1, 1000)

        print("\n--- Демонстрация отчетов ---")
        report_content = f"Баланс счета {account1.account_name}: {account1.get_balance()} {account1.currency}"
        report = Report(1, "Баланс счета", report_content)
        report.generate_report()

        print("\n--- Демонстрация AccountManager ---")
        manager = AccountManager()
        manager.add_account(account1)
        manager.add_account(account2)

        print(f"Счет с максимальным балансом: {manager.find_max_balance_account()}")
        print(f"Общий баланс всех счетов: {manager.get_total_balance()}")

        print("\n--- Демонстрация перевода ---")
        manager.transfer(1, 2, 150)
        print(f"Баланс счета 1: {account1.get_balance()}")
        print(f"Баланс счета 2: {account2.get_balance()}")

        print("\n--- Демонстрация DerivedAccount ---")
        derived_acc = DerivedAccount(3, "Сберегательный счет", 2000)
        derived_acc.display_info()
        derived_acc.deposit(500)

    except CustomError as e:
        print(f"Произошла ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    finally:
        print("\nПрограмма завершена.")