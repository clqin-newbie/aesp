from pathlib import Path
import dpdata
from dargs import Argument
from .base import PrepFp, RunFp, default_out_data_name
import os, shutil, re
from dflow.utils import run_command
from typing import Any, Tuple, List, Dict, Optional, Union
from dflow.python import OP, OPIO, OPIOSign, Artifact, TransientError, BigParameter

MASS_DICT = {
    "H": 1.0079,
    "He": 4.0026,
    "Li": 6.941,
    "Be": 9.0122,
    "B": 10.811,
    "C": 12.0107,
    "N": 14.0067,
    "O": 15.9994,
    "F": 18.9984,
    "Ne": 20.1797,
    "Na": 22.9897,
    "Mg": 24.305,
    "Al": 26.9815,
    "Si": 28.0855,
    "P": 30.9738,
    "S": 32.065,
    "Cl": 35.453,
    "K": 39.0983,
    "Ar": 39.948,
    "Ca": 40.078,
    "Sc": 44.9559,
    "Ti": 47.867,
    "V": 50.9415,
    "Cr": 51.9961,
    "Mn": 54.938,
    "Fe": 55.845,
    "Ni": 58.6934,
    "Co": 58.9332,
    "Cu": 63.546,
    "Zn": 65.39,
    "Ga": 69.723,
    "Ge": 72.64,
    "As": 74.9216,
    "Se": 78.96,
    "Br": 79.904,
    "Kr": 83.8,
    "Rb": 85.4678,
    "Sr": 87.62,
    "Y": 88.9059,
    "Zr": 91.224,
    "Nb": 92.9064,
    "Mo": 95.94,
    "Tc": 98,
    "Ru": 101.07,
    "Rh": 102.9055,
    "Pd": 106.42,
    "Ag": 107.8682,
    "Cd": 112.411,
    "In": 114.818,
    "Sn": 118.71,
    "Sb": 121.76,
    "I": 126.9045,
    "Te": 127.6,
    "Xe": 131.293,
    "Cs": 132.9055,
    "Ba": 137.327,
    "La": 138.9055,
    "Ce": 140.116,
    "Pr": 140.9077,
    "Nd": 144.24,
    "Pm": 145,
    "Sm": 150.36,
    "Eu": 151.964,
    "Gd": 157.25,
    "Tb": 158.9253,
    "Dy": 162.5,
    "Ho": 164.9303,
    "Er": 167.259,
    "Tm": 168.9342,
    "Yb": 173.04,
    "Lu": 174.967,
    "Hf": 178.49,
    "Ta": 180.9479,
    "W": 183.84,
    "Re": 186.207,
    "Os": 190.23,
    "Ir": 192.217,
    "Pt": 195.078,
    "Au": 196.9665,
    "Hg": 200.59,
    "Tl": 204.3833,
    "Pb": 207.2,
    "Bi": 208.9804,
    "Po": 209,
    "At": 210,
    "Rn": 222,
    "Fr": 223,
    "Ra": 226,
    "Ac": 227,
    "Pa": 231.0359,
    "Th": 232.0381,
    "Np": 237,
    "U": 238.0289,
    "Am": 243,
    "Pu": 244,
    "Cm": 247,
    "Bk": 247,
    "Cf": 251,
    "Es": 252,
    "Fm": 257,
    "Md": 258,
    "No": 259,
    "Rf": 261,
    "Lr": 262,
    "Db": 262,
    "Bh": 264,
    "Sg": 266,
    "Mt": 268,
    "Rg": 272,
    "Hs": 277,
    "H": 1.0079,
    "He": 4.0026,
    "Li": 6.941,
    "Be": 9.0122,
    "B": 10.811,
    "C": 12.0107,
    "N": 14.0067,
    "O": 15.9994,
    "F": 18.9984,
    "Ne": 20.1797,
    "Na": 22.9897,
    "Mg": 24.305,
    "Al": 26.9815,
    "Si": 28.0855,
    "P": 30.9738,
    "S": 32.065,
    "Cl": 35.453,
    "K": 39.0983,
    "Ar": 39.948,
    "Ca": 40.078,
    "Sc": 44.9559,
    "Ti": 47.867,
    "V": 50.9415,
    "Cr": 51.9961,
    "Mn": 54.938,
    "Fe": 55.845,
    "Ni": 58.6934,
    "Co": 58.9332,
    "Cu": 63.546,
    "Zn": 65.39,
    "Ga": 69.723,
    "Ge": 72.64,
    "As": 74.9216,
    "Se": 78.96,
    "Br": 79.904,
    "Kr": 83.8,
    "Rb": 85.4678,
    "Sr": 87.62,
    "Y": 88.9059,
    "Zr": 91.224,
    "Nb": 92.9064,
    "Mo": 95.94,
    "Tc": 98,
    "Ru": 101.07,
    "Rh": 102.9055,
    "Pd": 106.42,
    "Ag": 107.8682,
    "Cd": 112.411,
    "In": 114.818,
    "Sn": 118.71,
    "Sb": 121.76,
    "I": 126.9045,
    "Te": 127.6,
    "Xe": 131.293,
    "Cs": 132.9055,
    "Ba": 137.327,
    "La": 138.9055,
    "Ce": 140.116,
    "Pr": 140.9077,
    "Nd": 144.24,
    "Pm": 145,
    "Sm": 150.36,
    "Eu": 151.964,
    "Gd": 157.25,
    "Tb": 158.9253,
    "Dy": 162.5,
    "Ho": 164.9303,
    "Er": 167.259,
    "Tm": 168.9342,
    "Yb": 173.04,
    "Lu": 174.967,
    "Hf": 178.49,
    "Ta": 180.9479,
    "W": 183.84,
    "Re": 186.207,
    "Os": 190.23,
    "Ir": 192.217,
    "Pt": 195.078,
    "Au": 196.9665,
    "Hg": 200.59,
    "Tl": 204.3833,
    "Pb": 207.2,
    "Bi": 208.9804,
    "Po": 209,
    "At": 210,
    "Rn": 222,
    "Fr": 223,
    "Ra": 226,
    "Ac": 227,
    "Pa": 231.0359,
    "Th": 232.0381,
    "Np": 237,
    "U": 238.0289,
    "Am": 243,
    "Pu": 244,
    "Cm": 247,
    "Bk": 247,
    "Cf": 251,
    "Es": 252,
    "Fm": 257,
    "Md": 258,
    "No": 259,
    "Rf": 261,
    "Lr": 262,
    "Db": 262,
    "Bh": 264,
    "Sg": 266,
    "Mt": 268,
    "Rg": 272,
    "Hs": 277,
}

