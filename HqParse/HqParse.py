# import zone -_-
import httpx
import ujson
import time
import vdf
import aiofiles
import pathlib
import HqCommon.HqVars as V

from HqLogSystem.HqLogSystem import LOG_SYSTEM

from typing import Any, List, Tuple, Dict


_GITHUB_URLS = {
    "RateLimit": "https://api.github.com/rate_limit"
}

class HqParser:
    async def _GetLatestRepoInfo(self, app_id: str) -> str | None | Any:
        latest_date = None
        selected_repository = None
        for repository in V.REPO_LIST:
            git_url = f"https://api.github.com/repos/{repository}/branches/{app_id}"
            response = await V.HTTP_CLIENT.get(git_url, headers=V.HTTP_HEADER)
            response_json = response.json()
            if response_json and "commit" in response_json:
                date = response_json["commit"]["commit"]["author"]["date"]
                if (latest_date is None) or (date > latest_date):
                    latest_date = str(date)
                    selected_repository = str(repository)
                    
        return selected_repository, latest_date

    async def _FetchFromCDN(self, sha: str, path: str, repository: str):
        git_url = f"https://raw.githubusercontent.com/{repository}/{sha}/{path}"
        
        attemp = 3
        while attemp > 0:
            try:
                response = await V.HTTP_CLIENT.get(git_url, headers=V.HTTP_HEADER, timeout=30)
                if response.status_code == 200:
                    return response.read()
                else:
                    LOG_SYSTEM.Error(f"Failed to connect to Git: {path}. Status Code: {response.status_code}")
            except KeyboardInterrupt:
                LOG_SYSTEM.Info("Stopped...")
            except httpx.ConnectError as e:
                LOG_SYSTEM.Error(f"Failed to connect to Git: {path}. {str(e)}")
            except httpx.ConnectTimeout as e:
                LOG_SYSTEM.Error(f"Connection timeouted: {path}. {str(e)}")
            
            attemp -= 1
            LOG_SYSTEM.Warn(f"Trying again on {path}. Attemps remaining {attemp}")
        
        LOG_SYSTEM.Error(f"Failed to fetch {path}. You have no attemps.")
        raise Exception(f"Cannot load {path}")

    def _ParseKeyVDF(self, content: bytes) -> List[Tuple[str, str]]:
        try:
            depots = vdf.loads(content.decode())["depots"]
            return [(d_id, d_info["DecryptionKey"]) for d_id, d_info in depots.items()]
        except Exception as e:
            LOG_SYSTEM.Error(f"Something went wrong while parsing VDF. " + str(e))
            return []
    
    async def CheckGitHubApiRateLimit(self) -> None:
        url = _GITHUB_URLS["RateLimit"]
        try:
            response = await V.HTTP_CLIENT.get(url, headers=V.HTTP_HEADER)
            response_json: ujson = response.json()
            
            if response.status_code != 200:
                LOG_SYSTEM.Error("Failed to connect to GitHub. Status code - " + response.status_code)
                return
            
            rate_limit = response_json.get("rate", {})
            remaining_requests = rate_limit.get("remaining", 0)
            reset_time = rate_limit.get("reset", 0)
            reset_time_formatted = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(reset_time)
            )
            LOG_SYSTEM.Info(f"Remaining amount of GitHub Requests: {remaining_requests}")
            if remaining_requests <= 0:
                LOG_SYSTEM.Warn(f"You have no requests on GitHub API. Next reset time - {reset_time_formatted}")
        except httpx.ConnectError as e:
            LOG_SYSTEM.Error("Failed to connect to GitHub API. " + str(e))
        except httpx.ConnectTimeout as e:
            LOG_SYSTEM.Error("Response timeout to GitHub API. " + str(e))
        except KeyboardInterrupt:
            LOG_SYSTEM.Info("Stopped.")
        except Exception as e:
            LOG_SYSTEM.Error("Something went wrong. " + str(e))
    
    async def HandleDepotFiles(self, app_id: str) -> Tuple[List[Any], dict[Any, Any]]:
        collected = []
        depot_map = {}
        
        try:
            selected_repository, latest_repo_date = await self._GetLatestRepoInfo(app_id)
            
            if selected_repository:
                git_url = f"https://api.github.com/repos/{selected_repository}/branches/{app_id}"
                git_response = await V.HTTP_CLIENT.get(git_url, headers=V.HTTP_HEADER)
                git_response.raise_for_status()
                
                tree_url = git_response.json()["commit"]["commit"]["tree"]["url"]
                tree_response = await V.HTTP_CLIENT.get(tree_url)
                tree_response.raise_for_status()
                
                depot_cache = V.STEAM_PATH / "depotcache"
                depot_cache.mkdir(exist_ok=True)
                
                LOG_SYSTEM.Info(f"Choiced GitHub repository - https://github.com/{selected_repository}")
                LOG_SYSTEM.Info(f"Latest Git branch update - {latest_repo_date}")
                
                for item in tree_response.json()["tree"]:
                    file_path = str(item["path"])
                    if file_path.endswith(".manifest"):
                        save_path = depot_cache / file_path
                        if save_path.exists():
                            LOG_SYSTEM.Warn(f"File already exists ({save_path})")
                            continue
                        content = await self._FetchFromCDN(
                            git_response.json()["commit"]["sha"], file_path, selected_repository
                        )
                        LOG_SYSTEM.Info(f"Attempting to save manifest {file_path} to {save_path}")
                        LOG_SYSTEM.Info(f"Content size: {len(content) if content else 0} bytes")
                        async with aiofiles.open(save_path, "wb") as f:
                            await f.write(content)
                            LOG_SYSTEM.Info("File successfully created! " + str(save_path))
                    elif "key.vdf" in file_path.lower():
                        key_content = await self._FetchFromCDN(
                            git_response.json()["commit"]["sha"], file_path, selected_repository
                        )
                        collected.extend(self._ParseKeyVDF(key_content))
                
                for item in tree_response.json()["tree"]:
                    if not item["path"].endswith(".manifest"):
                        continue
                    
                    filename = pathlib.Path(item["path"]).stem
                    if "_" not in filename:
                        continue
                    
                    depot_id, manifest_id = filename.replace(".manifest", "").split("_", 1)
                    if not (depot_id.isdigit() and manifest_id.isdigit()):
                        continue
                    
                    depot_map.setdefault(depot_id, []).append(manifest_id)
                
                for depot_id in depot_map:
                    depot_map[depot_id].sort(key=lambda x: int(x), reverse=True)
                    
        except httpx.HTTPStatusError as e:
            LOG_SYSTEM.Error("HTTP Error. " + str(e))
        except Exception as e:
            LOG_SYSTEM.Error("Something went wrong. " + str(e))
        
        return collected, depot_map
    
    async def SetupSteamTools(self, depot_data: List[Tuple[str, str]], app_id: str, depot_map: Dict) -> bool:     
        st_path = V.STEAM_PATH / "config" / "stplug-in"
        st_path.mkdir(exist_ok=True)
        
        lock_version = True
        
        lua_content = f'addappid({app_id}, 1, "None")\n'
        for d_id, d_key in depot_data:
            if lock_version:
                for manifest_id in depot_map[d_id]:
                    lua_content += f'addappid({d_id}, 1, "{d_key}")\nsetManifestid({d_id},"{manifest_id}")\n'
            else:
                lua_content += f'addappid({d_id}, 1, "{d_key}")\n'
        
        lua_file = st_path / f"{app_id}.lua"
        async with aiofiles.open(lua_file, "w") as f:
            await f.write(lua_content)
            
        return True


HQ_PARSER = HqParser()