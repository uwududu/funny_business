import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ==============================================================================
# VERSÃO 1.0 - TRADUTOR DE LOGS COM INTERFACE GRÁFICA TKINTER
# Esta versão contém a funcionalidade inicial de tradução e exportação para .txt,
# antes da integração com banco de dados MySQL e rotinas de dump.
# ==============================================================================

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
# INTERFACE GRÁFICA (TKINTER) - VERSÃO 1.0
# ==========================================================
class AppTradutor(tk.Tk):
    def __init__(self, arquivo_inicial: str = ""):
        super().__init__()
        self.title("Tradutor de Logs de Teclado (.txt) - v1.0")
        self.geometry("700x560")
        self.minsize(600, 450)

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

        # Botão Principal de Ação
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=(0, 12))

        self.btn_salvar = ttk.Button(
            frame_botoes,
            text="💾 Traduzir e Salvar em Novo .txt",
            command=self._traduzir_e_salvar
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=(0, 8))

        btn_copiar = ttk.Button(
            frame_botoes,
            text="📋 Copiar Pré-visualização",
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

    def _copiar_texto(self):
        conteudo = self.txt_previa.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showinfo("Aviso", "Não há conteúdo na pré-visualização para copiar.")
            return

        self.clipboard_clear()
        self.clipboard_append(conteudo)
        messagebox.showinfo("Copiado", "Conteúdo copiado para a área de transferência!")


def main():
    arquivo_inicial = ""
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        arquivo_inicial = sys.argv[1]

    app = AppTradutor(arquivo_inicial=arquivo_inicial)
    app.mainloop()


if __name__ == "__main__":
    main()
