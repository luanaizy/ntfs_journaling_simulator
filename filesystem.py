import json
import os

class File:
    def __init__(self, name, content=''):
        self.name = name
        self.content = content
        self.acl = {}  # Exemplo: {'user1': 'rw', 'user2': 'r'}

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
        self.action = action
        self.target = target
        self.content = content
        self.user = user

    def to_dict(self):
        return {
            'action': self.action,
            'target': self.target,
            'content': self.content,
            'user': self.user
        }

    @staticmethod
    def from_dict(data):
        return JournalEntry(
            data['action'],
            data['target'],
            data.get('content'),
            data.get('user')
        )


class FileSystem:
    def __init__(self):
        self.root = Directory("root")
        self.journal = []
        self.journal_path = "log_journal.txt"

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

    def _log(self, action, path, content, user):
        entry = JournalEntry(action, path, content, user)
        self.journal.append(entry)
        with open(self.journal_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def salvar_log_em_arquivo(self):
        with open(self.journal_path, "w", encoding="utf-8") as f:
            for entry in self.journal:
                f.write(json.dumps(entry.to_dict()) + "\n")
        print("[LOG] Jornal salvo em arquivo.")

    def carregar_log_de_arquivo(self):
        if not os.path.exists(self.journal_path):
            print("[LOG] Arquivo de log não encontrado.")
            return
        with open(self.journal_path, "r", encoding="utf-8") as f:
            self.journal = [JournalEntry.from_dict(json.loads(line.strip())) for line in f]
        print("[LOG] Jornal carregado do arquivo.")

    def create_file(self, path, content='', user='root'):
        self._log('create', path, content, user)
        parent_dir, filename = self._navigate_to_dir(path)

        if parent_dir.find_file(filename):
            print(f"Arquivo '{filename}' já existe.")
            return

        new_file = File(filename, content)
        new_file.set_permission(user, 'rw')
        parent_dir.files.append(new_file)
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

        self._log('delete', path, file.content, user)
        parent_dir.files.remove(file)
        print(f"[{user}] Arquivo '{filename}' deletado.")

    def read_file(self, path, user='root'):
        parent_dir, filename = self._navigate_to_dir(path)
        file = parent_dir.find_file(filename)
        if not file:
            print(f"Arquivo '{filename}' não encontrado.")
            return

        perm = file.get_permission(user)
        if perm in ['r', 'rw']:
            self._log('read', path, file.content, user)
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
            self._log('write', path, new_content, user)
            file.content = new_content
            print(f"[{user}] Arquivo '{filename}' atualizado.")
        else:
            print(f"[{user}] Sem permissão para escrita.")

    def set_file_permission(self, path, user_alvo, permission, admin='root'):
        parent_dir, filename = self._navigate_to_dir(path)
        file = parent_dir.find_file(filename)
        if not file:
            print(f"Arquivo '{filename}' não encontrado.")
            return
        file.set_permission(user_alvo, permission)
        print(f"[{admin}] Permissão '{permission}' atribuída a '{user_alvo}' no arquivo '{filename}'.")

    def simulate_crash_and_recovery(self):
        print("\n[RECUPERAÇÃO APÓS FALHA]")
        self.root = Directory("root")

        for entry in self.journal:
            if entry.action == 'create':
                self._replay_create(entry)
            elif entry.action == 'delete':
                self._replay_delete(entry)
            elif entry.action == 'write':
                self._replay_write(entry)
        print("[RECUPERAÇÃO CONCLUÍDA]\n")

    def _replay_create(self, entry):
        parent_dir, filename = self._navigate_to_dir(entry.target)
        if not parent_dir.find_file(filename):
            new_file = File(filename, entry.content)
            new_file.set_permission(entry.user, 'rw')
            parent_dir.files.append(new_file)
            print(f"(Recuperado) Arquivo '{filename}' criado.")

    def _replay_delete(self, entry):
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            parent_dir.files.remove(file)
            print(f"(Recuperado) Arquivo '{filename}' deletado.")

    def _replay_write(self, entry):
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            file.content = entry.content
            print(f"(Recuperado) Arquivo '{filename}' atualizado.")
