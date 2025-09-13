from .matgl import MatglInputs, RunMatgl, PrepMatgl
from .dpmd import DpmdInputs, RunDpmd, PrepDpmd
from .gulp import GulpInputs, PrepGulp, RunGulp
from .emt import EmtInputs, PrepEmt, RunEmt
from .vasp import PrepVasp, RunVasp, VaspInputs
from .abacus import FpOpAbacusInputs, PrepFpOpAbacus, RunFpOpAbacus
from .cp2k import FpOpCp2kInputs, PrepFpOpCp2k, RunFpOpCp2k
from .gaussian import GaussianInputs, PrepGaussian, RunGaussian

calc_styles = {
    'matgl': {
        'inputs': MatglInputs,
        "prep": PrepMatgl,
        "run": RunMatgl
    },
    'dpmd': {
        'inputs': DpmdInputs,
        "prep": PrepDpmd,
        "run": RunDpmd
    },
    'gulp': {
        'inputs': GulpInputs,
        "prep": PrepGulp,
        "run": RunGulp
    },
    'emt': {
        'inputs': EmtInputs,
        "prep": PrepEmt,
        "run": RunEmt
    },
    "vasp": {
        "inputs": VaspInputs,
        "prep": PrepVasp,
        "run": RunVasp,
    },
    "gaussian": {
        "inputs": GaussianInputs,
        "prep": PrepGaussian,
        "run": RunGaussian,
    },
    "fpop_abacus": {
        "inputs": FpOpAbacusInputs,
        "prep": PrepFpOpAbacus,
        "run": RunFpOpAbacus,
    },
    "fpop_cp2k": {
        "inputs": FpOpCp2kInputs,
        "prep": PrepFpOpCp2k,
        "run": RunFpOpCp2k,
    }
}
