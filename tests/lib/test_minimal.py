import unittest
import os
import glob
from lammps import PyLammps

class MinimalTests(unittest.TestCase):
    def test_default_settings(self):
        L = PyLammps()

        # verify default settings
        self.assertEqual(L.system.natoms, 0)
        self.assertEqual(L.system.ntypes, 0)
        self.assertEqual(L.system.style, 'none')
        self.assertEqual(L.system.units, 'lj')
        self.assertEqual(L.system.kspace_style, 'none')
        self.assertEqual(L.system.atom_style, 'atomic')
        self.assertEqual(L.system.atom_map, 'none')

        # now explicitly set them and check if nothing changed
        L.units('lj')
        L.boundary("p p p")
        L.lattice("none 1.0")
        L.atom_style("atomic")

        self.assertEqual(L.system.natoms, 0)
        self.assertEqual(L.system.ntypes, 0)
        self.assertEqual(L.system.style, 'none')
        self.assertEqual(L.system.units, 'lj')
        self.assertEqual(L.system.kspace_style, 'none')
        self.assertEqual(L.system.atom_style, 'atomic')
        self.assertEqual(L.system.atom_map, 'none')

    def test_change_system(self):
        L = PyLammps()
        L.units('real')
        L.atom_style('charge')
        self.assertEqual(L.system.units, 'real')
        self.assertEqual(L.system.atom_style, 'charge')

    def test_create_box(self):
        L = PyLammps()
        L.units('real')
        L.lattice('fcc', 3.5)
        L.region("a block", 0, 1, 0, 1, 0, 1)
        L.create_box(1, 'a')

        self.assertEqual(L.system.dimensions, 3)
        self.assertEqual(L.system.orthogonal_box, [3.5, 3.5, 3.5])
        self.assertEqual(L.system.boundaries, 'p,p p,p p,p')
        self.assertEqual(L.system.xlo, 0.0)
        self.assertEqual(L.system.ylo, 0.0)
        self.assertEqual(L.system.zlo, 0.0)
        self.assertEqual(L.system.xhi, 3.5)
        self.assertEqual(L.system.yhi, 3.5)
        self.assertEqual(L.system.zhi, 3.5)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        L = PyLammps()
        L.units('lj')
        L.atom_style('atomic')
        L.boundary('p p p')
        L.atom_modify("map array")

        L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0)
        L.create_box(1, 'r1')

        L.mass(1, 1.0)

        L.create_atoms(1, 'single', -1.0, 0.0, 0.0)
        L.create_atoms(1, 'single',  1.0, 0.0, 0.0)

        L.pair_style('lj/cut', 5.0)
        L.pair_coeff(1, 1, 1.0, 1.0)

        L.run(0)
        self.L = L

    def test_create_atoms(self):
        L = self.L
        self.assertEqual(L.system.natoms, 2)
        self.assertEqual(L.atoms[0].position, (-1.0, 0.0, 0.0))
        self.assertEqual(L.atoms[1].position,  (1.0, 0.0, 0.0))

    def test_read_restart(self):
        L = self.L
        pe = L.eval("pe")

        L.write_restart('/tmp/test_read_restart.restart')
        del L

        L2 = PyLammps()
        L2.read_restart('/tmp/test_read_restart.restart')
        L2.run(0)
        os.remove('/tmp/test_read_restart.restart')

        self.assertEqual(L2.system.natoms, 2)
        self.assertEqual(L2.atoms[0].position, (-1.0, 0.0, 0.0))
        self.assertEqual(L2.atoms[1].position,  (1.0, 0.0, 0.0))
        self.assertEqual(L2.eval("pe"), pe)

    def test_minimization(self):
        L = self.L
        pe = L.eval("pe")
        L.minimize(1.0e-10, 1.0e-10, 1000, 1000)
        pe_min = L.eval("pe")
        self.assertLessEqual(pe_min, pe)

    def test_md_run_zero_velocity(self):
        L = self.L
        L.velocity('all set', 0.0, 0.0, 0.0, 'units box')

        L.run_style('verlet')  # default, select velocity verlet for MD
        L.timestep(0.005)      # default for units lj

        L.fix('f1 all nve')    # do time integration without any modification
        L.thermo(10)           # thermo output every 10 steps

        L.run(100)
        self.assertEqual(int(L.eval("step")), 100)

    def test_md_run_with_temperature(self):
        L = self.L
        L.velocity('all create', 2.0, 66445588)

        L.run_style('verlet')  # default, select velocity verlet for MD
        L.timestep(0.005)      # default for units lj

        L.fix('f1 all nve')    # do time integration without any modification
        L.thermo(10)           # thermo output every 10 steps

        L.run(100)
        self.assertEqual(int(L.eval("step")), 100)


