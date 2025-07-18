from filesystem import FileSystem

fs = FileSystem()
fs.create_file("/meuarquivo.txt", "conteúdo de teste")
fs.simulate_crash_and_recovery()
