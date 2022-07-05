import click


@click.group
def cli_commands():
    pass


@cli_commands.command()
def status():
    return


def main():
    cli_commands()


if __name__ == "__main__":
    main()
