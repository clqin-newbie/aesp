import os
from pathlib import Path
import dpdata
from dargs import Argument
from dflow.python import OP, OPIO, OPIOSign, Artifact, TransientError, BigParameter
import dpdata, os, shutil
from ase.io import read, write
from pathlib import Path
from dflow.utils import run_command
from typing import List, Dict, Optional
from .base import PrepFp, RunFp, default_out_data_name

class Cp2kInputs:
    def __init__(self, inp_file: str):
        """
        Initialize the Cp2kInputs class.

        Parameters
        ----------
        inp_file : str
            The path to the user-submitted CP2K input file.
        """
        self.inp_file_from_file(inp_file)

    @property
    def inp_template(self):
        """
        Return the template content of the input file.
        """
        return self._inp_template

    def inp_file_from_file(self, fname: str):
        """
        Read the content of the input file and store it.

        Parameters
        ----------
        fname : str
            The path to the input file.
        """
        self._inp_template = Path(fname).read_text()

    @staticmethod
    def args():
        """
        Define the arguments required by the Cp2kInputs class.
        """
        doc_inp_file = "The path to the user-submitted CP2K input file."
        return [
            Argument("inp_file", str, optional=False, doc=doc_inp_file),
        ]

class PrepCp2k(PrepFp):
    def prep_task(
            self,
            conf_frame: dpdata.System,
            inputs: Cp2kInputs,
            prepare_image_config: Optional[Dict] = None,
            optional_input: Optional[Dict] = None,
            optional_artifact: Optional[Dict] = None,
    ):
        """
        Define how one CP2K task is prepared.

        Parameters
        ----------
        conf_frame : dpdata.System
            One frame of configuration in the dpdata format.
        inputs: Cp2kInputs
            The Cp2kInputs object handles the input file of the task.
        prepare_image_config: Dict, optional
            Definition of runtime parameters in the process of preparing tasks.
        optional_input: Dict, optional
            Other parameters the developers or users may need.
        optional_artifact: Dict[str, Path], optional
            Other files that users or developers need.
        """
        # Generate POSCAR file from the configuration frame
        conf_frame.to('vasp/poscar', 'POSCAR')

        # Read the structure from the POSCAR file and write to a temporary XYZ file
        atoms = read('POSCAR')
        write('temp.xyz', atoms)

        # Read the temporary XYZ file, remove the first two lines, and write to coord.xyz
        with open('temp.xyz', 'r') as f:
            lines = f.readlines()[2:]  # Remove the first two lines
        with open('coord.xyz', 'w') as f:
            f.writelines(lines)

        # Generate CELL_PARAMETER file
        cell_params = conf_frame['cells'][0]
        with open('CELL_PARAMETER', 'w') as file:
            file.write(f"A {cell_params[0,0]:14.8f} {cell_params[0,1]:14.8f} {cell_params[0,2]:14.8f}\n")
            file.write(f"B {cell_params[1,0]:14.8f} {cell_params[1,1]:14.8f} {cell_params[1,2]:14.8f}\n")
            file.write(f"C {cell_params[2,0]:14.8f} {cell_params[2,1]:14.8f} {cell_params[2,2]:14.8f}\n")

        # Write the CP2K input file content
        Path('input.inp').write_text(inputs.inp_template)

        # Copy optional files to the working directory
        if optional_artifact:
            for file_name, file_path in optional_artifact.items():
                content = file_path.read_text()
                Path(file_name).write_text(content)


class RunCp2k(RunFp):
    def input_files(self, task_path) -> List[str]:
        """
        The mandatory input files to run a CP2K task.
        
        Returns
        -------
        files: List[str]
            A list of mandatory input file names.
        """
        return ["input.inp", "CELL_PARAMETER", "coord.xyz"]

    def run_task(
        self,
        backward_dir_name,
        log_name,
        backward_list: List[str],
        run_image_config: Optional[Dict] = None,
        optional_input: Optional[Dict] = None,
    ) -> str:
        """
        Defines how one FP task runs.

        Parameters
        ----------
        backward_dir_name : str
            The name of the directory which contains the backward files.
        log_name : str
            The name of log file.
        backward_list : List[str]
            The output files the users need. For example: ["output.log", "trajectory.xyz"]
        run_image_config : Dict, optional
            Keyword args defined by the developer. For example:
            {
              "command": "source /opt/intel/oneapi/setvars.sh && mpirun -n 64 /opt/cp2k/bin/cp2k.popt"
            }
        optional_input : Dict, optional
            The parameters developers need in runtime. For example:
            {
                "conf_format": "cp2k/input"
            }
        
        Returns
        -------
        backward_dir_name : str
            The directory name which contains the files users need.
        """
        # Get the run command
        if run_image_config:
            command = run_image_config.get("command")
            if not command:
                raise ValueError("Command not specified in run_image_config")
        else:
            raise ValueError("run_image_config is missing")
        
        # Run CP2K command and write output to log file
        command = " ".join([command, ">", log_name])
        kwargs = {"try_bash": True, "shell": True}
        if run_image_config:
            kwargs.update(run_image_config)
            kwargs.pop("command", None)
        
        # Execute command
        ret, out, err = run_command(command, raise_error=False, **kwargs)  # type: ignore
        if ret != 0:
            raise TransientError(
                "cp2k failed\n", "out msg", out, "\n", "err msg", err, "\n"
            )
        
        # Check if the task was successful
        if not self.check_run_success(log_name):
            raise TransientError(
                "cp2k failed, we could not check the exact cause. Please check the log file."
            )
        
        # Create output directory and copy log file
        os.makedirs(Path(backward_dir_name))
        shutil.copyfile(log_name, Path(backward_dir_name) / log_name)
        for ii in backward_list:
            try:
                shutil.copyfile(ii, Path(backward_dir_name) / ii)
            except:
                shutil.copytree(ii, Path(backward_dir_name) / ii)
        
        return backward_dir_name
    
    def check_run_success(self, log_name):
        """
        Check if the CP2K task ran successfully by examining the output file.

        Returns
        -------
        success : bool
            True if the task ran successfully with warnings line, False otherwise.
        """
        with open(log_name, "r") as f:
            lines = f.readlines()
        return any("The number of warnings for this run is" in line for line in lines)


