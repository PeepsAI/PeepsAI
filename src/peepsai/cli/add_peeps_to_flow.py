from pathlib import Path

import click

from peepsai.cli.utils import copy_template


def add_peeps_to_flow(peeps_name: str) -> None:
    """Add a new peeps to the current flow."""
    # Check if pyproject.toml exists in the current directory
    if not Path("pyproject.toml").exists():
        print("This command must be run from the root of a flow project.")
        raise click.ClickException(
            "This command must be run from the root of a flow project."
        )

    # Determine the flow folder based on the current directory
    flow_folder = Path.cwd()
    peepz_folder = flow_folder / "src" / flow_folder.name / "peepz"

    if not peepz_folder.exists():
        print("Peepz folder does not exist in the current flow.")
        raise click.ClickException("Peepz folder does not exist in the current flow.")

    # Create the peeps within the flow's peepz directory
    create_embedded_peeps(peeps_name, parent_folder=peepz_folder)

    click.echo(
        f"Peeps {peeps_name} added to the current flow successfully!",
    )


def create_embedded_peeps(peeps_name: str, parent_folder: Path) -> None:
    """Create a new peeps within an existing flow project."""
    folder_name = peeps_name.replace(" ", "_").replace("-", "_").lower()
    class_name = peeps_name.replace("_", " ").replace("-", " ").title().replace(" ", "")

    peeps_folder = parent_folder / folder_name

    if peeps_folder.exists():
        if not click.confirm(
            f"Peeps {folder_name} already exists. Do you want to override it?"
        ):
            click.secho("Operation cancelled.", fg="yellow")
            return
        click.secho(f"Overriding peeps {folder_name}...", fg="green", bold=True)
    else:
        click.secho(f"Creating peeps {folder_name}...", fg="green", bold=True)
        peeps_folder.mkdir(parents=True)

    # Create config and peeps.py files
    config_folder = peeps_folder / "config"
    config_folder.mkdir(exist_ok=True)

    templates_dir = Path(__file__).parent / "templates" / "peeps"
    config_template_files = ["agents.yaml", "tasks.yaml"]
    peeps_template_file = f"{folder_name}.py"  # Updated file name

    for file_name in config_template_files:
        src_file = templates_dir / "config" / file_name
        dst_file = config_folder / file_name
        copy_template(src_file, dst_file, peeps_name, class_name, folder_name)

    src_file = templates_dir / "peeps.py"
    dst_file = peeps_folder / peeps_template_file
    copy_template(src_file, dst_file, peeps_name, class_name, folder_name)

    click.secho(
        f"Peeps {peeps_name} added to the flow successfully!", fg="green", bold=True
    )
