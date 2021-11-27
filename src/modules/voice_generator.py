import asyncio
import platform
import subprocess

from NextHime import config
from src.modules.NextHimeUtils import NextHimeUtils

tmp_folder = NextHimeUtils().temp_path
input_file = f"{tmp_folder}/input.txt"  # ファイルの指定
csv_header = ["server_id", "before", "after"]


async def create_wave(input_text):
    if (config.jtalk.bin_path != "None" and config.jtalk.dic_path != "None"
            and config.jtalk.voice_path != "None"):
        # TODO: 2020/11/22 辞書を追加

        if platform.system() == "Windows":
            encoding = "shift_jis"
        else:
            encoding = "UTF-8"
        with open(input_file, "w", encoding=f"{encoding}") as file:
            file.write(input_text)

        command = "{c} -x {x} -m {m} -r {r} -ow {ow} {input_file}"

        args = {
            "c": config.jtalk.bin_path,
            "x": config.jtalk.dic_path,
            "m": config.jtalk.voice_path,
            "r": config.jtalk.speed,
            "ow": config.jtalk.output_wav_name,
            "input_file": input_file,
        }

        cmd = command.format(**args)
        subprocess.run(cmd, shell=True)
        return True


if __name__ == "__main__":
    asyncio.run(create_wave("これはテスト音声です。"))
