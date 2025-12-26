import tkinter
from tkinter import messagebox

class Quize:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Квиз")
        self.root.geometry("700x700")
        self.score = 0
        self.current_question = 0
