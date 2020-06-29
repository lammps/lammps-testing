# LAMMPS long-range electrostatics verification tests
# Author: Richard Berger (Temple University)
# Based on long-range electrostatics scripts from Paul Crozier and Stan Moore, Sandia National Lab

# Minimum requirements to run:
#  - Installed 'lammps_testing' package
#  - LAMMPS_BINARY environment variable to binary

import os
import math
import unittest

from jinja2 import Environment, FileSystemLoader, Template

from lammps_testing.formats import LammpsLog
from lammps_testing.testrunner import LAMMPSTestCase

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))

class TwoPointCharges(LAMMPSTestCase, unittest.TestCase):
    def test_periodic_box_with_ewald(self):
        """
        two point charges in a periodic box with Ewald
        """
        name = "tpc_periodic_box_with_ewald"
        kspace_style = "ewald"
        accuracy = "1e-18"
        kspace_modify = ""
        xbound = ybound = zbound = "p"
        energy, _ = self.two_point_charges(name, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound)
        self.assertLess(energy,    -119.15)
        self.assertGreater(energy, -119.17) 

    def test_periodic_box_with_pppm(self):
        """
        two point charges in a periodic box with PPPM
        """
        name = "tpc_periodic_box_with_pppm"
        kspace_style = "pppm"
        accuracy = "1e-8"
        kspace_modify = ""
        xbound = ybound = zbound = "p"
        energy, _ = self.two_point_charges(name, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound)
        self.assertLess(energy,    -119.15)
        self.assertGreater(energy, -119.17) 

    def test_periodic_box_with_ad_pppm(self):
        """
        two point charges in a periodic box with analytic differentiation (ad) PPPM
        """
        name = "tpc_periodic_box_with_ad_pppm"
        kspace_style = "pppm"
        accuracy = "1e-6"
        kspace_modify = "diff ad"
        xbound = ybound = zbound = "p"
        energy, _ = self.two_point_charges(name, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound)
        self.assertLess(energy,    -119.15)
        self.assertGreater(energy, -119.17) 

    def test_periodic_box_with_msm(self):
        """
        two point charges in a periodic box with MSM
        """
        name = "tpc_non_periodic_box_with_msm"
        kspace_style = "msm"
        accuracy = "1e-8"
        kspace_modify = "pressure/scalar yes"
        xbound = ybound = zbound = "p"
        energy, _ = self.two_point_charges(name, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound)
        self.assertLess(energy,    -119.15)
        self.assertGreater(energy, -119.17) 

    def test_non_periodic_box_with_msm(self):
        """
        two point charges in a non-periodic box with MSM
        """
        name = "tpc_non_periodic_box_with_msm"
        kspace_style = "msm"
        accuracy = "1e-8"
        kspace_modify = "pressure/scalar yes"
        xbound = ybound = zbound = "f"
        energy, pressure = self.two_point_charges(name, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound)
        self.assertEqual(energy, -113.41162)
        self.assertLess(pressure,    -2591.1516)
        self.assertGreater(pressure, -2593.1516)


    def test_slab_geometry_box_with_msm(self):
        """
        two point charges in a slab-geometry box with MSM
        """
        name = "tpc_slab_geometry_box_with_msm"
        kspace_style = "msm"
        accuracy = "1e-8"
        kspace_modify = "pressure/scalar yes"
        xbound = ybound = "p"
        zbound = "f"
        energy, _ = self.two_point_charges(name, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound)
        self.assertLess(energy,    -119.1)
        self.assertGreater(energy, -119.2) 

  
    def two_point_charges(self, name, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound):
        """
        run a two point charges in a box test
        """
        working_directory = os.path.join(TESTS_DIR, 'kspace')
        infile = os.path.join(working_directory, f"in.{name}")
        logfile = os.path.join(working_directory, f"log.{name}")

        self.in_write_tpc(infile,kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)

        self.run_script(infile, log=logfile, nprocs=4, test_name=name)

        lg = LammpsLog(logfile)
        total_energy_vector = lg.runs[0]["TotEng"]
        pressure_vector = lg.runs[0]["Press"]
        CPU = lg.runs[0]["CPU"]
        energy = total_energy_vector[0]
        pressure = pressure_vector[0]
        
        print(f"Two point charges in a box with boundary {xbound} {ybound} {zbound}")
        print(f"  kspace_style = {kspace_style}")
        print(f"  accuracy = {accuracy}")

        if (kspace_modify != ""):
            print(f"  kspace_modify = {kspace_modify}")

        print(f"  loop time = {CPU[1]}s")
        return energy, pressure

    def in_write_tpc(self, infile, kspace_style, accuracy, kspace_modify, xbound, ybound, zbound):
        """
        write out new LAMMPS input script for two point charges in a box
        """

        if kspace_style == "msm":
            pair_style = "lj/cut/coul/msm"
        else:
            pair_style = "lj/cut/coul/long"

        # in.tpc.tmpl
        loader = FileSystemLoader(os.path.join(TESTS_DIR, 'kspace'))
        env = Environment(loader=loader)
        template = env.get_template("in.tpc.tmpl")
        out = template.render({
            'pair_style': pair_style,
            'kspace_style': kspace_style,
            'accuracy': accuracy,
            'kspace_modify': kspace_modify,
            'xbound': xbound,
            'ybound': ybound,
            'zbound': zbound
        })

        with open(infile,'w') as f:
            print(out, file=f)


