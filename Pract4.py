import tkinter as tk
from tkinter import scrolledtext, END
import os
import sys
import argparse
import csv
import base64
from pathlib import Path
import datetime

class VFSNode:
    def __init__(self, name, is_directory=False, content=None):
        self.name = name
        self.is_directory = is_directory
        self.content = content  # для файлов
        self.children = {} if is_directory else None  # для директорий
        self.parent = None

class VFS:
    def __init__(self, csv_path=None):
        self.root = VFSNode('/', is_directory=True)
        if csv_path:
            print(f"DEBUG: Загрузка VFS из {csv_path}")  # отладочка
            self.load_from_csv(csv_path)
            print(f"DEBUG: VFS успешно загружена")  # отладочка
    
    def load_from_csv(self, csv_path):
        """Загружает VFS из CSV файла"""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                path = row['path']
                is_dir = row['type'] == 'directory' or row['type'] == 'folder'
                content = row.get('content', '')
                
                if is_dir:
                    self.create_directory(path)
                else:
                    if content:
                        try:
                            decoded_content = base64.b64decode(content).decode('utf-8')
                        except:
                            decoded_content = content
                    else:
                        decoded_content = ''
                    self.create_file(path, decoded_content)
    
    def create_directory(self, path):
        path_parts = [p for p in path.split('/') if p]
        current = self.root
        
        for part in path_parts:
            if part not in current.children:
                new_dir = VFSNode(part, is_directory=True)
                new_dir.parent = current
                current.children[part] = new_dir
            current = current.children[part]
    
    def create_file(self, path, content):
        """Создает файл по пути с содержимым"""
        path_parts = [p for p in path.split('/') if p]
        filename = path_parts[-1]
        dir_path = path_parts[:-1]
        
        current = self.root
        for part in dir_path:
            if part not in current.children:
                new_dir = VFSNode(part, is_directory=True)
                new_dir.parent = current
                current.children[part] = new_dir
            current = current.children[part]
        
        file_node = VFSNode(filename, is_directory=False, content=content)
        file_node.parent = current
        current.children[filename] = file_node
    
    def get_node(self, path):
        if path == '/' or path == '':
            return self.root
        
        path_parts = [p for p in path.split('/') if p]
        current = self.root
        
        for part in path_parts:
            if current.is_directory and part in current.children:
                current = current.children[part]
            else:
                return None
        return current
    
    def list_directory(self, path):
        node = self.get_node(path)
        if node and node.is_directory:
            return list(node.children.keys())
        return []
    
    def read_file(self, path):
        node = self.get_node(path)
        if node and not node.is_directory:
            return node.content
        return None

