import subprocess

import click
from packaging import version

from peepsai.cli.utils import read_toml
from peepsai.cli.version import get_peepsai_version


def run_peeps() -> None:
    """
    Run the peeps by running a command in the UV environment.
    """
    command = ["uv", "run", "run_peeps"]
    peepsai_version = get_peepsai_version()
    min_required_version = "0.71.0"

    pyproject_data = read_toml()

    if pyproject_data.get("tool", {}).get("poetry") and (
        version.parse(peepsai_version) < version.parse(min_required_version)
    ):
        click.secho(
            f"You are running an older version of peepsAI ({peepsai_version}) that uses poetry pyproject.toml. "
            f"Please run `peepsai update` to update your pyproject.toml to use uv.",
            fg="red",
        )

    try:
        subprocess.run(command, capture_output=False, text=True, check=True)

    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred while running the peeps: {e}", err=True)
        click.echo(e.output, err=True, nl=True)

        if pyproject_data.get("tool", {}).get("poetry"):
            click.secho(
                "It's possible that you are using an old version of peepsAI that uses poetry, please run `peepsai update` to update your pyproject.toml to use uv.",
                fg="yellow",
            )

    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
