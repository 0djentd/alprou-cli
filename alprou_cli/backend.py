import logging
import os
import json

from pprint import pprint


import colorama
import appdirs
import click
import requests

logger = logging.getLogger(__name__)

APP_NAME = "alprou_cli"
CONFIG_FILE = "alprou_cli_config"
DEFAULT_CONFIG = {"token": None}
LINKS = {
         "auth": {"authtoken": "authtoken/"},
         "habits": "habits/"
         }


def create_default_config_file(file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(DEFAULT_CONFIG))


def get_default_config_file(*args, **kwargs):
    """Retruns path to config file, or creates one."""

    config_dir_path = appdirs.user_config_dir(appname=APP_NAME)
    config_file_path = os.path.join(config_dir_path, CONFIG_FILE)

    if not os.path.exists(config_file_path):
        create = click.confirm(
            f'Create Alprou config file "{config_file_path}" ?',
            *args, default=True, **kwargs)
        if create:
            create_default_config_file(config_file_path)
    return config_file_path


def get_token(context) -> str | None:
    """Retruns saved token."""
    config = context.obj.config
    try:
        with open(config, encoding="utf-8") as file:
            data = json.load(file)
        return data["token"]
    except:
        return None


def get_auth(context, token=None) -> dict | None:
    """Returns authorization headers."""
    if not token:
        token = get_token(context)
    if token:
        data = {"Authorization": "Token " + token}
    else:
        data = None
    return data


def get_auth_wrapper(func,):
    """Auth wrapper"""
    def wrapper(context, *args, **kwargs):
        auth = get_auth(context)
        if not auth:
            click.UsageError("Err")
        result = func(context, auth, *args, **kwargs)
        return result
    return wrapper


# ====== Authentication commands =========

def login(context, username: str, password: str) -> dict | None:
    """Get token from API and save it in config file."""
    api = context.obj.api
    response = requests.post(api + LINKS["auth"]["authtoken"],
                             data={"username": username, "password": password})
    data = response.json()

    if response.status_code == 200:
        config = get_default_config_file()
        with open(config, "w", encoding="utf-8") as file:
            file.write(json.dumps({"token": data["token"]}))
        return {"token": data["token"]}

    if response.status_code == 400:
        click.echo(colorama.Fore.RED +
                   "Failed to login. Probably wrong username or password.",
                   color=True)
    else:
        click.echo(colorama.Fore.RED +
                   "Something is wrong with API.",
                   color=True)
    return None


def logout(context):
    """Removes saved token."""
    create_default_config_file(context.obj.config)


def list_habits(context):
    """Returns list of habits."""
    api = context.obj.api
    response = requests.get(api + LINKS["habits"], headers=context.obj.auth)
    habits = response.json().result
    return habits
