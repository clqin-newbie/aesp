
from ase.constraints import UnitCellFilter
from ase.io import read, write
from ase.optimize import LBFGS
from ase.calculators.emt import EMT

f_max = 0.05 
step_max = 1000
relax_cell = True
pstress = 0.0

# kBar to eV/A^3
aim_stress = 1.0 * pstress * 0.01 * 0.6242 / 10.0

ase_atom = read("POSCAR")
ase_atom.calc = EMT()
if relax_cell:
    ucf = UnitCellFilter(ase_atom, scalar_pressure=aim_stress)
    # opt
    opt = LBFGS(ucf, trajectory='relax.traj')
    opt.run(fmax=f_max, steps=step_max)
else:
    opt = LBFGS(trajectory='relax.traj')
    opt.run(fmax=f_max, steps=step_max)
write('CONTCAR', ase_atom, format='vasp')
