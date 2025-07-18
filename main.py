from filesystem import FileSystem

def main():
    fs = FileSystem()

    # Usuários
    admin = "admin"
    joao = "joao"
    maria = "maria"

    # Admin cria arquivos
    fs.create_file("/root/projetos/projeto1.txt", "documentação inicial", user=admin)
    fs.create_file("/root/projetos/projeto2.txt", "progresso", user=admin)

    # Admin define permissões
    fs.set_file_permission("/root/projetos/projeto1.txt", joao, "rw")
    fs.set_file_permission("/root/projetos/projeto2.txt", maria, "r")

    # João tenta ler e escrever
    fs.read_file("/root/projetos/projeto1.txt", user=joao)
    fs.write_file("/root/projetos/projeto1.txt", "documentação atualizada", user=joao)

    # Maria tenta ler e escrever
    fs.read_file("/root/projetos/projeto2.txt", user=maria)
    fs.write_file("/root/projetos/projeto2.txt", "tentativa de edição", user=maria)

    # João tenta deletar sem permissão
    fs.delete_file("/root/projetos/projeto2.txt", user=joao)

    # Admin remove arquivo
    fs.delete_file("/root/projetos/projeto2.txt", user=admin)

    # Simula falha e recuperação
    print("\n*** SIMULANDO FALHA ***")
    fs.simulate_crash_and_recovery()

    # Verifica leitura após recuperação
    fs.read_file("/root/projetos/projeto1.txt", user=joao)
    fs.read_file("/root/projetos/projeto2.txt", user=maria)

if __name__ == "__main__":
    main()
