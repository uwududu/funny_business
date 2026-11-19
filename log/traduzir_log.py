import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Mapeamento de Virtual Keys (VK codes comuns no Windows)
VK_MAP = {
    # Modificadores
    160: "[LSHIFT]",      # VK_LSHIFT
    161: "[RSHIFT]",      # VK_RSHIFT
    162: "[LCTRL]",       # VK_LCONTROL
    163: "[RCTRL]",       # VK_RCONTROL
    164: "[LALT]",        # VK_LMENU
    165: "[RALT]",        # VK_RMENU
    # Teclado Numérico (Numpad)
    96: "0",              # VK_NUMPAD0
    97: "1",              # VK_NUMPAD1
    98: "2",              # VK_NUMPAD2
    99: "3",              # VK_NUMPAD3
    100: "4",             # VK_NUMPAD4
    101: "5",             # VK_NUMPAD5
    102: "6",             # VK_NUMPAD6
    103: "7",             # VK_NUMPAD7
    104: "8",             # VK_NUMPAD8
    105: "9",             # VK_NUMPAD9
    106: "*",             # VK_MULTIPLY
    107: "+",             # VK_ADD
    108: "[SEPARATOR]",   # VK_SEPARATOR
    109: "-",             # VK_SUBTRACT
    110: ".",             # VK_DECIMAL
    111: "/",             # VK_DIVIDE
    # Teclas de Controle
    8: "[BACKSPACE]",     # VK_BACK
    9: "\t",              # VK_TAB
    13: "\n",             # VK_RETURN
    20: "[CAPSLOCK]",     # VK_CAPITAL
    27: "[ESC]",          # VK_ESCAPE
    32: " ",              # VK_SPACE
    33: "[PAGEUP]",       # VK_PRIOR
    34: "[PAGEDOWN]",     # VK_NEXT
    35: "[END]",          # VK_END
    36: "[HOME]",         # VK_HOME
    37: "[LEFT]",         # VK_LEFT
    38: "[UP]",           # VK_UP
    39: "[RIGHT]",        # VK_RIGHT
    40: "[DOWN]",         # VK_DOWN
    45: "[INSERT]",       # VK_INSERT
    46: "[DELETE]",       # VK_DELETE
    # Pontuação e Teclas ABNT2 comuns
    186: "ç",             # VK_OEM_1 (no ABNT2 geralmente é 'ç')
    187: "=",             # VK_OEM_PLUS
    188: ",",             # VK_OEM_COMMA
    189: "-",             # VK_OEM_MINUS
    190: ".",             # VK_OEM_PERIOD
    191: ";",             # VK_OEM_2
    192: "'",             # VK_OEM_3
    193: "/",             # VK_ABNT_C1 (barra / interrogação no ABNT2)
    194: ".",             # VK_ABNT_C2 (ponto no numpad ABNT2)
    219: "´",             # VK_OEM_4
    220: "]",             # VK_OEM_5
    221: "[",             # VK_OEM_6
    222: "~",             # VK_OEM_7
}

SPECIAL_KEYS = {
    "key.space": " ",
    "key.enter": "\n",
    "key.tab": "\t",
    "key.backspace": "[BACKSPACE]",
    "key.delete": "[DELETE]",
    "key.caps_lock": "[CAPSLOCK]",
    "key.shift": "[SHIFT]",
    "key.shift_l": "[LSHIFT]",
    "key.shift_r": "[RSHIFT]",
    "key.ctrl": "[CTRL]",
    "key.ctrl_l": "[LCTRL]",
    "key.ctrl_r": "[RCTRL]",
    "key.alt": "[ALT]",
    "key.alt_l": "[LALT]",
    "key.alt_r": "[RALT]",
    "key.alt_gr": "[ALTGR]",
    "key.cmd": "[CMD]",
    "key.cmd_l": "[CMD]",
    "key.cmd_r": "[CMD]",
    "key.esc": "[ESC]",
    "key.up": "[UP]",
    "key.down": "[DOWN]",
    "key.left": "[LEFT]",
    "key.right": "[RIGHT]",
    "key.home": "[HOME]",
    "key.end": "[END]",
    "key.page_up": "[PAGEUP]",
    "key.page_down": "[PAGEDOWN]",
    "key.insert": "[INSERT]",
}

