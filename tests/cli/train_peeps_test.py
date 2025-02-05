import subprocess
from unittest import mock

from peepsai.cli.train_peeps import train_peeps


@mock.patch("peepsai.cli.train_peeps.subprocess.run")
def test_train_peeps_positive_iterations(mock_subprocess_run):
    n_iterations = 5
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["uv", "run", "train", str(n_iterations)],
        returncode=0,
        stdout="Success",
        stderr="",
    )

    train_peeps(n_iterations, "trained_agents_data.pkl")

    mock_subprocess_run.assert_called_once_with(
        ["uv", "run", "train", str(n_iterations), "trained_agents_data.pkl"],
        capture_output=False,
        text=True,
        check=True,
    )


@mock.patch("peepsai.cli.train_peeps.click")
def test_train_peeps_zero_iterations(click):
    train_peeps(0, "trained_agents_data.pkl")
    click.echo.assert_called_once_with(
        "An unexpected error occurred: The number of iterations must be a positive integer.",
        err=True,
    )


@mock.patch("peepsai.cli.train_peeps.click")
def test_train_peeps_negative_iterations(click):
    train_peeps(-2, "trained_agents_data.pkl")
    click.echo.assert_called_once_with(
        "An unexpected error occurred: The number of iterations must be a positive integer.",
        err=True,
    )


@mock.patch("peepsai.cli.train_peeps.click")
@mock.patch("peepsai.cli.train_peeps.subprocess.run")
def test_train_peeps_called_process_error(mock_subprocess_run, click):
    n_iterations = 5
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["uv", "run", "train", str(n_iterations)],
        output="Error",
        stderr="Some error occurred",
    )
    train_peeps(n_iterations, "trained_agents_data.pkl")

    mock_subprocess_run.assert_called_once_with(
        ["uv", "run", "train", str(n_iterations), "trained_agents_data.pkl"],
        capture_output=False,
        text=True,
        check=True,
    )
    click.echo.assert_has_calls(
        [
            mock.call.echo(
                "An error occurred while training the peeps: Command '['uv', 'run', 'train', '5']' returned non-zero exit status 1.",
                err=True,
            ),
            mock.call.echo("Error", err=True),
        ]
    )


@mock.patch("peepsai.cli.train_peeps.click")
@mock.patch("peepsai.cli.train_peeps.subprocess.run")
def test_train_peeps_unexpected_exception(mock_subprocess_run, click):
    n_iterations = 5
    mock_subprocess_run.side_effect = Exception("Unexpected error")
    train_peeps(n_iterations, "trained_agents_data.pkl")

    mock_subprocess_run.assert_called_once_with(
        ["uv", "run", "train", str(n_iterations), "trained_agents_data.pkl"],
        capture_output=False,
        text=True,
        check=True,
    )
    click.echo.assert_called_once_with(
        "An unexpected error occurred: Unexpected error", err=True
    )
