#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from {{folder_name}}.peeps import {{peeps_name}}

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# peeps locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the peeps.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }
    
    try:
        {{peeps_name}}().peeps().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the peeps: {e}")


def train():
    """
    Train the peeps for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        {{peeps_name}}().peeps().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the peeps: {e}")

def replay():
    """
    Replay the peeps execution from a specific task.
    """
    try:
        {{peeps_name}}().peeps().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the peeps: {e}")

def test():
    """
    Test the peeps execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        {{peeps_name}}().peeps().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the peeps: {e}")