def get_pporbdpks_from_stru(stru: str= "STRU"):
    "read the label, pp, orb, cell, coord, deepks-descriptor"
    ABACUS_STRU_KEY_WORD = [
        "ATOMIC_SPECIES",
        "NUMERICAL_ORBITAL",
        "LATTICE_CONSTANT",
        "LATTICE_VECTORS",
        "ATOMIC_POSITIONS",
        "NUMERICAL_DESCRIPTOR",
    ]
    if not os.path.isfile(stru):
        return {}
    with open(stru) as f1: lines = f1.readlines()      
    def get_block(keyname):
        block = []
        for i,line in enumerate(lines):
            if line.strip() == "": continue
            elif line.split('#')[0].strip() == keyname:
                for ij in range(i+1,len(lines)):
                    if lines[ij].strip() == "": continue
                    elif lines[ij].strip() in ABACUS_STRU_KEY_WORD:
                        return block
                    else:
                        block.append(lines[ij])
                return block
        return None
    
    atomic_species = get_block("ATOMIC_SPECIES")
    numerical_orbital = get_block("NUMERICAL_ORBITAL")
    dpks = get_block("NUMERICAL_DESCRIPTOR")
    dpks = None if dpks == None else dpks[0].strip()
    
    #read species
    pp = []
    labels = []
    mass = []
    if atomic_species:
        for line in atomic_species:
            sline = line.split()
            labels.append(sline[0])
            pp.append(sline[2])
            mass.append(float(sline[1]))
        
    #read orbital
    if numerical_orbital == None:
        orb = None
    else:
        orb = []
        for line in numerical_orbital:
            orb.append(line.split()[0])

    return {
            "labels": labels,
            "mass": mass,
            "pp":pp,
            "orb":orb,
            "dpks":dpks,}


