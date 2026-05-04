import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Генератор случайных задач")
        self.root.geometry("800x650")
        self.root.configure(bg='#f0f0f0')
        
        # Файл для хранения данных
        self.data_file = "tasks_history.json"
        self.history = []
        
        # Предопределенные задачи по категориям
        self.predefined_tasks = {
            "Учёба": [
                "Прочитать статью по программированию",
                "Решить 3 задачи по математике",
                "Выучить 10 новых английских слов",
                "Посмотреть обучающее видео на YouTube",
                "Написать конспект по теме",
                "Пройти онлайн-тест",
                "Сделать домашнее задание",
                "Подготовиться к экзамену",
                "Изучить новую библиотеку Python",
                "Написать мини-проект"
            ],
            "Спорт": [
                "Сделать зарядку (15 минут)",
                "Пробежать 2 км",
                "Сделать растяжку",
                "Покататься на велосипеде",
                "Сходить в бассейн",
                "Сделать комплекс упражнений",
                "Погулять на свежем воздухе",
                "Сделать отжимания (30 раз)",
                "Попрыгать на скакалке",
                "Сходить в спортзал"
            ],
            "Работа": [
                "Проверить почту",
                "Составить план на день",
                "Сделать отчёт",
                "Провести встречу",
                "Оптимизировать рабочий процесс",
                "Написать документацию",
                "Разобрать backlog задач",
                "Сделать код-ревью",
                "Изучить новый инструмент",
                "Подготовить презентацию"
            ],
            "Дом": [
                "Убрать на столе",
                "Помыть посуду",
                "Пропылесосить комнату",
                "Полить цветы",
                "Приготовить ужин",
                "Постирать вещи",
                "Выбросить мусор",
                "Организовать хранение",
                "Протереть пыль",
                "Проветрить комнату"
            ],
            "Саморазвитие": [
                "Медитировать 10 минут",
                "Почитать книгу (20 страниц)",
                "Написать пост в блог",
                "Послушать подкаст",
                "Научиться чему-то новому",
                "Вести дневник благодарности",
                "Попрактиковаться в иностранном языке",
                "Сходить на онлайн-курс",
                "Развить полезную привычку",
                "Подумать о целях на неделю"
            ]
        }
        
        # Загрузка истории
        self.load_history()
        
        # Создание интерфейса
        self.create_task_display_frame()
        self.create_category_frame()
        self.create_generate_frame()
        self.create_history_frame()
        self.create_filter_frame()
        self.create_stats_frame()
        
        # Обновление отображения
        self.refresh_history_display()
        
    def create_task_display_frame(self):
        """Рамка для отображения текущей задачи"""
        display_frame = tk.LabelFrame(self.root, text="Текущая задача", 
                                     padx=10, pady=10, font=("Arial", 14, "bold"),
                                     bg='#e8f4f8')
        display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.current_task_label = tk.Label(display_frame, text="Нажмите 'Сгенерировать задачу'",
                                          font=("Arial", 16, "bold"), fg="#2196F3",
                                          bg='#e8f4f8', wraplength=700, height=3)
        self.current_task_label.pack(pady=20)
        
    def create_category_frame(self):
        """Рамка для выбора категории"""
        category_frame = tk.Frame(self.root, bg='#f0f0f0')
        category_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(category_frame, text="Категория задачи:", font=("Arial", 11),
                bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        self.category_var = tk.StringVar(value="Все категории")
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var,
                                           values=["Все категории", "Учёба", "Спорт", "Работа", "Дом", "Саморазвитие"],
                                           width=20, font=("Arial", 10), state="readonly")
        self.category_combo.pack(side=tk.LEFT, padx=5)
        
    def create_generate_frame(self):
        """Рамка с кнопками генерации"""
        generate_frame = tk.Frame(self.root, bg='#f0f0f0')
        generate_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Кнопка генерации случайной задачи
        self.generate_btn = tk.Button(generate_frame, text="🎲 Сгенерировать задачу",
                                     command=self.generate_random_task,
                                     bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                     padx=20, pady=10, cursor="hand2")
        self.generate_btn.pack(pady=5)
        
        # Кнопка добавления своей задачи
        self.add_custom_btn = tk.Button(generate_frame, text="➕ Добавить свою задачу",
                                       command=self.open_add_task_dialog,
                                       bg="#FF9800", fg="white", font=("Arial", 11),
                                       padx=15, pady=5, cursor="hand2")
        self.add_custom_btn.pack(pady=5)
        
    def create_history_frame(self):
        """Рамка с историей задач"""
        history_frame = tk.LabelFrame(self.root, text="История сгенерированных задач",
                                     padx=10, pady=10, font=("Arial", 12, "bold"),
                                     bg='#f0f0f0')
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создание Treeview для истории
        columns = ("Время", "Категория", "Задача")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        # Определение заголовков
        self.history_tree.heading("Время", text="Время генерации")
        self.history_tree.heading("Категория", text="Категория")
        self.history_tree.heading("Задача", text="Задача")
        
        # Настройка колонок
        self.history_tree.column("Время", width=150, anchor="center")
        self.history_tree.column("Категория", width=120, anchor="center")
        self.history_tree.column("Задача", width=400, anchor="w")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить задачу из истории", command=self.delete_selected_task)
        self.history_tree.bind("<Button-3>", self.show_context_menu)
        
    def create_filter_frame(self):
        """Рамка для фильтрации истории"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация истории",
                                    padx=10, pady=5, font=("Arial", 11, "bold"),
                                    bg='#f0f0f0')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Фильтр по категории:", font=("Arial", 10),
                bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=5)
        
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                         values=["Все", "Учёба", "Спорт", "Работа", "Дом", "Саморазвитие", "Пользовательская"],
                                         width=15, font=("Arial", 10), state="readonly")
        self.filter_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_history_display())
        
        # Кнопка сброса фильтра
        self.reset_filter_btn = tk.Button(filter_frame, text="Сбросить фильтр",
                                         command=self.reset_filter,
                                         bg="#9E9E9E", fg="white", font=("Arial", 9),
                                         cursor="hand2")
        self.reset_filter_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Кнопка очистки истории
        self.clear_history_btn = tk.Button(filter_frame, text="Очистить всю историю",
                                          command=self.clear_all_history,
                                          bg="#f44336", fg="white", font=("Arial", 9),
                                          cursor="hand2")
        self.clear_history_btn.grid(row=0, column=3, padx=10, pady=5)
        
    def create_stats_frame(self):
        """Рамка со статистикой"""
        stats_frame = tk.Frame(self.root, bg='#f0f0f0')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats_frame, text="📊 Статистика:", font=("Arial", 10, "bold"),
                bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        
        self.stats_label = tk.Label(stats_frame, text="Всего задач: 0",
                                   font=("Arial", 10), fg="#4CAF50",
                                   bg='#f0f0f0')
        self.stats_label.pack(side=tk.LEFT, padx=10)
        
    def generate_random_task(self):
        """Генерация случайной задачи"""
        category = self.category_var.get()
        
        # Выбор категории
        if category == "Все категории":
            # Выбираем случайную категорию из предопределенных
            selected_category = random.choice(list(self.predefined_tasks.keys()))
            # Выбираем случайную задачу из выбранной категории
            task = random.choice(self.predefined_tasks[selected_category])
            category_display = selected_category
        else:
            # Выбираем задачу из конкретной категории
            category_display = category
            if category not in self.predefined_tasks:
                messagebox.showerror("Ошибка", "Категория не найдена!")
                return
            task = random.choice(self.predefined_tasks[category])
        
        # Получаем текущее время
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        # Добавляем в историю
        history_item = {
            "id": len(self.history) + 1,
            "timestamp": current_time,
            "category": category_display,
            "task": task,
            "type": "predefined"
        }
        
        self.history.append(history_item)
        
        # Отображаем текущую задачу
        self.current_task_label.config(text=f"✨ {task} ✨", fg="#4CAF50")
        
        # Сохраняем и обновляем отображение
        self.save_history()
        self.refresh_history_display()
        self.update_stats()
        
        # Визуальный эффект
        self.animate_task_display()
        
    def open_add_task_dialog(self):
        """Открытие диалога для добавления своей задачи"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить свою задачу")
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        dialog.configure(bg='#f0f0f0')
        
        # Центрирование окна
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Добавить новую задачу", font=("Arial", 14, "bold"),
                bg='#f0f0f0', fg="#2196F3").pack(pady=15)
        
        # Выбор категории
        tk.Label(dialog, text="Категория:", font=("Arial", 11), bg='#f0f0f0').pack(pady=5)
        category_var = tk.StringVar(value="Работа")
        category_combo = ttk.Combobox(dialog, textvariable=category_var,
                                     values=["Учёба", "Спорт", "Работа", "Дом", "Саморазвитие"],
                                     width=20, state="readonly")
        category_combo.pack(pady=5)
        
        # Ввод задачи
        tk.Label(dialog, text="Текст задачи:", font=("Arial", 11), bg='#f0f0f0').pack(pady=5)
        task_text = tk.Text(dialog, height=5, width=50, font=("Arial", 10))
        task_text.pack(pady=5, padx=20)
        
        def add_task():
            task = task_text.get("1.0", tk.END).strip()
            
            # Проверка на пустую строку
            if not task:
                messagebox.showerror("Ошибка", "Текст задачи не может быть пустым!")
                return
            
            category = category_var.get()
            
            # Добавляем задачу в предопределенные (для текущей сессии)
            if category not in self.predefined_tasks:
                self.predefined_tasks[category] = []
            
            self.predefined_tasks[category].append(task)
            
            # Добавляем в историю как пользовательскую
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            history_item = {
                "id": len(self.history) + 1,
                "timestamp": current_time,
                "category": category,
                "task": task,
                "type": "custom"
            }
            
            self.history.append(history_item)
            self.save_history()
            self.refresh_history_display()
            self.update_stats()
            
            # Отображаем добавленную задачу как текущую
            self.current_task_label.config(text=f"➕ Добавлено: {task}", fg="#FF9800")
            
            messagebox.showinfo("Успех", f"Задача успешно добавлена в категорию '{category}'!")
            dialog.destroy()
        
        tk.Button(dialog, text="Добавить", command=add_task,
                 bg="#4CAF50", fg="white", font=("Arial", 11),
                 padx=20, pady=5, cursor="hand2").pack(pady=10)
        
    def delete_selected_task(self):
        """Удаление выбранной задачи из истории"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления!")
            return
        
        # Получаем индекс выбранной задачи
        item = self.history_tree.item(selected[0])
        task_text = item['values'][2]
        task_time = item['values'][0]
        
        # Удаляем из истории
        self.history = [h for h in self.history if not (h['timestamp'] == task_time and h['task'] == task_text)]
        
        # Перенумерация ID
        for i, item in enumerate(self.history):
            item['id'] = i + 1
        
        self.save_history()
        self.refresh_history_display()
        self.update_stats()
        
        messagebox.showinfo("Успех", "Задача удалена из истории!")
        
    def clear_all_history(self):
        """Очистка всей истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю? Это действие нельзя отменить!"):
            self.history = []
            self.save_history()
            self.refresh_history_display()
            self.update_stats()
            self.current_task_label.config(text="История очищена. Нажмите 'Сгенерировать задачу'", fg="#2196F3")
            messagebox.showinfo("Успех", "История успешно очищена!")
            
    def refresh_history_display(self):
        """Обновление отображения истории с учетом фильтра"""
        # Очищаем таблицу
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Получаем фильтр
        filter_category = self.filter_category_var.get()
        
        # Фильтрация истории
        filtered_history = self.history.copy()
        
        if filter_category != "Все":
            filtered_history = [h for h in filtered_history if h['category'] == filter_category]
        
        # Отображаем историю в обратном порядке (новые сверху)
        for item in reversed(filtered_history):
            # Выделяем пользовательские задачи цветом
            tags = ()
            if item.get('type') == 'custom':
                tags = ('custom',)
            
            self.history_tree.insert("", tk.END, values=(
                item['timestamp'],
                item['category'],
                item['task']
            ), tags=tags)
        
        # Настройка цветов
        self.history_tree.tag_configure('custom', background='#FFF9C4')
        
    def reset_filter(self):
        """Сброс фильтра"""
        self.filter_category_var.set("Все")
        self.refresh_history_display()
        
    def update_stats(self):
        """Обновление статистики"""
        total_tasks = len(self.history)
        custom_tasks = len([h for h in self.history if h.get('type') == 'custom'])
        
        stats_text = f"Всего задач: {total_tasks} | Пользовательских: {custom_tasks}"
        self.stats_label.config(text=stats_text)
        
    def animate_task_display(self):
        """Анимация отображения задачи"""
        def reset_color():
            self.current_task_label.config(fg="#2196F3")
        
        self.root.after(2000, reset_color)
        
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            # Создаем тестовые данные для демонстрации
            self.history = [
                {
                    "id": 1,
                    "timestamp": datetime.now().strftime("%d.%m.%Y 10:30:00"),
                    "category": "Учёба",
                    "task": "Прочитать статью по программированию",
                    "type": "predefined"
                },
                {
                    "id": 2,
                    "timestamp": datetime.now().strftime("%d.%m.%Y 11:15:00"),
                    "category": "Спорт",
                    "task": "Сделать зарядку (15 минут)",
                    "type": "predefined"
                }
            ]
            self.save_history()
            
    def save_history(self):
        """Сохранение истории в JSON файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

def main():
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
