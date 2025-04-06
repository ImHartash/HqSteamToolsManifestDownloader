import httpx
import pathlib

from HqCommon.HqConfig import HQ_CONFIG

STEAM_PATH: pathlib.Path = None
GITHUB_TOKEN = None if HQ_CONFIG.load_configuration().get("github_token", "") == "" else HQ_CONFIG.load_configuration().get("github_token", "")

HTTP_CLIENT: httpx.AsyncClient = None
HTTP_HEADER = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else None

REPO_LIST = ["SteamAutoCracks/ManifestHub",
             "ikun0014/ManifestHub",
             "Auiowu/ManifestAutoUpdate",]