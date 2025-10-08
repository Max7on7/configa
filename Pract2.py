import tkinter as tk
from tkinter import scrolledtext, END
import os
import sys
import argparse

class TerminalEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.hostname = "maxim"
        self.current_dir = os.getcwd()  # Текущая директория
        
        # Отладочный вывод параметров
        print(f"DEBUG: VFS path: {self.vfs_path}")
        print(f"DEBUG: Script path: {self.script_path}")
        
        self.root.title(f"Эмулятор - [{self.hostname}]")
        self.root.configure(bg='#2d2d2d')

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', bg='#14213D', fg='#E5E5E5', font=('Times New Roman', 14))
        self.output_text.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.prompt_label = tk.Label(self.input_frame, text=f"[{self.hostname} ~]$", font=('Times New Roman', 14), fg="#412B07")
        self.prompt_label.pack(side='left')
        
        self.command_entry = tk.Entry(self.input_frame, font=('Times New Roman', 14), fg='#E5E5E5', bg='#14213D')
        self.command_entry.pack(side='left', fill='x', expand=True)
        self.command_entry.bind('<Return>', self.process_command)

        self.print_output("Оно работает!\n")
        self.print_output("Команды: ls, cd, exit\n")
        self.print_output("Введите 'exit' для выхода из программы.\n\n")
        
        # Выполнить стартовый скрипт, если указан
        if self.script_path:
            self.execute_script(self.script_path)
    
    def print_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(END, text)
        self.output_text.config(state='disabled')
        self.output_text.see(END)
    
    def update_prompt(self):
        dir_name = os.path.basename(self.current_dir) or self.current_dir
        self.prompt_label.config(text=f"[{self.hostname} {dir_name}]$")
    
    def execute_script(self, script_path):
        """Выполняет команды из стартового скрипта"""
        if not os.path.exists(script_path):
            self.print_output(f"Ошибка: файл скрипта не найден - {script_path}\n")
            return
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Пропускаем пустые строки и комментарии
                    continue
                
                try:
                    self.print_output(f"[{self.hostname} {os.path.basename(self.current_dir) or self.current_dir}]$ {line}\n")
                    self.execute_single_command(line)
                except Exception as e:
                    self.print_output(f"Ошибка в строке {line_num}: {str(e)}\n")
                    continue
        except Exception as e:
            self.print_output(f"Ошибка при чтении скрипта: {str(e)}\n")
    
    def execute_single_command(self, command_line):
        """Выполняет одну команду (для скрипта)"""
        if not command_line.strip():
            return
        
        parts = command_line.strip().split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if command == "exit":
            self.exit_command(args)
        elif command == "ls":
            self.ls_command(args)
        elif command == "cd":
            self.cd_command(args)
        else:
            self.print_output(f"Команда не найдена: {command}\n")
    
    def process_command(self, event=None):
        command_line = self.command_entry.get()
        self.command_entry.delete(0, END)
        
        self.print_output(f"[{self.hostname} {os.path.basename(self.current_dir) or self.current_dir}]$ {command_line}\n")
        
        if not command_line.strip():
            return
        
        self.execute_single_command(command_line)
    
    def ls_command(self, args):
        # Заглушка: выводит название команды и аргументы
        self.print_output(f"Вызвана команда: ls, аргументы: {args}\n")
    
    def cd_command(self, args):
        # Заглушка: выводит название команды и аргументы
        self.print_output(f"Вызвана команда: cd, аргументы: {args}\n")
    
    def exit_command(self, args):
        self.root.after(1000, self.root.destroy)

def main():
    parser = argparse.ArgumentParser(description='Эмулятор терминала с поддержкой VFS и стартового скрипта')
    parser.add_argument('--vfs', help='Путь к физическому расположению VFS')
    parser.add_argument('--script', help='Путь к стартовому скрипту')
    
    args = parser.parse_args()
    
    root = tk.Tk()
    root.geometry("1000x1000")
    root.minsize(600, 400)
    
    app = TerminalEmulator(root, args.vfs, args.script)
    root.mainloop()

if __name__ == "__main__":
    main()