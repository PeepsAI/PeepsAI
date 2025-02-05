from peepsai import Agent, Peeps, Process, Task
from peepsai.project import PeepsBase, agent, peeps, task

# If you want to run a snippet of code before or after the peeps starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.peepsai.com/concepts/peepz#example-peeps-class-with-decorators


@PeepsBase
class PoemPeeps:
    """Poem Peeps"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.peepsai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.peepsai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would lik to add tools to your peeps, you can learn more about it here:
    # https://docs.peepsai.com/concepts/agents#agent-tools
    @agent
    def poem_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["poem_writer"],
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.peepsai.com/concepts/tasks#overview-of-a-task
    @task
    def write_poem(self) -> Task:
        return Task(
            config=self.tasks_config["write_poem"],
        )

    @peeps
    def peeps(self) -> Peeps:
        """Creates the Research Peeps"""
        # To learn how to add knowledge sources to your peeps, check out the documentation:
        # https://docs.peepsai.com/concepts/knowledge#what-is-knowledge

        return Peeps(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
