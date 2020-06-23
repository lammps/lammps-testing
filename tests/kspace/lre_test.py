#!/usr/bin/python

# Script:  lre_test.py
# Purpose: use lre_test.py tool to test LAMMPS's long-range electrostatics
# Syntax:  lre_test.py
# Example: lre_test.py
# Author:  Paul Crozier (Sandia)

# enable script to run from Python directly w/out Pizza.py

from lre_source import lre_verify
lre = lre_verify()

# command used for lammps executable (i.e. mpirun -np 8 /bin/lmp)
lre.execcmd = "mpiexec -np 4 ./lmp.exe"
lre.cleanup()

print
print "Starting LAMMPS long-range electrostatics testing."

# two point charges in a periodic box with Ewald
kspace_style = "ewald"
accuracy = "1e-18"
kspace_modify = ""
xbound = ybound = zbound = "p"
lre.two_point_charges(kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)

# two point charges in a periodic box with PPPM 
kspace_style = "pppm"
accuracy = "1e-8"
kspace_modify = ""
xbound = ybound = zbound = "p"
lre.two_point_charges(kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)

# two point charges in a periodic box with analytic differentiation (ad) PPPM
kspace_style = "pppm"
accuracy = "1e-6"
kspace_modify = "diff ad"
xbound = ybound = zbound = "p"
lre.two_point_charges(kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)

# two point charges in a periodic box with MSM
kspace_style = "msm"
accuracy = "1e-8"
kspace_modify = "pressure/scalar yes"
xbound = ybound = zbound = "p"
lre.two_point_charges(kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)

# two point charges in a non-periodic box with MSM
kspace_style = "msm"
accuracy = "1e-8"
kspace_modify = "pressure/scalar yes"
xbound = ybound = zbound = "f"
lre.two_point_charges(kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)

# two point charges in a slab-geometry box with MSM
kspace_style = "msm"
accuracy = "1e-8"
kspace_modify = "pressure/scalar yes"
xbound = ybound = "p"
zbound = "f"
lre.two_point_charges(kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)

# rhodopsin with Ewald
kspace_style = "ewald"
accuracy = "1e-4"
kspace_modify = ""
lre.rhodopsin(kspace_style,accuracy,kspace_modify)
  
# rhodopsin with PPPM
kspace_style = "pppm"
accuracy = "1e-4"
kspace_modify = ""
lre.rhodopsin(kspace_style,accuracy,kspace_modify)

# rhodopsin with analytic differentiation (ad) PPPM
kspace_style = "pppm"
accuracy = "1e-4"
kspace_modify = "diff ad"
lre.rhodopsin(kspace_style,accuracy,kspace_modify)

# rhodopsin with MSM
kspace_style = "msm"
accuracy = "1e-4"
kspace_modify = "pressure/scalar no"
lre.rhodopsin(kspace_style,accuracy,kspace_modify)

# random point charges in a box with Ewald
kspace_style = "ewald"
accuracy = "1e-5"
kspace_modify = ""
lre.random_point_charges(kspace_style,accuracy,kspace_modify)

# random point charges in a box with PPPM
kspace_style = "pppm"
accuracy = "1e-5"
kspace_modify = ""
lre.random_point_charges(kspace_style,accuracy,kspace_modify)

# random point charges in a box with analytic differentiation (ad) PPPM
kspace_style = "pppm"
accuracy = "1e-5"
kspace_modify = "diff ad"
lre.random_point_charges(kspace_style,accuracy,kspace_modify)

# random point charges in a box with MSM
kspace_style = "msm"
accuracy = "1e-5"
kspace_modify = "pressure/scalar yes"
lre.random_point_charges(kspace_style,accuracy,kspace_modify)

# SPC/E water per-atom dynamic test with Ewald
kspace_style = "ewald"
accuracy = "1e-4"
kspace_modify = ""
lre.spce(kspace_style,accuracy,kspace_modify)

# SPC/E water per-atom dynamic test with PPPM
kspace_style = "pppm"
accuracy = "1e-4"
kspace_modify = ""
lre.spce(kspace_style,accuracy,kspace_modify)

# SPC/E water per-atom dynamic test with analytic differentiation (ad) PPPM
kspace_style = "pppm"
accuracy = "1e-4"
kspace_modify = "diff ad"
lre.spce(kspace_style,accuracy,kspace_modify)

# SPC/E water per-atom dynamic test with MSM
kspace_style = "msm"
accuracy = "1e-4"
kspace_modify = "pressure/scalar no"
lre.spce(kspace_style,accuracy,kspace_modify)

# final tally
lre.final_tally()