class IncludeTests(unittest.TestCase):
    """
    include command doesn't work in library mode, since the parser isn't active
    """
    ATOMS_SETUP_FILE = "/tmp/inc.2atom"
    VERLET_CONFIG_FILE = "/tmp/inc.nve-verlet"

    def setUp(self):
        with open(IncludeTests.ATOMS_SETUP_FILE, "w") as f:
            f.write("""
# LAMMPS script to generate a simple 2 atom system

# it is good practice to make these settings explicit
units lj
atom_style atomic
boundary p p p

lattice sc 1.0

# create simulation cell
region r1 block -5.0 5.0 -5.0 5.0 -5.0 5.0
create_box 1 r1

# required must come after box is created
mass 1 1.0

# create two atoms,
create_atoms 1 single -1.0 0.0 0.0
create_atoms 1 single  1.0 0.0 0.0
""")
        with open(IncludeTests.VERLET_CONFIG_FILE, "w") as g:
            g.write("""
# set up NVE with Verlet for reduced units and no initial velocity

run_style verlet
timestep  0.005

fix f1 all nve
""")

    def tearDown(self):
        os.remove(IncludeTests.ATOMS_SETUP_FILE)
        os.remove(IncludeTests.VERLET_CONFIG_FILE)

    def test_file_inclusion(self):
        L = PyLammps()
        L.file(IncludeTests.ATOMS_SETUP_FILE)

        # set non-bonded potential
        L.pair_style('lj/cut', 5.0)
        L.pair_coeff(1, 1, 1.0, 1.0)

        # temperature T=1.0
        L.velocity('all create', 1.0, 54321, 'mom no rot no')

        # import time integration setting from include file
        L.file(IncludeTests.VERLET_CONFIG_FILE)

        L.thermo(10)         # thermo output every 10 steps

        L.run(100)

    def test_morse_potential(self):
        L = PyLammps()
        L.file(IncludeTests.ATOMS_SETUP_FILE)

        # set different non-bonded potential
        L.pair_style('morse', 5.0)
        L.pair_coeff(1, 1, 1.0, 5.0, 1.12)

        L.velocity('all create', 1.0, 54321, 'mom no rot no')

        # import time integration setting from include file
        L.file(IncludeTests.VERLET_CONFIG_FILE)

        L.thermo(10)         # thermo output every 10 steps

        L.run(100)

    def test_minimize_before_md(self):
        L = PyLammps()
        L.file(IncludeTests.ATOMS_SETUP_FILE)

        # set non-bonded potential
        L.pair_style('lj/cut', 5.0)
        L.pair_coeff(1, 1, 1.0, 1.0)

        # set different non-bonded potential
        L.velocity('all create', 1.0, 54321, 'mom no rot no')

        # import time integration setting from include file
        L.file(IncludeTests.VERLET_CONFIG_FILE)

        L.minimize(1.0e-10, 1.0e-10, 100, 1000)

        L.reset_timestep(0)  # set timestep counter to zero

        L.thermo(10)         # thermo output every 10 steps

        L.run(100)

    def test_run_post_no_pre_no(self):
        L = PyLammps()
        L.file(IncludeTests.ATOMS_SETUP_FILE)

        # set non-bonded potential
        L.pair_style('lj/cut', 5.0)
        L.pair_coeff(1, 1, 1.0, 1.0)

        # set different non-bonded potential
        L.velocity('all create', 1.0, 54321, 'mom no rot no')

        # import time integration setting from include file
        L.file(IncludeTests.VERLET_CONFIG_FILE)

        L.minimize(1.0e-10, 1.0e-10, 100, 1000)

        L.reset_timestep(0)  # set timestep counter to zero

        L.thermo(10)         # thermo output every 10 steps

        L.run(100, 'post no') # don't print post run information

        L.run(100, 'pre no')  # don't to pre-run preparation (not needed, if no change)

    def test_change_cutoff(self):
        L = PyLammps()
        L.file(IncludeTests.ATOMS_SETUP_FILE)

        # set non-bonded potential
        L.pair_style('lj/cut', 5.0)
        L.pair_coeff(1, 1, 1.0, 1.0)

        # set different non-bonded potential
        L.velocity('all create', 1.0, 54321, 'mom no rot no')

        # import time integration setting from include file
        L.file(IncludeTests.VERLET_CONFIG_FILE)

        L.minimize(1.0e-10, 1.0e-10, 100, 1000)

        L.reset_timestep(0)  # set timestep counter to zero

        L.thermo(10)         # thermo output every 10 steps

        L.run(100)

        L.pair_coeff(1, 1, 1.0, 1.0, 10.0)

        L.run(100)

    def test_change_potential(self):
        L = PyLammps()
        L.file(IncludeTests.ATOMS_SETUP_FILE)

        # set non-bonded potential
        L.pair_style('lj/cut', 5.0)
        L.pair_coeff(1, 1, 1.0, 1.0)

        # set different non-bonded potential
        L.velocity('all create', 1.0, 54321, 'mom no rot no')

        # import time integration setting from include file
        L.file(IncludeTests.VERLET_CONFIG_FILE)

        L.minimize(1.0e-10, 1.0e-10, 100, 1000)

        L.reset_timestep(0)  # set timestep counter to zero

        L.thermo(10)         # thermo output every 10 steps

        L.run(100, 'post no')

        # continue run with different potential
        L.pair_style('morse', 5.0)
        L.pair_coeff(1, 1, 1.0, 5.0, 1.12)

        L.run(100)


