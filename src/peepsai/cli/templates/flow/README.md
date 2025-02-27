# {{peeps_name}} Peeps

Welcome to the {{peeps_name}} project, powered by [Peeps AI](https://peepsai.io). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by Peeps AI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
peepsai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/{{folder_name}}/config/agents.yaml` to define your agents
- Modify `src/{{folder_name}}/config/tasks.yaml` to define your tasks
- Modify `src/{{folder_name}}/peeps.py` to add your own logic, tools and specific args
- Modify `src/{{folder_name}}/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your peeps of AI agents and begin task execution, run this from the root folder of your project:

```bash
peepsai run
```

This command initializes the {{name}} Peeps, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Peeps

The {{name}} Peeps is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your peeps.

## Support

For support, questions, or feedback regarding the {{peeps_name}} Peeps or Peeps AI.

- Visit our [documentation](https://docs.peepsai.io)
- Reach out to us through our [GitHub repository](https://github.com/PeepsAI/peepsai)
- [Join our Telegram](https://t.me/peeps_ai)

Let's create wonders together with the power and simplicity of Peeps AI.
