from dflow.plugins.dispatcher import DispatcherExecutor
from contextlib import contextmanager
from pathlib import Path
import os


@contextmanager
def set_directory(path: Path):
    """Sets the current working path within the context.

    Parameters
    ----------
    path : Path
        The path to the cwd

    Yields
    ------
    None

    Examples
    --------
    >>> with set_directory("some_path"):
    ...    do_something()
    """
    cwd = Path().absolute()
    path.mkdir(exist_ok=True, parents=True)
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def init_executor(
    executor_dict,
):
    if executor_dict is None:
        return None
    etype = executor_dict.pop("type")
    if etype == "dispatcher":
        return DispatcherExecutor(**executor_dict)
    else:
        raise RuntimeError("unknown executor type", etype)
    
workflow_subcommands = [
    "terminate",
    "stop",
    "suspend",
    "delete",
    "retry",
    "resume",
]