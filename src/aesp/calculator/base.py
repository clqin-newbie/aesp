from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
import dpdata
from ..utils.dpgen2 import set_directory
import os
import dargs
from dflow.python import OP, OPIO, Artifact, BigParameter, FatalError, OPIOSign
from dflow.config import config
from dflow.utils import run_command as dflow_run_command

default_log_name = "calc.log"
default_out_data_name = "data"
task_pattern = "task.%06d" 

def run_command(
    cmd: Union[str, List[str]],
    shell: bool = False,
) -> Tuple[int, str, str]:
    interactive = False if config["mode"] == "debug" else True
    return dflow_run_command(
        cmd, raise_error=False, try_bash=shell, interactive=interactive
    )



class PrepFp(OP, ABC):
    r"""Prepares the working directories for first-principles (FP) tasks.

    A list of (same length as ip["confs"]) working directories
    containing all files needed to start FP tasks will be
    created. The paths of the directories will be returned as
    `op["task_paths"]`. The identities of the tasks are returned as
    `op["task_names"]`.

    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "config": BigParameter(dict),
                "type_map": List[str],
                "confs": Artifact(List[Path]),
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "task_names": BigParameter(List[str]),
                "task_paths": Artifact(List[Path]),
            }
        )

    @abstractmethod
    def prep_task(
        self,
        conf_frame: dpdata.System,
        inputs: Any,
    ):
        r"""Define how one FP task is prepared.

        Parameters
        ----------
        conf_frame : dpdata.System
            One frame of configuration in the dpdata format.
        inputs : Any
            The class object handels all other input files of the task.
            For example, pseudopotential file, k-point file and so on.
        """
        pass

    @OP.exec_sign_check
    def execute(
        self,
        ip: OPIO,
    ) -> OPIO:
        r"""Execute the OP.

        Parameters
        ----------
        ip : dict
            Input dict with components:

            - `config` : (`dict`) Should have `config['inputs']`, which defines the input files of the FP task.
            - `confs` : (`Artifact(List[Path])`) Configurations for the FP tasks. Stored in folders as deepmd/npy format. Can be parsed as dpdata.MultiSystems.

        Returns
        -------
        op : dict
            Output dict with components:

            - `task_names`: (`List[str]`) The name of tasks. Will be used as the identities of the tasks. The names of different tasks are different.
            - `task_paths`: (`Artifact(List[Path])`) The parepared working paths of the tasks. Contains all input files needed to start the FP. The order fo the Paths should be consistent with `op["task_names"]`
        """

        inputs = ip["config"]["inputs"]
        confs = ip["confs"]
        type_map = ip["type_map"]

        task_names = []
        task_paths = []
        counter = 0
        # loop over list of MultiSystems
        for mm in confs:
            ms = dpdata.MultiSystems(type_map=type_map)
            ms.from_deepmd_npy(mm, labeled=False)  # type: ignore
            # loop over Systems in MultiSystems
            for ii in range(len(ms)):
                ss = ms[ii]
                # loop over frames
                for ff in range(ss.get_nframes()):
                    nn, pp = self._exec_one_frame(counter, inputs, ss[ff])
                    task_names.append(nn)
                    task_paths.append(pp)
                    counter += 1
        return OPIO(
            {
                "task_names": task_names,
                "task_paths": task_paths,
            }
        )

    def _exec_one_frame(
        self,
        idx,
        inputs,
        conf_frame: dpdata.System,
    ) -> Tuple[str, Path]:
        task_name = task_pattern % idx
        task_path = Path(task_name)
        with set_directory(task_path):
            self.prep_task(conf_frame, inputs)
        return task_name, task_path


class RunFp(OP, ABC):
    r"""Execute a first-principles (FP) task.

    A working directory named `task_name` is created. All input files
    are copied or symbol linked to directory `task_name`. The FP
    command is exectuted from directory `task_name`. The
    `op["labeled_data"]` in `"deepmd/npy"` format (HF5 in the future)
    provided by `dpdata` will be created.

    """

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "config": BigParameter(dict),
                "task_name": BigParameter(str),
                "task_path": Artifact(Path),
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "log": Artifact(Path),
                "labeled_data": Artifact(Path),
            }
        )

    @abstractmethod
    def input_files(self) -> List[str]:
        r"""The mandatory input files to run a FP task.

        Returns
        -------
        files: List[str]
            A list of madatory input files names.

        """
        pass

    @abstractmethod
    def optional_input_files(self) -> List[str]:
        r"""The optional input files to run a FP task.

        Returns
        -------
        files: List[str]
            A list of optional input files names.

        """
        pass

    @abstractmethod
    def run_task(
        self,
        **kwargs,
    ) -> Tuple[str, str]:
        r"""Defines how one FP task runs

        Parameters
        ----------
        **kwargs
            Keyword args defined by the developer.
            The fp/run_config session of the input file will be passed to this function.

        Returns
        -------
        out_name: str
            The file name of the output data. Should be in dpdata.LabeledSystem format.
        log_name: str
            The file name of the log.
        """
        pass

    @staticmethod
    @abstractmethod
    def args() -> List[dargs.Argument]:
        r"""The argument definition of the `run_task` method.

        Returns
        -------
        arguments: List[dargs.Argument]
            List of dargs.Argument defines the arguments of `run_task` method.
        """
        pass

    @classmethod
    def normalize_config(cls, data: Dict = {}, strict: bool = True) -> Dict:
        r"""Normalized the argument.

        Parameters
        ----------
        data : Dict
            The input dict of arguments.
        strict : bool
            Strictly check the arguments.

        Returns
        -------
        data: Dict
            The normalized arguments.

        """
        ta = cls.args()
        base = dargs.Argument("base", dict, ta)
        data = base.normalize_value(data, trim_pattern="_*")
        base.check_value(data, strict=strict)
        return data

    @OP.exec_sign_check
    def execute(
        self,
        ip: OPIO,
    ) -> OPIO:
        r"""Execute the OP.

        Parameters
        ----------
        ip : dict
            Input dict with components:

            - `config`: (`dict`) The config of FP task. Should have `config['run']`, which defines the runtime configuration of the FP task.
            - `task_name`: (`str`) The name of task.
            - `task_path`: (`Artifact(Path)`) The path that contains all input files prepareed by `PrepFp`.

        Returns
        -------
        Output dict with components:
        - `log`: (`Artifact(Path)`) The log file of FP.
        - `labeled_data`: (`Artifact(Path)`) The path to the labeled data in `"deepmd/npy"` format provided by `dpdata`.

        Raises
        ------
        TransientError
            On the failure of FP execution.
        FatalError
            When mandatory files are not found.
        """
        config = ip["config"]["run"] if ip["config"]["run"] is not None else {}
        config = type(self).normalize_config(config, strict=False)
        task_name = ip["task_name"]
        task_path = ip["task_path"]
        input_files = self.input_files()
        input_files = [(Path(task_path) / ii).resolve() for ii in input_files]
        opt_input_files = self.optional_input_files()
        opt_input_files = [(Path(task_path) / ii).resolve() for ii in opt_input_files]
        work_dir = Path(task_name)

        with set_directory(work_dir):
            # link input files
            for ii in input_files:
                if os.path.isfile(ii) or os.path.isdir(ii):
                    iname = ii.name
                    Path(iname).symlink_to(ii)
                else:
                    raise FatalError(f"cannot find file {ii}")

            for ii in opt_input_files:
                if os.path.isfile(ii) or os.path.isdir(ii):
                    iname = ii.name
                    Path(iname).symlink_to(ii)
            out_name, log_name = self.run_task(**config)

        return OPIO(
            {
                "log": work_dir / log_name,
                "labeled_data": work_dir / out_name,
            }
        )
