from pathlib import Path
from dargs import Argument
import dpdata
from typing import List, Tuple
from .base import PrepFp, RunFp, run_command, default_log_name, default_out_data_name 
import logging
from dflow.python import TransientError


class EmtInputs:
    def __init__(
        self,
        pstress,
        relax_cell,
        step_max,
        f_max
    ):
        """
        Parameters
        ----------
        incar : str
            A template INCAR file.
      
        """
        self.pstress = pstress
        self._incar_template = self.incar_from_file(pstress, relax_cell, step_max, f_max)

    @property
    def incar_template(self):
        return self._incar_template

    def incar_from_file(
        self,
        pstress,
        relax_cell,
        step_max,
        f_max
    ):
        c_path = Path(__file__).resolve().parent
        incar_template = Path(c_path / "template/emt.py").read_text()
        incar_template = incar_template.replace("{{pstress}}", str(pstress))
        incar_template = incar_template.replace("{{relax_cell}}", str(relax_cell))
        incar_template = incar_template.replace("{{step_max}}", str(step_max))
        incar_template = incar_template.replace("{{f_max}}", str(f_max))
        return incar_template

    @staticmethod
    def args():
        doc_step_max = "Maximum number of steps for structural relaxation."
        doc_relax_cell = "Whether to optimize the crystal cell"
        doc_f_max = "Force convergence conditions for structural relaxation"

        return [
            Argument("relax_cell", bool, optional=True, default=True, doc=doc_relax_cell),
            Argument("step_max", int, optional=True, default=1000, doc=doc_step_max),
            Argument("f_max", float, optional=True, default=0.05, doc=doc_f_max)
        ]

    @staticmethod
    def normalize_config(data={}, strict=True):
        ta = EmtInputs.args()
        base = Argument("base", dict, ta)
        data = base.normalize_value(data, trim_pattern="_*")
        base.check_value(data, strict=strict)
        return data
    
    

# global static variables
emt_conf_name = "POSCAR"
emt_input_name = "calc.py"

class PrepEmt(PrepFp):
    def prep_task(
        self,
        conf_frame: dpdata.System,
        emt_inputs: EmtInputs
    ):
        r"""Define how one Vasp task is prepared.

        Parameters
        ----------
        conf_frame : dpdata.System
            One frame of configuration in the dpdata format.
        vasp_inputs : VaspInputs
            The VaspInputs object handels all other input files of the task.
        """

        conf_frame.to("vasp/poscar", emt_conf_name)
        Path(emt_input_name).write_text(emt_inputs.incar_template)
        
        # fix the case when some element have 0 atom, e.g. H0O2


class RunEmt(RunFp):
    def input_files(self) -> List[str]:
        r"""The mandatory input files to run a vasp task.

        Returns
        -------
        files: List[str]
            A list of madatory input files names.

        """
        return [emt_conf_name, emt_input_name]

    def optional_input_files(self) -> List[str]:
        r"""The optional input files to run a vasp task.

        Returns
        -------
        files: List[str]
            A list of optional input files names.

        """
        return []

    def run_task(
        self,
        command: str,
        out: str,
        log: str,
    ) -> Tuple[str, str]:
        r"""Defines how one FP task runs

        Parameters
        ----------
        command : str
            The command of running vasp task
        out : str
            The name of the output data file.
        log : str
            The name of the log file

        Returns
        -------
        out_name: str
            The file name of the output data in the dpdata.LabeledSystem format.
        log_name: str
            The file name of the log.
        """

        log_name = log
        out_name = out
        # run vasp
        command = " ".join([command, emt_input_name, ">", log_name])
        ret, out, err = run_command(command, shell=True)
        if ret != 0:
            logging.error(
                "".join(
                    ("ase failed\n", "out msg: ", out, "\n", "err msg: ", err, "\n")
                )
            )
            raise TransientError("ase failed")
        
        # convert the output to deepmd/npy format
        from dpdata import LabeledSystem
        ls = LabeledSystem().from_ase_traj("relax.traj")
        ls.to("deepmd/npy", out_name)
        return out_name, log_name
        

    @staticmethod
    def args():
        r"""The argument definition of the `run_task` method.

        Returns
        -------
        arguments: List[dargs.Argument]
            List of dargs.Argument defines the arguments of `run_task` method.
        """

        doc_emt_cmd = "The run command of Emt"
        doc_emt_log = "The log file name of Emt"
        doc_emt_out = "The output dir name of labeled data. In `deepmd/npy` format provided by `dpdata`."
        return [
            Argument("command", str, optional=True, default="python", doc=doc_emt_cmd),
            Argument("out", str, optional=True, default=default_out_data_name , doc= doc_emt_out),
            Argument("log", str, optional=True, default=default_log_name, doc=doc_emt_log)
        ]
