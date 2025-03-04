from abc import ABC, abstractmethod
from typing import Dict, List

# Абстрактный класс для финансовых операциуц
class FinancialOperation(ABC):
    @abstractmethod
    def execute(self):
        pass

# Класс Account (Счет)
class Account:
    # Статическое поле для хранения всех счетов
    accounts: Dict[int, 'Account'] = {}

    def __init__(self, account_id: int, account_name: str, balance: float, currency: str):
        self.account_id = account_id
        self.account_name = account_name
        self.balance = balance
        self.currency = currency
        # Добавляем счет в статический словарь
        Account.accounts[account_id] = self

    def deposit(self, amount: float):
        self.balance += amount
        print(f"Счет '{self.account_name}' пополнен на {amount}. Новый баланс: {self.balance} {self.currency}")

    def withdraw(self, amount: float):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Со счета '{self.account_name}' снято {amount}. Новый баланс: {self.balance} {self.currency}")
        else:
            raise ValueError("Недостаточно средств на счете.")

    def get_balance(self):
        return self.balance

    # Статический метод для поиска счета по ID
    @staticmethod
    def find_account(account_id: int) -> 'Account':
        if account_id in Account.accounts:
            return Account.accounts[account_id]
        else:
            raise ValueError(f"Счет с ID {account_id} не найден.")

    # Перегрузка оператора сложения для объединения балансов
    def __add__(self, other: 'Account') -> float:
        return self.balance + other.balance

    # Перегрузка оператора сравнения
    def __gt__(self, other: 'Account') -> bool:
        return self.balance > other.balance

    # Перегрузка оператора строкового представления
    def __str__(self):
        return f"Счет {self.account_name} (ID: {self.account_id}), Баланс: {self.balance} {self.currency}"

# Класс Transaction (Транзакция)
class Transaction(FinancialOperation):
    def __init__(self, transaction_id: int, account: Account, transaction_type: str, amount: float, description: str):
        self.transaction_id = transaction_id
        self.account = account
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description

    def execute(self):
        if self.transaction_type == "доход":
            self.account.deposit(self.amount)
        elif self.transaction_type == "расход":
            self.account.withdraw(self.amount)
        else:
            raise ValueError("Неверный тип транзакции.")

# Класс Tax (Налог)
class Tax:
    def __init__(self, tax_name: str, rate: float):
        self.tax_name = tax_name
        self.rate = rate

    def calculate_tax(self, income: float) -> float:
        tax_amount = income * self.rate
        print(f"Налог '{self.tax_name}' рассчитан: {tax_amount}")
        return tax_amount

# Класс Report (Отчет)
class Report:
    def __init__(self, report_id: int, report_type: str, content: str):
        self.report_id = report_id
        self.report_type = report_type
        self.content = content

    def generate_report(self):
        print(f"Отчет '{self.report_type}' сгенерирован: {self.content}")

# Основной код программы
if __name__ == "__main__":
    try:
        # Создаем счета
        account1 = Account(1, "Основной счет", 1000, "RUB")
        account2 = Account(2, "Дополнительный счет", 500, "RUB")

        # Ввод данных для транзакции
        print("\n--- Управление транзакциями ---")
        transaction_type = input("Введите тип транзакции (доход/расход): ").strip().lower()
        while transaction_type not in ["доход", "расход"]:
            print("Неверный тип транзакции. Введите 'доход' или 'расход'.")
            transaction_type = input("Введите тип транзакции (доход/расход): ").strip().lower()

        amount = float(input("Введите сумму транзакции: "))
        description = input("Введите описание транзакции: ")

        # Создаем и обрабатываем транзакцию
        transaction1 = Transaction(1, account1, transaction_type, amount, description)
        transaction1.execute()

        # Ввод данных для налога
        print("\n--- Расчет налога ---")
        tax_name = input("Введите название налога: ")
        tax_rate = float(input("Введите ставку налога (например, 0.2 для 20%): "))
        income = float(input("Введите доход для расчета налога: "))

        # Создаем и рассчитываем налог
        tax1 = Tax(tax_name, tax_rate)
        tax_amount = tax1.calculate_tax(income)

        # Уплата налога (если есть средства на счете)
        if account1.get_balance() >= tax_amount:
            account1.withdraw(tax_amount)
            print(f"Налог '{tax_name}' уплачен.")
        else:
            print("Недостаточно средств для уплаты налога.")

        # Демонстрация работы с динамическими структурами данных (словарь счетов)
        print("\n--- Все счета ---")
        for acc_id, acc in Account.accounts.items():
            print(acc)

        # Демонстрация перегрузки операторов
        print("\n--- Перегрузка операторов ---")
        print(f"Суммарный баланс счетов: {account1 + account2}")
        print(f"Счет 1 больше счета 2: {account1 > account2}")

        # Генерация отчета
        report1 = Report(1, "Баланс", f"Баланс счета '{account1.account_name}': {account1.get_balance()} {account1.currency}")
        report1.generate_report()

    except ValueError as e:
        print(f"Ошибка: {e}")