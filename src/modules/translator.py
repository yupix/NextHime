from googletrans import Translator


def translator(ctx: str, original_lang: str, to_lang: str):
    """
    文章を指定した言語に翻訳して返します

    Parameters
    ----------
    ctx: str
        翻訳する内容
    original_lang: str
        もとの言語
    to_lang : str
        翻訳先の言語
    """

    tr = Translator()
    return tr.translate(
        text=f"{ctx}", src=f"{original_lang}", dest=f"{to_lang}"
    ).text


class Translate:  # TODO:削除
    """
    Deprecated
    """

    def __init__(self, original_lang: str = 'en', lang: str = 'japan'):
        self.lang = lang
        self.original_lang = original_lang

    async def run(self, content: str):
        tr = Translator()
        return tr.translate(
            text=f"{content}", src=f"{self.original_lang}", dest=f"{self.lang}"
        ).text
