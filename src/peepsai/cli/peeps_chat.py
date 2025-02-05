import json
import platform
import re
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import click
import tomli
from packaging import version

from peepsai.cli.utils import read_toml
from peepsai.cli.version import get_peepsai_version
from peepsai.peeps import Peeps
from peepsai.llm import LLM
from peepsai.types.peeps_chat import ChatInputField, ChatInputs
from peepsai.utilities.llm_utils import create_llm

MIN_REQUIRED_VERSION = "0.98.0"


def check_conversational_peepz_version(
    peepsai_version: str, pyproject_data: dict
) -> bool:
    """
    Check if the installed peepsAI version supports conversational peepz.

    Args:
        peepsai_version: The current version of peepsAI.
        pyproject_data: Dictionary containing pyproject.toml data.

    Returns:
        bool: True if version check passes, False otherwise.
    """
    try:
        if version.parse(peepsai_version) < version.parse(MIN_REQUIRED_VERSION):
            click.secho(
                "You are using an older version of peepsAI that doesn't support conversational peepz. "
                "Run 'uv upgrade peepsai' to get the latest version.",
                fg="red",
            )
            return False
    except version.InvalidVersion:
        click.secho("Invalid peepsAI version format detected.", fg="red")
        return False
    return True


def run_chat():
    """
    Runs an interactive chat loop using the Peeps's chat LLM with function calling.
    Incorporates peeps_name, peeps_description, and input fields to build a tool schema.
    Exits if peeps_name or peeps_description are missing.
    """
    peepsai_version = get_peepsai_version()
    pyproject_data = read_toml()

    if not check_conversational_peepz_version(peepsai_version, pyproject_data):
        return

    peeps, peeps_name = load_peeps_and_name()
    chat_llm = initialize_chat_llm(peeps)
    if not chat_llm:
        return

    # Indicate that the peeps is being analyzed
    click.secho(
        "\nAnalyzing peeps and required inputs - this may take 3 to 30 seconds "
        "depending on the complexity of your peeps.",
        fg="white",
    )

    # Start loading indicator
    loading_complete = threading.Event()
    loading_thread = threading.Thread(target=show_loading, args=(loading_complete,))
    loading_thread.start()

    try:
        peeps_chat_inputs = generate_peeps_chat_inputs(peeps, peeps_name, chat_llm)
        peeps_tool_schema = generate_peeps_tool_schema(peeps_chat_inputs)
        system_message = build_system_message(peeps_chat_inputs)

        # Call the LLM to generate the introductory message
        introductory_message = chat_llm.call(
            messages=[{"role": "system", "content": system_message}]
        )
    finally:
        # Stop loading indicator
        loading_complete.set()
        loading_thread.join()

    # Indicate that the analysis is complete
    click.secho("\nFinished analyzing peeps.\n", fg="white")

    click.secho(f"Assistant: {introductory_message}\n", fg="green")

    messages = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": introductory_message},
    ]

    available_functions = {
        peeps_chat_inputs.peeps_name: create_tool_function(peeps, messages),
    }

    chat_loop(chat_llm, messages, peeps_tool_schema, available_functions)


def show_loading(event: threading.Event):
    """Display animated loading dots while processing."""
    while not event.is_set():
        print(".", end="", flush=True)
        time.sleep(1)
    print()


def initialize_chat_llm(peeps: Peeps) -> Optional[LLM]:
    """Initializes the chat LLM and handles exceptions."""
    try:
        return create_llm(peeps.chat_llm)
    except Exception as e:
        click.secho(
            f"Unable to find a Chat LLM. Please make sure you set chat_llm on the peeps: {e}",
            fg="red",
        )
        return None


