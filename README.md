# ntfs_journaling_simulator
Simulator made for final work of the subject of operating systems

# To run

1. Na primeira vez que for mexer no projeto, rode no terminal dentro da pasta:

   ```bash
   python -m venv .venv
   ```

   Isso vai criar uma pasta chamada `.venv`.

2. Para ativar o `.venv`, rode:

   - Se estiver usando o **Git Bash**:

     ```bash
     source .venv/Scripts/activate
     ```

   - Se estiver usando o **CMD**:

     ```cmd
     .venv\Scripts\activate
     ```

   Faça isso **sempre que for mexer no projeto**, para usar as bibliotecas do ambiente virtual (`.venv`).


   Se estiver usando o VSCode, configure para **usar o ambiente virtual .venv que criou**, em vez do Python instalado no sistema:

   - Pressione Ctrl + Shift + P para abrir a paleta de comandos.

   - Digite e selecione: ">Python: Select Interpreter"

   - Selecione o interpretador correspondente a .venv (algo como):
    ```
    .venv\Scripts\python.exe
    ```

3. Na primeira vez que for mexer no projeto, instale as bibliotecas necessárias no ambiente com:

   ```bash
   pip install -r requirements.txt
   ```
