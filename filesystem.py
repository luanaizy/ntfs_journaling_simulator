class File:
    def __init__(self, name, content=''):
        self.name = name
        self.content = content

class Directory:
    def __init__(self, name):
        self.name = name
        self.files = []
        self.subdirectories = []

class JournalEntry:
    def __init__(self, action, target):
        self.action = action  # 'create', 'delete', 'write'
        self.target = target  # nome do arquivo ou diretório

class FileSystem:
    def __init__(self):
        self.root = Directory("root")
        self.journal = []

    def create_file(self, path, content=''):
        # adiciona entry ao journal e cria arquivo
        pass

    def delete_file(self, path):
        # adiciona entry ao journal e remove arquivo
        pass

    def simulate_crash_and_recovery(self):
        # simula recuperação baseada no journal
        pass
