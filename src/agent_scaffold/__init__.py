"""agent-scaffold: generate runnable AI agent projects from markdown specs."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("agent-scaffold")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