class Rhodopsin(LAMMPSTestCase, unittest.TestCase):
    def test_ewald(self):
        """
        rhodopsin with Ewald
        """
        name = "rhodopsin_with_ewald"
        kspace_style = "ewald"
        accuracy = "1e-4"
        kspace_modify = ""
        energy = self.rhodopsin(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(energy, -25340)
        self.assertGreater(energy, -25380)

    def test_pppm(self):
        """
        rhodopsin with PPPM
        """
        name = "rhodopsin_with_pppm"
        kspace_style = "pppm"
        accuracy = "1e-4"
        kspace_modify = ""
        energy = self.rhodopsin(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(energy, -25340)
        self.assertGreater(energy, -25380)

    def test_ad_pppm(self):
        """
        rhodopsin with analytic differentiation (ad) PPPM
        """
        name = "rhodopsin_with_ad_pppm"
        kspace_style = "pppm"
        accuracy = "1e-4"
        kspace_modify = "diff ad"
        energy = self.rhodopsin(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(energy, -25340)
        self.assertGreater(energy, -25380)

    def test_msm(self):
        """
        rhodopsin with MSM
        """
        name = "rhodopsin_with_msm"
        kspace_style = "msm"
        accuracy = "1e-4"
        kspace_modify = "pressure/scalar no"
        energy = self.rhodopsin(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(energy, -25340)
        self.assertGreater(energy, -25380)
  
    def rhodopsin(self, name, kspace_style, accuracy, kspace_modify):
        working_directory = os.path.join(TESTS_DIR, 'kspace')
        infile = os.path.join(working_directory, f"in.{name}")
        logfile = os.path.join(working_directory, f"log.{name}")

        self.in_write_rhodopsin(infile, kspace_style, accuracy, kspace_modify)

        self.run_script(infile, log=logfile, nprocs=4, test_name=name)

        lg = LammpsLog(logfile)
        total_energy_vector = lg.runs[0]["TotEng"]
        CPU = lg.runs[0]["CPU"]
        energy = total_energy_vector[0]
    
        print(f"Rhodopsin test")
        print(f"  kspace_style = {kspace_style}")
        print(f"  accuracy = {accuracy}")
        if kspace_modify != "":
            print(f"  kspace_modify = {kspace_modify}")
        print(f"  loop time = {CPU[1]}s")

        return energy

    def in_write_rhodopsin(self,infile,kspace_style,accuracy,kspace_modify):
        """
        write out new LAMMPS input script for rhodopsin
        """

        if (kspace_style == "msm"):
            pair_style = "lj/charmm/coul/msm"
        else:
            pair_style = "lj/charmm/coul/long"

        # in.rhodopsin.tmpl
        loader = FileSystemLoader(os.path.join(TESTS_DIR, 'kspace'))
        env = Environment(loader=loader)
        template = env.get_template("in.rhodopsin.tmpl")
        out = template.render({
            'pair_style': pair_style,
            'kspace_style': kspace_style,
            'accuracy': accuracy,
            'kspace_modify': kspace_modify
        })

        with open(infile,'w') as f:
            print(out, file=f)


class RandomPointCharges(LAMMPSTestCase, unittest.TestCase):
    def test_ewald(self):
        """
        random point charges in a box with Ewald
        """
        name = "rpc_with_ewald"
        kspace_style = "ewald"
        accuracy = "1e-5"
        kspace_modify = ""
        actual_accuracy = self.random_point_charges(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(actual_accuracy, 1e-2)

    def test_pppm(self):
        """
        random point charges in a box with PPPM
        """
        name = "rpc_with_pppm"
        kspace_style = "pppm"
        accuracy = "1e-5"
        kspace_modify = ""
        actual_accuracy = self.random_point_charges(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(actual_accuracy, 1e-2)

    def test_ad_pppm(self):
        """
        random point charges in a box with analytic differentiation (ad) PPPM
        """
        name = "rpc_with_ad_pppm"
        kspace_style = "pppm"
        accuracy = "1e-5"
        kspace_modify = "diff ad"
        actual_accuracy = self.random_point_charges(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(actual_accuracy, 1e-2)

    def test_msm(self):
        """
        random point charges in a box with MSM
        """
        name = "rpc_with_msm"
        kspace_style = "msm"
        accuracy = "1e-5"
        kspace_modify = "pressure/scalar yes"
        actual_accuracy = self.random_point_charges(name, kspace_style, accuracy, kspace_modify)
        self.assertLess(actual_accuracy, 1e-2)

  
    def random_point_charges(self, name, kspace_style, accuracy, kspace_modify):
        """
        run random point charges in a box test
        """
        working_directory = os.path.join(TESTS_DIR, 'kspace')
        infile = os.path.join(working_directory, f"in.{name}")
        logfile = os.path.join(working_directory, f"log.{name}")

        self.in_write_random(infile, kspace_style, accuracy, kspace_modify)

        self.run_script(infile, log=logfile, nprocs=4, test_name=name)

        lg = LammpsLog(logfile)
        avefersq_vector = lg.runs[2]["c_avefersq"]
        CPU = lg.runs[2]["CPU"]
        avefersq = avefersq_vector[0]
        actual_accuracy = math.sqrt(avefersq)
        
        print(f"Random point charges in a box test")
        print(f"  kspace_style = {kspace_style}")
        print(f"  accuracy = {accuracy}")
        if (kspace_modify != ""):
            print(f"  kspace_modify = {kspace_modify}")
        print(f"  actual_absolute_accuracy = {actual_accuracy}")
        print(f"  loop time = {CPU[1]}s")
        
        return actual_accuracy

    def in_write_random(self,infile,kspace_style,accuracy,kspace_modify):
        """
        write out new LAMMPS input script for random point charges in a box
        """

        if (kspace_style == "msm"):
            pair_style = "lj/cut/coul/msm"
        else:
            pair_style = "lj/cut/coul/long"

        # in.random.tmpl
        loader = FileSystemLoader(os.path.join(TESTS_DIR, 'kspace'))
        env = Environment(loader=loader)
        template = env.get_template("in.random.tmpl")
        out = template.render({
            'pair_style': pair_style,
            'kspace_style': kspace_style,
            'accuracy': accuracy,
            'kspace_modify': kspace_modify
        })

        with open(infile,'w') as f:
            print(out, file=f)


class SPCEWater(LAMMPSTestCase, unittest.TestCase):
    def test_ewald(self):
        """
        SPC/E water per-atom dynamic test with Ewald
        """
        name = "spce_water_with_ewald"
        kspace_style = "ewald"
        accuracy = "1e-4"
        kspace_modify = ""
        run = self.spce(name, kspace_style, accuracy, kspace_modify)
        self.assertEqualToStandard(run)

    def test_pppm(self):
        """
        SPC/E water per-atom dynamic test with PPPM
        """
        name = "spce_water_with_pppm"
        kspace_style = "pppm"
        accuracy = "1e-4"
        kspace_modify = ""
        run = self.spce(name, kspace_style, accuracy, kspace_modify)
        self.assertEqualToStandard(run)

    def test_ad_pppm(self):
        """
        SPC/E water per-atom dynamic test with analytic differentiation (ad) PPPM
        """
        name = "spce_water_with_ad_pppm"
        kspace_style = "pppm"
        accuracy = "1e-4"
        kspace_modify = "diff ad"
        run = self.spce(name, kspace_style, accuracy, kspace_modify)
        self.assertEqualToStandard(run)

    def test_msm(self):
        # SPC/E water per-atom dynamic test with MSM
        name = "spce_water_with_msm"
        kspace_style = "msm"
        accuracy = "1e-4"
        kspace_modify = "pressure/scalar no"
        run = self.spce(name, kspace_style, accuracy, kspace_modify)
        self.assertEqualToStandard(run)

    def spce(self, name, kspace_style, accuracy, kspace_modify):
        """
        SPC/E water per-atom dynamic test
        """
        working_directory = os.path.join(TESTS_DIR, 'kspace')
        infile = os.path.join(working_directory, f"in.{name}")
        logfile = os.path.join(working_directory, f"log.{name}")

        self.in_write_spce(infile, kspace_style, accuracy, kspace_modify)

        self.run_script(infile, log=logfile, nprocs=4, test_name=name)

        lg = LammpsLog(logfile)
        run = lg.runs[0]
        CPU = lg.runs[0]["CPU"]
    
        print(f"SPC/E test")
        print(f"  kspace_style = {kspace_style}")
        print(f"  accuracy = {accuracy}")
        if (kspace_modify != ""):
            print(f"  kspace_modify = {kspace_modify}")
        print(f"  loop time = {CPU[1]}s")
        return run
    
    def assertEqualToStandard(self, run):
        # standards are from an Ewald run with accuracy = 1e-11
        energy_standard_0 = {
            'PotEng': -132836.07,
            'sumpe':  -132836.07
        }        

        pressure_standard_0 = {
            'Press':    513.09891,
            'sumpress': 513.09891,
            'Pxx' :     739.08898,
            'sumpxx':   739.08898,
            'Pyy':      716.26619,
            'sumpyy':   716.26619,
            'Pzz':      83.941557,
            'sumpzz':   83.941557,
            'Pxy':    -199.36292,
            'sumpxy': -199.36292,
            'Pxz':     31.400221,
            'sumpxz':  31.400221,
            'Pyz':     48.176233,
            'sumpyz':  48.176233
        }

        energy_standard_1 = {
            'PotEng': -132836.07,
            'sumpe':  -132836.07
        }

        pressure_standard_1 = {
            'Press':     1171.2733,
            'sumpress':  1171.2733,
            'Pxx':       1177.1297,
            'sumpxx':    1177.1297,
            'Pyy':       1337.6253,
            'sumpyy':    1337.6253,
            'Pzz':       999.06488,
            'sumpzz':    999.06488,
            'Pxy':      -59.272685,
            'sumpxy':   -59.272685,
            'Pxz':      -37.35268,
            'sumpxz':   -37.35268,
            'Pyz':       26.972408,
            'sumpyz':    26.972408
        }

        energy_tolerance = 3
        pressure_tolerance = 12
        self.longMessage = True

        def assertEnergy(field, current, standard):
            self.assertGreater(current[field], standard[field] - energy_tolerance, f"{field} not within energy tolerance")
            self.assertLess(current[field], standard[field] + energy_tolerance, f"{field} not within energy tolerance")

        def assertPressure(field, current, standard):
            self.assertGreater(current[field], standard[field] - pressure_tolerance, f"{field} not within pressure tolerance")
            self.assertLess(current[field], standard[field] + pressure_tolerance, f"{field} not within pressure tolerance")

        def energy_and_pressure(run, index):
            energy = {
                'PotEng': run['PotEng'][index],
                'sumpe':  run['c_sumpe'][index]
            }
            pressure = {
                'Press':    run['Press'][index],
                'sumpress': run['v_sumpress'][index],
                'Pxx' :     run['Pxx'][index],
                'sumpxx':   run['v_sumpxx'][index],
                'Pyy':      run['Pyy'][index],
                'sumpyy':   run['v_sumpyy'][index],
                'Pzz':      run['Pzz'][index],
                'sumpzz':   run['v_sumpzz'][index],
                'Pxy':      run['Pxy'][index],
                'sumpxy':   run['v_sumpxy'][index],
                'Pxz':      run['Pxz'][index],
                'sumpxz':   run['v_sumpxz'][index],
                'Pyz':      run['Pyz'][index],
                'sumpyz':   run['v_sumpyz'][index]
            }
            return energy, pressure

        energy_0, pressure_0 = energy_and_pressure(run, 0)
        energy_1, pressure_1 = energy_and_pressure(run, 1)

        for field in energy_0.keys():
            assertEnergy(field, energy_0, energy_standard_0)

        for field in pressure_0.keys():
            assertPressure(field, pressure_0, pressure_standard_0)

        for field in energy_1.keys():
            assertEnergy(field, energy_1, energy_standard_1)

        for field in pressure_0.keys():
            assertPressure(field, pressure_1, pressure_standard_1)

    def in_write_spce(self,infile,kspace_style,accuracy,kspace_modify):
        """
        write out new LAMMPS input script for SPC/E test
        """
        if kspace_style == "msm":
            pair_style = "lj/cut/coul/msm"
        else:
            pair_style = "lj/cut/coul/long"
        
        # in.spce.tmpl
        loader = FileSystemLoader(os.path.join(TESTS_DIR, 'kspace'))
        env = Environment(loader=loader)
        template = env.get_template("in.spce.tmpl")
        out = template.render({
            'pair_style': pair_style,
            'kspace_style': kspace_style,
            'accuracy': accuracy,
            'kspace_modify': kspace_modify
        })

        with open(infile,'w') as f:
            print(out, file=f)

if __name__ == '__main__':
    unittest.main()