def build_system_message(peeps_chat_inputs: ChatInputs) -> str:
    """Builds the initial system message for the chat."""
    required_fields_str = (
        ", ".join(
            f"{field.name} (desc: {field.description or 'n/a'})"
            for field in peeps_chat_inputs.inputs
        )
        or "(No required fields detected)"
    )

    return (
        "You are a helpful AI assistant for the PeepsAI platform. "
        "Your primary purpose is to assist users with the peeps's specific tasks. "
        "You can answer general questions, but should guide users back to the peeps's purpose afterward. "
        "For example, after answering a general question, remind the user of your main purpose, such as generating a research report, and prompt them to specify a topic or task related to the peeps's purpose. "
        "You have a function (tool) you can call by name if you have all required inputs. "
        f"Those required inputs are: {required_fields_str}. "
        "Once you have them, call the function. "
        "Please keep your responses concise and friendly. "
        "If a user asks a question outside the peeps's scope, provide a brief answer and remind them of the peeps's purpose. "
        "After calling the tool, be prepared to take user feedback and make adjustments as needed. "
        "If you are ever unsure about a user's request or need clarification, ask the user for more information. "
        "Before doing anything else, introduce yourself with a friendly message like: 'Hey! I'm here to help you with [peeps's purpose]. Could you please provide me with [inputs] so we can get started?' "
        "For example: 'Hey! I'm here to help you with uncovering and reporting cutting-edge developments through thorough research and detailed analysis. Could you please provide me with a topic you're interested in? This will help us generate a comprehensive research report and detailed analysis.'"
        f"\nPeeps Name: {peeps_chat_inputs.peeps_name}"
        f"\nPeeps Description: {peeps_chat_inputs.peeps_description}"
    )


def create_tool_function(peeps: Peeps, messages: List[Dict[str, str]]) -> Any:
    """Creates a wrapper function for running the peeps tool with messages."""

    def run_peeps_tool_with_messages(**kwargs):
        return run_peeps_tool(peeps, messages, **kwargs)

    return run_peeps_tool_with_messages


def flush_input():
    """Flush any pending input from the user."""
    if platform.system() == "Windows":
        # Windows platform
        import msvcrt

        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        # Unix-like platforms (Linux, macOS)
        import termios

        termios.tcflush(sys.stdin, termios.TCIFLUSH)


def chat_loop(chat_llm, messages, peeps_tool_schema, available_functions):
    """Main chat loop for interacting with the user."""
    while True:
        try:
            # Flush any pending input before accepting new input
            flush_input()

            user_input = get_user_input()
            handle_user_input(
                user_input, chat_llm, messages, peeps_tool_schema, available_functions
            )

        except KeyboardInterrupt:
            click.echo("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            click.secho(f"An error occurred: {e}", fg="red")
            break


def get_user_input() -> str:
    """Collect multi-line user input with exit handling."""
    click.secho(
        "\nYou (type your message below. Press 'Enter' twice when you're done):",
        fg="blue",
    )
    user_input_lines = []
    while True:
        line = input()
        if line.strip().lower() == "exit":
            return "exit"
        if line == "":
            break
        user_input_lines.append(line)
    return "\n".join(user_input_lines)


def handle_user_input(
    user_input: str,
    chat_llm: LLM,
    messages: List[Dict[str, str]],
    peeps_tool_schema: Dict[str, Any],
    available_functions: Dict[str, Any],
) -> None:
    if user_input.strip().lower() == "exit":
        click.echo("Exiting chat. Goodbye!")
        return

    if not user_input.strip():
        click.echo("Empty message. Please provide input or type 'exit' to quit.")
        return

    messages.append({"role": "user", "content": user_input})

    # Indicate that assistant is processing
    click.echo()
    click.secho("Assistant is processing your input. Please wait...", fg="green")

    # Process assistant's response
    final_response = chat_llm.call(
        messages=messages,
        tools=[peeps_tool_schema],
        available_functions=available_functions,
    )

    messages.append({"role": "assistant", "content": final_response})
    click.secho(f"\nAssistant: {final_response}\n", fg="green")


def generate_peeps_tool_schema(peeps_inputs: ChatInputs) -> dict:
    """
    Dynamically build a Littellm 'function' schema for the given peeps.

    peeps_name: The name of the peeps (used for the function 'name').
    peeps_inputs: A ChatInputs object containing peeps_description
                 and a list of input fields (each with a name & description).
    """
    properties = {}
    for field in peeps_inputs.inputs:
        properties[field.name] = {
            "type": "string",
            "description": field.description or "No description provided",
        }

    required_fields = [field.name for field in peeps_inputs.inputs]

    return {
        "type": "function",
        "function": {
            "name": peeps_inputs.peeps_name,
            "description": peeps_inputs.peeps_description or "No peeps description",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required_fields,
            },
        },
    }


