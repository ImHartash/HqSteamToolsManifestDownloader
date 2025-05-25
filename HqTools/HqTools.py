import winreg
from pathlib import Path

from HqLogSystem.HqLogSystem import LOG_SYSTEM
from HqCommon.HqConfig import HQ_CONFIG
import HqCommon.HqVars as V


class HqTools:
    def GetSteamPath(self) -> Path:
        try:
            if HQ_CONFIG.load_configuration().get("steam_path", "") != "":
                return Path(HQ_CONFIG.load_configuration().get("steam_path", ""))
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam") as wKey:
                return Path(winreg.QueryValueEx(wKey, "SteamPath")[0])
        except Exception as e:
            LOG_SYSTEM.Error("Failed to get Steam Path from regedit. Exception: " + str(e))
            LOG_SYSTEM.Close()
    
    def GetAppIdFromReference(self, strGameUrl: str) -> str:
        try:
            app_id = strGameUrl.split("/")[4]
            LOG_SYSTEM.Info("Found id from link: " + app_id)
            return app_id
        except Exception as e:
            LOG_SYSTEM.Error("Failed to get App ID from steam URL. Exception: " + str(e))
            LOG_SYSTEM.Close()
    
    def ValidateId(self, nAppId: str) -> None:
        try:
            _ = int(nAppId)
        except Exception as e:
            LOG_SYSTEM.Error("Failed validate App ID. Exception: " + str(e))
            LOG_SYSTEM.Close()
            
    def GetFilesFromSteamDir(self, strSubfolder: str) -> list:
        folder_path: Path = V.STEAM_PATH / strSubfolder
        return [file.name for file in folder_path.iterdir() if file.is_file()]
            
            
HQ_TOOLS = HqTools()