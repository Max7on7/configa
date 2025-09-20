import tkinter as tk
from tkinter import scrolledtext, END
import os

class TerminalEmulator:
    def __init__(self, root):
        self.root = root
        self.hostname = "maxim"
        self.current_dir = os.getcwd()  # Текущая директория
        
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
    
    def print_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(END, text)
        self.output_text.config(state='disabled')
        self.output_text.see(END)
    
    def update_prompt(self):
        dir_name = os.path.basename(self.current_dir) or self.current_dir
        self.prompt_label.config(text=f"[{self.hostname} {dir_name}]$")
    
    def process_command(self, event=None):
        command_line = self.command_entry.get()
        self.command_entry.delete(0, END)
        
        self.print_output(f"[{self.hostname} {os.path.basename(self.current_dir) or self.current_dir}]${command_line}\n")
        
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
    
    def ls_command(self, args):
        try:
            items = os.listdir(self.current_dir)
            if items:
                items.sort() # сортировка без особого смысла, просто для крастоы
                output = "\n".join(items) + "\n"
                self.print_output(output)
            else:
                self.print_output("(пустая директория)\n")
        except PermissionError:
            self.print_output("ls: Доступ запрещен\n")
        except Exception as e:
            self.print_output(f"ls: Ошибка - {str(e)}\n")
    
    def cd_command(self, args):
        if not args:
            self.current_dir = os.path.expanduser("~")
        else:
            path = args[0]
            if path == "~":
                new_path = os.path.expanduser("~")
            else:
                new_path = os.path.join(self.current_dir, path) if not os.path.isabs(path) else path
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_dir = os.path.abspath(new_path)
            else:
                self.print_output(f"cd: Нет такого файла или директории: {path}\n")
                return
        
        self.update_prompt()
    
    def exit_command(self, args):
        self.print_output("Выход из эмулятора...\n")
        self.root.after(1000, self.root.destroy)

def main():
    root = tk.Tk()
    root.geometry("1000x1000")
    root.minsize(600, 400)
    
    app = TerminalEmulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()