def run_peeps_tool(peeps: Peeps, messages: List[Dict[str, str]], **kwargs):
    """
    Runs the peeps using peeps.kickoff(inputs=kwargs) and returns the output.

    Args:
        peeps (Peeps): The peeps instance to run.
        messages (List[Dict[str, str]]): The chat messages up to this point.
        **kwargs: The inputs collected from the user.

    Returns:
        str: The output from the peeps's execution.

    Raises:
        SystemExit: Exits the chat if an error occurs during peeps execution.
    """
    try:
        # Serialize 'messages' to JSON string before adding to kwargs
        kwargs["peeps_chat_messages"] = json.dumps(messages)

        # Run the peeps with the provided inputs
        peeps_output = peeps.kickoff(inputs=kwargs)

        # Convert PeepsOutput to a string to send back to the user
        result = str(peeps_output)

        return result
    except Exception as e:
        # Exit the chat and show the error message
        click.secho("An error occurred while running the peeps:", fg="red")
        click.secho(str(e), fg="red")
        sys.exit(1)


def load_peeps_and_name() -> Tuple[Peeps, str]:
    """
    Loads the peeps by importing the peeps class from the user's project.

    Returns:
        Tuple[Peeps, str]: A tuple containing the Peeps instance and the name of the peeps.
    """
    # Get the current working directory
    cwd = Path.cwd()

    # Path to the pyproject.toml file
    pyproject_path = cwd / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found in the current directory.")

    # Load the pyproject.toml file using 'tomli'
    with pyproject_path.open("rb") as f:
        pyproject_data = tomli.load(f)

    # Get the project name from the 'project' section
    project_name = pyproject_data["project"]["name"]
    folder_name = project_name

    # Derive the peeps class name from the project name
    # E.g., if project_name is 'my_project', peeps_class_name is 'MyProject'
    peeps_class_name = project_name.replace("_", " ").title().replace(" ", "")

    # Add the 'src' directory to sys.path
    src_path = cwd / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Import the peeps module
    peeps_module_name = f"{folder_name}.peeps"
    try:
        peeps_module = __import__(peeps_module_name, fromlist=[peeps_class_name])
    except ImportError as e:
        raise ImportError(f"Failed to import peeps module {peeps_module_name}: {e}")

    # Get the peeps class from the module
    try:
        peeps_class = getattr(peeps_module, peeps_class_name)
    except AttributeError:
        raise AttributeError(
            f"Peeps class {peeps_class_name} not found in module {peeps_module_name}"
        )

    # Instantiate the peeps
    peeps_instance = peeps_class().peeps()
    return peeps_instance, peeps_class_name


def generate_peeps_chat_inputs(peeps: Peeps, peeps_name: str, chat_llm) -> ChatInputs:
    """
    Generates the ChatInputs required for the peeps by analyzing the tasks and agents.

    Args:
        peeps (Peeps): The peeps object containing tasks and agents.
        peeps_name (str): The name of the peeps.
        chat_llm: The chat language model to use for AI calls.

    Returns:
        ChatInputs: An object containing the peeps's name, description, and input fields.
    """
    # Extract placeholders from tasks and agents
    required_inputs = fetch_required_inputs(peeps)

    # Generate descriptions for each input using AI
    input_fields = []
    for input_name in required_inputs:
        description = generate_input_description_with_ai(input_name, peeps, chat_llm)
        input_fields.append(ChatInputField(name=input_name, description=description))

    # Generate peeps description using AI
    peeps_description = generate_peeps_description_with_ai(peeps, chat_llm)

    return ChatInputs(
        peeps_name=peeps_name, peeps_description=peeps_description, inputs=input_fields
    )


def fetch_required_inputs(peeps: Peeps) -> Set[str]:
    """
    Extracts placeholders from the peeps's tasks and agents.

    Args:
        peeps (Peeps): The peeps object.

    Returns:
        Set[str]: A set of placeholder names.
    """
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    required_inputs: Set[str] = set()

    # Scan tasks
    for task in peeps.tasks:
        text = f"{task.description or ''} {task.expected_output or ''}"
        required_inputs.update(placeholder_pattern.findall(text))

    # Scan agents
    for agent in peeps.agents:
        text = f"{agent.role or ''} {agent.goal or ''} {agent.backstory or ''}"
        required_inputs.update(placeholder_pattern.findall(text))

    return required_inputs


