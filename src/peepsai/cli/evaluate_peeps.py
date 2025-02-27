import subprocess

import click


def evaluate_peeps(n_iterations: int, model: str) -> None:
    """
    Test and Evaluate the peeps by running a command in the UV environment.

    Args:
        n_iterations (int): The number of iterations to test the peeps.
        model (str): The model to test the peeps with.
    """
    command = ["uv", "run", "test", str(n_iterations), model]

    try:
        if n_iterations <= 0:
            raise ValueError("The number of iterations must be a positive integer.")

        result = subprocess.run(command, capture_output=False, text=True, check=True)

        if result.stderr:
            click.echo(result.stderr, err=True)

    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred while testing the peeps: {e}", err=True)
        click.echo(e.output, err=True)

    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
