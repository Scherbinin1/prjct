import sys
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit,
                             QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox, QDialog,
                             QFormLayout, QHeaderView, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FinancialEntity(ABC):
    def __init__(self, entity_id: int, name: str):
        self._id = entity_id
        self._name = name
        self._creation_date = datetime.now()
        logger.info(f"Создан объект {self.__class__.__name__}: ID={entity_id}, Name='{name}'")

    @abstractmethod
    def get_info(self) -> str:
        pass

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return self.get_info()


class Account(FinancialEntity):
    def __init__(self, account_id: int, account_name: str, balance: float, currency: str):
        super().__init__(account_id, account_name)
        self._balance = balance
        self._currency = currency
        self._transactions: List[Transaction] = []

    def deposit(self, amount: float, description: str = "") -> None:
        if amount <= 0:
            logger.error(f"Ошибка пополнения счета {self.id}: неверная сумма {amount}")
            raise ValueError("Сумма должна быть положительной")
        self._balance += amount
        transaction = Transaction(self, "deposit", amount, description)
        self._transactions.append(transaction)
        logger.info(f"Счет {self.id} пополнен на {amount} {self.currency}. Новый баланс: {self.balance}")

    def withdraw(self, amount: float, description: str = "") -> None:
        if amount <= 0:
            logger.error(f"Ошибка снятия со счета {self.id}: неверная сумма {amount}")
            raise ValueError("Сумма должна быть положительной")
        if self._balance < amount:
            logger.error(f"Ошибка снятия со счета {self.id}: недостаточно средств ({self.balance} < {amount})")
            raise ValueError("Недостаточно средств на счете")
        self._balance -= amount
        transaction = Transaction(self, "withdraw", amount, description)
        self._transactions.append(transaction)
        logger.info(f"Со счета {self.id} снято {amount} {self.currency}. Новый баланс: {self.balance}")

    def get_info(self) -> str:
        return f"Счет {self._name} (ID: {self._id}), Баланс: {self._balance:.2f} {self._currency}"

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def transactions(self) -> List['Transaction']:
        return self._transactions.copy()


class Transaction(FinancialEntity):
    def __init__(self, account: Account, transaction_type: str, amount: float, description: str = ""):
        transaction_id = hash(f"{account.id}{datetime.now().timestamp()}")
        super().__init__(transaction_id, f"Transaction for account {account.id}")
        self._account = account
        self._type = transaction_type
        self._amount = amount
        self._description = description
        self._execution_time = datetime.now()

    def get_info(self) -> str:
        return (f"Транзакция {self._id}: {self._type} {self._amount:.2f} {self._account.currency}, "
                f"Счет: {self._account.name}, Описание: {self._description}")

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def transaction_type(self) -> str:
        return self._type

    @property
    def description(self) -> str:
        return self._description


class TaxCalculator(FinancialEntity):
    def __init__(self, tax_id: int, tax_name: str, rate: float):
        super().__init__(tax_id, tax_name)
        self._rate = rate

    def calculate(self, income: float) -> float:
        tax_amount = income * self._rate
        logger.info(f"Рассчитан налог {self.name}: ставка {self._rate}, доход {income}, сумма {tax_amount:.2f}")
        return tax_amount

    def get_info(self) -> str:
        return f"Налог {self.name} (ID: {self.id}), Ставка: {self._rate:.2%}"

    @property
    def rate(self) -> float:
        return self._rate

account_filter = lambda accounts, min_balance: list(filter(lambda acc: acc.balance >= min_balance, accounts))
sort_accounts_by_balance = lambda accounts: sorted(accounts, key=lambda acc: acc.balance, reverse=True)
get_total_balance = lambda accounts: sum(acc.balance for acc in accounts)
format_account_info = lambda account: f"{account.name}: {account.balance:.2f} {account.currency}"


class FinancialApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Финансовая система")
        self.setGeometry(100, 100, 900, 600)

        self._account_manager = AccountManager()
        self._tax_calculator = TaxCalculator(1, "НДФЛ", 0.13)

        self.init_ui()
        self.apply_dark_theme()
        self.load_sample_data()

        logger.info("Приложение инициализировано")

    class AccountManager:
        def __init__(self):
            self._accounts: List[Account] = []

        def add_account(self, account: Account) -> None:
            self._accounts.append(account)
            logger.info(f"Добавлен счет в менеджер: {account.id}")

        def get_account(self, account_id: int) -> Optional[Account]:
            for account in self._accounts:
                if account.id == account_id:
                    return account
            return None

        def get_all_accounts(self) -> List[Account]:
            return self._accounts.copy()

        def get_total_balance(self) -> float:
            return get_total_balance(self._accounts)

        def get_rich_accounts(self, min_balance: float = 1000) -> List[Account]:
            return account_filter(self._accounts, min_balance)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Левая панель навигации
        self.create_navigation_panel(main_layout)

        # Правая рабочая область
        self.create_workspace(main_layout)

    def create_navigation_panel(self, main_layout):
        nav_frame = QFrame()
        nav_frame.setFrameShape(QFrame.Shape.StyledPanel)
        nav_frame.setFixedWidth(150)
        nav_layout = QVBoxLayout()
        nav_frame.setLayout(nav_layout)

        buttons = [
            ("Счета", self.show_accounts_tab),
            ("Операции", self.show_transactions_tab),
            ("Налоги", self.show_taxes_tab),
            ("Отчеты", self.show_reports_tab),
            ("Логи", self.show_logs_tab)
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.clicked.connect(handler)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        main_layout.addWidget(nav_frame)

    def create_workspace(self, main_layout):
        self.tab_widget = QTabWidget()

        # Создание вкладок
        self.create_accounts_tab()
        self.create_transactions_tab()
        self.create_taxes_tab()
        self.create_reports_tab()
        self.create_logs_tab()

        main_layout.addWidget(self.tab_widget)

    def create_accounts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Панель управления
        control_panel = QHBoxLayout()

        self.new_account_btn = QPushButton("Новый счет")
        self.new_account_btn.clicked.connect(self.show_new_account_dialog)
        control_panel.addWidget(self.new_account_btn)

        self.refresh_accounts_btn = QPushButton("Обновить")
        self.refresh_accounts_btn.clicked.connect(self.update_accounts_table)
        control_panel.addWidget(self.refresh_accounts_btn)

        layout.addLayout(control_panel)

        # Таблица счетов
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels(["ID", "Название", "Баланс", "Валюта"])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.accounts_table.cellDoubleClicked.connect(self.show_account_details)
        layout.addWidget(self.accounts_table)

        self.tab_widget.addTab(tab, "Счета")

    def create_transactions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Форма операции
        form = QFormLayout()

        self.account_combo = QComboBox()
        form.addRow("Счет:", self.account_combo)

        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems(["deposit", "withdraw"])
        form.addRow("Тип:", self.transaction_type_combo)

        self.amount_edit = QLineEdit()
        form.addRow("Сумма:", self.amount_edit)

        self.description_edit = QLineEdit()
        form.addRow("Описание:", self.description_edit)

        self.execute_btn = QPushButton("Выполнить")
        self.execute_btn.clicked.connect(self.execute_transaction)
        form.addRow(self.execute_btn)

        layout.addLayout(form)

        # Таблица операций
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(["ID", "Дата", "Тип", "Сумма", "Описание"])
        layout.addWidget(self.transactions_table)

        self.tab_widget.addTab(tab, "Операции")

    def create_taxes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Форма налога
        form = QFormLayout()

        self.tax_income_edit = QLineEdit()
        form.addRow("Доход для расчета:", self.tax_income_edit)

        self.calculate_tax_btn = QPushButton("Рассчитать налог")
        self.calculate_tax_btn.clicked.connect(self.calculate_tax)
        form.addRow(self.calculate_tax_btn)

        self.tax_result_label = QLabel()
        self.tax_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addRow(self.tax_result_label)

        layout.addLayout(form)
        self.tab_widget.addTab(tab, "Налоги")

    def create_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Панель отчетов
        report_panel = QHBoxLayout()

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Балансы счетов", "Богатые счета", "Общий баланс"])
        report_panel.addWidget(self.report_type_combo)

        self.generate_report_btn = QPushButton("Сформировать")
        self.generate_report_btn.clicked.connect(self.generate_report)
        report_panel.addWidget(self.generate_report_btn)

        layout.addLayout(report_panel)

        # Поле отчета
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)

        self.tab_widget.addTab(tab, "Отчеты")

    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)

        self.update_logs()

        self.tab_widget.addTab(tab, "Логи")

    def apply_dark_theme(self):
        dark_palette = self.palette()
        dark_palette.setColor(dark_palette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(dark_palette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(dark_palette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(dark_palette.ColorRole.ButtonText, Qt.GlobalColor.white)
        self.setPalette(dark_palette)

    def load_sample_data(self):
        try:
            accounts = [
                Account(1, "Основной счет", 100000, "RUB"),
                Account(2, "Долларовый счет", 5000, "USD"),
                Account(3, "Резервный счет", 25000, "RUB")
            ]

            for acc in accounts:
                self._account_manager.add_account(acc)
                acc.deposit(10000, "Первоначальное пополнение")

            self.update_accounts_table()
            self.update_accounts_combo()

        except Exception as e:
            logger.error(f"Ошибка загрузки тестовых данных: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить тестовые данные: {str(e)}")

    def update_accounts_table(self):
        self.accounts_table.setRowCount(0)
        for account in sort_accounts_by_balance(self._account_manager.get_all_accounts()):
            row = self.accounts_table.rowCount()
            self.accounts_table.insertRow(row)

            self.accounts_table.setItem(row, 0, QTableWidgetItem(str(account.id)))
            self.accounts_table.setItem(row, 1, QTableWidgetItem(account.name))
            self.accounts_table.setItem(row, 2, QTableWidgetItem(f"{account.balance:.2f}"))
            self.accounts_table.setItem(row, 3, QTableWidgetItem(account.currency))

    def update_accounts_combo(self):
        self.account_combo.clear()
        for account in self._account_manager.get_all_accounts():
            self.account_combo.addItem(account.name, account.id)

    def update_transactions_table(self, account_id: int):
        self.transactions_table.setRowCount(0)
        account = self._account_manager.get_account(account_id)
        if account:
            for trans in account.transactions:
                row = self.transactions_table.rowCount()
                self.transactions_table.insertRow(row)

                self.transactions_table.setItem(row, 0, QTableWidgetItem(str(trans.id)))
                self.transactions_table.setItem(row, 1,
                                                QTableWidgetItem(trans._execution_time.strftime("%Y-%m-%d %H:%M")))
                self.transactions_table.setItem(row, 2, QTableWidgetItem(trans.transaction_type))
                self.transactions_table.setItem(row, 3, QTableWidgetItem(f"{trans.amount:.2f}"))
                self.transactions_table.setItem(row, 4, QTableWidgetItem(trans.description))

    def update_logs(self):
        try:
            with open('finance_system.log', 'r') as log_file:
                self.logs_text.setPlainText(log_file.read())
        except Exception as e:
            logger.error(f"Ошибка чтения логов: {str(e)}")

    def show_new_account_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Новый счет")
        dialog.setFixedSize(300, 200)

        layout = QFormLayout()
        dialog.setLayout(layout)

        le_id = QLineEdit()
        le_name = QLineEdit()
        le_balance = QLineEdit()
        le_currency = QLineEdit()

        layout.addRow("ID счета:", le_id)
        layout.addRow("Название:", le_name)
        layout.addRow("Начальный баланс:", le_balance)
        layout.addRow("Валюта:", le_currency)

        btn_box = QHBoxLayout()
        btn_ok = QPushButton("Создать")
        btn_ok.clicked.connect(lambda: self.create_account(
            le_id.text(), le_name.text(), le_balance.text(), le_currency.text(), dialog
        ))
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(dialog.reject)

        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)

        dialog.exec()

    def create_account(self, acc_id, name, balance, currency, dialog):
        try:
            account = Account(
                int(acc_id),
                name.strip(),
                float(balance),
                currency.strip().upper()
            )
            self._account_manager.add_account(account)
            self.update_accounts_table()
            self.update_accounts_combo()
            dialog.accept()

            logger.info(f"Создан новый счет: {account.get_info()}")

        except ValueError as e:
            logger.error(f"Ошибка создания счета: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Некорректные данные: {str(e)}")
        except Exception as e:
            logger.error(f"Ошибка создания счета: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать счет: {str(e)}")

    def execute_transaction(self):
        try:
            account_id = self.account_combo.currentData()
            account = self._account_manager.get_account(account_id)
            if not account:
                raise ValueError("Счет не найден")

            amount = float(self.amount_edit.text())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")

            transaction_type = self.transaction_type_combo.currentText()
            description = self.description_edit.text()

            if transaction_type == "deposit":
                account.deposit(amount, description)
            else:
                account.withdraw(amount, description)

            self.update_accounts_table()
            self.update_transactions_table(account_id)

            QMessageBox.information(self, "Успех", "Операция выполнена успешно")

        except ValueError as e:
            logger.error(f"Ошибка выполнения операции: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Некорректные данные: {str(e)}")
        except Exception as e:
            logger.error(f"Ошибка выполнения операции: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить операцию: {str(e)}")

    def calculate_tax(self):
        try:
            income = float(self.tax_income_edit.text())
            if income < 0:
                raise ValueError("Доход не может быть отрицательным")

            tax_amount = self._tax_calculator.calculate(income)
            self.tax_result_label.setText(f"Сумма налога ({self._tax_calculator.name}): {tax_amount:.2f} RUB")

        except ValueError as e:
            logger.error(f"Ошибка расчета налога: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Некорректные данные: {str(e)}")
        except Exception as e:
            logger.error(f"Ошибка расчета налога: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать налог: {str(e)}")

    def generate_report(self):
        report_type = self.report_type_combo.currentText()
        report_text = ""

        if report_type == "Балансы счетов":
            report_text = "ОТЧЕТ ПО БАЛАНСАМ СЧЕТОВ\n\n"
            for account in sort_accounts_by_balance(self._account_manager.get_all_accounts()):
                report_text += f"{format_account_info(account)}\n"

        elif report_type == "Богатые счета":
            report_text = "СЧЕТА С БАЛАНСОМ > 1000\n\n"
            for account in self._account_manager.get_rich_accounts(1000):
                report_text += f"{format_account_info(account)}\n"

        elif report_type == "Общий баланс":
            total = self._account_manager.get_total_balance()
            report_text = f"ОБЩИЙ БАЛАНС (RUB): {total:.2f}\n"

        self.report_text.setPlainText(report_text)
        logger.info(f"Сформирован отчет: {report_type}")

    def show_account_details(self, row, column):
        account_id = int(self.accounts_table.item(row, 0).text())
        account = self._account_manager.get_account(account_id)

        if not account:
            QMessageBox.warning(self, "Ошибка", "Счет не найден")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Детали счета: {account.name}")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        info = QLabel(
            f"ID: {account.id}\n"
            f"Название: {account.name}\n"
            f"Баланс: {account.balance:.2f} {account.currency}\n"
            f"Операций: {len(account.transactions)}"
        )
        layout.addWidget(info)

        trans_table = QTableWidget()
        trans_table.setColumnCount(4)
        trans_table.setHorizontalHeaderLabels(["Дата", "Тип", "Сумма", "Описание"])
        trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for trans in account.transactions:
            row = trans_table.rowCount()
            trans_table.insertRow(row)

            trans_table.setItem(row, 0, QTableWidgetItem(trans._execution_time.strftime("%Y-%m-%d %H:%M")))
            trans_table.setItem(row, 1, QTableWidgetItem(trans.transaction_type))
            trans_table.setItem(row, 2, QTableWidgetItem(f"{trans.amount:.2f}"))
            trans_table.setItem(row, 3, QTableWidgetItem(trans.description))

        layout.addWidget(trans_table)
        dialog.exec()

    # Методы переключения вкладок
    def show_accounts_tab(self):
        self.tab_widget.setCurrentIndex(0)

    def show_transactions_tab(self):
        self.tab_widget.setCurrentIndex(1)

    def show_taxes_tab(self):
        self.tab_widget.setCurrentIndex(2)

    def show_reports_tab(self):
        self.tab_widget.setCurrentIndex(3)

    def show_logs_tab(self):
        self.update_logs()
        self.tab_widget.setCurrentIndex(4)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Настройка шрифта
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)

    window = FinancialApp()
    window.show()
    sys.exit(app.exec())