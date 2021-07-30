import asyncio
from src.modules.color import Color

with open('src/assets/logo.txt') as logo:
    print(Color.PINK + logo.read())

from NextHime.main import run

if __name__ == "__main__":
    loop_bot = asyncio.new_event_loop()
    asyncio.set_event_loop(loop_bot)
    loop_api = asyncio.new_event_loop()

    run(loop_bot, loop_api)
