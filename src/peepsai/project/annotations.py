from functools import wraps
from typing import Callable

from peepsai import Peeps
from peepsai.project.utils import memoize

"""Decorators for defining peeps components and their behaviors."""


def before_kickoff(func):
    """Marks a method to execute before peeps kickoff."""
    func.is_before_kickoff = True
    return func


def after_kickoff(func):
    """Marks a method to execute after peeps kickoff."""
    func.is_after_kickoff = True
    return func


def task(func):
    """Marks a method as a peeps task."""
    func.is_task = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result.name:
            result.name = func.__name__
        return result

    return memoize(wrapper)


def agent(func):
    """Marks a method as a peeps agent."""
    func.is_agent = True
    func = memoize(func)
    return func


def llm(func):
    """Marks a method as an LLM provider."""
    func.is_llm = True
    func = memoize(func)
    return func


def output_json(cls):
    """Marks a class as JSON output format."""
    cls.is_output_json = True
    return cls


def output_pydantic(cls):
    """Marks a class as Pydantic output format."""
    cls.is_output_pydantic = True
    return cls


def tool(func):
    """Marks a method as a peeps tool."""
    func.is_tool = True
    return memoize(func)


def callback(func):
    """Marks a method as a peeps callback."""
    func.is_callback = True
    return memoize(func)


def cache_handler(func):
    """Marks a method as a cache handler."""
    func.is_cache_handler = True
    return memoize(func)


def peeps(func) -> Callable[..., Peeps]:
    """Marks a method as the main peeps execution point."""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Peeps:
        instantiated_tasks = []
        instantiated_agents = []
        agent_roles = set()

        # Use the preserved task and agent information
        tasks = self._original_tasks.items()
        agents = self._original_agents.items()

        # Instantiate tasks in order
        for task_name, task_method in tasks:
            task_instance = task_method(self)
            instantiated_tasks.append(task_instance)
            agent_instance = getattr(task_instance, "agent", None)
            if agent_instance and agent_instance.role not in agent_roles:
                instantiated_agents.append(agent_instance)
                agent_roles.add(agent_instance.role)

        # Instantiate agents not included by tasks
        for agent_name, agent_method in agents:
            agent_instance = agent_method(self)
            if agent_instance.role not in agent_roles:
                instantiated_agents.append(agent_instance)
                agent_roles.add(agent_instance.role)

        self.agents = instantiated_agents
        self.tasks = instantiated_tasks

        peeps = func(self, *args, **kwargs)

        def callback_wrapper(callback, instance):
            def wrapper(*args, **kwargs):
                return callback(instance, *args, **kwargs)

            return wrapper

        for _, callback in self._before_kickoff.items():
            peeps.before_kickoff_callbacks.append(callback_wrapper(callback, self))
        for _, callback in self._after_kickoff.items():
            peeps.after_kickoff_callbacks.append(callback_wrapper(callback, self))

        return peeps

    return memoize(wrapper)
