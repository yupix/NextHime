import traceback

from alembic import command, util
from alembic.config import Config


class Migrate:
    def __init__(self):
        self.alembic_config = Config("./alembic.ini")
        self.alembic_config.set_main_option("script_location", "src/alembic")

    async def generate(self):
        try:
            command.revision(self.alembic_config, autogenerate=True)
        except util.exc.CommandError as err:
            print(err)
            if "Target database is not up to date." in str(err):
                await self.upgrade()
        except Exception:
            traceback.print_exc()

    async def upgrade(self):
        print("upgrade complete")
        command.upgrade(self.alembic_config, "+1")
