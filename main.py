from HqTools.HqTools import HQ_TOOLS
from HqLogSystem.HqLogSystem import LOG_SYSTEM
from HqParse.HqParse import HQ_PARSER
from HqCommon.HqConfig import HQ_CONFIG

from colorama import init

import HqCommon.HqVars as Vars

import httpx
import asyncio
import pathlib


def InitializeVars() -> None:
    # Initializing Global Vars
    Vars.STEAM_PATH = HQ_TOOLS.GetSteamPath()
    # Initializing Var for requests
    Vars.HTTP_CLIENT = httpx.AsyncClient(verify=False)
    Vars.HTTP_HEADER = {"Authorization" : f"Bearer {Vars.GITHUB_TOKEN}"} if Vars.GITHUB_TOKEN is not None else None # Add adding github token
    

async def ProcedureSetup(nAppId: str) -> None:
    try:
        await HQ_PARSER.CheckGitHubApiRateLimit()
        
        depot_data, depot_map = await HQ_PARSER.HandleDepotFiles(nAppId)
        
        if await HQ_PARSER.SetupSteamTools(depot_data, nAppId, depot_map):
            LOG_SYSTEM.Success(f"Game {nAppId} successfully added. To see it you need to reload steam client.")
    except Exception as e:
        LOG_SYSTEM.Error(str(e))
        

def MenuAddGame():
    try:
        APP_ID = LOG_SYSTEM.GetString("Enter game app id or game URL")
        if "https://store.steampowered.com/app/" in APP_ID:
            APP_ID = HQ_TOOLS.GetAppIdFromReference(APP_ID)
        HQ_TOOLS.ValidateId(APP_ID)
        asyncio.run(ProcedureSetup(APP_ID))
    except (asyncio.CancelledError, KeyboardInterrupt):
        LOG_SYSTEM.Close()


def MenuAddFileList():
    try:
        config = HQ_CONFIG.load_configuration()
        custom_path = config.get("auto_read_filepath", "")
        if custom_path == "":
            return LOG_SYSTEM.Warn("Please, before start, enter file path to the config " + str(HQ_CONFIG.cfg_path))
        file_path = pathlib.Path(custom_path)
        if not file_path.exists():
            return LOG_SYSTEM.Error("File not found. Check it in config file " + str(HQ_CONFIG.cfg_path))
        LOG_SYSTEM.Info("File found. Starting setup...")
        with open(file_path, "r") as f:
            for line in f:
                app_id = line.lstrip()
                if "https://store.steampowered.com/app/" in app_id:
                    app_id = HQ_TOOLS.GetAppIdFromReference(app_id)
                HQ_TOOLS.ValidateId(app_id)
                asyncio.run(ProcedureSetup(app_id))
    except (asyncio.CancelledError, KeyboardInterrupt):
        LOG_SYSTEM.Close()
        

if __name__ == '__main__':
    init()
    InitializeVars()
    
    while True:
        LOG_SYSTEM.ClearConsole()
        LOG_SYSTEM.PrintBanner()
        user_choice = LOG_SYSTEM.Menu()
        
        LOG_SYSTEM.ClearConsole()
        LOG_SYSTEM.PrintBanner()
        
        match user_choice:
            case "1":
                MenuAddGame()
            case "2":
                MenuAddFileList()
            case "9":
                asyncio.run(Vars.HTTP_CLIENT.aclose())
                LOG_SYSTEM.Close()