class AbacusInputs():
    def __init__(
            self,
            input_file: Union[str,Path],
            pp_files: Dict[str, Union[str,Path]],
            element_mass: Optional[Dict[str,float]] = None,
            kpt_file: Optional[Union[str,Path]] = None,
            orb_files: Optional[Dict[str, Union[str,Path]]] = None,
            deepks_descriptor: Optional[Union[str,Path]] = None,
            deepks_model: Optional[Union[str,Path]] = None
    ):     
        """The input information of an ABACUS job except for STRU.

        Parameters
        ----------
        input_file : str
            A template INPUT file.
        element_mass : Dict[str, float]
            Specify the mass of some elements. 
            For example: {"H" : 1.0079,"O" : 15.9994}.    
        pp_files : Dict[str, str]
            The pseudopotential files for the elements. 
            For example: {"H" : "/path/to/H.upf","O" : "/path/to/O.upf"}.
        kpt_file : str, optional
            The KPT file, by default None. 
        orb_files : Dict[str, str], optional
            The numerical orbital fiels for the elements, by default None. 
            For example: {"H": "/path/to/H.orb","O": "/path/to/O.orb"}.
        deepks_descriptor : str, optional
            The deepks descriptor file, by default None.
        deepks_model : str, optional
            The deepks model file, by default None.
        """        
        self.input_file = input_file
        self._input = AbacusInputs.read_inputf(self.input_file)

        self._pp_files = self._read_dict_file(pp_files)
        self._mass = element_mass if element_mass != None else {}
        self._kpt_file = None if kpt_file == None else Path(kpt_file).read_text()
        self._orb_files = {} if orb_files == None else self._read_dict_file(orb_files)
        self._deepks_descriptor = None if deepks_descriptor == None else (os.path.split(deepks_descriptor)[1], Path(deepks_descriptor).read_text())
        self._deepks_model = None if deepks_model == None else (os.path.split(deepks_model)[1], Path(deepks_model).read_bytes())

    def _read_dict_file(self,input_dict,out_dict=None):
        # input_dict is a dict whose value is a file.
        # The filename and context will make up a tuple, which is 
        # the value of out_dict
        if not out_dict:
            out_dict = {}
        for k,v in input_dict.items():
            out_dict[k] = (os.path.split(v)[1],Path(v).read_text())
        return out_dict

    def set_input(self, key:str, value:Any):
        #if set the value to be None, can remove the key
        if value == None:
            del self._input[key.strip().lower()]
        else:
            self._input[key.strip().lower()] = value
    
    def set_mass(self, key:str, value:float):
        self._mass[key] = value
    
    def set_pp(self,key:str, value:str):
        self._read_dict_file({key:value},self._pp_files)
    
    def set_orb(self,key:str,value:str):
        self._read_dict_file({key:value},self._orb_files)
    
    def set_deepks_descriptor(self, value:str):
        self._deepks_descriptor = (os.path.split(value)[1], Path(value).read_text())
    
    def set_deepks_model(self, value:str):
        self._deepks_model = (os.path.split(value)[1], Path(value).read_bytes())

    def get_input(self):
        return self._input
    
    def get_pp(self):
        return self._pp_files
    
    def get_orb(self):
        return self._orb_files
    
    def get_deepks_descriptor(self):
        return self._deepks_descriptor
    
    def get_deepks_model(self):
        return self._deepks_model

    @staticmethod
    def read_inputf(inputf: Union[str,Path]) -> dict:
        """Read INPUT and transfer to a dict.

        Parameters
        ----------
        inputf : str
            INPUT file name

        Returns
        -------
        dict[str,str]
            all input parameters
        """  
        input_context = {}
        with open(inputf) as f1: input_lines = f1.readlines()
        readinput = False
        for i,iline in enumerate(input_lines):
            if iline.strip() == 'INPUT_PARAMETERS':
                readinput = True
            elif iline.strip() == '' or iline.strip()[0] in ['#']:
                continue
            elif readinput:
                sline =re.split('[ \t]',iline.split("#")[0].strip(),maxsplit=1)
                if len(sline) == 2:
                    input_context[sline[0].lower().strip()] = sline[1].strip() 
        return input_context    

    def write_input(self,inputf :str = "INPUT"):
        with open(inputf,'w') as f1:
            f1.write("INPUT_PARAMETERS\n")
            for k,v in self._input.items():
                f1.write("%s %s\n" % (str(k),str(v)))
    
    def write_kpt(self,kptf = "KPT"):
        if self._kpt_file:
            Path(kptf).write_text(self._kpt_file)

    def write_pporb(self,element_list : List[str]):
        """Based on element list, write the pp/orb files, and return a list of the filename. 

        Parameters
        ----------
        element_list : List[str]
            a list of element name

        Returns
        -------
        List[List]
            a list of the list of pp files, and orbital files 
        """  
        need_orb = False
        if self._input.get("basis_type","pw").lower() in ["lcao","lcao_in_pw"]:
            need_orb = True
        pp,orb = [],[]
        for ielement in element_list:
            if ielement in self._pp_files:
                Path(self._pp_files[ielement][0]).write_text(self._pp_files[ielement][1])
                pp.append(self._pp_files[ielement][0])
            if need_orb and ielement in self._orb_files:
                Path(self._orb_files[ielement][0]).write_text(self._orb_files[ielement][1]) 
                orb.append(self._orb_files[ielement][0])

        if not orb: 
            orb = None

        return [pp,orb]     

    def write_deepks(self):
        """Check if INPUT is a deepks job, if yes, will return the deepks descriptor file name, 
        else will return None.

        Returns
        -------
        str
            deepks descriptor file name or None.
        """
        need_descriptor =  need_model = False  
        if self._input.get("deepks_out_labels",False):
            need_descriptor = True
        if self._input.get("deepks_scf",False):
            need_descriptor = True
            need_model = True 

        if need_descriptor:
            assert(self._deepks_descriptor != None)
            descriptor_file = self._deepks_descriptor[0]
            Path(descriptor_file).write_text(self._deepks_descriptor[1])
        else:
            descriptor_file = None

        if need_model:
            assert(self._deepks_model != None)
            Path(self._deepks_model[0]).write_bytes(self._deepks_model[1])

        return descriptor_file
        
    def get_mass(self,element_list: List[str]) -> List[float]:
        """Get the mass of elements.
        If the element is not specified in self._mass, this funciton will firstly search it 
        in a standard element-mass dictionary. And if the element is also not found in the
        dictionary, the mass will be set to 1.0. 

        Parameters
        ----------
        element_list : List[str]
            element name

        Returns
        -------
        List[float]
            the mass of each element
        """ 
        mass = []
        for i in element_list:
            mass.append(self._mass.get(i,MASS_DICT.get(i,1.0)))
        return mass