class DifferentUnitsTests(unittest.TestCase):
    def test_real_units(self):
        L = PyLammps()
        L.units('real') # angstrom, kcal/mol, femtoseconds
        L.atom_style('atomic')
        L.boundary('p p p')

        L.lattice('none', 1.0)

        # create simulation cell
        L.region('r1 block', -15.0, 15.0, -15.0, 15.0, -15.0, 15.0)
        L.create_box(1, 'r1')

        # argon
        L.mass(1, 39.948002)
        L.pair_style('lj/cut', 8.5)
        L.pair_coeff(1, 1, 0.2379, 3.405)

        L.timestep(10.0)

        L.create_atoms(1, 'single', -1.0, 0.0, 0.0)
        L.create_atoms(1, 'single',  1.0, 0.0, 0.0)

        L.velocity('all create', 250.0, 54321, 'mom no rot no')

        L.minimize(1.0e-10, 1.0e-10, 100, 1000)

        L.reset_timestep(0)

        L.thermo(100)
        L.fix('f1 all nve')
        L.run(1000)

    def test_use_data_file(self):
        L = PyLammps()
        L.units('real') # angstrom, kcal/mol, femtoseconds
        L.atom_style('atomic')
        L.boundary('p p p')

        L.lattice('none', 1.0)

        # create simulation cell
        L.region('r1 block', -15.0, 15.0, -15.0, 15.0, -15.0, 15.0)
        L.create_box(1, 'r1')

        # argon
        L.mass(1, 39.948002)
        L.pair_style('lj/cut', 8.5)
        L.pair_coeff(1, 1, 0.2379, 3.405)

        L.timestep(10.0)

        L.create_atoms(1, 'single', -1.0, 0.0, 0.0)
        L.create_atoms(1, 'single',  1.0, 0.0, 0.0)

        L.velocity('all create', 250.0, 54321, 'mom no rot no')

        L.minimize(1.0e-10, 1.0e-10, 100, 1000)

        L.reset_timestep(0)

        L.thermo(100)
        L.fix('f1 all nve')
        L.run(1000)

        L.write_restart('run.restart')
        L.write_data('run.data')

        L2 = PyLammps()
        L2.units('real')           # angstrom, kcal/mol, femtoseconds
        L2.atom_style('atomic')
        L2.boundary('p p p')

        L2.pair_style('lj/cut', 8.5)
        L2.read_data('run.data')

        L2.timestep(10.0)

        L2.thermo(100)
        L2.fix('f1 all nve')
        L2.run(1000)

        # reset status. forget all settings. delete system
        L2.clear()

        L2.read_restart('run.restart')

        L2.thermo(100)
        L2.fix('f1 all nve')
        L2.run(1000)

        os.remove('run.restart')
        os.remove('run.data')

        self.assertEqual(L.system, L2.system)



