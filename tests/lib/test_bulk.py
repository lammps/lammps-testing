import unittest
import os
import glob
from lammps import PyLammps

class BulkTests(unittest.TestCase):
    def test_melt(self):
        """ 3d Lennard-Jones melt """
        L = PyLammps()
        L.units('lj')
        L.atom_style('atomic')

        L.lattice('fcc', 0.8442)   # NOTE: lattice command is different in LJ units
                                   #       0.8442 is density fraction
        L.region('r1 block', 0, 10, 0, 10, 0, 10)
        L.create_box(1, 'r1')

        # fill box with atoms according to lattice positions
        L.create_atoms(1, 'box')
        L.mass(1, 1.0)
        L.velocity('all create', 3.0, 87287, 'mom no')

        L.timestep(0.002)

        L.pair_style('lj/cut', 2.5)
        L.pair_coeff(1, 1, 1.0, 1.0, 2.5)
        L.fix('f1 all nve')

        L.dump('d1 all image 500 snap-01.*.jpg type type')

        L.thermo(50)
        L.run(500)

        self.assertTrue(os.path.exists('snap-01.0.jpg'))
        self.assertTrue(os.path.exists('snap-01.500.jpg'))
        os.remove('snap-01.0.jpg')
        os.remove('snap-01.500.jpg')

    def test_melt_two_types(self):
        """ 3d Lennard-Jones melt with two atom types """
        L = PyLammps()
        L.units('lj')
        L.atom_style('atomic')
        L.lattice('fcc', 0.8442) # NOTE: lattice command is different in LJ units
        L.region('whole block', 0.0, 10.0, 0, 10, 0, 10)
        L.create_box(2, 'whole')
        L.region('upper block', 4.9, 10.1, 'EDGE EDGE EDGE EDGE')
        L.region('lower block', 0.0,  4.9, 'EDGE EDGE EDGE EDGE')

        # fill box with atoms according to lattice positions
        L.create_atoms(1, 'region upper')
        L.create_atoms(2, 'region lower')

        L.mass(1, 1.0)
        L.mass(2, 2.0)

        L.velocity('all create', 3.0, 87287, 'mom no')
        L.timestep(0.002)
        L.pair_style('lj/cut', 2.5)
        L.pair_coeff('* *', 1.0, 1.0, 2.5)
        L.fix('f1 all nve')

        #L.dump('d1 all image 500 snap-02.*.jpg type type')

        L.thermo(50)
        L.run(500)

    def test_melt_using_groups(self):
        """ 3d Lennard-Jones melt with two atom types """
        L = PyLammps()
        L.units('lj')
        L.atom_style('atomic')
        L.lattice('fcc', 0.8442) # NOTE: lattice command is different in LJ units
        L.region('whole block', 0.0, 10.0, 0, 10, 0, 10)
        L.create_box(2, 'whole')
        L.region('upper block', 4.9, 10.1, 'EDGE EDGE EDGE EDGE')
        L.region('lower block', 0.0,  4.9, 'EDGE EDGE EDGE EDGE')

        # fill box with atoms according to lattice positions
        L.create_atoms(1, 'region upper')
        L.create_atoms(2, 'region lower')

        L.mass(1, 1.0)
        L.mass(2, 2.0)

        L.group('gu', 'type', 1)
        L.group('gl', 'type', 2)

        L.velocity('gu', 'create 2.0 12345 mom no rot no')
        L.velocity('gl', 'create 4.0 54321 mom no rot no')


        L.timestep(0.002)
        L.pair_style('lj/cut', 2.5)
        L.pair_coeff('* *', 1.0, 1.0, 2.5)
        L.fix('f1 all nve')

        #L.dump('d1 all image 500 snap-03.*.jpg type type')

        L.thermo(50)
        L.run(500)


    def test_melt_lorenz_berthelot_mixing(self):
        """ 3d Lennard-Jones melt with two atom types """
        L = PyLammps()
        L.units('lj')
        L.atom_style('atomic')
        L.lattice('fcc', 0.8442) # NOTE: lattice command is different in LJ units
        L.region('whole block', 0.0, 10.0, 0, 10, 0, 10)
        L.create_box(2, 'whole')
        L.region('upper block', 4.9, 10.1, 'EDGE EDGE EDGE EDGE')
        L.region('lower block', 0.0,  4.9, 'EDGE EDGE EDGE EDGE')

        # fill box with atoms according to lattice positions
        L.create_atoms(1, 'region upper')
        L.create_atoms(2, 'region lower')

        L.mass(1, 1.0)
        L.mass(2, 2.0)

        L.group('gu', 'type', 1)
        L.group('gl', 'type', 2)

        L.velocity('gu', 'create 2.0 12345 mom no rot no')
        L.velocity('gl', 'create 4.0 54321 mom no rot no')


        L.timestep(0.002)
        L.pair_style('lj/cut', 2.5)
        L.pair_coeff(1, 1, 1.0, 1.0)
        L.pair_coeff(2, 2, 2.0, 1.0)
        L.pair_modify('mix arithmetic') # use Lorenz-Berthelot mixing rules for coeffs

        L.fix('f1 all nve')

        #L.dump('d1 all image 500 snap-03.*.jpg type type')

        L.thermo(50)
        L.run(500)


