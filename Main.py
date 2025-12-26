import tkinter
import json
import random
import os
import sys
from PIL import Image, ImageTk
from tkinter import messagebox, ttk, font

class Quiz:
    def __init__(self):
        try:
            self.root = tkinter.Tk()
            self.window()
            self.questions()
            self.variables()
            self.styles()
            self.widgets()
            self.new_game()

        except Exception as e:
            self.show_critical_error(f"Ошибка при запуске игры:\n{str(e)}")

    def window(self):
        self.root.title("Умный Квиз - Проверь свои знания!")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)

        try:
            self.root.iconbitmap(default="icon.ico")
        except:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def questions(self):
        self.questions_file = "Questions.json"
        self.all_questions = []