class LatticeBoxTests(unittest.TestCase):
    def setUp(self):
        self.L = PyLammps()
        self.L.units('lj')           # default, use reduced units
        self.L.atom_style('atomic')  # default, point particles with mass and type
        self.L.boundary('p p p')     # default, periodic boundaries in 3-d
        self.L.processors('* * *')   # default, automatic domain decomposition
        self.L.newton('on')          # default, use newton's 3rd law for ghost particles

    def assertAlmostEqualList(self, a_list, b_list):
        for a, b in zip(a_list, b_list):
            self.assertAlmostEqual(a, b, places=3)

    def test_lj_none_box(self):
        self.L.lattice('none', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_lj_sc_box(self):
        self.L.lattice('sc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_lj_fcc_box(self):
        self.L.lattice('fcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_lj_bcc_box(self):
        self.L.lattice('bcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_lj_none_lattice(self):
        self.L.lattice('none', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_lj_sc_lattice(self):
        self.L.lattice('sc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertAlmostEqual(self.L.system.xlo, -5.0)
        self.assertAlmostEqual(self.L.system.ylo, -5.0)
        self.assertAlmostEqual(self.L.system.zlo, -5.0)
        self.assertAlmostEqual(self.L.system.xhi, 5.0)
        self.assertAlmostEqual(self.L.system.yhi, 5.0)
        self.assertAlmostEqual(self.L.system.zhi, 5.0)

    def test_lj_fcc_lattice(self):
        self.L.lattice('fcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        lattice_spacing = 1.5874

        self.assertAlmostEqualList(self.L.system.orthogonal_box, [10*lattice_spacing, 10*lattice_spacing, 10*lattice_spacing])
        self.assertAlmostEqual(self.L.system.xlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.ylo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.xhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.yhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zhi,  5.0 * lattice_spacing, places=3)

    def test_lj_bcc_lattice(self):
        self.L.lattice('bcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        lattice_spacing = 1.25992

        self.assertAlmostEqualList(self.L.system.orthogonal_box, [10*lattice_spacing, 10*lattice_spacing, 10*lattice_spacing])
        self.assertAlmostEqual(self.L.system.xlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.ylo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.xhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.yhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zhi,  5.0 * lattice_spacing, places=3)


class RealUnitsLatticeBoxTests(unittest.TestCase):
    def setUp(self):
        self.L = PyLammps()
        self.L.units('real')           # default, use reduced units
        self.L.atom_style('atomic')  # default, point particles with mass and type
        self.L.boundary('p p p')     # default, periodic boundaries in 3-d
        self.L.processors('* * *')   # default, automatic domain decomposition
        self.L.newton('on')          # default, use newton's 3rd law for ghost particles

    def assertAlmostEqualList(self, a_list, b_list):
        for a, b in zip(a_list, b_list):
            self.assertAlmostEqual(a, b, places=3)

    def test_real_none_box(self):
        self.L.lattice('none', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_real_sc_box(self):
        self.L.lattice('sc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_real_fcc_box(self):
        self.L.lattice('fcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_real_bcc_box(self):
        self.L.lattice('bcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units box')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_real_none_lattice(self):
        self.L.lattice('none', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertEqual(self.L.system.xlo, -5.0)
        self.assertEqual(self.L.system.ylo, -5.0)
        self.assertEqual(self.L.system.zlo, -5.0)
        self.assertEqual(self.L.system.xhi, 5.0)
        self.assertEqual(self.L.system.yhi, 5.0)
        self.assertEqual(self.L.system.zhi, 5.0)

    def test_real_sc_lattice(self):
        self.L.lattice('sc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        self.assertEqual(self.L.system.orthogonal_box, [10, 10, 10])
        self.assertAlmostEqual(self.L.system.xlo, -5.0)
        self.assertAlmostEqual(self.L.system.ylo, -5.0)
        self.assertAlmostEqual(self.L.system.zlo, -5.0)
        self.assertAlmostEqual(self.L.system.xhi, 5.0)
        self.assertAlmostEqual(self.L.system.yhi, 5.0)
        self.assertAlmostEqual(self.L.system.zhi, 5.0)

    def test_real_fcc_lattice(self):
        self.L.lattice('fcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        lattice_spacing = 1.0

        self.assertAlmostEqualList(self.L.system.orthogonal_box, [10*lattice_spacing, 10*lattice_spacing, 10*lattice_spacing])
        self.assertAlmostEqual(self.L.system.xlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.ylo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.xhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.yhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zhi,  5.0 * lattice_spacing, places=3)

    def test_real_bcc_lattice(self):
        self.L.lattice('bcc', 1.0)

        self.L.region('r1 block', -5.0, 5.0, -5.0, 5.0, -5.0, 5.0, 'units lattice')
        self.L.create_box(1, 'r1')

        lattice_spacing = 1.0

        self.assertAlmostEqualList(self.L.system.orthogonal_box, [10*lattice_spacing, 10*lattice_spacing, 10*lattice_spacing])
        self.assertAlmostEqual(self.L.system.xlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.ylo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zlo, -5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.xhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.yhi,  5.0 * lattice_spacing, places=3)
        self.assertAlmostEqual(self.L.system.zhi,  5.0 * lattice_spacing, places=3)


if __name__ == '__main__':
    unittest.main()