CAMINHO_DUMP_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dump_completo_banco.sql")


# ==========================================================
# FUNÇÕES DE BANCO DE DADOS MYSQL
# ==========================================================
def obter_conexao_mysql(config: dict):
    """Tenta conectar ao MySQL usando mysql.connector ou pymysql."""
    # Tentativa 1: mysql.connector
    try:
        import mysql.connector
        return mysql.connector.connect(
            host=config.get("host", "localhost"),
            port=int(config.get("port", 3306)),
            user=config.get("user", "root"),
            password=config.get("password", ""),
            database=config.get("database", "db_logs_teclado")
        )
    except ModuleNotFoundError:
        pass
    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ao MySQL (mysql.connector): {e}")

    # Tentativa 2: pymysql
    try:
        import pymysql
        return pymysql.connect(
            host=config.get("host", "localhost"),
            port=int(config.get("port", 3306)),
            user=config.get("user", "root"),
            password=config.get("password", ""),
            database=config.get("database", "db_logs_teclado")
        )
    except ModuleNotFoundError:
        pass
    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ao MySQL (pymysql): {e}")

    raise ModuleNotFoundError(
        "Nenhum conector MySQL encontrado no Python.\n\n"
        "Instale executando o comando no terminal:\n"
        "pip install mysql-connector-python"
    )


def inicializar_tabela_mysql(config: dict):
    """Cria o banco e a tabela no MySQL se não existirem."""
    config_sem_banco = config.copy()
    banco_alvo = config_sem_banco.pop("database", "db_logs_teclado")

    conn_root = None
    try:
        import mysql.connector
        conn_root = mysql.connector.connect(
            host=config_sem_banco.get("host", "localhost"),
            port=int(config_sem_banco.get("port", 3306)),
            user=config_sem_banco.get("user", "root"),
            password=config_sem_banco.get("password", "")
        )
    except Exception:
        try:
            import pymysql
            conn_root = pymysql.connect(
                host=config_sem_banco.get("host", "localhost"),
                port=int(config_sem_banco.get("port", 3306)),
                user=config_sem_banco.get("user", "root"),
                password=config_sem_banco.get("password", "")
            )
        except Exception:
            pass

    if conn_root:
        try:
            cursor = conn_root.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{banco_alvo}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{banco_alvo}`;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs_traduzidos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome_arquivo VARCHAR(255) NOT NULL,
                    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    modo VARCHAR(50) NOT NULL,
                    conteudo_traduzido LONGTEXT NOT NULL,
                    conteudo_bruto LONGTEXT,
                    INDEX idx_nome_arquivo (nome_arquivo),
                    INDEX idx_data_registro (data_registro)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn_root.commit()
        finally:
            conn_root.close()


def escapar_valor_sql(valor) -> str:
    """Escapa valores para inserção segura em sintaxe MySQL."""
    if valor is None:
        return "NULL"
    if isinstance(valor, (int, float)):
        return str(valor)
    texto = str(valor)
    texto = texto.replace("\\", "\\\\").replace("'", "\\'").replace("\r", "\\r").replace("\n", "\\n")
    return f"'{texto}'"


def exportar_dump_mysql(config: dict, caminho_saida: str = CAMINHO_DUMP_PADRAO) -> int:
    """
    Gera o dump completo em formato .sql contendo CREATE DATABASE,
    CREATE TABLE e todos os comandos INSERT dos dados já gravados.
    Retorna a quantidade de registros exportados.
    """
    conn = obter_conexao_mysql(config)
    cursor = conn.cursor()

    try:
        nome_banco = config.get("database", "db_logs_teclado")
        tabela = "logs_traduzidos"

        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write("-- ============================================================\n")
            f.write(f"-- DUMP MYSQL: BANCO `{nome_banco}`\n")
            f.write("-- ESTRUTURA E DADOS GERADOS AUTOMATICAMENTE\n")
            f.write("-- ============================================================\n\n")

            f.write(f"CREATE DATABASE IF NOT EXISTS `{nome_banco}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n")
            f.write(f"USE `{nome_banco}`;\n\n")

            cursor.execute(f"SHOW CREATE TABLE `{tabela}`;")
            resultado_tabela = cursor.fetchone()
            if resultado_tabela:
                create_table_sql = resultado_tabela[1]
                f.write(f"DROP TABLE IF EXISTS `{tabela}`;\n")
                f.write(f"{create_table_sql};\n\n")

            cursor.execute(f"SELECT id, nome_arquivo, data_registro, modo, conteudo_traduzido, conteudo_bruto FROM `{tabela}` ORDER BY id ASC;")
            linhas = cursor.fetchall()

            if linhas:
                f.write(f"-- Dados da tabela `{tabela}`\n")
                f.write(f"LOCK TABLES `{tabela}` WRITE;\n")
                for linha in linhas:
                    valores = [escapar_valor_sql(v) for v in linha]
                    valores_str = ", ".join(valores)
                    f.write(f"INSERT INTO `{tabela}` (id, nome_arquivo, data_registro, modo, conteudo_traduzido, conteudo_bruto) VALUES ({valores_str});\n")
                f.write("UNLOCK TABLES;\n\n")
            else:
                f.write(f"-- (Tabela `{tabela}` não possui registros no momento)\n\n")

            return len(linhas)
    finally:
        cursor.close()
        conn.close()