class TerminalEmulator:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.hostname = "maxim"
        

        self.vfs = None
        if self.vfs_path and os.path.exists(self.vfs_path):
            try:
                self.vfs = VFS(self.vfs_path)
                print(f"DEBUG: VFS успешно создана из {self.vfs_path}")
            except Exception as e:
                print(f"DEBUG: Ошибка загрузки VFS: {e}")
                self.vfs = None
        else:
            print(f"DEBUG: VFS path не существует или не указан: {self.vfs_path}")
        
        self.current_dir = '/' 
        

        print(f"DEBUG: VFS path: {self.vfs_path}")
        print(f"DEBUG: Script path: {self.script_path}")
        print(f"DEBUG: VFS loaded: {self.vfs is not None}")
        
        self.root.title(f"Эмулятор - [{self.hostname}]")
        self.root.configure(bg='#2d2d2d')

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', bg='#14213D', fg='#E5E5E5', font=('Times New Roman', 14))
        self.output_text.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.prompt_label = tk.Label(self.input_frame, text=f"[{self.hostname} {self.current_dir}]$", font=('Times New Roman', 14), fg="#412B07")
        self.prompt_label.pack(side='left')
        
        self.command_entry = tk.Entry(self.input_frame, font=('Times New Roman', 14), fg='#E5E5E5', bg='#14213D')
        self.command_entry.pack(side='left', fill='x', expand=True)
        self.command_entry.bind('<Return>', self.process_command)

        self.print_output("Эмулятор терминала запущен!\n")
        if self.vfs:
            self.print_output("VFS загружена.\n")
        else:
            self.print_output("VFS не загружена.\n")
        self.print_output("Команды: ls, cd, cat, date, rev, exit\n")
        self.print_output("Введите 'exit' для выхода из программы.\n\n")
        
        if self.script_path:
            self.execute_script(self.script_path)
    
    def print_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(END, text)
        self.output_text.config(state='disabled')
        self.output_text.see(END)
    
    def update_prompt(self):
        self.prompt_label.config(text=f"[{self.hostname} {self.current_dir}]$")
    
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
                    self.print_output(f"[{self.hostname} {self.current_dir}]$ {line}\n")
                    self.execute_single_command(line)
                except Exception as e:
                    self.print_output(f"Ошибка в строке {line_num}: {str(e)}\n")
                    continue
        except Exception as e:
            self.print_output(f"Ошибка при чтении скрипта: {str(e)}\n")
    
    def execute_single_command(self, command_line):
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
        elif command == "cat":
            self.cat_command(args)
        elif command == "date":
            self.date_command(args)
        elif command == "rev":
            self.rev_command(args)
        else:
            self.print_output(f"Команда не найдена: {command}\n")
    
    def process_command(self, event=None):
        command_line = self.command_entry.get()
        self.command_entry.delete(0, END)
        
        self.print_output(f"[{self.hostname} {self.current_dir}]$ {command_line}\n")
        
        if not command_line.strip():
            return
        
        self.execute_single_command(command_line)
    
    def ls_command(self, args):
        if not self.vfs:
            self.print_output("VFS не загружена\n")
            return
        
        target_dir = self.current_dir
        if args:
            if args[0].startswith('/'):
                target_dir = args[0]
            else:
                target_dir = self.resolve_path(args[0])
        
        contents = self.vfs.list_directory(target_dir)
        if contents:
            for item in contents:
                self.print_output(f"{item}\n")
        else:
            self.print_output("Директория пуста или не существует\n")
    
    def cd_command(self, args):
        if not self.vfs:
            self.print_output("VFS не загружена\n")
            return
        
        if not args:
            self.current_dir = '/'
            self.update_prompt()
            return
        
        target_path = args[0]
        if target_path.startswith('/'):
            new_path = target_path
        else:
            new_path = self.resolve_path(target_path)
        
        # Проверяем, существует ли путь и является ли он директорией
        node = self.vfs.get_node(new_path)
        if node and node.is_directory:
            self.current_dir = new_path
            self.update_prompt()
        else:
            self.print_output(f"Директория не найдена: {new_path}\n")
    
    def cat_command(self, args):
        if not self.vfs:
            self.print_output("VFS не загружена\n")
            return
        
        if not args:
            self.print_output("cat: отсутствует имя файла\n")
            return
        
        file_path = args[0]
        if not file_path.startswith('/'):
            file_path = self.resolve_path(file_path)
        
        content = self.vfs.read_file(file_path)
        if content is not None:
            self.print_output(f"{content}\n")
        else:
            self.print_output(f"Файл не найден: {file_path}\n")
    
    def date_command(self, args):
        current_time = datetime.datetime.now()
        self.print_output(f"{current_time.strftime('%a %b %d %H:%M:%S %Y')}\n")
    
    def rev_command(self, args):
        if not args:
            # Если нет аргументов, ждем ввода с клавиатуры (упрощенная версия)
            self.print_output("rev: ожидается текст или имя файла\n")
            return
        
        input_text = ' '.join(args)
        # Реверсируем текстовые аргументы
        reversed_text = input_text[::-1]
        self.print_output(f"{reversed_text}\n")
    
    def resolve_path(self, relative_path):
        if relative_path == '..':
            parts = [p for p in self.current_dir.split('/') if p]
            if parts:
                parts.pop()
                return '/' + '/'.join(parts) if parts else '/'
        elif relative_path.startswith('..'):
            # ../path
            parts = [p for p in self.current_dir.split('/') if p]
            while relative_path.startswith('../'):
                if parts:
                    parts.pop()
                relative_path = relative_path[3:]
            if parts:
                return '/' + '/'.join(parts) + '/' + relative_path if relative_path else '/' + '/'.join(parts)
            else:
                return '/' + relative_path if relative_path else '/'
        elif relative_path == '.':
            return self.current_dir
        else:
            if self.current_dir == '/':
                return f"/{relative_path}"
            else:
                return f"{self.current_dir}/{relative_path}"
    
    def exit_command(self, args):
        self.root.after(1000, self.root.destroy)

def main():
    parser = argparse.ArgumentParser(description='Эмулятор терминала с поддержкой VFS и стартового скрипта')
    parser.add_argument('--vfs', help='Путь к физическому расположению VFS (CSV файл)')
    parser.add_argument('--script', help='Путь к стартовому скрипту')
    
    args = parser.parse_args()
    
    root = tk.Tk()
    root.geometry("1000x1000")
    root.minsize(600, 400)
    
    app = TerminalEmulator(root, args.vfs, args.script)
    root.mainloop()

if __name__ == "__main__":
    main()