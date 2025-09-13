import logging
from pathlib import Path
import dpdata
from dargs import Argument
from dflow.python import TransientError
from .base import default_log_name, default_out_data_name, PrepFp, RunFp, run_command
from typing import Dict, List, Tuple, Union
import numpy as np 


class VaspInputs:
    def __init__(
        self,
        kspacing: Union[float, List[float]],
        incar: str,
        pp_files: Dict[str, str],
        kgamma: bool = True,
    ):
        """
        Parameters
        ----------
        kspacing : Union[float, List[float]]
            The kspacing. If it is a number, then three directions use the same
            ksapcing, otherwise it is a list of three numbers, specifying the
            kspacing used in the x, y and z dimension.
        incar : str
            A template INCAR file.
        pp_files : Dict[str,str]
            The potcar files for the elements. For example
            {
               "H" : "/path/to/POTCAR_H",
               "O" : "/path/to/POTCAR_O",
            }
        kgamma : bool
            K-mesh includes the gamma point
        """
        self.kspacing = kspacing
        self.kgamma = kgamma
        self.incar_from_file(incar)
        self.potcars_from_file(pp_files)

    @property
    def incar_template(self):
        return self._incar_template

    @property
    def potcars(self):
        return self._potcars

    def incar_from_file(
        self,
        fname: str,
    ):
        self._incar_template = Path(fname).read_text()

    def potcars_from_file(
        self,
        dict_fnames: Dict[str, str],
    ):
        self._potcars = {}
        for kk, vv in dict_fnames.items():
            self._potcars[kk] = Path(vv).read_text()

    def make_potcar(
        self,
        atom_names,
    ) -> str:
        potcar_contents = []
        for nn in atom_names:
            potcar_contents.append(self._potcars[nn])
        return "".join(potcar_contents)

    def make_kpoints(
        self,
        box: np.ndarray,
    ) -> str:
        return make_kspacing_kpoints(box, self.kspacing, self.kgamma)

    @staticmethod
    def args():
        doc_pp_files = 'The pseudopotential files set by a dict, e.g. {"Al" : "path/to/the/al/pp/file", "Mg" : "path/to/the/mg/pp/file"}'
        doc_incar = "The path to the template incar file"
        doc_kspacing = "The spacing of k-point sampling. `ksapcing` will overwrite the incar template"
        doc_kgamma = "If the k-mesh includes the gamma point. `kgamma` will overwrite the incar template"
        return [
            Argument("incar", str, optional=False, doc=doc_incar),
            Argument("pp_files", dict, optional=False, doc=doc_pp_files),
            Argument("kspacing", float, optional=False, doc=doc_kspacing),
            Argument("kgamma", bool, optional=True, default=True, doc=doc_kgamma),
        ]

    @staticmethod
    def normalize_config(data={}, strict=True):
        ta = VaspInputs.args()
        base = Argument("base", dict, ta)
        data = base.normalize_value(data, trim_pattern="_*")
        base.check_value(data, strict=strict)
        return data


def make_kspacing_kpoints(box, kspacing, kgamma):
    if type(kspacing) is not list:
        kspacing = [kspacing, kspacing, kspacing]
    box = np.array(box)
    rbox = _reciprocal_box(box)
    kpoints = [
        max(1, (np.ceil(2 * np.pi * np.linalg.norm(ii) / ks).astype(int)))
        for ii, ks in zip(rbox, kspacing)  # type: ignore
    ]
    ret = _make_vasp_kpoints(kpoints, kgamma)
    return ret


def _make_vasp_kp_gamma(kpoints):
    ret = ""
    ret += "Automatic mesh\n"
    ret += "0\n"
    ret += "Gamma\n"
    ret += "%d %d %d\n" % (kpoints[0], kpoints[1], kpoints[2])
    ret += "0  0  0\n"
    return ret


def _make_vasp_kp_mp(kpoints):
    ret = ""
    ret += "K-Points\n"
    ret += "0\n"
    ret += "Monkhorst Pack\n"
    ret += "%d %d %d\n" % (kpoints[0], kpoints[1], kpoints[2])
    ret += "0  0  0\n"
    return ret


def _make_vasp_kpoints(kpoints, kgamma=False):
    if kgamma:
        ret = _make_vasp_kp_gamma(kpoints)
    else:
        ret = _make_vasp_kp_mp(kpoints)
    return ret


def _reciprocal_box(box):
    rbox = np.linalg.inv(box)
    rbox = rbox.T
    return rbox

# global static variables
vasp_conf_name = "POSCAR"
vasp_input_name = "INCAR"
vasp_pot_name = "POTCAR"
vasp_kp_name = "KPOINTS"


class PrepVasp(PrepFp):
    def prep_task(
        self,
        conf_frame: dpdata.System,
        vasp_inputs: VaspInputs,
    ):
        r"""Define how one Vasp task is prepared.

        Parameters
        ----------
        conf_frame : dpdata.System
            One frame of configuration in the dpdata format.
        vasp_inputs : VaspInputs
            The VaspInputs object handels all other input files of the task.
        """

        conf_frame.to("vasp/poscar", vasp_conf_name)
        Path(vasp_input_name).write_text(vasp_inputs.incar_template)
        # fix the case when some element have 0 atom, e.g. H0O2
        tmp_frame = dpdata.System(vasp_conf_name, fmt="vasp/poscar")
        Path(vasp_pot_name).write_text(vasp_inputs.make_potcar(tmp_frame["atom_names"]))
        Path(vasp_kp_name).write_text(vasp_inputs.make_kpoints(conf_frame["cells"][0]))  # type: ignore


class RunVasp(RunFp):
    def input_files(self) -> List[str]:
        r"""The mandatory input files to run a vasp task.

        Returns
        -------
        files: List[str]
            A list of madatory input files names.

        """
        return [vasp_conf_name, vasp_input_name, vasp_pot_name, vasp_kp_name]

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
        command = " ".join([command, ">", log_name])
        ret, out, err = run_command(command, shell=True)
        if ret != 0:
            logging.error(
                "".join(
                    ("vasp failed\n", "out msg: ", out, "\n", "err msg: ", err, "\n")
                )
            )
            raise TransientError("vasp failed")
        # convert the output to deepmd/npy format
        sys = dpdata.LabeledSystem("OUTCAR")
        sys.to("deepmd/npy", out_name)
        return out_name, log_name

    @staticmethod
    def args():
        r"""The argument definition of the `run_task` method.

        Returns
        -------
        arguments: List[dargs.Argument]
            List of dargs.Argument defines the arguments of `run_task` method.
        """

        doc_vasp_cmd = "The command of VASP"
        doc_vasp_log = "The log file name of VASP"
        doc_vasp_out = "The output dir name of labeled data. In `deepmd/npy` format provided by `dpdata`."
        return [
            Argument("command", str, optional=True, default="vasp", doc=doc_vasp_cmd),
            Argument(
                "out",
                str,
                optional=True,
                default=default_out_data_name,
                doc=doc_vasp_out,
            ),
            Argument(
                "log", str, optional=True, default=default_log_name, doc=doc_vasp_log
            ),
        ]
