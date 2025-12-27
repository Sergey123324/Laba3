import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import random
import os
import sys
from typing import List, Dict, Optional



class QuizGame:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.setup_window()
            self.load_questions()
            self.setup_variables()
            self.setup_styles()
            self.create_widgets()
            self.start_new_game()

        except Exception as e:
            self.show_critical_error(f"Ошибка при запуске игры:\n{str(e)}")

    def setup_window(self):
        self.root.title("Умный Квиз - Проверь свои знания!")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        try:
            self.root.iconbitmap(default="icon.ico")
        except:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_questions(self):
        self.questions_file = "questions.json"
        self.all_questions = []

        try:
            if not os.path.exists(self.questions_file):
                raise FileNotFoundError(f"Файл '{self.questions_file}' не найден!")

            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Файл должен содержать список вопросов")

            required_fields = {"question", "answers", "correct"}
            for i, q in enumerate(data):
                if not isinstance(q, dict):
                    raise ValueError(f"Вопрос {i + 1} должен быть словарем")

                missing = required_fields - set(q.keys())
                if missing:
                    raise ValueError(f"Вопрос {i + 1}: отсутствуют поля {missing}")

                if not isinstance(q["question"], str):
                    raise ValueError(f"Вопрос {i + 1}: поле 'question' должно быть строкой")

                if not isinstance(q["answers"], list) or len(q["answers"]) != 4:
                    raise ValueError(f"Вопрос {i + 1}: должно быть 4 варианта ответа")

                if not isinstance(q["correct"], int) or not (0 <= q["correct"] <= 3):
                    raise ValueError(f"Вопрос {i + 1}: 'correct' должен быть числом от 0 до 3")

            self.all_questions = data

            if len(self.all_questions) < 5:
                raise ValueError(f"Слишком мало вопросов ({len(self.all_questions)}). Нужно минимум 5")

            print(f"Успешно загружено {len(self.all_questions)} вопросов")

        except FileNotFoundError as e:
            self.show_critical_error(str(e) + "\n\nСоздайте файл questions.json с вопросами.")
        except json.JSONDecodeError as e:
            self.show_critical_error(f"Ошибка в формате JSON файла:\n{str(e)}")
        except ValueError as e:
            self.show_critical_error(f"Ошибка в данных вопросов:\n{str(e)}")
        except Exception as e:
            self.show_critical_error(f"Неизвестная ошибка при загрузке вопросов:\n{str(e)}")

    def setup_variables(self):
        self.score = 0
        self.current_question_index = 0
        self.total_questions = 10
        self.used_questions_indices = set()
        self.current_question = None
        self.time_left = 30
        self.timer_running = False
        self.game_active = False

        self.colors = {
            "correct": "#4CAF50",
            "incorrect": "#F44336",
            "neutral": "#2196F3",
            "timer_warning": "#FF9800",
            "timer_danger": "#F44336",
            "bg": "#f0f0f0",
            "button_bg": "#e0e0e0"
        }

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure("Game.TButton",
                             font=("Arial", 14, "bold"),
                             padding=15)

        self.style.configure("Timer.TLabel",
                             font=("Arial", 20, "bold"))

    def create_widgets(self):
        try:
            self.root.grid_columnconfigure(0, weight=1)
            for i in range(6):
                self.root.grid_rowconfigure(i, weight=1)

            self.create_top_panel()

            self.create_question_area()

            self.create_answers_area()

            self.create_control_panel()

            self.create_status_bar()

        except Exception as e:
            self.show_error("Ошибка создания интерфейса", str(e))

    def create_top_panel(self):
        top_frame = ttk.Frame(self.root, relief="ridge", padding=10)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.score_label = tk.Label(top_frame,
                                    text="Счет: 0",
                                    font=("Arial", 16, "bold"),
                                    fg="darkblue")
        self.score_label.grid(row=0, column=0, sticky="w")

        self.progress_label = tk.Label(top_frame,
                                       text="Вопрос 0/10",
                                       font=("Arial", 16),
                                       fg="darkgreen")
        self.progress_label.grid(row=0, column=1)

        self.timer_label = tk.Label(top_frame,
                                    text="⏱ 30 сек",
                                    font=("Arial", 16, "bold"),
                                    fg="darkred")
        self.timer_label.grid(row=0, column=2, sticky="e")

    def create_question_area(self):
        question_frame = ttk.Frame(self.root, relief="solid", padding=20)
        question_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        question_frame.grid_columnconfigure(0, weight=1)
        question_frame.grid_rowconfigure(0, weight=1)

        self.category_label = tk.Label(question_frame,
                                       text="",
                                       font=("Arial", 12),
                                       fg="gray")
        self.category_label.grid(row=0, column=0, sticky="w")

        self.question_text = tk.Text(question_frame,
                                     height=4,
                                     font=("Arial", 18),
                                     wrap="word",
                                     bg="white",
                                     relief="flat",
                                     padx=10,
                                     pady=10)
        self.question_text.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        self.question_text.config(state="disabled")

        self.image_label = tk.Label(question_frame)
        self.image_label.grid(row=2, column=0, pady=10)

    def create_answers_area(self):
        answers_frame = ttk.Frame(self.root)
        answers_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.answer_buttons = []
        button_texts = ["A", "B", "C", "D"]

        for i in range(4):
            row = i // 2
            col = i % 2

            btn_frame = ttk.Frame(answers_frame)
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_rowconfigure(0, weight=1)

            btn = tk.Button(btn_frame,
                            text="",
                            font=("Arial", 14),
                            command=lambda idx=i: self.check_answer(idx),
                            bg=self.colors["button_bg"],
                            activebackground="#d0d0d0",
                            relief="raised",
                            bd=3,
                            padx=20,
                            pady=15,
                            wraplength=300)
            btn.grid(sticky="nsew")
            letter_label = tk.Label(btn_frame,
                                    text=button_texts[i],
                                    font=("Arial", 16, "bold"),
                                    bg="white",
                                    fg="black",
                                    width=3,
                                    relief="sunken")
            letter_label.grid(row=0, column=1, sticky="ns", padx=(5, 0))

            self.answer_buttons.append(btn)

            answers_frame.grid_columnconfigure(col, weight=1)
            answers_frame.grid_rowconfigure(row, weight=1)

    def create_control_panel(self):
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.skip_button = tk.Button(control_frame,
                                     text="⏭ Пропустить",
                                     font=("Arial", 12),
                                     command=self.skip_question,
                                     bg="#FF9800",
                                     state="disabled")
        self.skip_button.grid(row=0, column=0, sticky="w")

        self.hint_button = tk.Button(control_frame,
                                     text="💡 Подсказка",
                                     font=("Arial", 12),
                                     command=self.show_hint,
                                     bg="#9C27B0",
                                     fg="white",
                                     state="disabled")
        self.hint_button.grid(row=0, column=1)

        self.next_button = tk.Button(control_frame,
                                     text="Следующий вопрос →",
                                     font=("Arial", 14, "bold"),
                                     command=self.next_question,
                                     bg="#4CAF50",
                                     fg="white",
                                     state="disabled")
        self.next_button.grid(row=0, column=2, sticky="e")

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, relief="sunken", padding=5)
        status_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        self.status_label = tk.Label(status_frame,
                                     text="Готов к игре! Нажмите 'Начать игру'",
                                     font=("Arial", 10),
                                     fg="gray")
        self.status_label.pack()

        start_frame = ttk.Frame(self.root)
        start_frame.grid(row=5, column=0, pady=20)

        self.start_button = tk.Button(start_frame,
                                      text="🎮 Начать новую игру",
                                      font=("Arial", 16, "bold"),
                                      command=self.start_new_game,
                                      bg="#2196F3",
                                      fg="white",
                                      padx=30,
                                      pady=15)
        self.start_button.pack()

    def get_random_question(self) -> Optional[Dict]:
        try:
            if len(self.used_questions_indices) >= len(self.all_questions):
                return None

            available = [i for i in range(len(self.all_questions))
                         if i not in self.used_questions_indices]

            if not available:
                return None

            idx = random.choice(available)
            self.used_questions_indices.add(idx)

            return self.all_questions[idx]

        except Exception as e:
            self.show_error("Ошибка выбора вопроса", str(e))
            return None

    def load_question(self):
        try:
            self.current_question = self.get_random_question()

            if not self.current_question:
                self.end_game("Все вопросы закончились!")
                return

            self.question_text.config(state="normal")
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(1.0, self.current_question["question"])
            self.question_text.config(state="disabled")

            category = self.current_question.get("category", "Общее")
            difficulty = self.current_question.get("difficulty", 1)
            stars = "★" * difficulty
            self.category_label.config(
                text=f"Категория: {category} | Сложность: {stars}"
            )

            answers = self.current_question["answers"]
            for i, btn in enumerate(self.answer_buttons):
                btn.config(text=answers[i],
                           bg=self.colors["button_bg"],
                           state="normal")

            self.show_question_image()

            self.skip_button.config(state="normal")
            self.hint_button.config(state="normal")
            self.next_button.config(state="disabled")

            self.progress_label.config(
                text=f"Вопрос {self.current_question_index + 1}/{self.total_questions}"
            )

            self.start_timer()

            self.update_status(f"Вопрос загружен. У вас {self.time_left} секунд!")

        except Exception as e:
            self.show_error("Ошибка загрузки вопроса", str(e))
            self.next_question()

    def show_question_image(self):
        try:
            image_path = self.current_question.get("image")
            self.image_label.config(image="")

            if image_path and os.path.exists(image_path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(image_path)
                    img.thumbnail((400, 300))
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.config(image=photo)
                    self.image_label.image = photo

                except ImportError:
                    if image_path.lower().endswith(('.gif', '.ppm', '.pgm')):
                        photo = tk.PhotoImage(file=image_path)
                        self.image_label.config(image=photo)
                        self.image_label.image = photo
                    else:
                        self.image_label.config(
                            text="[Формат не поддерживается. \nУстановите Pillow для PNG/JPG]",
                            fg="red"
                        )

        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            self.image_label.config(
                text=f"[Ошибка: {str(e)[:50]}...]",
                fg="red"
            )

    def start_timer(self):
        self.time_left = 30
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or not self.game_active:
            return

        self.time_left -= 1

        if self.time_left > 10:
            color = "darkred"
        elif self.time_left > 5:
            color = self.colors["timer_warning"]
        else:
            color = self.colors["timer_danger"]

        self.timer_label.config(text=f"⏱ {self.time_left} сек", fg=color)

        if self.time_left <= 0:
            self.time_up()
        else:
            self.root.after(1000, self.update_timer)

    def time_up(self):
        self.timer_running = False
        self.update_status("Время вышло!")

        for btn in self.answer_buttons:
            btn.config(state="disabled")

        correct_idx = self.current_question["correct"]
        self.answer_buttons[correct_idx].config(bg=self.colors["correct"])

        self.skip_button.config(state="disabled")
        self.hint_button.config(state="disabled")
        self.next_button.config(state="normal")

        messagebox.showwarning("Время вышло!",
                               f"Правильный ответ: {self.current_question['answers'][correct_idx]}")

    def check_answer(self, answer_index):
        if not self.timer_running:
            return

        try:
            self.timer_running = False
            correct_index = self.current_question["correct"]

            for btn in self.answer_buttons:
                btn.config(state="disabled")

            if answer_index == correct_index:
                self.answer_buttons[answer_index].config(bg=self.colors["correct"])
                self.score += 10 * self.current_question.get("difficulty", 1)
                self.update_status("Правильно! +{} очков".format(
                    10 * self.current_question.get("difficulty", 1)))

                self.animate_correct_answer(answer_index)

                self.score_label.config(text=f"Счет: {self.score}")

            else:
                self.answer_buttons[answer_index].config(bg=self.colors["incorrect"])
                self.answer_buttons[correct_index].config(bg=self.colors["correct"])
                self.update_status(f"Неправильно! Правильный ответ: {self.current_question['answers'][correct_index]}")

            self.skip_button.config(state="disabled")
            self.hint_button.config(state="disabled")
            self.next_button.config(state="normal")

        except Exception as e:
            self.show_error("Ошибка проверки ответа", str(e))

    def animate_correct_answer(self, button_index):
        try:
            btn = self.answer_buttons[button_index]
            original_bg = self.colors["correct"]

            def flash(count=0):
                if count < 3:
                    current_color = btn.cget("bg")
                    new_color = "yellow" if current_color == original_bg else original_bg
                    btn.config(bg=new_color)
                    self.root.after(200, flash, count + 1)

            flash()
        except:
            pass

    def skip_question(self):
        self.timer_running = False
        self.time_up()

    def show_hint(self):
        try:
            if not self.current_question:
                return

            correct_idx = self.current_question["correct"]
            answers = self.current_question["answers"]

            wrong_indices = [i for i in range(4) if i != correct_idx]
            to_remove = random.sample(wrong_indices, 2)

            for idx in to_remove:
                self.answer_buttons[idx].config(
                    text="???",
                    state="disabled",
                    bg="lightgray"
                )

            self.hint_button.config(state="disabled")
            self.score = max(0, self.score - 5)
            self.score_label.config(text=f"Счет: {self.score}")

            self.update_status("Использована подсказка! -5 очков")

        except Exception as e:
            self.show_error("Ошибка подсказки", str(e))

    def next_question(self):
        self.current_question_index += 1

        if self.current_question_index >= self.total_questions:
            self.end_game()
        else:
            self.load_question()

    def start_new_game(self):
        try:
            self.score = 0
            self.current_question_index = 0
            self.used_questions_indices.clear()
            self.game_active = True

            self.score_label.config(text="Счет: 0")
            self.progress_label.config(text="Вопрос 0/10")
            self.timer_label.config(text="⏱ 30 сек", fg="darkred")
            self.category_label.config(text="")

            self.question_text.config(state="normal")
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(1.0, "Готовьтесь к первому вопросу...")
            self.question_text.config(state="disabled")

            for btn in self.answer_buttons:
                btn.config(text="", bg=self.colors["button_bg"], state="disabled")

            self.image_label.config(image="")

            self.skip_button.config(state="disabled")
            self.hint_button.config(state="disabled")
            self.next_button.config(state="disabled")

            self.update_status("Новая игра началась! Первый вопрос через 3 секунды...")

            self.root.after(3000, self.load_question)

        except Exception as e:
            self.show_error("Ошибка начала новой игры", str(e))

    def end_game(self, message=None):
        self.game_active = False
        self.timer_running = False

        if not message:
            message = f"Игра завершена!\nВаш итоговый счет: {self.score}"

        result_text = f"""
        {message}

        Правильных ответов: {self.score // 10}
        Всего вопросов: {self.total_questions}

        Спасибо за игру!
        """

        messagebox.showinfo("Игра завершена", result_text)

        if messagebox.askyesno("Новая игра?", "Хотите сыграть еще раз?"):
            self.start_new_game()

    def update_status(self, message: str):
        self.status_label.config(text=message)
        print(f"[STATUS] {message}")

    def show_error(self, title: str, message: str):
        print(f"[ERROR] {title}: {message}")
        messagebox.showerror(title, message)

    def show_critical_error(self, message: str):
        print(f"[CRITICAL ERROR] {message}")
        messagebox.showerror("Критическая ошибка",
                             f"{message}\n\nПрограмма будет закрыта.")

        try:
            self.root.destroy()
        except:
            pass

        sys.exit(1)

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            self.show_critical_error(f"Критическая ошибка во время выполнения:\n{str(e)}")


if __name__ == "__main__":
    print("=" * 50)
    print("Запуск Квиз-игры")
    print("=" * 50)

    try:
        app = QuizGame()
        app.run()

    except Exception as e:
        print(f"ФАТАЛЬНАЯ ОШИБКА: {e}")
        messagebox.showerror("Фатальная ошибка",
                             f"Программа завершилась с ошибкой:\n{str(e)}")