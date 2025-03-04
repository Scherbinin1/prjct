class Account:
    def init(self, account_id, account_name, balance, currency):
        self.account_id = account_id
        self.account_name = account_name
        self.balance = balance
        self.currency = currency

    def deposit(self, amount):
        self.balance += amount
        print(f"Счет '{self.account_name}' пополнен на {amount}. Новый баланс: {self.balance} {self.currency}")

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Со счета '{self.account_name}' снято {amount}. Новый баланс: {self.balance} {self.currency}")
        else:
            print("Недостаточно средств на счете.")

    def get_balance(self):
        return self.balance

class Transaction:
    def init(self, transaction_id, account, transaction_type, amount, description):
        self.transaction_id = transaction_id
        self.account = account
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description

    def process_transaction(self):
        if self.transaction_type == "доход":
            self.account.deposit(self.amount)
        elif self.transaction_type == "расход":
            self.account.withdraw(self.amount)
        else:
            print("Неверный тип транзакции.")

class Tax:
    def init(self, tax_name, rate):
        self.tax_name = tax_name
        self.rate = rate

    def calculate_tax(self, income):
        tax_amount = income * self.rate
        print(f"Налог '{self.tax_name}' рассчитан: {tax_amount}")
        return tax_amount

# Функция для ввода числа с клавиатуры
def input_number(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value >= 0:
                return value
            else:
                print("Число должно быть положительным. Попробуйте снова.")
        except ValueError:
            print("Неверный ввод. Введите число.")

# Основной код программы
 if name == "main":
    # Создаем счет
    account1 = Account(1, "Основной счет", 1000, "RUB")

    # Ввод данных для транзакции
    print("\n--- Управление транзакциями ---")
    transaction_type = input("Введите тип транзакции (доход/расход): ").strip().lower()
    while transaction_type not in ["доход", "расход"]:
        print("Неверный тип транзакции. Введите 'доход' или 'расход'.")
        transaction_type = input("Введите тип транзакции (доход/расход): ").strip().lower()

    amount = input_number("Введите сумму транзакции: ")
    description = input("Введите описание транзакции: ")

    # Создаем и обрабатываем транзакцию
    transaction1 = Transaction(1, account1, transaction_type, amount, description)
    transaction1.process_transaction()

    # Ввод данных для налога
    print("\n--- Расчет налога ---")
    tax_name = input("Введите название налога: ")
    tax_rate = input_number("Введите ставку налога (например, 0.2 для 20%): ")
    income = input_number("Введите доход для расчета налога: ")

    # Создаем и рассчитываем налог
    tax1 = Tax(tax_name, tax_rate)
    tax_amount = tax1.calculate_tax(income)

    # Уплата налога (если есть средства на счете)
    if account1.get_balance() >= tax_amount:
        account1.withdraw(tax_amount)
        print(f"Налог '{tax_name}' уплачен.")
    else:
        print("Недостаточно средств для уплаты налога.")

    # Вывод итогового баланса
    print("\n--- Итоговый баланс ---")
    print(f"Баланс счета '{account1.account_name}': {account1.get_balance()} {account1.currency}")