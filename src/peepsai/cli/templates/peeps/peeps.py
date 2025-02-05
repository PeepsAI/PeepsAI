from peepsai import Agent, Peeps, Process, Task
from peepsai.project import PeepsBase, agent, peeps, task

# If you want to run a snippet of code before or after the peeps starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.peepsai.io/concepts/peepz#example-peeps-class-with-decorators

@PeepsBase
class {{peeps_name}}():
	"""{{peeps_name}} peeps"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.peepsai.io/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.peepsai.io/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.peepsai.io/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.peepsai.io/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@peeps
	def peeps(self) -> Peeps:
		"""Creates the {{peeps_name}} peeps"""
		# To learn how to add knowledge sources to your peeps, check out the documentation:
		# https://docs.peepsai.io/concepts/knowledge#what-is-knowledge

		return Peeps(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.peepsai.io/how-to/Hierarchical/
		)
