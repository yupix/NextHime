import yaml


class LanguageManager:
    def __init__(self, base_path=None, lang=None, module_name=None):
        """
        Parameters
        ----------
        base_path: str
            ファイルがあるフォルダまでのパス
        lang: str
            言語を指定
        module_name: str
            どのモジュールの言語ファイルかを指定(拡張子はyamlのみサポート)
        """
        self.base_path = base_path
        self.lang = lang
        self.module_name = module_name

    def get(self):
        """
        returns
        -------
        dict:
            取得したyamlを返します
        """
        with open(f"{self.base_path}{self.lang}/{self.module_name}",
                  encoding="utf-8") as f:
            return yaml.safe_load(f)
