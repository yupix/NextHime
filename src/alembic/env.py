import sys
from importlib import import_module
from logging.config import fileConfig

from sqlalchemy import MetaData, engine_from_config, pool

from alembic import context

sys.path = ["", ".."] + sys.path[1:]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

base_model_path = "src.sql.models"
target_models = [
    "src.sql.models.basic",
    "src.sql.models.blocklist",
    "src.sql.models.blog",
    "src.sql.models.eew",
    "src.sql.models.note",
    "src.sql.models.guild",
    "src.sql.models.user",
    "src.sql.models.WarframeFissure",
]


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
def combine_metadata(*args):
    """Short summary.

    Parameters
    ----------
    *args : type
        Description of parameter `*args`.

    Returns
    -------
    type
        Description of returned object.

    """
    m = MetaData()
    for metadata in args:
        for t in metadata.tables.values():
            t.tometadata(m)
    return m


for target in target_models:
    model = import_module(f"{target}")
    target_metadata = combine_metadata(model.Base.metadata)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Short summary.

    Returns
    -------
    type
        Description of returned object.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Short summary.

    Returns
    -------
    type
        Description of returned object.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata,
                          compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
