""" Sistema de arquivos simulado com journaling para operações de CRUD """
class File:
    """Representa um arquivo no sistema de arquivos"""
    
    def __init__(self, name, content=''):
        """
        Inicializa um novo arquivo
        Args:
            name (str): Nome do arquivo
            content (str): Conteúdo inicial do arquivo (opcional)
        """
        
        self.name = name
        self.content = content
        self.acl = {}  # Dicionário de controle de acesso (usuário: permissão)

    def set_permission(self, user, permission):
        """
        Define permissões de acesso para um usuário
        Args:
            user (str): Nome do usuário
            permission (str): Tipo de permissão ('rw', 'r', 'w' ou 'none')
        Raises:
            ValueError: Se a permissão for inválida
        """
        
        if permission in ['rw', 'r', 'w', 'none']:
            self.acl[user] = permission
        else:
            raise ValueError("Permissão inválida. Use 'rw', 'r', 'w' ou 'none'")

    def get_permission(self, user):
        """
        Obtém a permissão de um usuário
        Args:
            user (str): Nome do usuário
        Returns:
            str: Permissão do usuário ou 'none' se não existir
        """
        
        return self.acl.get(user, 'none')


class Directory:
    """Representa um diretório no sistema de arquivos"""
    
    def __init__(self, name):
        """
        Inicializa um novo diretório
        Args:
            name (str): Nome do diretório
        """
        
        self.name = name
        self.files = []  # Lista de arquivos no diretório
        self.subdirectories = [] # Lista de subdiretórios

    def find_subdir(self, name):
        """
        Localiza um subdiretório pelo nome
        Args:
            name (str): Nome do subdiretório
        Returns:
            Directory: Objeto Directory se encontrado, None caso contrário
        """
        
        for subdir in self.subdirectories:
            if subdir.name == name:
                return subdir
        return None

    def find_file(self, name):
        """
        Localiza um arquivo pelo nome
        Args:
            name (str): Nome do arquivo
        Returns:
            File: Objeto File se encontrado, None caso contrário
        """
        
        for file in self.files:
            if file.name == name:
                return file
        return None


class JournalEntry:
    """Registro de uma operação no journal do sistema de arquivos"""

    def __init__(self, action, target, content=None, user=None):
        """
        Inicializa uma entrada no journal
        Args:
            action (str): Tipo de operação ('create', 'delete', 'write', 'append')
            target (str): Caminho do arquivo/diretório afetado
            content (str): Conteúdo envolvido na operação (opcional)
            user (str): Usuário que realizou a operação (opcional)
        """
        
        self.action = action   # Tipo de operação
        self.target = target   # Caminho do alvo  
        self.content = content # Conteúdo modificado
        self.user = user       # Usuário responsável


