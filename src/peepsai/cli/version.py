import importlib.metadata


def get_peepsai_version() -> str:
    """Get the version number of PeepsAI running the CLI"""
    return importlib.metadata.version("peepsai")
