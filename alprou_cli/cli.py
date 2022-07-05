"""Alprou CLI"""

import logging
import dataclasses

from pprint import pprint

import click
import colorama

from alprou_cli import backend


logger = logging.getLogger(__name__)


def add_commands(group: click.Group, commands: list[click.Command]) -> None:
    """Add commands to commands group"""
    for command in commands:
        group.add_command(command)


@dataclasses.dataclass
class Config():
    """Config."""
    debug: bool
    verbose: bool
    config: str
    api: str
    auth: dict | None = None

    def setup(self):
        """Setup config."""
        logger_level = logger.level
        if self.verbose:
            logger_level = logging.INFO
        elif self.debug:
            logger_level = logging.DEBUG
        logger.setLevel(logger_level)


@click.group
@click.pass_context
@click.option("--verbose/--no-verbose")
@click.option("--debug/--no-debug")
@click.option("--api", type=str, default="http://localhost:8000/api/")
@click.option("--config",
              type=click.Path(exists=True, dir_okay=False, readable=True),
              default=backend.get_default_config_file())
def cli_commands(context, **kwargs):
    """All CLI commands."""
    context.obj = Config(**kwargs)


# ====== Authentication commands =========
@cli_commands.group()
@click.pass_context
def auth(context):  # pylint: disable=unused-argument
    """Authentication."""


@click.command()
@click.pass_context
def status(context):
    """Show authentication status."""
    if backend.get_token(context):
        click.echo("Authenticated")


@click.command()
@click.pass_context
@click.option("--username", prompt="Username")
@click.password_option("--password", prompt="Password")
def login(context, username, password):
    """Login."""
    backend.login(context, username, password)


@click.command()
@click.pass_context
def logout(context):
    """Logout."""
    backend.logout(context)


add_commands(auth, [status, login, logout])


# ====== Usual commands =========
@cli_commands.group()
@click.pass_context
@click.option("--token", type=str, required=False, default=None)
def habits(context, *args, **kwargs):
    """Habits."""
    token = kwargs["token"]
    if not token:
        token = backend.get_token(context)
    auth = backend.get_auth(context, token=token)
    if not auth:
        click.UsageError(colorama.Fore.RED + "Error.")
        click.Abort()
    else:
        context.obj.auth = auth

@click.command("list")
@click.pass_context
def habits_list(context, *args, **kwargs):
    habits = backend.list_habits(context)
    pprint(habits)
    return


add_commands(habits, [habits_list])


def main():
    """Main function."""
    cli_commands()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
