#!/usr/bin/env python3
"""
Quick Installer — Interface gráfica simples para instalar programas no Linux.

Suporta APT (Debian/Ubuntu), DNF (Fedora), Pacman (Arch), Flatpak e Snap.
Execute com:  sudo python3 quick_installer.py
          ou: python3 quick_installer.py  (pede senha via pkexec/sudo)
"""

import os
import subprocess
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable

# ─────────────────────────── Detecção de gerenciador ────────────────────────

def detect_pkg_manager() -> str:
    """Retorna 'apt', 'dnf' ou 'pacman' conforme o sistema."""
    for mgr in ("apt", "dnf", "pacman"):
        if shutil.which(mgr):
            return mgr
    return "apt"  # fallback

PKG = detect_pkg_manager()

def _pkg_install_cmd(packages: list[str]) -> list[str]:
    """Comando de instalação nativo conforme o gerenciador."""
    if PKG == "apt":
        return ["apt", "install", "-y"] + packages
    elif PKG == "dnf":
        return ["dnf", "install", "-y"] + packages
    elif PKG == "pacman":
        return ["pacman", "-S", "--noconfirm"] + packages
    return ["apt", "install", "-y"] + packages

def _pkg_update_cmd() -> list[str]:
    if PKG == "apt":
        return ["apt", "update"]
    elif PKG == "dnf":
        return ["dnf", "check-update"]
    elif PKG == "pacman":
        return ["pacman", "-Sy"]
    return ["apt", "update"]

HAS_FLATPAK = shutil.which("flatpak") is not None
HAS_SNAP    = shutil.which("snap") is not None

# ─────────────────────── Catálogo de softwares ──────────────────────────────

