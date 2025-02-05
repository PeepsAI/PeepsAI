import os
from importlib.metadata import version as get_version
from typing import Optional, Tuple

import click

from peepsai.cli.add_peeps_to_flow import add_peeps_to_flow
from peepsai.cli.create_peeps import create_peeps
from peepsai.cli.create_flow import create_flow
from peepsai.cli.peeps_chat import run_chat
from peepsai.memory.storage.kickoff_task_outputs_storage import (
    KickoffTaskOutputsSQLiteStorage,
)

from .authentication.main import AuthenticationCommand
from .deploy.main import DeployCommand
from .evaluate_peeps import evaluate_peeps
from .install_peeps import install_peeps
from .kickoff_flow import kickoff_flow
from .plot_flow import plot_flow
from .replay_from_task import replay_task_command
from .reset_memories_command import reset_memories_command
from .run_peeps import run_peeps
from .tools.main import ToolCommand
from .train_peeps import train_peeps
from .update_peeps import update_peeps


@click.group()
@click.version_option(get_version("peepsai"))
def peepsai():
    """Top-level command group for peepsai."""


@peepsai.command()
@click.argument("type", type=click.Choice(["peeps", "flow"]))
@click.argument("name")
@click.option("--provider", type=str, help="The provider to use for the peeps")
@click.option("--skip_provider", is_flag=True, help="Skip provider validation")
def create(type, name, provider, skip_provider=False):
    """Create a new peeps, or flow."""
    if type == "peeps":
        create_peeps(name, provider, skip_provider)
    elif type == "flow":
        create_flow(name)
    else:
        click.secho("Error: Invalid type. Must be 'peeps' or 'flow'.", fg="red")


@peepsai.command()
@click.option(
    "--tools", is_flag=True, help="Show the installed version of peepsai tools"
)
def version(tools):
    """Show the installed version of peepsai."""
    try:
        peepsai_version = get_version("peepsai")
    except Exception:
        peepsai_version = "unknown version"
    click.echo(f"peepsai version: {peepsai_version}")

    if tools:
        try:
            tools_version = get_version("peepsai")
            click.echo(f"peepsai tools version: {tools_version}")
        except Exception:
            click.echo("peepsai tools not installed")


@peepsai.command()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=5,
    help="Number of iterations to train the peeps",
)
@click.option(
    "-f",
    "--filename",
    type=str,
    default="trained_agents_data.pkl",
    help="Path to a custom file for training",
)
def train(n_iterations: int, filename: str):
    """Train the peeps."""
    click.echo(f"Training the Peeps for {n_iterations} iterations")
    train_peeps(n_iterations, filename)


@peepsai.command()
@click.option(
    "-t",
    "--task_id",
    type=str,
    help="Replay the peeps from this task ID, including all subsequent tasks.",
)
def replay(task_id: str) -> None:
    """
    Replay the peeps execution from a specific task.

    Args:
        task_id (str): The ID of the task to replay from.
    """
    try:
        click.echo(f"Replaying the peeps from task {task_id}")
        replay_task_command(task_id)
    except Exception as e:
        click.echo(f"An error occurred while replaying: {e}", err=True)


@peepsai.command()
def log_tasks_outputs() -> None:
    """
    Retrieve your latest peeps.kickoff() task outputs.
    """
    try:
        storage = KickoffTaskOutputsSQLiteStorage()
        tasks = storage.load()

        if not tasks:
            click.echo(
                "No task outputs found. Only peeps kickoff task outputs are logged."
            )
            return

        for index, task in enumerate(tasks, 1):
            click.echo(f"Task {index}: {task['task_id']}")
            click.echo(f"Description: {task['expected_output']}")
            click.echo("------")

    except Exception as e:
        click.echo(f"An error occurred while logging task outputs: {e}", err=True)


@peepsai.command()
@click.option("-l", "--long", is_flag=True, help="Reset LONG TERM memory")
@click.option("-s", "--short", is_flag=True, help="Reset SHORT TERM memory")
@click.option("-e", "--entities", is_flag=True, help="Reset ENTITIES memory")
@click.option("-kn", "--knowledge", is_flag=True, help="Reset KNOWLEDGE storage")
@click.option(
    "-k",
    "--kickoff-outputs",
    is_flag=True,
    help="Reset LATEST KICKOFF TASK OUTPUTS",
)
@click.option("-a", "--all", is_flag=True, help="Reset ALL memories")
def reset_memories(
    long: bool,
    short: bool,
    entities: bool,
    knowledge: bool,
    kickoff_outputs: bool,
    all: bool,
) -> None:
    """
    Reset the peeps memories (long, short, entity, latest_peeps_kickoff_ouputs). This will delete all the data saved.
    """
    try:
        if not all and not (long or short or entities or knowledge or kickoff_outputs):
            click.echo(
                "Please specify at least one memory type to reset using the appropriate flags."
            )
            return
        reset_memories_command(long, short, entities, knowledge, kickoff_outputs, all)
    except Exception as e:
        click.echo(f"An error occurred while resetting memories: {e}", err=True)