class FpOpCp2kInputs(Cp2kInputs):  # type: ignore
    @staticmethod
    def args():
        doc_inp_file = "The path to the user-submitted CP2K input file."
        return [
            Argument("inp_file", str, optional=False, doc=doc_inp_file),
        ]


class PrepFpOpCp2k(OP):
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

    @OP.exec_sign_check
    def execute(
        self,
        ip: OPIO,
    ) -> OPIO:
        confs = []
        # remove atom types with 0 atom from type map
        # for all atom types in the type map
        for p in ip["confs"]:
            for f in p.rglob("type.raw"):
                system = f.parent
                s = dpdata.System(system, fmt="deepmd/npy")
                atom_numbs = []
                atom_names = []
                for numb, name in zip(s["atom_numbs"], s["atom_names"]):  # type: ignore https://github.com/microsoft/pyright/issues/5620
                    if numb > 0:
                        atom_numbs.append(numb)
                        atom_names.append(name)
                if atom_names != s["atom_names"]:
                    for i, t in enumerate(s["atom_types"]):  # type: ignore https://github.com/microsoft/pyright/issues/5620
                        s["atom_types"][i] = atom_names.index(s["atom_names"][t])  # type: ignore https://github.com/microsoft/pyright/issues/5620
                    s.data["atom_numbs"] = atom_numbs
                    s.data["atom_names"] = atom_names
                    target = "output/%s" % system
                    s.to("deepmd/npy", target)
                    confs.append(Path(target))
                else:
                    confs.append(system)
        op_in = OPIO(
            {
                "inputs": ip["config"]["inputs"],
                "type_map": ip["type_map"],
                "confs": confs,
                "prep_image_config": ip["config"].get("prep", {}),
            }
        )
        op = PrepCp2k()
        return op.execute(op_in)  # type: ignore in the case of not importing fpop


def get_run_type(lines: List[str]) -> Optional[str]:
    for line in lines:
        if "RUN_TYPE" in line:
            return line.split()[-1]
    return None


class RunFpOpCp2k(OP):
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

    @OP.exec_sign_check
    def execute(
        self,
        ip: OPIO,
    ) -> OPIO:
        run_config = ip["config"].get("run", {})
        op_in = OPIO(
            {
                "task_name": ip["task_name"],
                "task_path": ip["task_path"],
                "backward_list": [],
                "log_name": "output.log",
                "run_image_config": run_config,
            }
        )
        op = RunCp2k()
        op_out = op.execute(op_in)  # type: ignore in the case of not importing fpop
        workdir = op_out["backward_dir"].parent

        file_path = os.path.join(str(workdir), "output.log")

        # convert the output to deepmd/npy format
        with open(workdir / "input.inp", "r") as f:
            lines = f.readlines()

        # 获取 RUN_TYPE
        run_type = get_run_type(lines)

        if run_type == "ENERGY_FORCE":
            sys = dpdata.LabeledSystem(file_path, fmt="cp2kdata/e_f")
        elif run_type == "MD":
            sys = dpdata.LabeledSystem(
                str(workdir), cp2k_output_name="output.log", fmt="cp2kdata/md"
            )
        else:
            raise ValueError(f"Type of calculation {run_type} not supported")

        # out_name = run_config.get("out", fp_default_out_data_name)
        out_name = default_out_data_name
        sys.to("deepmd/npy", workdir / out_name)

        return OPIO(
            {
                "log": workdir / "output.log",
                "labeled_data": workdir / out_name,
            }
        )

    @staticmethod
    def args():
        doc_cmd = "The command of cp2k"
        return [
            Argument("command", str, optional=True, default="cp2k", doc=doc_cmd),
        ]