class RockSaltTests(unittest.TestCase):
    def setUp(self):
        """create 3d rocksalt-like structure"""
        L = PyLammps()
        L.units('real')         # kcal/mol, Angstrom, picoseconds
        L.atom_style('charge')  # atomic + charge

        # lattice for Na+ ions and box
        L.lattice('fcc', 6.0, 'origin', 0.0, 0.0, 0.0)
        L.region('r1', 'block', -3, 3,-3, 3,-3, 3)
        L.create_box(2, 'r1')

        # fill box with Na+ ions according to lattice positions
        L.create_atoms(1, 'box')

        # new lattice for Cl- ions shifted by half box diagonal
        L.lattice('fcc', 6.0, 'origin', 0.5, 0.5, 0.5)
        L.create_atoms(2, 'box')

        L.mass(1, 22.989770)
        L.mass(2, 35.453)
        L.set('type', 1, 'charge',  1.0)
        L.set('type', 2, 'charge', -1.0)

        L.group('na type', 1)
        L.group('cl type', 2)

        L.velocity('all create', 800.0, 12345, 'mom no rot no')
        L.timestep(0.001)
        self.L = L

    def test_rocksalt_like_struct(self):
        """3d rocksalt-like structure with lj and charge"""
        L = self.L

        # LJ with cutoff coulomb added
        L.pair_style('lj/cut/coul/cut', 15.0)
        L.pair_coeff(1, 1, 0.264, 2.30)
        L.pair_coeff(2, 2, 0.158, 3.20)
        L.pair_modify('mix arithmetic')

        L.fix('f1 all nve')
        #dump		d1 all image 500 snap-05.*.jpg element element
        #dump_modify	d1 element Na Cl

        L.thermo(50)
        L.run(500)


    def test_rocksalt_with_ewalt_summation(self):
        """3d rocksalt-like structure with lj and charge and ewald summation"""
        L = self.L

        # Tosi/Fumi style potential (no mixing)
        L.pair_style('lj/cut/coul/long', 15.0)
        L.pair_coeff(1, 1, 0.264, 2.30)
        L.pair_coeff(2, 2, 0.158, 3.20)
        L.pair_modify('mix arithmetic')
        L.kspace_style('ewald', 1.0e-6)

        L.fix('f1 all nve')
        #dump		d1 all image 500 snap-06.*.jpg element element
        #dump_modify	d1 element Na Cl

        L.thermo(50)
        L.run(500)

    def test_rocksalt_with_pppm_summation(self):
        """3d rocksalt-like structure with lj and charge and ewald summation"""
        L = self.L

        # Tosi/Fumi style potential (no mixing)
        L.pair_style('lj/cut/coul/long', 15.0)
        L.pair_coeff(1, 1, 0.264, 2.30)
        L.pair_coeff(2, 2, 0.158, 3.20)
        L.pair_modify('mix arithmetic')
        L.kspace_style('pppm', 1.0e-6)

        L.fix('f1 all nve')
        #dump		d1 all image 500 snap-07.*.jpg element element
        #dump_modify	d1 element Na Cl

        L.thermo(50)
        L.run(500)

    def test_rocksalt(self):
       """3d rocksalt-like structure with lj and charge and ewald summation"""
       L = self.L
       L.clear()

       L.units('real')        # kcal/mol, Angstrom, picoseconds
       L.atom_style('charge') # atomic + charge

       # lattice for Na+ ions and box
       L.lattice('fcc', 6.0, 'origin', 0.0, 0.0, 0.0)
       L.region('r1', 'block', -3, 3, -3, 3, -3, 3)
       L.create_box(2, 'r1')

       # fill box with Na+ ions according to lattice positions
       L.create_atoms(1, 'box')

       # new lattice for Cl- ions shifted by half box diagonal
       L.lattice('fcc', 6.0, 'origin', 0.5, 0.5, 0.5)
       L.create_atoms(2, 'box')

       L.mass(1, 22.989770)
       L.mass(2, 35.453)
       L.set('type', 1, 'charge',  1.0)
       L.set('type', 2, 'charge', -1.0)

       L.group('na type', 1)
       L.group('cl type', 2)

       L.velocity('all create', 800.0, 12345, 'mom no rot no')
       L.timestep(0.001)

       L.pair_style('lj/cut/coul/long', 15.0)
       L.pair_coeff(1, 1, 0.264, 2.30)
       L.pair_coeff(2, 2, 0.158, 3.20)
       L.pair_modify('mix arithmetic')
       L.kspace_style('pppm', 1.0e-6)

       L.fix('f1 all nve')
       #dump		d1 all image 500 snap-07.*.jpg element element
       #dump_modify	d1 element Na Cl

       L.thermo(50)
       L.run(500)

if __name__ == '__main__':
    unittest.main()
