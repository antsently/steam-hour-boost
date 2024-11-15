from steam.client import SteamClient
from stdiomask import getpass
from os import system
from time import sleep

import sys
import requests as req
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg

ascii_art = """
   ____________________    __  ___                          
  / ___/_  __/ ____/   |  /  |/  /                          
  \__ \ / / / __/ / /| | / /|_/ /                           
 ___/ // / / /___/ ___ |/ /  / /                            
/____//_/_/_____/_/ _|_/_/  /_/
    __  __ ____  __  __ __     ____  ____  ____  ___________
   / / / / __ \/ / / / __ \   / __ )/ __ \/ __ \/ ___/_  __/
  / /_/ / / / / / / / /_/ /  / __  / / / / / / /\__ \ / /   
 / __  / /_/ / /_/ / _, _/  / /_/ / /_/ / /_/ /___/ // /    
/_/ /_/\____/\____/_/ |_|  /_____/\____/\____//____//_/   

github.com/flooowd

"""

client = SteamClient()

def login():
    print(ascii_art)
    user,passw = str(input('[STB] Username: ')), getpass("[STB] Password: ")
    account_login = client.login(username=user, password=passw)
    if str(account_login) == "EResult.AccountLoginDeniedNeedTwoFactor":
        system('cls')
        login_with_steam_guard(user, passw)
        main(user, passw)
    elif str(account_login) == "EResult.AccountLogonDenied":
        system('cls')
        login_with_email_auth_code(user, passw)
        main(user, passw)
    elif str(account_login) == "EResult.InvalidPassword":
        system('cls')
        print('[ERROR] Invalid Login or Password.')
        login()
    elif str(account_login) == "EResult.OK":
        main(user, passw)
    else:
        print("[ERROR]: " + str(account_login))
        system('pause')
        sys.exit()

def validate_steam_guard_code(prompt):
    while True:
        code = input(prompt).strip().upper() 
        if len(code) == 5 and code.isalnum():  
            return code
        else:
            print("[ERROR] Invalid code. Please enter a valid 5-character alphanumeric Steam Guard code.")

def login_with_email_auth_code(username, password):
    print(ascii_art)
    code = str(input('[STB] Steam Guard Code (sended to your email): '))
    account_login = client.login(username=username, password=password, auth_code=code)
    if str(account_login) == "EResult.InvalidPassword":
        system('cls')
        print('[STB] Wrong Password\n')
        login()
    elif str(account_login) == "EResult.OK":
        system('cls')
        main()
    elif str(account_login) == "EResult.InvalidLoginAuthCode":
        system('cls')
        print('[ERROR] Invalid Steam Guard Code.')
        login_with_email_auth_code(username, password)
    else:
        print("[ERROR]: " + str(account_login))
        system('pause')
        sys.exit()


def login_with_steam_guard(username, password):
    print(ascii_art)
    code = validate_steam_guard_code('Steam Guard Code: ')
    account_login = client.login(username=username, password=password, two_factor_code=code)
    if str(account_login) == "EResult.InvalidPassword":
        system('cls')
        print('[STB] Wrong Password\n')
        login()
    elif str(account_login) == "EResult.OK":
        system('cls')
        main()
    elif str(account_login) == "EResult.TwoFactorCodeMismatch":
        system('cls')
        print('[ERROR] Invalid Steam Guard Code.')
        login_with_steam_guard(username, password)
    else:
        print("[ERROR]: " + str(account_login))
        system('pause')
        sys.exit()

def main():
    print(ascii_art)
    print(f'Logged in as {client.user.name}')
    
    current_game_id = None  

    while True:  
        try:
            
            if not current_game_id:  
                print("\n[1] Start a new game")
                print("[2] Exit")
            else:
                print("\n[1] Start a new game (stop current game first)")
                print("[2] Stop current game")
                print("[3] Exit")

            choice = input("Choose an option: ")

            if choice == "1": 
                if current_game_id:
                    confirm = input("A game is already running. Do you want to stop it and start a new one? (y/n): ").lower()
                    if confirm != "y":
                        continue

                    client.games_played([])  
                    print(f"Stopped the current game (ID: {current_game_id}).")
                    current_game_id = None  

                game_id = int(input('Game ID: '))
                custom_game_name = str(input('Custom Game Name: '))
                if game_id:
                    system('cls')
                    print(ascii_art)
                    get_game_name = req.get(f"https://store.steampowered.com/api/appdetails/?appids={game_id}").json()

                    # I just don't understand the logic of the service yet. 
                    # Sometimes it shows that the game by id does not exist, but if you try to find it a couple of times, it will be able to run.

                    if not get_game_name.get(str(game_id), {}).get("success", False):
                        print(f"{game_id} is not a valid game ID.")
                        continue  
                    game_name = get_game_name[str(game_id)]["data"]["name"]
                    client.send(
                        MsgProto(EMsg.ClientGamesPlayed), 
                        {'games_played': [{'game_id': game_id, 'game_extra_info': custom_game_name}]}
                    )
                    system(f"title Steam Hour Boost - @antsently - Running {game_name}")
                    print(f'Game: {game_name} | Status: Running | @antsently')
                    
                    current_game_id = game_id

            elif choice == "2" and current_game_id:  
                client.games_played([]) 
                print(f"Stopped the current game (ID: {current_game_id}).")
                current_game_id = None  

            elif choice == "3": 
                print("Exiting...")
                if current_game_id:
                    client.games_played([]) 
                client.logout()
                break

            else:
                print("Invalid choice. Please try again.")
        except (ValueError, KeyError):
            print("Invalid input. Please try again.")


if __name__ in "__main__":
    system("cls && color c && title Steam Hour Boost - @antsently")
    login()