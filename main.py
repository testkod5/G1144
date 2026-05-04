import tkinter as tk
from tkinter import messagebox, Listbox, END
import json
import urllib.request
import urllib.error
import os

FAV_FILE = "favorites.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("400x500")

        self.favorites = self.load_favorites()

        self.label = tk.Label(root, text="Введите имя пользователя GitHub:")
        self.label.pack(pady=5)

        self.entry = tk.Entry(root, width=40)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', lambda event: self.search_user())

        self.search_btn = tk.Button(root, text="Найти", command=self.search_user)
        self.search_btn.pack(pady=5)

        self.result_list = Listbox(root, height=10, width=50)
        self.result_list.pack(pady=10)

        self.add_btn = tk.Button(root, text="Добавить в избранное", command=self.add_to_favorites)
        self.add_btn.pack(pady=5)

        self.fav_label = tk.Label(root, text="Избранное:")
        self.fav_label.pack(pady=(10, 0))
        
        self.fav_list = Listbox(root, height=10, width=50)
        self.fav_list.pack(pady=5)
        self.update_fav_list()

    def search_user(self):
        username = self.entry.get().strip()
        
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        self.result_list.delete(0, END)

        try:
            url = f"https://api.github.com/users/{username}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Python-GitHub-Finder')
            
            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode('utf-8'))
            
            login = data.get('login', 'N/A')
            name = data.get('name', 'Нет имени')
            bio = data.get('bio', 'Нет био')
            
            display_text = f"{login} | {name}"
            self.result_list.insert(END, display_text)
            
            self.current_user_data = {
                "login": login,
                "name": name,
                "bio": bio
            }

        except urllib.error.HTTPError as e:
            if e.code == 404:
                messagebox.showwarning("Не найдено", "Пользователь не найден.")
            else:
                messagebox.showerror("Ошибка API", f"Ошибка сервера: {e.code}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def add_to_favorites(self):
        if not hasattr(self, 'current_user_data'):
            messagebox.showwarning("Внимание", "Сначала найдите пользователя!")
            return
        
        user = self.current_user_data
        login = user['login']

        for fav in self.favorites:
            if fav['login'] == login:
                messagebox.showinfo("Инфо", "Этот пользователь уже в избранном.")
                return

        self.favorites.append(user)
        self.save_favorites()
        self.update_fav_list()
        messagebox.showinfo("Успех", f"{login} добавлен в избранное!")

    def update_fav_list(self):
        self.fav_list.delete(0, END)
        for user in self.favorites:
            self.fav_list.insert(END, f"{user['login']} | {user['name']}")

    def save_favorites(self):
        with open(FAV_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

    def load_favorites(self):
        if os.path.exists(FAV_FILE):
            try:
                with open(FAV_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
