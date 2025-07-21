from filesystem import FileSystem

def interface():
    """
    Interface de linha de comando para o simulador de sistema de arquivos com journaling.
    Oferece comandos interativos para manipulação do sistema de arquivos.
    """

    # Inicializa o sistema de arquivos e variáveis de estado
    fs = FileSystem()
    current_path = "/root"  # Diretório atual
    user = "admin"          # Usuário atual

    def normalize_path(path):
        """
        Normaliza um caminho relativo para absoluto baseado no diretório atual.
        
        Args:
            path (str): Caminho a ser normalizado
            
        Returns:
            str: Caminho absoluto normalizado
        """
        
        if path.startswith("/"):
            return path
        if current_path.endswith("/"):
            return current_path + path
        return current_path + "/" + path

    print("Simulador de Sistema de Arquivos - Digite 'help' para ajuda.")

    # Loop principal da interface
    while True:
        # Prompt de comando personalizado
        cmd = input(f"{user}@simulador:{current_path}$ ").strip()
        if not cmd:
            continue

        # Processa o comando
        parts = cmd.split()
        comando = parts[0].lower()
        args = parts[1:]

        # Processa o comando
        if comando == "exit":
            print("Saindo do simulador...")
            break

        # Comando help - Mostra ajuda
        elif comando == "help":
            print("""Comandos disponíveis:
mkdir <nome_dir>         - Cria um diretório no caminho atual
cd <caminho>              - Navega para outro diretório
ls                        - Lista arquivos e pastas no diretório atual
create <nome_arquivo>    - Cria um arquivo vazio no diretório atual
read <nome_arquivo>      - Mostra o conteúdo do arquivo
write <nome_arquivo>     - Escreve ou adiciona conteúdo no arquivo
delete <nome_arquivo>    - Deleta o arquivo
chmod <arquivo> <usuario> <perm> - Ajusta permissões no arquivo
journal                  - Exibe o conteúdo do journal (log) do sistema
user <nome_usuario>      - Altera o usuário ativo na sessão
crash                    - Simula falha e recuperação do sistema
help                     - Mostra esta ajuda
exit                     - Sai do simulador
""")

        # Comando user - Altera o usuário atual
        elif comando == "user":
            if len(args) == 1:
                user = args[0]
                print(f"Usuário alterado para '{user}'")
            else:
                print("Comando inválido.")

        # Comando mkdir - Cria novo diretório
        elif comando == "mkdir":
            if len(args) == 1:
                dir_path = normalize_path(args[0])
                fs.create_directory(dir_path)
            else:
                print("Comando inválido.")

        # Comando cd - Muda diretório atual
        elif comando == "cd":
            if len(args) == 1:
                target_path = normalize_path(args[0])
                if fs.directory_exists(target_path):
                    current_path = target_path
                else:
                    print(f"Diretório '{args[0]}' não encontrado.")
            else:
                print("Comando inválido.")

        # Comando ls - Lista conteúdo do diretório
        elif comando == "ls":
            fs.list_directory(current_path)

        # Comando create - Cria novo arquivo
        elif comando == "create":
            if len(args) == 1:
                file_path = normalize_path(args[0])
                fs.create_file(file_path, content="", user=user)
            else:
                print("Comando inválido.")

        # Comando read - Lê conteúdo de arquivo
        elif comando == "read":
            if len(args) == 1:
                file_path = normalize_path(args[0])
                fs.read_file(file_path, user=user)
            else:
                print("Comando inválido.")

        # Comando write - Escreve em arquivo
        elif comando == "write":
            if len(args) == 1:
                file_path = normalize_path(args[0])
                parent_dir, filename = fs._navigate_to_dir(file_path)
                file = parent_dir.find_file(filename)

                if not file:
                    print(f"Arquivo '{filename}' não encontrado.")
                    continue

                current_content = file.content.strip()

                if current_content:
                    escolha = input("O arquivo já contém conteúdo. Deseja substituir (s) ou adicionar (a)? [s/a]: ").strip().lower()
                    if escolha == "s":
                        novo_conteudo = input("Novo conteúdo (será substituído): ")
                        fs.write_file(file_path, novo_conteudo, user=user)
                    elif escolha == "a":
                        conteudo_adicional = input("Conteúdo a ser adicionado: ")
                        fs.append_to_file(file_path, conteudo_adicional, user=user)
                    else:
                        print("Opção inválida. Use 's' para substituir ou 'a' para adicionar.")
                else:
                    novo_conteudo = input("Arquivo vazio. Digite o conteúdo: ")
                    fs.write_file(file_path, novo_conteudo, user=user)
            else:
                print("Comando inválido.")

        # Comando delete - Remove arquivo
        elif comando == "delete":
            if len(args) == 1:
                file_path = normalize_path(args[0])
                fs.delete_file(file_path, user=user)
            else:
                print("Comando inválido.")

        # Comando chmod - Altera permissões
        elif comando == "chmod":
            if len(args) == 3:
                file_path = normalize_path(args[0])
                fs.set_file_permission(file_path, args[1], args[2], admin=user)
            else:
                print("Comando inválido.")

        # Comando journal - Mostra log de operações
        elif comando == "journal":
            if not fs.journal:
                print("O journal está vazio.")
            else:
                print("Conteúdo do journal:")
                for i, entry in enumerate(fs.journal, 1):
                    content_preview = entry.content
                    if content_preview is not None and len(str(content_preview)) > 20:
                        content_preview = str(content_preview)[:20] + "..."
                    print(f"{i}. Ação: {entry.action}, Arquivo: {entry.target}, Usuário: {entry.user}, Conteúdo: {content_preview}")

        # Comando crash - Simula falha e recuperação
        elif comando == "crash":
            try:
                fs.simulate_crash_and_recovery()
                print("💥 Falha simulada com sucesso!")
                print("🔁 Sistema recuperado automaticamente com base no journal.")
            except Exception as e:
                print(f"Erro na simulação de falha: {str(e)}")
        
        # Comando desconhecido
        else:
            print(f"Comando desconhecido: {comando}. Digite 'help' para ajuda.")

if __name__ == "__main__":
    interface()
