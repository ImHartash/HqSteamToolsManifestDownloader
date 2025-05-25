import json
import pathlib
import sys

from HqLogSystem.HqLogSystem import LOG_SYSTEM


CFG_DEFAULT = {
    "github_token": "",
    "steam_path": "",
    "auto_read_filepath": "",
    "auto_save_in_file": True,
}


class HqConfig:
    def __init__(self, cfg_name: str, subfolder: str) -> None:
        self.cfg_subfolder = self.__get_app_dir() / subfolder
        self.cfg_name = cfg_name
        self.cfg_path = self.cfg_subfolder / self.cfg_name
        
        # Initializing Configuration
        if not self.cfg_path.exists():
            self.cfg_subfolder.mkdir(exist_ok=True, parents=True)
            self.__create_configuration()   
    
    def __create_configuration(self) -> None:
        try:
            with open(self.cfg_path, "w+", encoding="utf-8") as f:
                f.write(json.dumps(CFG_DEFAULT, indent=2, ensure_ascii=False))
            LOG_SYSTEM.Info(f"Created config file. Path - {self.cfg_path}")
        except IOError as e:
            LOG_SYSTEM.Error(f"Failed to create file configuration. {str(e)}")
            LOG_SYSTEM.Close()
    
    def __get_app_dir(self) -> pathlib.Path:
        if getattr(sys, 'frozen', False):
            return pathlib.Path(sys.executable).parent
        else:
            return pathlib.Path(__file__).parents[1]
    
    def load_configuration(self) -> dict:
        if not self.cfg_path.exists():
            self.__create_configuration()
            LOG_SYSTEM.Info(f"Created config file. Path - {self.cfg_path}")
        
        try:
            with open(self.cfg_path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except json.JSONDecodeError:
            LOG_SYSTEM.Error("Failed to decode config file.")
            LOG_SYSTEM.Close()
        except Exception as e:
            LOG_SYSTEM.Error(f"Something went wrong while getting config. Error - {str(e)}")
            LOG_SYSTEM.Close()


HQ_CONFIG = HqConfig("config.json", "configuration")