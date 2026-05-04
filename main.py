import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from tkcalendar import DateEntry

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x650")
        
        # Файл для хранения данных
        self.data_file = "expenses.json"
        self.expenses = []
        
        # Загрузка сохраненных данных
        self.load_data()
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table_frame()
        self.create_stats_frame()
        
        # Обновление таблицы и статистики
        self.refresh_table()
        self.update_stats()
        
    def create_input_frame(self):
        """Форма для добавления расходов"""
        input_frame = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10, font=("Arial", 12, "bold"))
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поле суммы
        tk.Label(input_frame, text="Сумма (₽):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=20, font=("Arial", 10))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле категории
        tk.Label(input_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=["Еда", "Транспорт", "Развлечения", "Жилье", 
                                                  "Здоровье", "Одежда", "Образование", "Другое"],
                                           width=15, font=("Arial", 10))
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("Еда")
        
        # Поле даты
        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):", font=("Arial", 10)).grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='dd.mm.yyyy', font=("Arial", 10))
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_button = tk.Button(input_frame, text="Добавить расход", command=self.add_expense,
                                   bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                                   padx=10, pady=5)
        self.add_button.grid(row=0, column=6, padx=10, pady=5)
        
    def create_filter_frame(self):
        """Фильтрация данных"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10, font=("Arial", 12, "bold"))
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                  values=["Все", "Еда", "Транспорт", "Развлечения", 
                                                         "Жилье", "Здоровье", "Одежда", "Образование", "Другое"],
                                                  width=15, font=("Arial", 10))
        self.filter_category_combo.grid(row=0, column=1, padx=5)
        self.filter_category_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        # Фильтр по дате
        tk.Label(filter_frame, text="Дата от:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.date_from = DateEntry(filter_frame, width=12, date_pattern='dd.mm.yyyy', font=("Arial", 10))
        self.date_from.grid(row=0, column=3, padx=5)
        
        tk.Label(filter_frame, text="Дата до:", font=("Arial", 10)).grid(row=0, column=4, sticky=tk.W, padx=5)
        self.date_to = DateEntry(filter_frame, width=12, date_pattern='dd.mm.yyyy', font=("Arial", 10))
        self.date_to.grid(row=0, column=5, padx=5)
        
        # Кнопка применения фильтра
        self.apply_filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table,
                                         bg="#2196F3", fg="white", font=("Arial", 10))
        self.apply_filter_btn.grid(row=0, column=6, padx=10)
        
        # Кнопка сброса фильтра
        self.reset_filter_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter,
                                         bg="#FF9800", fg="white", font=("Arial", 10))
        self.reset_filter_btn.grid(row=0, column=7, padx=5)
        
    def create_table_frame(self):
        """Таблица для отображения расходов"""
        table_frame = tk.LabelFrame(self.root, text="Список расходов", padx=10, pady=10, font=("Arial", 12, "bold"))
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создание Treeview
        columns = ("ID", "Дата", "Категория", "Сумма")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Определение заголовков
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма", text="Сумма (₽)")
        
        # Настройка колонок
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Дата", width=120, anchor="center")
        self.tree.column("Категория", width=150, anchor="center")
        self.tree.column("Сумма", width=100, anchor="e")
        
        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстное меню для удаления
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить запись", command=self.delete_expense)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def create_stats_frame(self):
        """Статистика расходов"""
        stats_frame = tk.LabelFrame(self.root, text="Статистика", padx=10, pady=10, font=("Arial", 12, "bold"))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Общая сумма
        tk.Label(stats_frame, text="Общая сумма расходов:", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        self.total_label = tk.Label(stats_frame, text="0 ₽", font=("Arial", 14, "bold"), fg="#4CAF50")
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        # Количество записей
        tk.Label(stats_frame, text="Количество записей:", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        self.count_label = tk.Label(stats_frame, text="0", font=("Arial", 14, "bold"), fg="#2196F3")
        self.count_label.pack(side=tk.LEFT, padx=10)
        
        # Кнопка удаления всех данных
        self.clear_all_btn = tk.Button(stats_frame, text="Удалить все данные", command=self.clear_all_data,
                                      bg="#f44336", fg="white", font=("Arial", 10))
        self.clear_all_btn.pack(side=tk.RIGHT, padx=10)
        
    def add_expense(self):
        """Добавление нового расхода"""
        # Проверка суммы
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректную сумму!")
            return
        
        # Получение категории
        category = self.category_var.get()
        
        # Получение даты
        date = self.date_entry.get()
        
        # Проверка формата даты
        try:
            datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return
        
        # Создание записи
        expense = {
            "id": len(self.expenses) + 1,
            "date": date,
            "category": category,
            "amount": amount
        }
        
        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()
        self.update_stats()
        
        # Очистка поля суммы
        self.amount_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Расход успешно добавлен!")
        
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        # Получение ID записи
        item = self.tree.item(selected_item[0])
        expense_id = item['values'][0]
        
        # Удаление из списка
        self.expenses = [e for e in self.expenses if e['id'] != expense_id]
        
        # Перенумерация ID
        for i, expense in enumerate(self.expenses):
            expense['id'] = i + 1
        
        self.save_data()
        self.refresh_table()
        self.update_stats()
        
        messagebox.showinfo("Успех", "Запись удалена!")
        
    def refresh_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение фильтров
        filter_category = self.filter_category_var.get()
        filter_date_from = self.date_from.get()
        filter_date_to = self.date_to.get()
        
        # Фильтрация расходов
        filtered_expenses = self.expenses.copy()
        
        if filter_category != "Все":
            filtered_expenses = [e for e in filtered_expenses if e['category'] == filter_category]
        
        if filter_date_from and filter_date_to:
            try:
                from_date = datetime.strptime(filter_date_from, "%d.%m.%Y")
                to_date = datetime.strptime(filter_date_to, "%d.%m.%Y")
                
                filtered_expenses = [e for e in filtered_expenses 
                                   if from_date <= datetime.strptime(e['date'], "%d.%m.%Y") <= to_date]
            except:
                pass
        
        # Сортировка по дате (новые сверху)
        filtered_expenses.sort(key=lambda x: datetime.strptime(x['date'], "%d.%m.%Y"), reverse=True)
        
        # Добавление в таблицу
        for expense in filtered_expenses:
            self.tree.insert("", tk.END, values=(
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}"
            ))
        
        # Обновление статистики для отфильтрованных данных
        total = sum(e['amount'] for e in filtered_expenses)
        self.total_label.config(text=f"{total:.2f} ₽")
        self.count_label.config(text=str(len(filtered_expenses)))
        
    def update_stats(self):
        """Обновление общей статистики"""
        total = sum(e['amount'] for e in self.expenses)
        self.total_label.config(text=f"{total:.2f} ₽")
        self.count_label.config(text=str(len(self.expenses)))
        
    def reset_filter(self):
        """Сброс всех фильтров"""
        self.filter_category_var.set("Все")
        self.date_from.set_date(datetime.now())
        self.date_to.set_date(datetime.now())
        self.refresh_table()
        
    def clear_all_data(self):
        """Удаление всех данных"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все данные? Это действие нельзя отменить!"):
            self.expenses = []
            self.save_data()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Все данные удалены!")
        
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []
        else:
            # Создание тестовых данных для демонстрации
            self.expenses = [
                {"id": 1, "date": "15.01.2024", "category": "Еда", "amount": 500.00},
                {"id": 2, "date": "16.01.2024", "category": "Транспорт", "amount": 200.00},
                {"id": 3, "date": "17.01.2024", "category": "Развлечения", "amount": 1000.00},
            ]
            self.save_data()
            
    def save_data(self):
        """Сохранение данных в JSON файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