class FileSystem:
    """Sistema de arquivos simulado com funcionalidades básicas e journaling"""

    def __init__(self):
        """Inicializa o sistema de arquivos com diretório raiz e journal vazio"""
        self.root = Directory("root") # Diretório raiz
        self.journal = []             # Lista de operações registradas

    def _navigate_to_dir(self, path):
        """
        Navega até o diretório pai do caminho especificado
        Args:
            path (str): Caminho completo (ex: "/dir1/dir2/arquivo")
        Returns:
            tuple: (Directory: diretório pai, str: nome do item final)
        """
        
        parts = path.strip("/").split("/")
        current = self.root
        for part in parts[:-1]:  # Navega até o penúltimo item
            next_dir = current.find_subdir(part)
            if not next_dir:
                next_dir = Directory(part)  # Cria diretórios intermediários se não existirem
                current.subdirectories.append(next_dir)
            current = next_dir
        return current, parts[-1]  # Retorna diretório pai e nome do item final

    def create_file(self, path, content='', user='root'):
        """
        Cria um novo arquivo
        Args:
            path (str): Caminho completo do arquivo
            content (str): Conteúdo inicial do arquivo
            user (str): Usuário criador
        """
        
        parent_dir, filename = self._navigate_to_dir(path)
        if parent_dir.find_file(filename):
            print(f"Arquivo '{filename}' já existe.")
            return
        new_file = File(filename, content)
        new_file.set_permission(user, 'rw')  # Permissão padrão: leitura e escrita
        parent_dir.files.append(new_file)
        self.journal.append(JournalEntry('create', path, content, user))
        print(f"[{user}] Arquivo '{filename}' criado.")

    def delete_file(self, path, user='root'):
        """
        Remove um arquivo
        Args:
            path (str): Caminho do arquivo
            user (str): Usuário solicitante
        """
        
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
        """
        Lê o conteúdo de um arquivo
        Args:
            path (str): Caminho do arquivo
            user (str): Usuário solicitante
        """
        
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
        """
        Sobrescreve o conteúdo de um arquivo
        Args:
            path (str): Caminho do arquivo
            new_content (str): Novo conteúdo
            user (str): Usuário solicitante
        """
        
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
        """
        Adiciona conteúdo ao final de um arquivo
        Args:
            path (str): Caminho do arquivo
            additional_content (str): Conteúdo a ser adicionado
            user (str): Usuário solicitante
        """
        
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
        """
        Altera permissões de um arquivo (apenas para admin)
        Args:
            path (str): Caminho do arquivo
            user_alvo (str): Usuário que receberá a permissão
            permission (str): Nova permissão
            admin (str): Usuário admin que está modificando
        """
        
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
        """
        Cria um novo diretório
        Args:
            path (str): Caminho completo do novo diretório
        """
        
        parent_dir, dirname = self._navigate_to_dir(path)
        if parent_dir.find_subdir(dirname):
            print(f"Diretório '{dirname}' já existe.")
            return
        new_dir = Directory(dirname)
        parent_dir.subdirectories.append(new_dir)
        print(f"Diretório '{dirname}' criado.")

    def list_directory(self, path):
        """
        Lista o conteúdo de um diretório
        Args:
            path (str): Caminho do diretório
        """
        
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
        """
        Verifica se um diretório existe
        Args:
            path (str): Caminho do diretório
        Returns:
            bool: True se o diretório existe, False caso contrário
        """
        
        if path == "/":
            return True
        parent_dir, dirname = self._navigate_to_dir(path)
        if dirname == '':
            return True
        return parent_dir.find_subdir(dirname) is not None

    def simulate_crash_and_recovery(self):
        """Simula uma falha no sistema e recuperação usando o journal"""
                
        print("\n[RECUPERAÇÃO APÓS FALHA]")
        self.root = Directory("root")  # Recria estrutura básica
        
        # Reexecuta todas as operações do journal
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
        
    # Métodos internos para recuperação de falhas
    def _replay_create(self, entry):
        """Reexecuta operação de criação durante recuperação"""
        parent_dir, filename = self._navigate_to_dir(entry.target)
        if not parent_dir.find_file(filename):
            new_file = File(filename, entry.content)
            new_file.set_permission(entry.user, 'rw')
            parent_dir.files.append(new_file)
            print(f"(Recuperado) Arquivo '{filename}' criado.")

    def _replay_write(self, entry):
        """Reexecuta operação de escrita durante recuperação"""
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            file.content = entry.content
            print(f"(Recuperado) Arquivo '{filename}' atualizado.")

    def _replay_append(self, entry):
        """Reexecuta operação de append durante recuperação"""
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            file.content += "\n" + entry.content
            print(f"(Recuperado) Conteúdo adicionado ao arquivo '{filename}'.")

    def _replay_delete(self, entry):
        """Reexecuta operação de exclusão durante recuperação"""
        parent_dir, filename = self._navigate_to_dir(entry.target)
        file = parent_dir.find_file(filename)
        if file:
            parent_dir.files.remove(file)
            print(f"(Recuperado) Arquivo '{filename}' deletado.")