@peepsai.command()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=3,
    help="Number of iterations to Test the peeps",
)
@click.option(
    "-m",
    "--model",
    type=str,
    default="gpt-4o-mini",
    help="LLM Model to run the tests on the Peeps. For now only accepting only OpenAI models.",
)
def test(n_iterations: int, model: str):
    """Test the peeps and evaluate the results."""
    click.echo(f"Testing the peeps for {n_iterations} iterations with model {model}")
    evaluate_peeps(n_iterations, model)


@peepsai.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.pass_context
def install(context):
    """Install the Peeps."""
    install_peeps(context.args)


@peepsai.command()
def run():
    """Run the Peeps."""
    click.echo("Running the Peeps")
    run_peeps()


@peepsai.command()
def update():
    """Update the pyproject.toml of the Peeps project to use uv."""
    update_peeps()


@peepsai.command()
def signup():
    """Sign Up/Login to PeepsAI+."""
    AuthenticationCommand().signup()


@peepsai.command()
def login():
    """Sign Up/Login to PeepsAI+."""
    AuthenticationCommand().signup()


# DEPLOY CREWAI+ COMMANDS
@peepsai.group()
def deploy():
    """Deploy the Peeps CLI group."""
    pass


@peepsai.group()
def tool():
    """Tool Repository related commands."""
    pass


@deploy.command(name="create")
@click.option("-y", "--yes", is_flag=True, help="Skip the confirmation prompt")
def deploy_create(yes: bool):
    """Create a Peeps deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.create_peeps(yes)


@deploy.command(name="list")
def deploy_list():
    """List all deployments."""
    deploy_cmd = DeployCommand()
    deploy_cmd.list_peepz()


@deploy.command(name="push")
@click.option("-u", "--uuid", type=str, help="Peeps UUID parameter")
def deploy_push(uuid: Optional[str]):
    """Deploy the Peeps."""
    deploy_cmd = DeployCommand()
    deploy_cmd.deploy(uuid=uuid)


@deploy.command(name="status")
@click.option("-u", "--uuid", type=str, help="Peeps UUID parameter")
def deply_status(uuid: Optional[str]):
    """Get the status of a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.get_peeps_status(uuid=uuid)


@deploy.command(name="logs")
@click.option("-u", "--uuid", type=str, help="Peeps UUID parameter")
def deploy_logs(uuid: Optional[str]):
    """Get the logs of a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.get_peeps_logs(uuid=uuid)


@deploy.command(name="remove")
@click.option("-u", "--uuid", type=str, help="Peeps UUID parameter")
def deploy_remove(uuid: Optional[str]):
    """Remove a deployment."""
    deploy_cmd = DeployCommand()
    deploy_cmd.remove_peeps(uuid=uuid)


@tool.command(name="create")
@click.argument("handle")
def tool_create(handle: str):
    tool_cmd = ToolCommand()
    tool_cmd.create(handle)


@tool.command(name="install")
@click.argument("handle")
def tool_install(handle: str):
    tool_cmd = ToolCommand()
    tool_cmd.login()
    tool_cmd.install(handle)


@tool.command(name="publish")
@click.option(
    "--force",
    is_flag=True,
    show_default=True,
    default=False,
    help="Bypasses Git remote validations",
)
@click.option("--public", "is_public", flag_value=True, default=False)
@click.option("--private", "is_public", flag_value=False)
def tool_publish(is_public: bool, force: bool):
    tool_cmd = ToolCommand()
    tool_cmd.login()
    tool_cmd.publish(is_public, force)


@peepsai.group()
def flow():
    """Flow related commands."""
    pass


@flow.command(name="kickoff")
def flow_run():
    """Kickoff the Flow."""
    click.echo("Running the Flow")
    kickoff_flow()


@flow.command(name="plot")
def flow_plot():
    """Plot the Flow."""
    click.echo("Plotting the Flow")
    plot_flow()


@flow.command(name="add-peeps")
@click.argument("peeps_name")
def flow_add_peeps(peeps_name):
    """Add a peeps to an existing flow."""
    click.echo(f"Adding peeps {peeps_name} to the flow")
    add_peeps_to_flow(peeps_name)


@peepsai.command()
def chat():
    """
    Start a conversation with the Peeps, collecting user-supplied inputs,
    and using the Chat LLM to generate responses.
    """
    click.secho(
        "\nStarting a conversation with the Peeps\n" "Type 'exit' or Ctrl+C to quit.\n",
    )

    run_chat()


if __name__ == "__main__":
    peepsai()
