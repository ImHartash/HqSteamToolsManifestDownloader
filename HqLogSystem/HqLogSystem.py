import keyboard, sys

from os import system, name
from colorama import Fore, Style

LOG_ENABLED = True

MenuActionsButtons = {
    1: "Add game for SteamTools",
    2: "Add game list file",
    9: "Exit"
}

class HqLogSystem:
    def PrintBanner(self) -> None:
        print(f'''{Fore.LIGHTCYAN_EX}
██╗░░██╗░██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗░██████╗
██║░░██║██╔═══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝██╔════╝
███████║██║██╗██║███████║███████║██║░░╚═╝█████═╝░╚█████╗░
██╔══██║╚██████╔╝██╔══██║██╔══██║██║░░██╗██╔═██╗░░╚═══██╗
██║░░██║░╚═██╔═╝░██║░░██║██║░░██║╚█████╔╝██║░╚██╗██████╔╝
╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚═════╝░
              {Style.RESET_ALL}''')
        print("GitHub repo - https://github.com/ImHartash/HqSteamToolsManifestDownloader")
        print("Also join to our discord server - https://discord.gg/bH9w3UmgYe")
        print("Made by HqHacks, with love!\n")
    
    def Menu(self) -> str:
        for key, value in MenuActionsButtons.items():
            print(f"[{Fore.LIGHTCYAN_EX}{key}{Style.RESET_ALL}] - {value}")
        
        print()
        
        user_choice: str = ""
        while user_choice == "" or not user_choice.isdigit() or not int(user_choice) in MenuActionsButtons.keys():
            user_choice = self.GetString("Choose your action")
        
        return user_choice
    
    def Info(self, message: str) -> None:
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}") if LOG_ENABLED else ...
    
    def Error(self, message: str) -> None:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}") if LOG_ENABLED else ...
    
    def Warn(self, message: str) -> None:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {message}") if LOG_ENABLED else ...
        
    def Success(self, message: str) -> None:
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}") if LOG_ENABLED else ... 
        
    def GetString(self, message: str = "") -> str:
        return input(f"{Fore.LIGHTMAGENTA_EX}[IN]{Style.RESET_ALL} {message}: ")
    
    def Close(self) -> None:
        print(f"{Fore.LIGHTCYAN_EX}[OUT]{Style.RESET_ALL} Press space or enter to exit...")
        while True:
            if keyboard.read_key() in ['space', 'enter']:
                sys.exit(1)
                
    def PauseConsole(self) -> None:
        LOG_SYSTEM.Info("Press space or enter to continue...")
        while True:
            if keyboard.read_key() in ['space', 'enter']:
                break
    
    def ClearConsole(self) -> None:
        LOG_SYSTEM.PauseConsole()
        system("clear" if name == "posix" else "cls")
 
LOG_SYSTEM = HqLogSystem()