# ==========================================================
# PARSER E TRADUTOR DO LOG
# ==========================================================
def parse_line(line: str) -> str:
    """Traduz uma linha bruta do arquivo para seu caractere ou tag correspondente."""
    line = line.strip("\r\n").strip()
    if not line:
        return ""

    if (line.startswith("'") and line.endswith("'")) or (line.startswith('"') and line.endswith('"')):
        content = line[1:-1]
        if content == "\\'":
            return "'"
        elif content == '\\"':
            return '"'
        elif content == "\\\\":
            return "\\"
        elif content == "\\n":
            return "\n"
        elif content == "\\t":
            return "\t"
        elif content == "\\r":
            return ""
        return content

    line_lower = line.lower()

    vk_match = re.search(r"(?:key\.)?(?:vk[_\s]*)?<?(\d+)>?", line_lower)
    if ("vk" in line_lower or line.startswith("<")) and vk_match:
        vk_code = int(vk_match.group(1))
        if vk_code in VK_MAP:
            return VK_MAP[vk_code]
        if 32 <= vk_code <= 126:
            return chr(vk_code)
        return f"[VK_{vk_code}]"

    if line_lower in SPECIAL_KEYS:
        return SPECIAL_KEYS[line_lower]

    if line_lower.startswith("key."):
        return f"[{line[4:].upper()}]"

    return line