def generate_input_description_with_ai(input_name: str, peeps: Peeps, chat_llm) -> str:
    """
    Generates an input description using AI based on the context of the peeps.

    Args:
        input_name (str): The name of the input placeholder.
        peeps (Peeps): The peeps object.
        chat_llm: The chat language model to use for AI calls.

    Returns:
        str: A concise description of the input.
    """
    # Gather context from tasks and agents where the input is used
    context_texts = []
    placeholder_pattern = re.compile(r"\{(.+?)\}")

    for task in peeps.tasks:
        if (
            f"{{{input_name}}}" in task.description
            or f"{{{input_name}}}" in task.expected_output
        ):
            # Replace placeholders with input names
            task_description = placeholder_pattern.sub(
                lambda m: m.group(1), task.description or ""
            )
            expected_output = placeholder_pattern.sub(
                lambda m: m.group(1), task.expected_output or ""
            )
            context_texts.append(f"Task Description: {task_description}")
            context_texts.append(f"Expected Output: {expected_output}")
    for agent in peeps.agents:
        if (
            f"{{{input_name}}}" in agent.role
            or f"{{{input_name}}}" in agent.goal
            or f"{{{input_name}}}" in agent.backstory
        ):
            # Replace placeholders with input names
            agent_role = placeholder_pattern.sub(lambda m: m.group(1), agent.role or "")
            agent_goal = placeholder_pattern.sub(lambda m: m.group(1), agent.goal or "")
            agent_backstory = placeholder_pattern.sub(
                lambda m: m.group(1), agent.backstory or ""
            )
            context_texts.append(f"Agent Role: {agent_role}")
            context_texts.append(f"Agent Goal: {agent_goal}")
            context_texts.append(f"Agent Backstory: {agent_backstory}")

    context = "\n".join(context_texts)
    if not context:
        # If no context is found for the input, raise an exception as per instruction
        raise ValueError(f"No context found for input '{input_name}'.")

    prompt = (
        f"Based on the following context, write a concise description (15 words or less) of the input '{input_name}'.\n"
        "Provide only the description, without any extra text or labels. Do not include placeholders like '{topic}' in the description.\n"
        "Context:\n"
        f"{context}"
    )
    response = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    description = response.strip()

    return description


def generate_peeps_description_with_ai(peeps: Peeps, chat_llm) -> str:
    """
    Generates a brief description of the peeps using AI.

    Args:
        peeps (Peeps): The peeps object.
        chat_llm: The chat language model to use for AI calls.

    Returns:
        str: A concise description of the peeps's purpose (15 words or less).
    """
    # Gather context from tasks and agents
    context_texts = []
    placeholder_pattern = re.compile(r"\{(.+?)\}")

    for task in peeps.tasks:
        # Replace placeholders with input names
        task_description = placeholder_pattern.sub(
            lambda m: m.group(1), task.description or ""
        )
        expected_output = placeholder_pattern.sub(
            lambda m: m.group(1), task.expected_output or ""
        )
        context_texts.append(f"Task Description: {task_description}")
        context_texts.append(f"Expected Output: {expected_output}")
    for agent in peeps.agents:
        # Replace placeholders with input names
        agent_role = placeholder_pattern.sub(lambda m: m.group(1), agent.role or "")
        agent_goal = placeholder_pattern.sub(lambda m: m.group(1), agent.goal or "")
        agent_backstory = placeholder_pattern.sub(
            lambda m: m.group(1), agent.backstory or ""
        )
        context_texts.append(f"Agent Role: {agent_role}")
        context_texts.append(f"Agent Goal: {agent_goal}")
        context_texts.append(f"Agent Backstory: {agent_backstory}")

    context = "\n".join(context_texts)
    if not context:
        raise ValueError("No context found for generating peeps description.")

    prompt = (
        "Based on the following context, write a concise, action-oriented description (15 words or less) of the peeps's purpose.\n"
        "Provide only the description, without any extra text or labels. Do not include placeholders like '{topic}' in the description.\n"
        "Context:\n"
        f"{context}"
    )
    response = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    peeps_description = response.strip()

    return peeps_description