CATEGORIES: dict[str, list[dict]] = {
    "🌐 Navegadores": [
        {
            "name": "Brave Origin Nightly",
            "description": "Versão nightly experimental do Brave (Origin) — pode ser instável",
            "method": "script",
            "commands": [
                ["bash", "-c",
                 "curl -fsSLo /usr/share/keyrings/brave-browser-nightly-archive-keyring.gpg "
                 "https://brave-browser-apt-nightly.s3.brave.com/brave-browser-nightly-archive-keyring.gpg"],
                ["bash", "-c",
                 "curl -fsSLo /etc/apt/sources.list.d/brave-browser-nightly.sources "
                 "https://brave-browser-apt-nightly.s3.brave.com/brave-browser.sources"],
                ["apt", "update"],
                ["apt", "install", "-y", "brave-origin-nightly"],
            ],
        },
    ],

    "💻 Desenvolvimento": [
        {
            "name": "Visual Studio Code",
            "description": "Editor de código da Microsoft",
            "method": "script",
            "commands": [
                ["bash", "-c",
                 "curl -fsSL https://packages.microsoft.com/keys/microsoft.asc "
                 "| gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg"],
                ["bash", "-c",
                 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] '
                 'https://packages.microsoft.com/repos/vscode stable main" '
                 "> /etc/apt/sources.list.d/vscode.list"],
                ["apt", "update"],
                ["apt", "install", "-y", "code"],
            ],
            "flatpak": "com.visualstudio.code",
            "snap": "code --classic",
        },
        {
            "name": "MySQL Workbench",
            "description": "Ferramenta visual para gerenciamento de bancos MySQL",
            "method": "native",
            "packages": {
                "apt": ["mysql-workbench"],
                "dnf": ["mysql-workbench-community"],
                "pacman": ["mysql-workbench"],
            },
            "snap": "mysql-workbench-community",
        },
        {
            "name": "git",
            "description": "Sistema de controle de versão distribuído (pula se já instalado)",
            "method": "native",
            "packages": ["git"],
            "skip_if_installed": "git",
        },
    ],

    "🎮 Jogos": [
        {
            "name": "Steam",
            "description": "Plataforma de jogos da Valve",
            "method": "native",
            "packages": {
                "apt": ["steam-installer"],
                "dnf": ["steam"],
                "pacman": ["steam"],
            },
            "flatpak": "com.valvesoftware.Steam",
        },
        {
            "name": "Prism Launcher",
            "description": "Launcher open-source para Minecraft Java Edition",
            "method": "flatpak_only",
            "flatpak": "org.prismlauncher.PrismLauncher",
        },
        {
            "name": "Lunar Client",
            "description": "Cliente otimizado para Minecraft com mods e cosmetics",
            "method": "flatpak_only",
            "flatpak": "com.lunarclient.LunarClient",
            "snap": "lunarclient",
        },
        {
            "name": "Bedrock on Linux",
            "description": "Roda Minecraft Bedrock Edition no Linux (github.com/Wyze3306/BedrockOnLinux)",
            "method": "script",
            "commands": [
                ["bash", "-c",
                 "apt install -y git curl jq || true"],
                ["bash", "-c",
                 # Baixa o .deb da última release do GitHub
                 'DEB_URL=$(curl -fsSL https://api.github.com/repos/Wyze3306/BedrockOnLinux/releases/latest '
                 '| jq -r \'.assets[] | select(.name | endswith(".deb")) | .browser_download_url\') '
                 '&& if [ -n "$DEB_URL" ] && [ "$DEB_URL" != "null" ]; then '
                 '  curl -fsSL -o /tmp/bedrock-on-linux.deb "$DEB_URL" '
                 '  && dpkg -i /tmp/bedrock-on-linux.deb '
                 '  && apt install -f -y '
                 '  && rm -f /tmp/bedrock-on-linux.deb; '
                 'else '
                 '  echo "Pacote .deb não encontrado na release, clonando repositório..." '
                 '  && git clone https://github.com/Wyze3306/BedrockOnLinux.git /opt/BedrockOnLinux '
                 '  && ln -sf /opt/BedrockOnLinux/bedrock-on-linux /usr/local/bin/bedrock-on-linux '
                 '  && echo "Instalado em /opt/BedrockOnLinux — execute: bedrock-on-linux"; '
                 'fi'],
            ],
        },
    ],

    "💬 Comunicação": [
        {
            "name": "Discord",
            "description": "Chat de voz, vídeo e texto para comunidades",
            "method": "flatpak_only",
            "flatpak": "com.discordapp.Discord",
            "snap": "discord",
            "deb_url": "https://discord.com/api/download?platform=linux&format=deb",
        },
        {
            "name": "Telegram Desktop",
            "description": "Cliente desktop do Telegram",
            "method": "native",
            "packages": {
                "apt": ["telegram-desktop"],
                "dnf": ["telegram-desktop"],
                "pacman": ["telegram-desktop"],
            },
            "flatpak": "org.telegram.desktop",
            "snap": "telegram-desktop",
        },
    ],

    "🔧 Ferramentas do Sistema": [
        {
            "name": "Flatpak",
            "description": "Sistema de empacotamento universal Flatpak",
            "method": "native",
            "packages": ["flatpak"],
            "post_commands": [
                ["flatpak", "remote-add", "--if-not-exists",
                 "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"],
            ],
        },
        {
            "name": "Snap (snapd)",
            "description": "Sistema de empacotamento Snap da Canonical",
            "method": "native",
            "packages": {
                "apt": ["snapd"],
                "dnf": ["snapd"],
                "pacman": ["snapd"],
            },
        },
        {
            "name": "htop",
            "description": "Monitor de processos interativo",
            "method": "native",
            "packages": ["htop"],
        },
        {
            "name": "neofetch",
            "description": "Exibe informações do sistema de forma estilizada",
            "method": "native",
            "packages": ["neofetch"],
        },
        {
            "name": "GDebi",
            "description": "Instalador gráfico de pacotes .deb",
            "method": "native",
            "packages": {
                "apt": ["gdebi"],
                "dnf": [],
                "pacman": [],
            },
        },
    ],

    "📦 Outros": [
        {
            "name": "VLC Media Player",
            "description": "Reprodutor multimídia universal",
            "method": "native",
            "packages": ["vlc"],
            "flatpak": "org.videolan.VLC",
            "snap": "vlc",
        },
        {
            "name": "OBS Studio",
            "description": "Software de gravação e streaming",
            "method": "native",
            "packages": {
                "apt": ["obs-studio"],
                "dnf": ["obs-studio"],
                "pacman": ["obs-studio"],
            },
            "flatpak": "com.obsproject.Studio",
        },
        {
            "name": "GIMP",
            "description": "Editor de imagens avançado",
            "method": "native",
            "packages": ["gimp"],
            "flatpak": "org.gimp.GIMP",
            "snap": "gimp",
        },
    ],
}