class PrepAbacus(PrepFp):
    def prep_task(
            self,
            conf_frame,
            inputs: AbacusInputs,
            prepare_image_config: Optional[Dict] = None,
            optional_input: Optional[Dict] = None,
            optional_artifact: Optional[Dict] = None,
    ):
        r"""Define how one Abacus task is prepared.

        Parameters
        ----------
        conf_frame : dpdata.System
            One frame of configuration in the dpdata format.
        inputs: AbacusInputs
            The AbacusInputs object handels all other input files of the task.
        prepare_image_config: Dict
            Definition of runtime parameters in the process of preparing tasks. 
        optional_input: 
            Other parameters the developers or users may need.
        optional_artifact
            Other files that users or developers need. 
        """

        element_list = conf_frame['atom_names']
        pp, orb = inputs.write_pporb(element_list)
        dpks = inputs.write_deepks()
        mass = inputs.get_mass(element_list)
        conf_frame.to('abacus/stru', 'STRU', pp_file=pp,numerical_orbital=orb,numerical_descriptor=dpks,mass=mass)
        
        inputs.write_input("INPUT")
        inputs.write_kpt("KPT")

        if optional_artifact:
            for file_name, file_path in optional_artifact.items():
                content = file_path.read_text()
                Path(file_name).write_text(content)
       

