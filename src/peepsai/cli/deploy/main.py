from typing import Any, Dict, List, Optional

from rich.console import Console

from peepsai.cli import git
from peepsai.cli.command import BaseCommand, PlusAPIMixin
from peepsai.cli.utils import fetch_and_json_env_file, get_project_name

console = Console()


class DeployCommand(BaseCommand, PlusAPIMixin):
    """
    A class to handle deployment-related operations for PeepsAI projects.
    """

    def __init__(self):
        """
        Initialize the DeployCommand with project name and API client.
        """

        BaseCommand.__init__(self)
        PlusAPIMixin.__init__(self, telemetry=self._telemetry)
        self.project_name = get_project_name(require=True)

    def _standard_no_param_error_message(self) -> None:
        """
        Display a standard error message when no UUID or project name is available.
        """
        console.print(
            "No UUID provided, project pyproject.toml not found or with error.",
            style="bold red",
        )

    def _display_deployment_info(self, json_response: Dict[str, Any]) -> None:
        """
        Display deployment information.

        Args:
            json_response (Dict[str, Any]): The deployment information to display.
        """
        console.print("Deploying the peeps...\n", style="bold blue")
        for key, value in json_response.items():
            console.print(f"{key.title()}: [green]{value}[/green]")
        console.print("\nTo check the status of the deployment, run:")
        console.print("peepsai deploy status")
        console.print(" or")
        console.print(f"peepsai deploy status --uuid \"{json_response['uuid']}\"")

    def _display_logs(self, log_messages: List[Dict[str, Any]]) -> None:
        """
        Display log messages.

        Args:
            log_messages (List[Dict[str, Any]]): The log messages to display.
        """
        for log_message in log_messages:
            console.print(
                f"{log_message['timestamp']} - {log_message['level']}: {log_message['message']}"
            )

    def deploy(self, uuid: Optional[str] = None) -> None:
        """
        Deploy a peeps using either UUID or project name.

        Args:
            uuid (Optional[str]): The UUID of the peeps to deploy.
        """
        self._start_deployment_span = self._telemetry.start_deployment_span(uuid)
        console.print("Starting deployment...", style="bold blue")
        if uuid:
            response = self.plus_api_client.deploy_by_uuid(uuid)
        elif self.project_name:
            response = self.plus_api_client.deploy_by_name(self.project_name)
        else:
            self._standard_no_param_error_message()
            return

        self._validate_response(response)
        self._display_deployment_info(response.json())

    def create_peeps(self, confirm: bool = False) -> None:
        """
        Create a new peeps deployment.
        """
        self._create_peeps_deployment_span = (
            self._telemetry.create_peeps_deployment_span()
        )
        console.print("Creating deployment...", style="bold blue")
        env_vars = fetch_and_json_env_file()

        try:
            remote_repo_url = git.Repository().origin_url()
        except ValueError:
            remote_repo_url = None

        if remote_repo_url is None:
            console.print("No remote repository URL found.", style="bold red")
            console.print(
                "Please ensure your project has a valid remote repository.",
                style="yellow",
            )
            return

        self._confirm_input(env_vars, remote_repo_url, confirm)
        payload = self._create_payload(env_vars, remote_repo_url)
        response = self.plus_api_client.create_peeps(payload)

        self._validate_response(response)
        self._display_creation_success(response.json())

    def _confirm_input(
        self, env_vars: Dict[str, str], remote_repo_url: str, confirm: bool
    ) -> None:
        """
        Confirm input parameters with the user.

        Args:
            env_vars (Dict[str, str]): Environment variables.
            remote_repo_url (str): Remote repository URL.
            confirm (bool): Whether to confirm input.
        """
        if not confirm:
            input(f"Press Enter to continue with the following Env vars: {env_vars}")
            input(
                f"Press Enter to continue with the following remote repository: {remote_repo_url}\n"
            )

    def _create_payload(
        self,
        env_vars: Dict[str, str],
        remote_repo_url: str,
    ) -> Dict[str, Any]:
        """
        Create the payload for peeps creation.

        Args:
            remote_repo_url (str): Remote repository URL.
            env_vars (Dict[str, str]): Environment variables.

        Returns:
            Dict[str, Any]: The payload for peeps creation.
        """
        return {
            "deploy": {
                "name": self.project_name,
                "repo_clone_url": remote_repo_url,
                "env": env_vars,
            }
        }

    def _display_creation_success(self, json_response: Dict[str, Any]) -> None:
        """
        Display success message after peeps creation.

        Args:
            json_response (Dict[str, Any]): The response containing peeps information.
        """
        console.print("Deployment created successfully!\n", style="bold green")
        console.print(
            f"Name: {self.project_name} ({json_response['uuid']})", style="bold green"
        )
        console.print(f"Status: {json_response['status']}", style="bold green")
        console.print("\nTo (re)deploy the peeps, run:")
        console.print("peepsai deploy push")
        console.print(" or")
        console.print(f"peepsai deploy push --uuid {json_response['uuid']}")

    def list_peepz(self) -> None:
        """
        List all available peepz.
        """
        console.print("Listing all Peepz\n", style="bold blue")

        response = self.plus_api_client.list_peepz()
        json_response = response.json()
        if response.status_code == 200:
            self._display_peepz(json_response)
        else:
            self._display_no_peepz_message()

    def _display_peepz(self, peepz_data: List[Dict[str, Any]]) -> None:
        """
        Display the list of peepz.

        Args:
            peepz_data (List[Dict[str, Any]]): List of peeps data to display.
        """
        for peeps_data in peepz_data:
            console.print(
                f"- {peeps_data['name']} ({peeps_data['uuid']}) [blue]{peeps_data['status']}[/blue]"
            )

    def _display_no_peepz_message(self) -> None:
        """
        Display a message when no peepz are available.
        """
        console.print("You don't have any Peepz yet. Let's create one!", style="yellow")
        console.print("  peepsai create peeps <peeps_name>", style="green")

    def get_peeps_status(self, uuid: Optional[str] = None) -> None:
        """
        Get the status of a peeps.

        Args:
            uuid (Optional[str]): The UUID of the peeps to check.
        """
        console.print("Fetching deployment status...", style="bold blue")
        if uuid:
            response = self.plus_api_client.peeps_status_by_uuid(uuid)
        elif self.project_name:
            response = self.plus_api_client.peeps_status_by_name(self.project_name)
        else:
            self._standard_no_param_error_message()
            return

        self._validate_response(response)
        self._display_peeps_status(response.json())

    def _display_peeps_status(self, status_data: Dict[str, str]) -> None:
        """
        Display the status of a peeps.

        Args:
            status_data (Dict[str, str]): The status data to display.
        """
        console.print(f"Name:\t {status_data['name']}")
        console.print(f"Status:\t {status_data['status']}")

    def get_peeps_logs(self, uuid: Optional[str], log_type: str = "deployment") -> None:
        """
        Get logs for a peeps.

        Args:
            uuid (Optional[str]): The UUID of the peeps to get logs for.
            log_type (str): The type of logs to retrieve (default: "deployment").
        """
        self._get_peeps_logs_span = self._telemetry.get_peeps_logs_span(uuid, log_type)
        console.print(f"Fetching {log_type} logs...", style="bold blue")

        if uuid:
            response = self.plus_api_client.peeps_by_uuid(uuid, log_type)
        elif self.project_name:
            response = self.plus_api_client.peeps_by_name(self.project_name, log_type)
        else:
            self._standard_no_param_error_message()
            return

        self._validate_response(response)
        self._display_logs(response.json())

    def remove_peeps(self, uuid: Optional[str]) -> None:
        """
        Remove a peeps deployment.

        Args:
            uuid (Optional[str]): The UUID of the peeps to remove.
        """
        self._remove_peeps_span = self._telemetry.remove_peeps_span(uuid)
        console.print("Removing deployment...", style="bold blue")

        if uuid:
            response = self.plus_api_client.delete_peeps_by_uuid(uuid)
        elif self.project_name:
            response = self.plus_api_client.delete_peeps_by_name(self.project_name)
        else:
            self._standard_no_param_error_message()
            return

        if response.status_code == 204:
            console.print(
                f"Peeps '{self.project_name}' removed successfully.", style="green"
            )
        else:
            console.print(
                f"Failed to remove peeps '{self.project_name}'", style="bold red"
            )
