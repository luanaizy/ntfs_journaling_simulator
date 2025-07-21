import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from filesystem import FileSystem

class NTFSJournalingSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NTFS Journaling Simulator")
        self.root.geometry("1000x700")
        self.fs = FileSystem()
        self.current_path = "/"
        self.current_user = "admin"
        self.selected_file = None

        self.create_widgets()
        self.update_file_list()
        self.update_journal()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # Controle de usuário
        user_frame = ttk.Frame(top_frame)
        user_frame.pack(side=tk.LEFT)
        
        ttk.Label(user_frame, text="Usuário:").pack(side=tk.LEFT)
        self.user_var = tk.StringVar(value=self.current_user)
        user_entry = ttk.Entry(user_frame, textvariable=self.user_var, width=10)
        user_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(user_frame, text="Mudar", command=self.change_user).pack(side=tk.LEFT)

        ttk.Label(top_frame, text=" Caminho:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=self.current_path)
        path_entry = ttk.Entry(top_frame, textvariable=self.path_var, width=40)
        path_entry.pack(side=tk.LEFT)
        path_entry.bind("<Return>", lambda event: self.change_directory())

        ttk.Button(top_frame, text="Voltar", command=self.go_back).pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10)

        ttk.Button(button_frame, text="Novo Arquivo", command=self.create_file).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Novo Diretório", command=self.create_directory).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Editar Conteúdo", command=self.edit_content).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Visualizar Conteúdo", command=self.view_content).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Excluir", command=self.delete_item).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Permissão", command=self.apply_permission).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Simular Falha", command=self.simulate_crash).pack(side=tk.LEFT)

        self.file_tree = ttk.Treeview(self.root, columns=("Nome", "Tipo", "Permissões"), show="headings")
        self.file_tree.heading("Nome", text="Nome")
        self.file_tree.heading("Tipo", text="Tipo")
        self.file_tree.heading("Permissões", text="Permissões")
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        self.file_tree.bind("<Double-1>", self.on_item_double_click)

        self.journal_text = scrolledtext.ScrolledText(self.root, height=10, state=tk.DISABLED)
        self.journal_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)

    def change_user(self):
        new_user = self.user_var.get().strip()
        if not new_user:
            messagebox.showerror("Erro", "Nome de usuário não pode ser vazio")
            return
        
        self.current_user = new_user
        self.update_file_list()
        self.update_status(f"Usuário alterado para: {self.current_user}")
        self.selected_file = None

    def change_directory(self):
        new_path = self.path_var.get()
        if self.fs.directory_exists(new_path):
            self.current_path = new_path
            self.update_file_list()
            self.update_status(f"Diretório alterado para: {self.current_path}")
        else:
            messagebox.showerror("Erro", f"Diretório '{new_path}' não encontrado")

    def go_back(self):
        if self.current_path == "/":
            return
        parts = self.current_path.rstrip("/").split("/")
        new_path = "/".join(parts[:-1]) or "/"
        self.path_var.set(new_path)
        self.change_directory()

    def update_file_list(self):
        self.file_tree.delete(*self.file_tree.get_children())
        
        if self.current_path == "/":
            current_dir = self.fs.root
        else:
            parent_dir, dirname = self.fs._navigate_to_dir(self.current_path)
            current_dir = parent_dir.find_subdir(dirname) if dirname else parent_dir

        for d in current_dir.subdirectories:
            self.file_tree.insert("", "end", values=(d.name, "<DIR>", ""))
        
        for f in current_dir.files:
            if self.can_read_file(f):
                perms = ", ".join([f"{u}:{p}" for u, p in f.acl.items()])
                self.file_tree.insert("", "end", values=(f.name, "Arquivo", perms))
            else:
                self.file_tree.insert("", "end", values=(f.name, "Arquivo", "ACESSO NEGADO"), tags=('denied',))
        
        self.file_tree.tag_configure('denied', foreground='gray')

    def can_read_file(self, file):
        if self.current_user == "admin":
            return True
        permission = file.get_permission(self.current_user)
        return permission in ['r', 'rw']

    def can_write_file(self, file):
        if self.current_user == "admin":
            return True
        permission = file.get_permission(self.current_user)
        return permission in ['w', 'rw']

    def on_file_select(self, event):
        selected = self.file_tree.focus()
        if not selected:
            return
            
        item = self.file_tree.item(selected)
        name = item["values"][0]
        type_ = item["values"][1]
        
        if type_ == "Arquivo":
            self.selected_file = name
            self.update_status(f"Arquivo selecionado: {name}")

    def update_journal(self):
        self.journal_text.config(state=tk.NORMAL)
        self.journal_text.delete(1.0, tk.END)
        
        if not self.fs.journal:
            self.journal_text.insert(tk.END, "O journal está vazio.")
        else:
            for i, entry in enumerate(self.fs.journal, 1):
                content_preview = entry.content
                if content_preview is not None and len(str(content_preview)) > 20:
                    content_preview = str(content_preview)[:20] + "..."
                self.journal_text.insert(tk.END, 
                    f"{i}. Ação: {entry.action}, Arquivo: {entry.target}, Usuário: {entry.user}, Conteúdo: {content_preview}\n")
        
        self.journal_text.config(state=tk.DISABLED)

    def update_status(self, message):
        self.status_var.set(message)

    def on_item_double_click(self, event):
        selected = self.file_tree.focus()
        if not selected:
            return
            
        item = self.file_tree.item(selected)
        name = item["values"][0]
        type_ = item["values"][1]
        
        if type_ == "<DIR>":
            new_path = f"{self.current_path.rstrip('/')}/{name}"
            self.path_var.set(new_path)
            self.change_directory()

    def create_file(self):
        name = simpledialog.askstring("Novo Arquivo", "Nome do arquivo:")
        if name:
            path = f"{self.current_path.rstrip('/')}/{name}"
            self.fs.create_file(path, user=self.current_user)
            self.update_file_list()
            self.update_journal()
            
            if messagebox.askyesno("Conteúdo", "Deseja adicionar conteúdo ao arquivo agora?"):
                content = simpledialog.askstring("Conteúdo", f"Conteúdo para {name}:")
                if content is not None:
                    self.fs.write_file(path, content, user=self.current_user)
                    self.update_file_list()
                    self.update_journal()
                    self.update_status(f"Conteúdo adicionado ao arquivo '{name}'")

    def create_directory(self):
        name = simpledialog.askstring("Novo Diretório", "Nome do diretório:")
        if name:
            path = f"{self.current_path.rstrip('/')}/{name}"
            self.fs.create_directory(path)
            self.update_file_list()
            self.update_journal()

    def edit_content(self):
        if not self.selected_file:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado")
            return
            
        if self.current_path == "/":
            current_dir = self.fs.root
        else:
            parent_dir, dirname = self.fs._navigate_to_dir(self.current_path)
            current_dir = parent_dir.find_subdir(dirname) if dirname else parent_dir
        
        file = current_dir.find_file(self.selected_file)
        
        if not file:
            messagebox.showerror("Erro", "Arquivo não encontrado")
            return
            
        if not self.can_write_file(file):
            messagebox.showerror("Erro", "Você não tem permissão para editar este arquivo")
            return
            
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editando: {self.selected_file}")
        edit_window.geometry("800x600")
        
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert(tk.END, file.content if file.content else "")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Salvar Edição", 
                 command=lambda: self.save_edited_content(content_text, edit_window)).pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Cancelar", 
                 command=edit_window.destroy).pack(side=tk.RIGHT, padx=5)

    def save_edited_content(self, content_text, edit_window):
        new_content = content_text.get(1.0, tk.END).strip()
        path = f"{self.current_path.rstrip('/')}/{self.selected_file}"
        self.fs.write_file(path, new_content, user=self.current_user)
        self.update_file_list()
        self.update_journal()
        edit_window.destroy()
        self.update_status(f"Conteúdo do arquivo '{self.selected_file}' atualizado")

    def view_content(self):
        if not self.selected_file:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado")
            return
            
        if self.current_path == "/":
            current_dir = self.fs.root
        else:
            parent_dir, dirname = self.fs._navigate_to_dir(self.current_path)
            current_dir = parent_dir.find_subdir(dirname) if dirname else parent_dir
        
        file = current_dir.find_file(self.selected_file)
        
        if not file:
            messagebox.showerror("Erro", "Arquivo não encontrado")
            return
            
        if not self.can_read_file(file):
            messagebox.showerror("Erro", "Você não tem permissão para visualizar este arquivo")
            return
            
        view_window = tk.Toplevel(self.root)
        view_window.title(f"Visualizando: {self.selected_file}")
        view_window.geometry("600x400")
        
        main_frame = ttk.Frame(view_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state=tk.DISABLED)
        content_text.pack(fill=tk.BOTH, expand=True)
        
        content_text.config(state=tk.NORMAL)
        content_text.insert(tk.END, file.content if file.content else "")
        content_text.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Fechar", 
                 command=view_window.destroy).pack(side=tk.RIGHT)

    def delete_item(self):
        selected = self.file_tree.focus()
        if not selected:
            return
            
        item = self.file_tree.item(selected)
        name = item["values"][0]
        type_ = item["values"][1]
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir {name}?"):
            path = f"{self.current_path.rstrip('/')}/{name}"
            if type_ == "Arquivo":
                if self.current_path == "/":
                    current_dir = self.fs.root
                else:
                    parent_dir, dirname = self.fs._navigate_to_dir(self.current_path)
                    current_dir = parent_dir.find_subdir(dirname) if dirname else parent_dir
                
                file = current_dir.find_file(name)
                if file and not self.can_write_file(file) and self.current_user != "admin":
                    messagebox.showerror("Erro", "Você não tem permissão para excluir este arquivo")
                    return
                self.fs.delete_file(path, user=self.current_user)
            else:
                messagebox.showwarning("Aviso", "Exclusão de diretórios não implementada")
            self.update_file_list()
            self.update_journal()

    def apply_permission(self):
        if not self.selected_file:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado")
            return
            
        if self.current_user != "admin":
            messagebox.showerror("Erro", "Apenas o administrador pode alterar permissões")
            return
            
        path = f"{self.current_path.rstrip('/')}/{self.selected_file}"
        user = simpledialog.askstring("Permissão", "Usuário:")
        if not user:
            return
            
        perm = simpledialog.askstring("Permissão", "Permissão (rw/r/w/none):")
        if perm:
            if perm.lower() not in ["rw", "r", "w", "none"]:
                messagebox.showerror("Erro", "Permissão inválida. Use rw, r, w ou none")
                return
                
            self.fs.set_file_permission(path, user, perm, admin=self.current_user)
            self.update_file_list()
            self.update_journal()

    def simulate_crash(self):
        if messagebox.askyesno("Simular Falha", "Tem certeza que deseja simular uma falha no sistema?"):
            self.fs.simulate_crash_and_recovery()
            self.update_file_list()
            self.update_journal()
            self.update_status("Sistema recuperado após falha")

if __name__ == "__main__":
    root = tk.Tk()
    app = NTFSJournalingSimulatorGUI(root)
    root.mainloop()