def traduzir_log(caminho_arquivo: str, modo: str = "reconstruido") -> str:
    """
    Lê e traduz o arquivo de log.
    Modos: 'reconstruido', 'bruto', 'ambos'
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo '{caminho_arquivo}' não encontrado.")

    tokens = []
    with open(caminho_arquivo, "r", encoding="utf-8", errors="replace") as f:
        for linha in f:
            t = parse_line(linha)
            if t != "":
                tokens.append(t)

    if modo == "bruto":
        return "".join(tokens)

    resultado = []
    shift_ativo = False
    caps_ativo = False

    for token in tokens:
        if token in ("[SHIFT]", "[LSHIFT]", "[RSHIFT]"):
            shift_ativo = True
            continue
        elif token == "[CAPSLOCK]":
            caps_ativo = not caps_ativo
            continue
        elif token == "[BACKSPACE]":
            if resultado:
                resultado.pop()
            continue
        elif token.startswith("[") and token.endswith("]"):
            continue

        char = token
        if len(char) == 1 and char.isalpha():
            maiuscula = shift_ativo ^ caps_ativo
            char = char.upper() if maiuscula else char.lower()

        resultado.append(char)
        shift_ativo = False

    texto_reconstruido = "".join(resultado)

    if modo == "ambos":
        texto_bruto = "".join(tokens)
        return (
            "=== TEXTO DIGITADO (RECONSTRUÍDO) ===\n\n"
            + texto_reconstruido
            + "\n\n=== TEXTO COM TECLAS ESPECIAIS (BRUTO) ===\n\n"
            + texto_bruto
        )

    return texto_reconstruido


# ==========================================================
# JANELA DE CONFIGURAÇÃO DO MYSQL
# ==========================================================
class JanelaConfigMySQL(tk.Toplevel):
    def __init__(self, parent, config_atual, callback_salvar):
        super().__init__(parent)
        self.title("Configurações do MySQL")
        self.geometry("380x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.config_atual = config_atual
        self.callback_salvar = callback_salvar

        frame = ttk.Frame(self, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        campos = [
            ("Host:", "host", config_atual.get("host", "localhost")),
            ("Porta:", "port", str(config_atual.get("port", 3306))),
            ("Usuário:", "user", config_atual.get("user", "root")),
            ("Senha:", "password", config_atual.get("password", "")),
            ("Banco de Dados:", "database", config_atual.get("database", "db_logs_teclado")),
        ]

        self.entradas = {}
        for idx, (label_txt, chave, valor_padrao) in enumerate(campos):
            ttk.Label(frame, text=label_txt, font=("Comic Sans MS", 9)).grid(row=idx, column=0, sticky="w", pady=4)
            entry = ttk.Entry(frame, font=("Comic Sans MS", 9), show="*" if chave == "password" else "")
            entry.insert(0, valor_padrao)
            entry.grid(row=idx, column=1, sticky="ew", pady=4, padx=(8, 0))
            self.entradas[chave] = entry

        frame.columnconfigure(1, weight=1)

        btn_salvar = ttk.Button(frame, text="Salvar Configuração", command=self._salvar)
        btn_salvar.grid(row=len(campos), column=0, columnspan=2, pady=(15, 0))

    def _salvar(self):
        nova_config = {
            "host": self.entradas["host"].get().strip(),
            "port": int(self.entradas["port"].get().strip() or 3306),
            "user": self.entradas["user"].get().strip(),
            "password": self.entradas["password"].get(),
            "database": self.entradas["database"].get().strip(),
        }
        self.callback_salvar(nova_config)
        self.destroy()


# ==========================================================
# INTERFACE GRÁFICA PRINCIPAL
# ==========================================================
class AppTradutor(tk.Tk):
    def __init__(self, arquivo_inicial: str = ""):
        super().__init__()
        self.title("Tradutor de Logs de Teclado (.txt)")
        self.geometry("820x620")
        self.minsize(700, 500)

        self.mysql_config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "db_logs_teclado"
        }

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self._criar_widgets(arquivo_inicial)

    def _criar_widgets(self, arquivo_inicial: str):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(
            main_frame,
            text="Tradutor de Teclas / Logs (.txt)",
            font=("Comic Sans MS", 14, "bold")
        )
        titulo.pack(anchor="w", pady=(0, 5))

        descricao = ttk.Label(
            main_frame,
            text="Anexe o arquivo .txt para traduzir caracteres por linha e códigos como key.vk_160.",
            font=("Comic Sans MS", 9)
        )
        descricao.pack(anchor="w", pady=(0, 15))

        # Seção do Arquivo de Entrada
        frame_arquivo = ttk.LabelFrame(main_frame, text=" Arquivo de Entrada ", padding="10")
        frame_arquivo.pack(fill=tk.X, pady=(0, 12))

        self.var_caminho = tk.StringVar(value=arquivo_inicial)
        entry_caminho = ttk.Entry(frame_arquivo, textvariable=self.var_caminho, font=("Comic Sans MS", 9))
        entry_caminho.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        btn_procurar = ttk.Button(frame_arquivo, text="Anexar Arquivo...", command=self._procurar_arquivo)
        btn_procurar.pack(side=tk.RIGHT)

        # Seção de Modos
        frame_opcoes = ttk.LabelFrame(main_frame, text=" Modo de Conversão ", padding="10")
        frame_opcoes.pack(fill=tk.X, pady=(0, 12))

        self.var_modo = tk.StringVar(value="reconstruido")

        rb1 = ttk.Radiobutton(
            frame_opcoes,
            text="Texto Reconstruído (Aplica Shift, apaga com Backspace e gera o texto final)",
            variable=self.var_modo,
            value="reconstruido",
            command=self._atualizar_previa_se_carregado
        )
        rb1.pack(anchor="w", pady=2)

        rb2 = ttk.Radiobutton(
            frame_opcoes,
            text="Texto Bruto (Mostra cada tecla e tags literais: [SHIFT], [BACKSPACE], etc.)",
            variable=self.var_modo,
            value="bruto",
            command=self._atualizar_previa_se_carregado
        )
        rb2.pack(anchor="w", pady=2)

        rb3 = ttk.Radiobutton(
            frame_opcoes,
            text="Ambos (Salva tanto a versão reconstruída quanto a versão com tags)",
            variable=self.var_modo,
            value="ambos",
            command=self._atualizar_previa_se_carregado
        )
        rb3.pack(anchor="w", pady=2)

        # Barra de Ações / Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=(0, 12))

        self.btn_salvar_txt = ttk.Button(
            frame_botoes,
            text="💾 Salvar em .txt",
            command=self._traduzir_e_salvar
        )
        self.btn_salvar_txt.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_salvar_banco = ttk.Button(
            frame_botoes,
            text="🗄️ Salvar no MySQL",
            command=self._salvar_no_banco
        )
        self.btn_salvar_banco.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_dump = ttk.Button(
            frame_botoes,
            text="📦 Exportar Dump .sql",
            command=self._exportar_dump_gui
        )
        self.btn_dump.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_config_mysql = ttk.Button(
            frame_botoes,
            text="⚙️ Conexão MySQL",
            command=self._abrir_config_mysql
        )
        self.btn_config_mysql.pack(side=tk.LEFT, padx=(0, 6))

        btn_copiar = ttk.Button(
            frame_botoes,
            text="📋 Copiar",
            command=self._copiar_texto
        )
        btn_copiar.pack(side=tk.LEFT)

        # Pré-visualização
        frame_previa = ttk.LabelFrame(main_frame, text=" Pré-visualização do Conteúdo Traduzido ", padding="8")
        frame_previa.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(frame_previa, orient=tk.VERTICAL)
        self.txt_previa = tk.Text(
            frame_previa,
            wrap=tk.WORD,
            yscrollcommand=scroll_y.set,
            font=("Comic Sans MS", 10),
            bg="#fdfdfd"
        )
        scroll_y.config(command=self.txt_previa.yview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_previa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if arquivo_inicial:
            self._gerar_previa()

    def _abrir_config_mysql(self):
        def atualizar(nova_config):
            self.mysql_config = nova_config
            messagebox.showinfo("Configuração", "Configurações do MySQL atualizadas com sucesso!")

        JanelaConfigMySQL(self, self.mysql_config, atualizar)

    def _procurar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo de log .txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            self.var_caminho.set(caminho)
            self._gerar_previa()

    def _obter_texto_traduzido(self) -> str:
        caminho = self.var_caminho.get().strip()
        if not caminho:
            raise ValueError("Por favor, selecione um arquivo de texto primeiro.")
        return traduzir_log(caminho, modo=self.var_modo.get())

    def _gerar_previa(self):
        try:
            texto = self._obter_texto_traduzido()
            self.txt_previa.delete("1.0", tk.END)
            self.txt_previa.insert(tk.END, texto)
        except Exception as e:
            self.txt_previa.delete("1.0", tk.END)
            self.txt_previa.insert(tk.END, f"[Aviso] {e}")

    def _atualizar_previa_se_carregado(self):
        if self.var_caminho.get().strip():
            self._gerar_previa()

    def _traduzir_e_salvar(self):
        caminho_origem = self.var_caminho.get().strip()
        if not caminho_origem:
            messagebox.showwarning("Atenção", "Por favor, anexe um arquivo .txt de entrada antes de salvar.")
            return

        try:
            texto_traduzido = self._obter_texto_traduzido()

            pasta_origem = os.path.dirname(caminho_origem) or "."
            nome_base, _ = os.path.splitext(os.path.basename(caminho_origem))
            nome_sugerido = f"{nome_base}_traduzido.txt"

            caminho_destino = filedialog.asksaveasfilename(
                title="Salvar Arquivo Traduzido",
                initialdir=pasta_origem,
                initialfile=nome_sugerido,
                defaultextension=".txt",
                filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
            )

            if not caminho_destino:
                return

            with open(caminho_destino, "w", encoding="utf-8") as f:
                f.write(texto_traduzido)

            self.txt_previa.delete("1.0", tk.END)
            self.txt_previa.insert(tk.END, texto_traduzido)

            messagebox.showinfo(
                "Sucesso",
                f"Arquivo traduzido criado com sucesso!\n\nSalvo em:\n{caminho_destino}"
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao traduzir/salvar o arquivo:\n{e}")

    def _salvar_no_banco(self):
        caminho_origem = self.var_caminho.get().strip()
        if not caminho_origem:
            messagebox.showwarning("Atenção", "Por favor, anexe um arquivo .txt de entrada antes de salvar no MySQL.")
            return

        try:
            inicializar_tabela_mysql(self.mysql_config)

            conn = obter_conexao_mysql(self.mysql_config)
            try:
                nome_arquivo = os.path.basename(caminho_origem)
                modo = self.var_modo.get()
                texto_traduzido = traduzir_log(caminho_origem, modo=modo)
                texto_bruto = traduzir_log(caminho_origem, modo="bruto")

                cursor = conn.cursor()
                sql = """
                    INSERT INTO logs_traduzidos (nome_arquivo, modo, conteudo_traduzido, conteudo_bruto)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (nome_arquivo, modo, texto_traduzido, texto_bruto))
                novo_id = cursor.lastrowid
                conn.commit()

                messagebox.showinfo(
                    "Sucesso",
                    f"Registro gravado no MySQL com sucesso!\n\n"
                    f"• ID: {novo_id}\n"
                    f"• Arquivo: {nome_arquivo}\n"
                    f"• Modo: {modo}\n"
                    f"• Banco: {self.mysql_config.get('database')}"
                )
            finally:
                conn.close()

        except ModuleNotFoundError as e:
            messagebox.showerror("Conector MySQL Não Encontrado", str(e))
        except Exception as e:
            messagebox.showerror("Erro no MySQL", f"Não foi possível salvar no MySQL:\n{e}")

    def _exportar_dump_gui(self):
        """Exporta o dump SQL completo do MySQL com interface gráfica."""
        caminho_destino = filedialog.asksaveasfilename(
            title="Salvar Dump Completo do MySQL (.sql)",
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            initialfile="dump_completo_banco.sql",
            defaultextension=".sql",
            filetypes=[("Arquivos SQL", "*.sql"), ("Todos os Arquivos", "*.*")]
        )
        if not caminho_destino:
            return

        try:
            total_linhas = exportar_dump_mysql(self.mysql_config, caminho_destino)
            messagebox.showinfo(
                "Dump Concluído",
                f"Dump do MySQL exportado com sucesso!\n\n"
                f"• Registros exportados: {total_linhas}\n"
                f"• Arquivo: {caminho_destino}"
            )
        except ModuleNotFoundError as e:
            messagebox.showerror("Conector MySQL Não Encontrado", str(e))
        except Exception as e:
            messagebox.showerror("Erro ao Gerar Dump", f"Não foi possível exportar o dump:\n{e}")

    def _copiar_texto(self):
        conteudo = self.txt_previa.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showinfo("Aviso", "Não há conteúdo na pré-visualização para copiar.")
            return

        self.clipboard_clear()
        self.clipboard_append(conteudo)
        messagebox.showinfo("Copiado", "Conteúdo copiado para a área de transferência!")


def main():
    # Suporte a CLI para gerar dump diretamente pelo terminal: python traduzir_log.py --dump [caminho.sql]
    if len(sys.argv) > 1 and sys.argv[1] in ("--dump", "-d"):
        caminho_saida = sys.argv[2] if len(sys.argv) > 2 else CAMINHO_DUMP_PADRAO
        config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "db_logs_teclado"
        }
        try:
            print("Exportando dump MySQL...")
            total = exportar_dump_mysql(config, caminho_saida)
            print(f"Sucesso! {total} registros exportados para: {caminho_saida}")
        except Exception as e:
            print(f"Erro: {e}")
        return

    arquivo_inicial = ""
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        arquivo_inicial = sys.argv[1]

    app = AppTradutor(arquivo_inicial=arquivo_inicial)
    app.mainloop()


if __name__ == "__main__":
    main()
