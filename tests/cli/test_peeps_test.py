import subprocess
from unittest import mock

import pytest

from peepsai.cli import evaluate_peeps


@pytest.mark.parametrize(
    "n_iterations,model",
    [
        (1, "gpt-4o"),
        (5, "gpt-3.5-turbo"),
        (10, "gpt-4"),
    ],
)
@mock.patch("peepsai.cli.evaluate_peeps.subprocess.run")
def test_peeps_success(mock_subprocess_run, n_iterations, model):
    """Test the peeps function for successful execution."""
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=f"uv run test {n_iterations} {model}", returncode=0
    )
    result = evaluate_peeps.evaluate_peeps(n_iterations, model)

    mock_subprocess_run.assert_called_once_with(
        ["uv", "run", "test", str(n_iterations), model],
        capture_output=False,
        text=True,
        check=True,
    )
    assert result is None


@mock.patch("peepsai.cli.evaluate_peeps.click")
def test_test_peeps_zero_iterations(click):
    evaluate_peeps.evaluate_peeps(0, "gpt-4o")
    click.echo.assert_called_once_with(
        "An unexpected error occurred: The number of iterations must be a positive integer.",
        err=True,
    )


@mock.patch("peepsai.cli.evaluate_peeps.click")
def test_test_peeps_negative_iterations(click):
    evaluate_peeps.evaluate_peeps(-2, "gpt-4o")
    click.echo.assert_called_once_with(
        "An unexpected error occurred: The number of iterations must be a positive integer.",
        err=True,
    )


@mock.patch("peepsai.cli.evaluate_peeps.click")
@mock.patch("peepsai.cli.evaluate_peeps.subprocess.run")
def test_test_peeps_called_process_error(mock_subprocess_run, click):
    n_iterations = 5
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["uv", "run", "test", str(n_iterations), "gpt-4o"],
        output="Error",
        stderr="Some error occurred",
    )
    evaluate_peeps.evaluate_peeps(n_iterations, "gpt-4o")

    mock_subprocess_run.assert_called_once_with(
        ["uv", "run", "test", "5", "gpt-4o"],
        capture_output=False,
        text=True,
        check=True,
    )
    click.echo.assert_has_calls(
        [
            mock.call.echo(
                "An error occurred while testing the peeps: Command '['uv', 'run', 'test', '5', 'gpt-4o']' returned non-zero exit status 1.",
                err=True,
            ),
            mock.call.echo("Error", err=True),
        ]
    )


@mock.patch("peepsai.cli.evaluate_peeps.click")
@mock.patch("peepsai.cli.evaluate_peeps.subprocess.run")
def test_test_peeps_unexpected_exception(mock_subprocess_run, click):
    # Arrange
    n_iterations = 5
    mock_subprocess_run.side_effect = Exception("Unexpected error")
    evaluate_peeps.evaluate_peeps(n_iterations, "gpt-4o")

    mock_subprocess_run.assert_called_once_with(
        ["uv", "run", "test", "5", "gpt-4o"],
        capture_output=False,
        text=True,
        check=True,
    )
    click.echo.assert_called_once_with(
        "An unexpected error occurred: Unexpected error", err=True
    )
