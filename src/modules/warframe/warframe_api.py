import json
import os

import requests


class WarframeAPI:
    def __init__(self):
        self.result = None
        self.fissures = None
        self.old_fissures = None

    def fetch_api(self, url: str) -> requests.models.Response:
        self.result = requests.get(url)
        return self.result

    def get_fissures(self) -> "WarframeAPI":
        url = "https://api.warframestat.us/pc/fissures"
        self.fissures = self.fetch_api(url).json()
        return self

    def save_fissure_json(self, path: str, check: bool = False):
        """指定された"""
        if not check or not os.path.isfile(path):
            with open(path, mode="w", encoding="utf-8") as f:
                f.write(str(json.dumps(self.fissures, indent=2)))
                f.close()
        return self.fissures

    def load_fissure_json(self, path: str):
        with open(path, mode="r", encoding="utf-8") as f:
            self.old_fissures = json.loads(f.read())
            f.close()
        return self.old_fissures


if __name__ == "__main__":
    WarframeAPI().get_fissures()