class RunAbacus(RunFp):
    def input_files(self,task_path) -> List[str]:
        r'''The mandatory input files to run an abacus task.
        Returns
        -------
        files: List[str]
            A list of madatory input files names.
        '''
        
        cwd = os.getcwd()
        os.chdir(task_path)

        files = ["INPUT","STRU"]
        if os.path.isfile("KPT"):
            files.append("KPT")
            
        files_tmp = []
        #read STRU
        stru_data = get_pporbdpks_from_stru("STRU")
        if stru_data != None:
            orb_files = stru_data["orb"]
            pp_files = stru_data["pp"]
            dpks_descriptor = stru_data["dpks"]

            files_tmp += pp_files
            if orb_files: files_tmp += orb_files
            if dpks_descriptor: files_tmp += [dpks_descriptor]

        #read INPUT
        input = AbacusInputs.read_inputf("INPUT")
        if "deepks_model" in input: files_tmp += [input["deepks_model"]]

        for ii in files_tmp:
            if os.path.isfile(ii):
                files.append(ii)
            else:
                print("ERROR: file %s is not found" % ii)

        os.chdir(cwd)

        return files

    def run_task(
        self,
        backward_dir_name,
        log_name,
        backward_list: List[str],
        run_image_config: Optional[Dict]=None,
        optional_input: Optional[Dict]=None,
    ) -> str:
        r'''Defines how one FP task runs
        Parameters
        ----------
        backward_dir_name:
            The name of the directory which contains the backward files.
        log_name:
            The name of log file.
        backward_list:
            The output files the users need.
        run_image_config:
            Keyword args defined by the developer.For example:
            {
              "command": "source /opt/intel/oneapi/setvars.sh && mpirun -n 16 abacus"
            }
        optional_input:
            The parameters developers need in runtime.
        
        Returns
        -------
        backward_dir_name: str
            The directory name which containers the files users need.
        '''
        
        if run_image_config:
            command = run_image_config["command"]
        else:
            command = "abacus"
        # run abacus
        command = " ".join([command, ">", log_name])
        kwargs = {"try_bash": True, "shell": True}
        if run_image_config:
            kwargs.update(run_image_config)
            kwargs.pop("command", None)
        ret, out, err = run_command(command, raise_error=False, **kwargs) # type: ignore
        if ret != 0:
            raise TransientError(
                "abacus failed\n", "out msg", out, "\n", "err msg", err, "\n"
            )
        if not self.check_run_success(log_name):
            raise TransientError(
                "abacus failed , we could not check the exact cause . Please check log file ."
            )
        os.makedirs(Path(backward_dir_name))
        shutil.copyfile(log_name,Path(backward_dir_name)/log_name)
        for ii in backward_list:
            try:
                shutil.copyfile(ii,Path(backward_dir_name)/ii)
            except:
                shutil.copytree(ii,Path(backward_dir_name)/ii)
        return backward_dir_name

    def check_run_success(self,log_name):
        with open(log_name,"r") as f:
            lines = f.readlines()
        if "SEE INFORMATION IN" in lines[-1]:
            return True
        else:
            return False


