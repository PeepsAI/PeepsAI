from __future__ import annotations

import asyncio
import json
import os
import platform
import warnings
from contextlib import contextmanager
from importlib.metadata import version
from typing import TYPE_CHECKING, Any, Optional


@contextmanager
def suppress_warnings():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        yield


from opentelemetry import trace  # noqa: E402
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,  # noqa: E402
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource  # noqa: E402
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
from opentelemetry.sdk.trace.export import BatchSpanProcessor  # noqa: E402
from opentelemetry.trace import Span, Status, StatusCode  # noqa: E402

if TYPE_CHECKING:
    from peepsai.peeps import Peeps
    from peepsai.task import Task


class Telemetry:
    """A class to handle anonymous telemetry for the peepsai package.

    The data being collected is for development purpose, all data is anonymous.

    There is NO data being collected on the prompts, tasks descriptions
    agents backstories or goals nor responses or any data that is being
    processed by the agents, nor any secrets and env vars.

    Users can opt-in to sharing more complete data using the `share_peeps`
    attribute in the Peeps class.
    """

    def __init__(self):
        self.ready = False
        self.trace_set = False

        if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
            return

        try:
            telemetry_endpoint = "https://telemetry.peepsai.io:4319"
            self.resource = Resource(
                attributes={SERVICE_NAME: "peepsAI-telemetry"},
            )
            with suppress_warnings():
                self.provider = TracerProvider(resource=self.resource)

            processor = BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=f"{telemetry_endpoint}/v1/traces",
                    timeout=30,
                )
            )

            self.provider.add_span_processor(processor)
            self.ready = True
        except Exception as e:
            if isinstance(
                e,
                (SystemExit, KeyboardInterrupt, GeneratorExit, asyncio.CancelledError),
            ):
                raise  # Re-raise the exception to not interfere with system signals
            self.ready = False

    def set_tracer(self):
        if self.ready and not self.trace_set:
            try:
                with suppress_warnings():
                    trace.set_tracer_provider(self.provider)
                    self.trace_set = True
            except Exception:
                self.ready = False
                self.trace_set = False

    def _safe_telemetry_operation(self, operation):
        if not self.ready:
            return
        try:
            operation()
        except Exception:
            pass

    def peeps_creation(self, peeps: Peeps, inputs: dict[str, Any] | None):
        """Records the creation of a peeps."""

        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Peeps Created")
            self._add_attribute(
                span,
                "peepsai_version",
                version("peepsai"),
            )
            self._add_attribute(span, "python_version", platform.python_version())
            self._add_attribute(span, "peeps_key", peeps.key)
            self._add_attribute(span, "peeps_id", str(peeps.id))
            self._add_attribute(span, "peeps_process", peeps.process)
            self._add_attribute(span, "peeps_memory", peeps.memory)
            self._add_attribute(span, "peeps_number_of_tasks", len(peeps.tasks))
            self._add_attribute(span, "peeps_number_of_agents", len(peeps.agents))
            if peeps.share_peeps:
                self._add_attribute(
                    span,
                    "peeps_agents",
                    json.dumps(
                        [
                            {
                                "key": agent.key,
                                "id": str(agent.id),
                                "role": agent.role,
                                "goal": agent.goal,
                                "backstory": agent.backstory,
                                "verbose?": agent.verbose,
                                "max_iter": agent.max_iter,
                                "max_rpm": agent.max_rpm,
                                "i18n": agent.i18n.prompt_file,
                                "function_calling_llm": (
                                    agent.function_calling_llm.model
                                    if agent.function_calling_llm
                                    else ""
                                ),
                                "llm": agent.llm.model,
                                "delegation_enabled?": agent.allow_delegation,
                                "allow_code_execution?": agent.allow_code_execution,
                                "max_retry_limit": agent.max_retry_limit,
                                "tools_names": [
                                    tool.name.casefold() for tool in agent.tools or []
                                ],
                            }
                            for agent in peeps.agents
                        ]
                    ),
                )
                self._add_attribute(
                    span,
                    "peeps_tasks",
                    json.dumps(
                        [
                            {
                                "key": task.key,
                                "id": str(task.id),
                                "description": task.description,
                                "expected_output": task.expected_output,
                                "async_execution?": task.async_execution,
                                "human_input?": task.human_input,
                                "agent_role": (
                                    task.agent.role if task.agent else "None"
                                ),
                                "agent_key": task.agent.key if task.agent else None,
                                "context": (
                                    [task.description for task in task.context]
                                    if task.context
                                    else None
                                ),
                                "tools_names": [
                                    tool.name.casefold() for tool in task.tools or []
                                ],
                            }
                            for task in peeps.tasks
                        ]
                    ),
                )
                self._add_attribute(span, "platform", platform.platform())
                self._add_attribute(span, "platform_release", platform.release())
                self._add_attribute(span, "platform_system", platform.system())
                self._add_attribute(span, "platform_version", platform.version())
                self._add_attribute(span, "cpus", os.cpu_count())
                self._add_attribute(
                    span, "peeps_inputs", json.dumps(inputs) if inputs else None
                )
            else:
                self._add_attribute(
                    span,
                    "peeps_agents",
                    json.dumps(
                        [
                            {
                                "key": agent.key,
                                "id": str(agent.id),
                                "role": agent.role,
                                "verbose?": agent.verbose,
                                "max_iter": agent.max_iter,
                                "max_rpm": agent.max_rpm,
                                "function_calling_llm": (
                                    agent.function_calling_llm.model
                                    if agent.function_calling_llm
                                    else ""
                                ),
                                "llm": agent.llm.model,
                                "delegation_enabled?": agent.allow_delegation,
                                "allow_code_execution?": agent.allow_code_execution,
                                "max_retry_limit": agent.max_retry_limit,
                                "tools_names": [
                                    tool.name.casefold() for tool in agent.tools or []
                                ],
                            }
                            for agent in peeps.agents
                        ]
                    ),
                )
                self._add_attribute(
                    span,
                    "peeps_tasks",
                    json.dumps(
                        [
                            {
                                "key": task.key,
                                "id": str(task.id),
                                "async_execution?": task.async_execution,
                                "human_input?": task.human_input,
                                "agent_role": (
                                    task.agent.role if task.agent else "None"
                                ),
                                "agent_key": task.agent.key if task.agent else None,
                                "tools_names": [
                                    tool.name.casefold() for tool in task.tools or []
                                ],
                            }
                            for task in peeps.tasks
                        ]
                    ),
                )
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def task_started(self, peeps: Peeps, task: Task) -> Span | None:
        """Records task started in a peeps."""

        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")

            created_span = tracer.start_span("Task Created")

            self._add_attribute(created_span, "peeps_key", peeps.key)
            self._add_attribute(created_span, "peeps_id", str(peeps.id))
            self._add_attribute(created_span, "task_key", task.key)
            self._add_attribute(created_span, "task_id", str(task.id))

            if peeps.share_peeps:
                self._add_attribute(
                    created_span, "formatted_description", task.description
                )
                self._add_attribute(
                    created_span, "formatted_expected_output", task.expected_output
                )

            created_span.set_status(Status(StatusCode.OK))
            created_span.end()

            span = tracer.start_span("Task Execution")

            self._add_attribute(span, "peeps_key", peeps.key)
            self._add_attribute(span, "peeps_id", str(peeps.id))
            self._add_attribute(span, "task_key", task.key)
            self._add_attribute(span, "task_id", str(task.id))

            if peeps.share_peeps:
                self._add_attribute(span, "formatted_description", task.description)
                self._add_attribute(
                    span, "formatted_expected_output", task.expected_output
                )

            return span

        return self._safe_telemetry_operation(operation)

    def task_ended(self, span: Span, task: Task, peeps: Peeps):
        """Records task execution in a peeps."""

        def operation():
            if peeps.share_peeps:
                self._add_attribute(
                    span,
                    "task_output",
                    task.output.raw if task.output else "",
                )

            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def tool_repeated_usage(self, llm: Any, tool_name: str, attempts: int):
        """Records the repeated usage 'error' of a tool by an agent."""

        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Tool Repeated Usage")
            self._add_attribute(
                span,
                "peepsai_version",
                version("peepsai"),
            )
            self._add_attribute(span, "tool_name", tool_name)
            self._add_attribute(span, "attempts", attempts)
            if llm:
                self._add_attribute(span, "llm", llm.model)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def tool_usage(self, llm: Any, tool_name: str, attempts: int):
        """Records the usage of a tool by an agent."""

        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Tool Usage")
            self._add_attribute(
                span,
                "peepsai_version",
                version("peepsai"),
            )
            self._add_attribute(span, "tool_name", tool_name)
            self._add_attribute(span, "attempts", attempts)
            if llm:
                self._add_attribute(span, "llm", llm.model)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def tool_usage_error(self, llm: Any):
        """Records the usage of a tool by an agent."""

        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Tool Usage Error")
            self._add_attribute(
                span,
                "peepsai_version",
                version("peepsai"),
            )
            if llm:
                self._add_attribute(span, "llm", llm.model)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def individual_test_result_span(
        self, peeps: Peeps, quality: float, exec_time: int, model_name: str
    ):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Peeps Individual Test Result")

            self._add_attribute(
                span,
                "peepsai_version",
                version("peepsai"),
            )
            self._add_attribute(span, "peeps_key", peeps.key)
            self._add_attribute(span, "peeps_id", str(peeps.id))
            self._add_attribute(span, "quality", str(quality))
            self._add_attribute(span, "exec_time", str(exec_time))
            self._add_attribute(span, "model_name", model_name)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def test_execution_span(
        self,
        peeps: Peeps,
        iterations: int,
        inputs: dict[str, Any] | None,
        model_name: str,
    ):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Peeps Test Execution")

            self._add_attribute(
                span,
                "peepsai_version",
                version("peepsai"),
            )
            self._add_attribute(span, "peeps_key", peeps.key)
            self._add_attribute(span, "peeps_id", str(peeps.id))
            self._add_attribute(span, "iterations", str(iterations))
            self._add_attribute(span, "model_name", model_name)

            if peeps.share_peeps:
                self._add_attribute(
                    span, "inputs", json.dumps(inputs) if inputs else None
                )

            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def deploy_signup_error_span(self):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Deploy Signup Error")
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def start_deployment_span(self, uuid: Optional[str] = None):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Start Deployment")
            if uuid:
                self._add_attribute(span, "uuid", uuid)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def create_peeps_deployment_span(self):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Create Peeps Deployment")
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def get_peeps_logs_span(self, uuid: Optional[str], log_type: str = "deployment"):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Get Peeps Logs")
            self._add_attribute(span, "log_type", log_type)
            if uuid:
                self._add_attribute(span, "uuid", uuid)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def remove_peeps_span(self, uuid: Optional[str] = None):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Remove Peeps")
            if uuid:
                self._add_attribute(span, "uuid", uuid)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def peeps_execution_span(self, peeps: Peeps, inputs: dict[str, Any] | None):
        """Records the complete execution of a peeps.
        This is only collected if the user has opted-in to share the peeps.
        """
        self.peeps_creation(peeps, inputs)

        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Peeps Execution")
            self._add_attribute(
                span,
                "peepsai_version",
                version("peepsai"),
            )
            self._add_attribute(span, "peeps_key", peeps.key)
            self._add_attribute(span, "peeps_id", str(peeps.id))
            self._add_attribute(
                span, "peeps_inputs", json.dumps(inputs) if inputs else None
            )
            self._add_attribute(
                span,
                "peeps_agents",
                json.dumps(
                    [
                        {
                            "key": agent.key,
                            "id": str(agent.id),
                            "role": agent.role,
                            "goal": agent.goal,
                            "backstory": agent.backstory,
                            "verbose?": agent.verbose,
                            "max_iter": agent.max_iter,
                            "max_rpm": agent.max_rpm,
                            "i18n": agent.i18n.prompt_file,
                            "llm": agent.llm.model,
                            "delegation_enabled?": agent.allow_delegation,
                            "tools_names": [
                                tool.name.casefold() for tool in agent.tools or []
                            ],
                        }
                        for agent in peeps.agents
                    ]
                ),
            )
            self._add_attribute(
                span,
                "peeps_tasks",
                json.dumps(
                    [
                        {
                            "id": str(task.id),
                            "description": task.description,
                            "expected_output": task.expected_output,
                            "async_execution?": task.async_execution,
                            "human_input?": task.human_input,
                            "agent_role": task.agent.role if task.agent else "None",
                            "agent_key": task.agent.key if task.agent else None,
                            "context": (
                                [task.description for task in task.context]
                                if task.context
                                else None
                            ),
                            "tools_names": [
                                tool.name.casefold() for tool in task.tools or []
                            ],
                        }
                        for task in peeps.tasks
                    ]
                ),
            )
            return span

        if peeps.share_peeps:
            return self._safe_telemetry_operation(operation)
        return None

    def end_peeps(self, peeps, final_string_output):
        def operation():
            self._add_attribute(
                peeps._execution_span,
                "peepsai_version",
                version("peepsai"),
            )
            self._add_attribute(
                peeps._execution_span, "peeps_output", final_string_output
            )
            self._add_attribute(
                peeps._execution_span,
                "peeps_tasks_output",
                json.dumps(
                    [
                        {
                            "id": str(task.id),
                            "description": task.description,
                            "output": task.output.raw_output,
                        }
                        for task in peeps.tasks
                    ]
                ),
            )
            peeps._execution_span.set_status(Status(StatusCode.OK))
            peeps._execution_span.end()

        if peeps.share_peeps:
            self._safe_telemetry_operation(operation)

    def _add_attribute(self, span, key, value):
        """Add an attribute to a span."""

        def operation():
            return span.set_attribute(key, value)

        self._safe_telemetry_operation(operation)

    def flow_creation_span(self, flow_name: str):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Flow Creation")
            self._add_attribute(span, "flow_name", flow_name)
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def flow_plotting_span(self, flow_name: str, node_names: list[str]):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Flow Plotting")
            self._add_attribute(span, "flow_name", flow_name)
            self._add_attribute(span, "node_names", json.dumps(node_names))
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)

    def flow_execution_span(self, flow_name: str, node_names: list[str]):
        def operation():
            tracer = trace.get_tracer("peepsai.telemetry")
            span = tracer.start_span("Flow Execution")
            self._add_attribute(span, "flow_name", flow_name)
            self._add_attribute(span, "node_names", json.dumps(node_names))
            span.set_status(Status(StatusCode.OK))
            span.end()

        self._safe_telemetry_operation(operation)