# ─────────────────────────── Lógica de instalação ───────────────────────────

def _resolve_packages(entry: dict) -> list[str]:
    """Resolve pacotes nativos considerando o gerenciador."""
    pkgs = entry.get("packages", [])
    if isinstance(pkgs, dict):
        return pkgs.get(PKG, [])
    return pkgs


def build_install_steps(entry: dict, prefer: str = "auto") -> list[list[str]]:
    """
    Retorna lista de comandos (cada um = lista de strings) para instalar
    o software descrito por *entry*.

    *prefer*: 'auto' | 'native' | 'flatpak' | 'snap'
    """
    method = entry.get("method", "native")
    steps: list[list[str]] = []

    # --- Flatpak -------------------------------------------------------
    if prefer == "flatpak" or (method == "flatpak_only" and prefer == "auto"):
        fid = entry.get("flatpak")
        if fid and HAS_FLATPAK:
            steps.append(["flatpak", "install", "-y", "flathub", fid])
            return steps

    # --- Snap ----------------------------------------------------------
    if prefer == "snap":
        snap = entry.get("snap")
        if snap and HAS_SNAP:
            parts = snap.split()
            steps.append(["snap", "install"] + parts)
            return steps

    # --- .deb direto ---------------------------------------------------
    if method == "flatpak_only" and prefer in ("auto", "native"):
        # Tenta flatpak primeiro, senão deb_url, senão snap
        fid = entry.get("flatpak")
        deb_url = entry.get("deb_url")
        snap = entry.get("snap")
        if fid and HAS_FLATPAK:
            steps.append(["flatpak", "install", "-y", "flathub", fid])
        elif deb_url:
            steps.append(["bash", "-c",
                          f'curl -fsSL -o /tmp/_quick_inst.deb "{deb_url}" '
                          f"&& dpkg -i /tmp/_quick_inst.deb "
                          f"&& apt install -f -y "
                          f"&& rm -f /tmp/_quick_inst.deb"])
        elif snap and HAS_SNAP:
            parts = snap.split()
            steps.append(["snap", "install"] + parts)
        return steps

    # --- Script (repo externo) -----------------------------------------
    if method == "script" and prefer in ("auto", "native"):
        if prefer == "auto" and PKG != "apt":
            # Para distros não-Debian, preferir flatpak se disponível
            fid = entry.get("flatpak")
            if fid and HAS_FLATPAK:
                steps.append(["flatpak", "install", "-y", "flathub", fid])
                return steps
        steps.extend(entry.get("commands", []))
        return steps

    # --- Nativo --------------------------------------------------------
    if method == "native" or prefer == "native":
        pkgs = _resolve_packages(entry)
        if pkgs:
            steps.append(_pkg_install_cmd(pkgs))
        # post_commands
        for cmd in entry.get("post_commands", []):
            steps.append(cmd)
        return steps

    return steps


# ─────────────────────────── GUI ────────────────────────────────────────────

DARK_BG       = "#1e1e2e"
DARK_SURFACE  = "#2a2a3c"
DARK_CARD     = "#313145"
DARK_FG       = "#cdd6f4"
DARK_FG_DIM   = "#7f849c"
DARK_ACCENT   = "#89b4fa"
DARK_GREEN    = "#a6e3a1"
DARK_RED      = "#f38ba8"
DARK_YELLOW   = "#f9e2af"
DARK_BORDER   = "#45475a"
LOG_BG        = "#181825"


class InstallerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("⚡ Quick Installer — Linux")
        self.geometry("900x720")
        self.minsize(750, 550)
        self.configure(bg=DARK_BG)

        # Estilo ttk
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        # Estado
        self.check_vars: dict[str, tk.BooleanVar] = {}
        self.entries_map: dict[str, dict] = {}
        self._running = False

        self._build_ui()

    # ── Estilos ──────────────────────────────────────────────────────────

    def _configure_styles(self) -> None:
        s = self.style
        s.configure(".", background=DARK_BG, foreground=DARK_FG, font=("Segoe UI", 10))
        s.configure("TFrame", background=DARK_BG)
        s.configure("Card.TFrame", background=DARK_CARD)
        s.configure("TLabel", background=DARK_BG, foreground=DARK_FG)
        s.configure("Title.TLabel", font=("Segoe UI", 18, "bold"),
                     foreground=DARK_ACCENT, background=DARK_BG)
        s.configure("Sub.TLabel", font=("Segoe UI", 9),
                     foreground=DARK_FG_DIM, background=DARK_BG)
        s.configure("Cat.TLabel", font=("Segoe UI", 13, "bold"),
                     foreground=DARK_YELLOW, background=DARK_BG)
        s.configure("TCheckbutton", background=DARK_BG, foreground=DARK_FG,
                     font=("Segoe UI", 10))
        s.map("TCheckbutton",
              background=[("active", DARK_SURFACE)],
              foreground=[("active", DARK_ACCENT)])
        s.configure("Install.TButton",
                     font=("Segoe UI", 12, "bold"),
                     foreground="#1e1e2e", background=DARK_GREEN,
                     padding=(20, 10))
        s.map("Install.TButton",
              background=[("active", "#77d590"), ("disabled", DARK_BORDER)])
        s.configure("Select.TButton",
                     font=("Segoe UI", 9),
                     foreground=DARK_FG, background=DARK_SURFACE,
                     padding=(8, 4))
        s.map("Select.TButton",
              background=[("active", DARK_CARD)])

    # ── Construção da interface ──────────────────────────────────────────

    def _build_ui(self) -> None:
        # Header
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", padx=20, pady=(18, 4))
        ttk.Label(hdr, text="⚡ Quick Installer", style="Title.TLabel").pack(side="left")
        ttk.Label(hdr, text=f"Gerenciador detectado: {PKG}  |  "
                            f"Flatpak: {'✔' if HAS_FLATPAK else '✘'}  |  "
                            f"Snap: {'✔' if HAS_SNAP else '✘'}",
                  style="Sub.TLabel").pack(side="right")

        # Botões de seleção
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill="x", padx=20, pady=(4, 2))
        ttk.Button(btn_bar, text="Selecionar tudo", style="Select.TButton",
                   command=self._select_all).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bar, text="Desmarcar tudo", style="Select.TButton",
                   command=self._deselect_all).pack(side="left")

        # Área rolável com as categorias
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=20, pady=6)

        canvas = tk.Canvas(container, bg=DARK_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-3, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(3, "units"))

        self._populate_categories()

        # Botão instalar
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=20, pady=(2, 6))
        self.install_btn = ttk.Button(
            bottom, text="⬇  Instalar Selecionados",
            style="Install.TButton", command=self._on_install)
        self.install_btn.pack(side="left")
        self.status_label = ttk.Label(bottom, text="", style="Sub.TLabel")
        self.status_label.pack(side="right")

        # Log de saída
        self.log = scrolledtext.ScrolledText(
            self, height=10, bg=LOG_BG, fg=DARK_FG,
            font=("Cascadia Mono", 9), insertbackground=DARK_FG,
            selectbackground=DARK_ACCENT, wrap="word",
            relief="flat", bd=0)
        self.log.pack(fill="x", padx=20, pady=(0, 14))
        self.log.configure(state="disabled")

        # Tags do log
        self.log.tag_configure("ok",   foreground=DARK_GREEN)
        self.log.tag_configure("err",  foreground=DARK_RED)
        self.log.tag_configure("info", foreground=DARK_ACCENT)
        self.log.tag_configure("warn", foreground=DARK_YELLOW)

    def _populate_categories(self) -> None:
        for cat_name, entries in CATEGORIES.items():
            ttk.Label(self.scroll_frame, text=cat_name,
                      style="Cat.TLabel").pack(anchor="w", pady=(12, 4), padx=4)
            for entry in entries:
                key = entry["name"]
                var = tk.BooleanVar(value=False)
                self.check_vars[key] = var
                self.entries_map[key] = entry

                row = ttk.Frame(self.scroll_frame)
                row.pack(fill="x", padx=8, pady=1)
                cb = ttk.Checkbutton(row, text=key, variable=var)
                cb.pack(side="left")
                ttk.Label(row, text=f"  — {entry['description']}",
                          style="Sub.TLabel").pack(side="left")

    # ── Ações ────────────────────────────────────────────────────────────

    def _select_all(self) -> None:
        for v in self.check_vars.values():
            v.set(True)

    def _deselect_all(self) -> None:
        for v in self.check_vars.values():
            v.set(False)

    def _log_write(self, text: str, tag: str = "") -> None:
        self.log.configure(state="normal")
        if tag:
            self.log.insert("end", text + "\n", tag)
        else:
            self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    def _on_install(self) -> None:
        if self._running:
            return
        selected = [name for name, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showinfo("Nada selecionado",
                                "Marque pelo menos um programa para instalar.")
            return

        self._running = True
        self.install_btn.state(["disabled"])
        # Limpa log
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        thread = threading.Thread(target=self._install_worker,
                                  args=(selected,), daemon=True)
        thread.start()

    def _install_worker(self, selected: list[str]) -> None:
        total = len(selected)
        ok_count = 0
        fail_count = 0

        self._log_safe(f"{'═'*60}", "info")
        self._log_safe(f"  Iniciando instalação de {total} programa(s)...", "info")
        self._log_safe(f"{'═'*60}", "info")

        # Atualizar lista de pacotes primeiro
        self._log_safe("\n📦 Atualizando lista de pacotes...", "info")
        self._run_cmd(_pkg_update_cmd())

        for i, name in enumerate(selected, 1):
            entry = self.entries_map[name]
            self._status_safe(f"[{i}/{total}] Instalando {name}...")
            self._log_safe(f"\n▸ [{i}/{total}] {name}", "info")

            # Verificar se já está instalado (skip_if_installed)
            skip_bin = entry.get("skip_if_installed")
            if skip_bin and shutil.which(skip_bin):
                self._log_safe(f"  ✔ {name} já está instalado — pulando.", "ok")
                ok_count += 1
                continue

            steps = build_install_steps(entry, prefer="auto")
            if not steps:
                self._log_safe(f"  ⚠ Sem método de instalação disponível para {name}.", "warn")
                fail_count += 1
                continue

            success = True
            for cmd in steps:
                if not self._run_cmd(cmd):
                    success = False
                    break

            if success:
                self._log_safe(f"  ✔ {name} instalado com sucesso!", "ok")
                ok_count += 1
            else:
                self._log_safe(f"  ✘ Falha ao instalar {name}.", "err")
                fail_count += 1

        self._log_safe(f"\n{'═'*60}", "info")
        summary = f"  Concluído — ✔ {ok_count} instalado(s)"
        if fail_count:
            summary += f"  |  ✘ {fail_count} falha(s)"
        self._log_safe(summary, "ok" if fail_count == 0 else "warn")
        self._log_safe(f"{'═'*60}", "info")

        self._status_safe(f"Pronto! {ok_count}✔  {fail_count}✘")
        self.after(0, lambda: self.install_btn.state(["!disabled"]))
        self._running = False

    def _run_cmd(self, cmd: list[str]) -> bool:
        """Executa comando com sudo se necessário. Retorna True em sucesso."""
        # Se não for root, prepend sudo
        if os.geteuid() != 0:
            cmd = ["sudo"] + cmd

        self._log_safe(f"  $ {' '.join(cmd)}", "")
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1)
            for line in proc.stdout:              # type: ignore[union-attr]
                stripped = line.rstrip()
                if stripped:
                    self._log_safe(f"    {stripped}", "")
            proc.wait()
            return proc.returncode == 0
        except FileNotFoundError:
            self._log_safe(f"  ✘ Comando não encontrado: {cmd[0]}", "err")
            return False
        except Exception as exc:
            self._log_safe(f"  ✘ Erro: {exc}", "err")
            return False

    # Helpers thread-safe
    def _log_safe(self, text: str, tag: str) -> None:
        self.after(0, self._log_write, text, tag)

    def _status_safe(self, text: str) -> None:
        self.after(0, self._set_status, text)


# ──────────────────────────── Ponto de entrada ──────────────────────────────

def main() -> None:
    app = InstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