class FpOpAbacusInputs(AbacusInputs):  # type: ignore
    @staticmethod
    def args():
        doc_input_file = "A template INPUT file."
        doc_pp_files = (
            "The pseudopotential files for the elements. "
            'For example: {"H": "/path/to/H.upf", "O": "/path/to/O.upf"}.'
        )
        doc_element_mass = (
            "Specify the mass of some elements. "
            'For example: {"H": 1.0079, "O": 15.9994}.'
        )
        doc_kpt_file = "The KPT file, by default None."
        doc_orb_files = (
            "The numerical orbital fiels for the elements, "
            "by default None. "
            'For example: {"H": "/path/to/H.orb", "O": "/path/to/O.orb"}.'
        )
        doc_deepks_descriptor = "The deepks descriptor file, by default None."
        doc_deepks_model = "The deepks model file, by default None."
        return [
            Argument("input_file", str, optional=False, doc=doc_input_file),
            Argument("pp_files", dict, optional=False, doc=doc_pp_files),
            Argument(
                "element_mass", dict, optional=True, default=None, doc=doc_element_mass
            ),
            Argument("kpt_file", str, optional=True, default=None, doc=doc_kpt_file),
            Argument("orb_files", dict, optional=True, default=None, doc=doc_orb_files),
            Argument(
                "deepks_descriptor",
                str,
                optional=True,
                default=None,
                doc=doc_deepks_descriptor,
            ),
            Argument(
                "deepks_model", str, optional=True, default=None, doc=doc_deepks_model
            ),
        ]


class PrepFpOpAbacus(OP):
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
        # remove atom types with 0 atom from type map, for abacus need pp_files
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
        op = PrepAbacus()
        return op.execute(op_in)  # type: ignore in the case of not importing fpop


from typing import (
    Tuple,
)


def get_suffix_calculation(INPUT: List[str]) -> Tuple[str, str]:
    suffix = "ABACUS"
    calculation = "scf"
    for iline in INPUT:
        sline = iline.split("#")[0].split()
        if len(sline) >= 2 and sline[0].lower() == "suffix":
            suffix = sline[1].strip()
        elif len(sline) >= 2 and sline[0].lower() == "calculation":
            calculation = sline[1].strip()
    return suffix, calculation


class RunFpOpAbacus(OP):
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
                "run_image_config": run_config,
            }
        )
        op = RunAbacus()
        op_out = op.execute(op_in)  # type: ignore in the case of not importing fpop
        workdir = op_out["backward_dir"].parent

        # convert the output to deepmd/npy format
        with open("%s/INPUT" % workdir, "r") as f:
            INPUT = f.readlines()
        _, calculation = get_suffix_calculation(INPUT)
        if calculation == "scf":
            sys = dpdata.LabeledSystem(str(workdir), fmt="abacus/scf")
        elif calculation == "md":
            sys = dpdata.LabeledSystem(str(workdir), fmt="abacus/md")
        elif calculation in ["relax", "cell-relax"]:
            sys = dpdata.LabeledSystem(str(workdir), fmt="abacus/relax")
        else:
            raise ValueError("Type of calculation %s not supported" % calculation)
        out_name = default_out_data_name
        sys.to("deepmd/npy", workdir / out_name)

        return OPIO(
            {
                "log": workdir / "log",
                "labeled_data": workdir / out_name,
            }
        )

    @staticmethod
    def args():
        doc_cmd = "The command of abacus"
        return [
            Argument("command", str, optional=True, default="abacus", doc=doc_cmd),
        ]
