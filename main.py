import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomQuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("900x650")
        self.root.configure(bg='#2c3e50')
        
        self.data_file = "quotes_history.json"
        self.history = []
        
        # Предопределенные цитаты
        self.quotes = [
            {"text": "Будьте тем изменением, которое хотите видеть в мире.", "author": "Махатма Ганди", "theme": "Мотивация"},
            {"text": "Единственный способ сделать великую работу — любить то, что вы делаете.", "author": "Стив Джобс", "theme": "Мотивация"},
            {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "theme": "Жизнь"},
            {"text": "Знание — сила.", "author": "Фрэнсис Бэкон", "theme": "Мудрость"},
            {"text": "Любовь — это когда чужое счастье становится твоим собственным.", "author": "Бертран Рассел", "theme": "Любовь"},
            {"text": "Успех — это не конечная цель, это путь.", "author": "Генри Форд", "theme": "Успех"},
            {"text": "Не важно, как медленно вы идете, главное — не останавливаться.", "author": "Конфуций", "theme": "Мотивация"},
            {"text": "Смысл жизни в том, чтобы найти свой дар.", "author": "Пабло Пикассо", "theme": "Жизнь"},
            {"text": "Мудрый человек требует всего только от себя.", "author": "Лев Толстой", "theme": "Мудрость"},
            {"text": "Где любовь, там и жизнь.", "author": "Махатма Ганди", "theme": "Любовь"},
            {"text": "Секрет успеха — начать.", "author": "Марк Твен", "theme": "Успех"}
        ]
        
        self.load_history()
        self.create_widgets()
        self.refresh_history()
        
    def create_widgets(self):
        # Текущая цитата
        display_frame = tk.LabelFrame(self.root, text="Текущая цитата", font=("Arial", 12, "bold"), bg='#34495e', fg='white')
        display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.quote_text = tk.Text(display_frame, height=4, font=("Georgia", 12, "italic"), wrap=tk.WORD, bg='#ecf0f1')
        self.quote_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.quote_text.config(state=tk.DISABLED)
        
        info_frame = tk.Frame(display_frame, bg='#34495e')
        info_frame.pack(fill=tk.X, pady=5)
        
        self.author_label = tk.Label(info_frame, text="Автор: ---", font=("Arial", 10), bg='#34495e', fg='white')
        self.author_label.pack(side=tk.LEFT, padx=20)
        
        self.theme_label = tk.Label(info_frame, text="Тема: ---", font=("Arial", 10), bg='#34495e', fg='white')
        self.theme_label.pack(side=tk.RIGHT, padx=20)
        
        # Панель фильтров
        filter_frame = tk.Frame(self.root, bg='#2c3e50')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Фильтр по теме:", bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=5)
        self.theme_filter = ttk.Combobox(filter_frame, values=["Все"] + list(set(q['theme'] for q in self.quotes)), width=15, state="readonly")
        self.theme_filter.set("Все")
        self.theme_filter.pack(side=tk.LEFT, padx=5)
        self.theme_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_history())
        
        tk.Label(filter_frame, text="Фильтр по автору:", bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=5)
        self.author_filter = ttk.Combobox(filter_frame, values=["Все"] + sorted(list(set(q['author'] for q in self.quotes))), width=20, state="readonly")
        self.author_filter.set("Все")
        self.author_filter.pack(side=tk.LEFT, padx=5)
        self.author_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_history())
        
        # Кнопки
        btn_frame = tk.Frame(self.root, bg='#2c3e50')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.generate_btn = tk.Button(btn_frame, text="🎲 Сгенерировать цитату", command=self.generate_quote, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"))
        self.generate_btn.pack(pady=5)
        
        self.add_btn = tk.Button(btn_frame, text="➕ Добавить свою цитату", command=self.add_quote, bg="#3498db", fg="white")
        self.add_btn.pack(pady=5)
        
        # История
        history_frame = tk.LabelFrame(self.root, text="История цитат", font=("Arial", 10, "bold"))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Время", "Автор", "Тема", "Цитата")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "Цитата" else 400)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстное меню
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Удалить", command=self.delete_quote)
        self.tree.bind("<Button-3>", self.show_menu)
        
        # Статистика
        stats_frame = tk.Frame(self.root, bg='#2c3e50')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="Всего цитат: 0", bg='#2c3e50', fg='white', font=("Arial", 10))
        self.stats_label.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(stats_frame, text="Очистить историю", command=self.clear_history, bg="#f44336", fg="white")
        clear_btn.pack(side=tk.RIGHT, padx=10)
        
    def generate_quote(self):
        # Выбор темы и автора
        theme_filter = self.theme_filter.get()
        author_filter = self.author_filter.get()
        
        available = self.quotes.copy()
        if theme_filter != "Все":
            available = [q for q in available if q['theme'] == theme_filter]
        if author_filter != "Все":
            available = [q for q in available if q['author'] == author_filter]
        
        if not available:
            messagebox.showwarning("Нет цитат", "Нет цитат с выбранными фильтрами!")
            return
        
        quote = random.choice(available)
        
        # Отображение
        self.quote_text.config(state=tk.NORMAL)
        self.quote_text.delete(1.0, tk.END)
        self.quote_text.insert(1.0, f'"{quote["text"]}"')
        self.quote_text.config(state=tk.DISABLED)
        
        self.author_label.config(text=f"Автор: {quote['author']}")
        self.theme_label.config(text=f"Тема: {quote['theme']}")
        
        # Сохранение в историю
        self.history.append({
            "id": len(self.history) + 1,
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "author": quote['author'],
            "theme": quote['theme'],
            "text": quote['text']
        })
        
        self.save_history()
        self.refresh_history()
        
    def add_quote(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить цитату")
        dialog.geometry("500x400")
        dialog.configure(bg='#ecf0f1')
        
        tk.Label(dialog, text="Добавить новую цитату", font=("Arial", 14, "bold"), bg='#ecf0f1').pack(pady=10)
        
        tk.Label(dialog, text="Текст цитаты:", bg='#ecf0f1').pack(pady=5)
        text_entry = tk.Text(dialog, height=5, width=60)
        text_entry.pack(pady=5)
        
        tk.Label(dialog, text="Автор:", bg='#ecf0f1').pack(pady=5)
        author_entry = tk.Entry(dialog, width=40)
        author_entry.pack(pady=5)
        
        tk.Label(dialog, text="Тема:", bg='#ecf0f1').pack(pady=5)
        theme_entry = ttk.Combobox(dialog, values=["Мотивация", "Жизнь", "Мудрость", "Любовь", "Успех"], width=37)
        theme_entry.pack(pady=5)
        
        def save():
            text = text_entry.get("1.0", tk.END).strip()
            author = author_entry.get().strip()
            theme = theme_entry.get().strip()
            
            # Проверка на пустые строки
            if not text:
                messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
                return
            if not author:
                messagebox.showerror("Ошибка", "Автор не может быть пустым!")
                return
            if not theme:
                messagebox.showerror("Ошибка", "Тема не может быть пустой!")
                return
            
            # Добавление в список цитат
            new_quote = {"text": text, "author": author, "theme": theme}
            self.quotes.append(new_quote)
            
            # Обновление фильтров
            themes = list(set(q['theme'] for q in self.quotes))
            authors = sorted(list(set(q['author'] for q in self.quotes)))
            self.theme_filter['values'] = ["Все"] + themes
            self.author_filter['values'] = ["Все"] + authors
            
            messagebox.showinfo("Успех", "Цитата добавлена!")
            dialog.destroy()
        
        tk.Button(dialog, text="Сохранить", command=save, bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=20)
        
    def delete_quote(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите цитату для удаления!")
            return
        
        item = self.tree.item(selected[0])
        quote_text = item['values'][3]
        
        self.history = [h for h in self.history if h['text'] != quote_text]
        for i, h in enumerate(self.history):
            h['id'] = i + 1
        
        self.save_history()
        self.refresh_history()
        
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history()
        
    def refresh_history(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтрация
        filtered = self.history.copy()
        theme_filter = self.theme_filter.get()
        author_filter = self.author_filter.get()
        
        if theme_filter != "Все":
            filtered = [h for h in filtered if h['theme'] == theme_filter]
        if author_filter != "Все":
            filtered = [h for h in filtered if h['author'] == author_filter]
        
        # Отображение
        for item in reversed(filtered):
            self.tree.insert("", tk.END, values=(
                item['timestamp'],
                item['author'],
                item['theme'],
                item['text'][:100] + ("..." if len(item['text']) > 100 else "")
            ))
        
        # Обновление статистики
        self.stats_label.config(text=f"Всего цитат: {len(self.history)} | Отфильтровано: {len(filtered)}")
        
    def show_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)
        
    def load_history(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            # Тестовые данные
            self.history = [
                {"id": 1, "timestamp": datetime.now().strftime("%d.%m.%Y 12:00:00"), 
                 "author": "Махатма Ганди", "theme": "Мотивация", 
                 "text": "Будьте тем изменением, которое хотите видеть в мире."}
            ]
            self.save_history()
        
    def save_history(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomQuoteGenerator(root)
    root.mainloop()
