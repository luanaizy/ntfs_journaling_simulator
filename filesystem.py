class File:
    def __init__(self, name, content=''):
        self.name = name
        self.content = content
        self.acl = {}  # {'user1': 'rw', 'user2': 'r'}

    def set_permission(self, user, permission):
        if permission in ['rw', 'r', 'w', 'none']:
            self.acl[user] = permission
        else:
            raise ValueError("Permissão inválida. Use 'rw', 'r', 'w' ou 'none'")

    def get_permission(self, user):
        return self.acl.get(user, 'none')


class Directory:
    def __init__(self, name):
        self.name = name
        self.files = []
        self.subdirectories = []

    def find_subdir(self, name):
        for subdir in self.subdirectories:
            if subdir.name == name:
                return subdir
        return None

    def find_file(self, name):
        for file in self.files:
            if file.name == name:
                return file
        return None


class JournalEntry:
    def __init__(self, action, target, content=None, user=None):
        self.action = action  # 'create', 'delete', 'write', 'append'
        self.target = target  # path string
        self.content = content
        self.user = user


class FileSystem:
    def __init__(self):
        self.root = Directory("root")
        self.journal = []

    def _navigate_to_dir(self, path):
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts[:-1]:
            next_dir = current.find_subdir(part)
            if not next_dir:
                next_dir = Directory(part)
                current.subdirectories.append(next_dir)
            current = next_dir
        return current, parts[-1]

    def create_file(self, path, content='', user='root'):
        parent_dir, filename = self._navigate_to_dir(path)
        if parent_dir.find_file(filename):
            print(f"Arquivo '{filename}' já existe.")
            return
        new_file = File(filename, content)
        new_file.set_permission(user, 'rw')
        parent_dir.files.append(new_file)
        self.journal.append(JournalEntry('create', path, content, user))
        print(f"[{user}] Arquivo '{filename}' criado.")

    def delete_file(self, path, user='root'):
        parent_dir, filename = self._navigate_to_dir(path)
        file = parent_dir.find_file(filename)
        if not file:
            print(f"Arquivo '{filename}' não encontrado.")
            return
        if file.get_permission(user) not in ['rw', 'w']:
            print(f"[{user}] Sem permissão para deletar '{filename}'.")
            return
        parent_dir.files.remove(file)
        self.journal.append(JournalEntry('delete', path, file.content, user))
        print(f"[{user}] Arquivo '{filename}' deletado.")

    def read_file(self, path, user='root'):
        parent_dir, filename = self._navigate_to_dir(path)
        file = parent_dir.find_file(filename)
        if not file:
            print(f"Arquivo '{filename}' não encontrado.")
            return
        perm = file.get_permission(user)
        if perm in ['r', 'rw']:
            print(f"[{user}] Conteúdo de '{filename}': {file.content}")
        else:
            print(f"[{user}] Sem permissão para leitura.")

    def write_file(self, path, new_content, user='root'):
        parent_dir, filename = self._navigate_to_dir(path)
        file = parent_dir.find_file(filename)
        if not file:
            print(f"Arquivo '{filename}' não encontrado.")
            return
        perm = file.get_permission(user)
        if perm in ['w', 'rw']:
            file.content = new_content
            self.journal.append(JournalEntry('write', path, new_content, user))
            print(f"[{user}] Arquivo '{filename}' atualizado.")
        else:
            print(f"[{user}] Sem permissão para escrita.")

    def append_to_file(self, path, additional_content, user='root'):
        parent_dir, filename = self._navigate_to_dir(path)
        file = parent_dir.find_file(filename)
        if not file:
            print(f"Arquivo '{filename}' não encontrado.")
            return
        perm = file.get_permission(user)
        if perm in ['w', 'rw']:
            file.content += "\n" + additional_content
            self.journal.append(JournalEntry('write', path, additional_content, user))
            print(f"[{user}] Conteúdo adicionado ao arquivo '{filename}'.")
        else:
            print(f"[{user}] Sem permissão para escrita.")

    def set_file_permission(self, path, user_alvo, permission, admin='root'):
        if admin != 'admin':
            print(f"[{admin}] Sem permissão para alterar permissões.")
            return
        parent_dir, filename = self._navigate_to_dir(path)
        file = parent_dir.find_file(filename)
        if not file:
            print(f"Arquivo '{filename}' não encontrado.")
            return
        file.set_permission(user_alvo, permission)
        print(f"[{admin}] Permissão '{permission}' atribuída a '{user_alvo}' no arquivo '{filename}'.")

    def create_directory(self, path):
        parent_dir, dirname = self._navigate_to_dir(path)
        if parent_dir.find_subdir(dirname):
            print(f"Diretório '{dirname}' já existe.")
            return
        new_dir = Directory(dirname)
        parent_dir.subdirectories.append(new_dir)
        print(f"Diretório '{dirname}' criado.")

    def list_directory(self, path):
        if path == "/":
            target_dir = self.root
        else:
            parent_dir, dirname = self._navigate_to_dir(path)
            if dirname == '':
                target_dir = parent_dir
            else:
                target_dir = parent_dir.find_subdir(dirname)
            if not target_dir:
                print(f"Diretório '{path}' não encontrado.")
                return
        print(f"Conteúdo de '{path}':")
        for d in target_dir.subdirectories:
            print(f"  <DIR> {d.name}")
        for f in target_dir.files:
            print(f"       {f.name}")

    def directory_exists(self, path):
        if path == "/":
            return True
        parent_dir, dirname = self._navigate_to_dir(path)
        if dirname == '':
            return True
        return parent_dir.find_subdir(dirname) is not None

    def simulate_crash_and_recovery(self):
        print("\n[RECUPERAÇÃO APÓS FALHA]")
        self.root = Directory("root")
        for entry in self.journal:
            if entry.action == 'create':
                self._replay_create(entry)
            elif entry.action == 'write':
                self._replay_write(entry)
            elif entry.action == 'append':
                self._replay_append(entry)
            elif entry.action == 'delete':
                self._replay_delete(entry)
        print("[RECUPERAÇÃO CONCLUÍDA]\n")

    def _replay_create(self, entry):
        parent_dir, filename = self._navigate_to_dir(entry.target)
        if not parent_dir.find_file(filename):
            new_file = File(filename, entry.content)
            new_file.set_permission(entry.user, 'rw')
            parent_dir.files.append(new_file)
            print(f"(Recuperado) Arquivo '{filename}' criado.")

    def _replay_write(self, entry):
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            file.content = entry.content
            print(f"(Recuperado) Arquivo '{filename}' atualizado.")

    def _replay_append(self, entry):
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            file.content += "\n" + entry.content
            print(f"(Recuperado) Conteúdo adicionado ao arquivo '{filename}'.")

    def _replay_delete(self, entry):
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            parent_dir.files.remove(file)
            print(f"(Recuperado) Arquivo '{filename}' deletado.")
