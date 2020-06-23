# LAMMPS long-range electrostatics verification testing tool
# authors: Paul Crozier and Stan Moore, Sandia National Labs

oneline = "Test LAMMPS's long-range electrostatics capabilities"

docstr = """
lre = lre_verify()         create an lre object
"""

# History
#   January 2013, Paul Crozier and Stan Moore: original version

# Imports and external programs

from log import log
import os, sys, math

# Class definition

class lre_verify:

  # --------------------------------------------------------------------
  
  def __init__(self):

    self.seed = 12345
    self.tests = 0
    self.passes = 0
    self.fails = 0

  # --------------------------------------------------------------------
  # run a two point charges in a box test
  
  def two_point_charges(self,kspace_style,accuracy,kspace_modify,xbound,ybound,zbound):
    
    self.tests += 1
    infile = "test" + str(self.tests) + ".in"
    logfile = "test" + str(self.tests) + ".log"
    self.in_write_tpc(infile,kspace_style,accuracy,kspace_modify,xbound,ybound,zbound)
    self.run(infile,logfile)
    lg = log(logfile)
    total_energy_vector, pressure_vector, CPU = lg.get("TotEng", "Press", "CPU")
    energy = total_energy_vector[0]
    pressure = pressure_vector[0]
    
    print
    print "Test #" + str(self.tests) + ":"
    print "  Two point charges in a box with boundary " + xbound + " " + ybound + " " + zbound
    print "    kspace_style = " + kspace_style
    print "    accuracy = " + accuracy
    if (kspace_modify != ""): print "    kspace_modify = " + kspace_modify
    print "    loop time = " + str(CPU[1]) + " s"
    
    if (((xbound == "p") and (ybound == "p") and (zbound == "p") and (energy < -119.15) and (energy > -119.17)) or \
        ((xbound == "f") and (ybound == "f") and (zbound == "f") and (energy == -113.41162) and (pressure < -2591.1516) and (pressure > -2593.1516)) or \
        ((xbound == "p") and (ybound == "p") and (zbound == "f") and (energy < -119.1) and (energy > -119.2))):
      print "  PASSED"
      self.passes += 1
    else: 
      print "  FAILED"
      self.fails += 1

  # --------------------------------------------------------------------
  # write out new LAMMPS input script for two point charges in a box

  def in_write_tpc(self,infile,kspace_style,accuracy,kspace_modify,xbound,ybound,zbound):

    input_txt = """
units           real
atom_style      charge
atom_modify     map array

boundary        %s %s %s

lattice         sc 1.0
region          box block 0 10 0 10 0 10
create_box      1 box

create_atoms    1 single 5 5 5 units box
variable        q equal 1.0
set             atom 1 charge $q
print           "Atom number 1 created."

create_atoms    1 single 3.14 2.78 5.43 units box
variable        q equal -1.0
set             atom 2 charge $q
print           "Atom number 2 created."

mass            1 1.0
pair_style      %s 10.0
pair_coeff      1 1 0.0 0.0
pair_modify     table 0 
kspace_style    %s %s
kspace_modify   %s
thermo_style    custom step cpu etotal press
run             100
""" 

    pair_style = "lj/cut/coul/long"
    if (kspace_style == "msm"): pair_style = "lj/cut/coul/msm"
    txt = input_txt % (xbound, ybound, zbound, pair_style, kspace_style, accuracy, kspace_modify)

    f = open(infile,'w')
    print >>f,txt
    f.close()

  # --------------------------------------------------------------------
  # run rhodopsin test
  
  def rhodopsin(self,kspace_style,accuracy,kspace_modify):
    
    self.tests += 1
    infile = "test" + str(self.tests) + ".in"
    logfile = "test" + str(self.tests) + ".log"
    self.in_write_rhodopsin(infile,kspace_style,accuracy,kspace_modify)
    self.run(infile,logfile)
    lg = log(logfile)
    total_energy, CPU = lg.get("TotEng", "CPU")
    energy = total_energy[0]
    
    print
    print "Test #" + str(self.tests) + ":"
    print "  Rhodopsin test"
    print "    kspace_style = " + kspace_style
    print "    accuracy = " + accuracy
    if (kspace_modify != ""): print "    kspace_modify = " + kspace_modify
    print "    loop time = " + str(CPU[1]) + " s"
        
    if ((energy < -25340) and (energy > -25380)):
      print "  PASSED"
      self.passes += 1
    else: 
      print "  FAILED"
      self.fails += 1

  # --------------------------------------------------------------------
  # write out new LAMMPS input script for rhodopsin

  def in_write_rhodopsin(self,infile,kspace_style,accuracy,kspace_modify):

    input_txt = """
# Rhodopsin model

units           real  
neigh_modify    delay 5 every 1   

atom_style      full  
bond_style      harmonic 
angle_style     charmm 
dihedral_style  charmm 
improper_style  harmonic 
pair_style      %s 8.0 10.0 
pair_modify     mix arithmetic 
kspace_style    %s %s 
kspace_modify   %s

read_data       data.rhodo

fix             1 all shake 0.0001 5 0 m 1.0 a 232
fix             2 all npt temp 300.0 300.0 100.0 &
                z 0.0 0.0 1000.0 mtk no pchain 0 tchain 1

special_bonds   charmm
 
thermo          50
thermo_style    custom step etotal cpu 
timestep        2.0

run             1
""" 

    pair_style = "lj/charmm/coul/long"
    if (kspace_style == "msm"): pair_style = "lj/charmm/coul/msm"
    txt = input_txt % (pair_style, kspace_style, accuracy, kspace_modify)

    f = open(infile,'w')
    print >>f,txt
    f.close()

  # --------------------------------------------------------------------
  # run random point charges in a box test
  
  def random_point_charges(self,kspace_style,accuracy,kspace_modify):
    
    self.tests += 1
    infile = "test" + str(self.tests) + ".in"
    logfile = "test" + str(self.tests) + ".log"
    self.in_write_random(infile,kspace_style,accuracy,kspace_modify)
    self.run(infile,logfile)
    lg = log(logfile)
    avefersq_vec, CPU = lg.get("c_avefersq", "CPU")
    avefersq = avefersq_vec[0]
    actual_accuracy = math.sqrt(avefersq)
    delete_args = "rm tmp.log"
    os.popen(delete_args, 'w')
    
    print
    print "Test #" + str(self.tests) + ":"
    print "  Random point charges in a box test"
    print "    kspace_style = " + kspace_style
    print "    accuracy = " + accuracy
    if (kspace_modify != ""): print "    kspace_modify = " + kspace_modify
    print "    actual_absolute_accuracy = " + str(actual_accuracy)
    print "    loop time = " + str(CPU[1]) + " s"
    
    if (actual_accuracy < 1e-2):
      print "  PASSED"
      self.passes += 1
    else: 
      print "  FAILED"
      self.fails += 1

  # --------------------------------------------------------------------
  # write out new LAMMPS input script for random point charges in a box

  def in_write_random(self,infile,kspace_style,accuracy,kspace_modify):

    input_txt = """
log             tmp.log
variable        n equal 100                # number of particles (choose an even integer)
variable        box_length equal 30        # size of the box in real units
variable        rmin equal 2               # minimum separation between particles

units           real
atom_style      charge
atom_modify     map array

lattice         sc 1.0
region          box block 0 ${box_length} 0 ${box_length} 0 ${box_length}
create_box      1 box

variable        q equal 1
variable        x equal random(xlo,xhi,123456)
variable        y equal random(ylo,yhi,123456)
variable        z equal random(zlo,zhi,123456)
label           loopa
variable        a loop $n
  label           loopb
  label           try_again
  variable        xtmp equal $x
  variable        ytmp equal $y
  variable        ztmp equal $z
  variable        b loop $a
    if              '$a == $b' then "jump SELF break"
    variable        xb equal x[$b]
    variable        yb equal y[$b]
    variable        zb equal z[$b]
    variable        r equal sqrt((${xtmp}-${xb})^2+(${ytmp}-${yb})^2+(${ztmp}-${zb})^2)
    if              '$r < ${rmin}' then "jump SELF try_again"
    label           break
  next            b
  jump            SELF loopb
  create_atoms    1 single $x $y $z units box
  variable        q equal -$q
  set             atom $a charge $q
  print           "Atom number $a created."
next            a
jump            SELF loopa

mass            1 1.0
pair_style      lj/cut/coul/long 10.0
pair_coeff      1 1 0.0 0.0
pair_modify     table 0

kspace_style    ewald 1e-18
run             0
fix             ref all store/state 0 fx fy fz

pair_style      %s 10.0
pair_coeff      1 1 0.0 0.0
pair_modify     table 0
kspace_style    %s %s
kspace_modify   %s
thermo_style    one
run             0
fix             test all store/state 0 fx fy fz
variable        ferrsq atom ((f_ref[1]-f_test[1])^2+(f_ref[2]-f_test[2])^2+(f_ref[3]-f_test[3])^2)
compute         avefersq all reduce ave v_ferrsq
thermo_style    custom step c_avefersq cpu
log             test%s.log
run             100
variable        rms_force_error equal sqrt(c_avefersq)
print           "computed absolute RMS force accuracy = ${rms_force_error}"
unfix           test
uncompute       avefersq
""" 

    pair_style = "lj/cut/coul/long"
    if (kspace_style == "msm"): pair_style = "lj/cut/coul/msm"
    txt = input_txt % (pair_style, kspace_style, accuracy, kspace_modify, str(self.tests))
    
    f = open(infile,'w')
    print >>f,txt
    f.close()

  # --------------------------------------------------------------------
  # run random point charges in a box test
  
  def spce(self,kspace_style,accuracy,kspace_modify):
    
    self.tests += 1
    infile = "test" + str(self.tests) + ".in"
    logfile = "test" + str(self.tests) + ".log"
    self.in_write_spce(infile,kspace_style,accuracy,kspace_modify)
    self.run(infile,logfile)
    lg = log(logfile)
    Step, CPU, PotEng, sumpe, Press, sumpress, Pxx, sumpxx, Pyy, sumpyy, Pzz, sumpzz, Pxy, sumpxy, Pxz, sumpxz, Pyz, sumpyz = \
    lg.get("Step", "CPU", "PotEng", "c_sumpe", "Press", "v_sumpress", "Pxx", "v_sumpxx", "Pyy", "v_sumpyy", "Pzz", "v_sumpzz", "Pxy", "v_sumpxy", "Pxz", "v_sumpxz", "Pyz", "v_sumpyz")
    
    print
    print "Test #" + str(self.tests) + ":"
    print "  SPC/E test"
    print "    kspace_style = " + kspace_style
    print "    accuracy = " + accuracy
    if (kspace_modify != ""): print "    kspace_modify = " + kspace_modify
    print "    loop time = " + str(CPU[1]) + " s"
    
    # standards are from an Ewald run with accuracy = 1e-11

    PotEng0_standard =   -132836.07
    sumpe0_standard =    -132836.07 
    Press0_standard =     513.09891
    sumpress0_standard =  513.09891
    Pxx0_standard =       739.08898
    sumpxx0_standard =    739.08898 
    Pyy0_standard =       716.26619
    sumpyy0_standard =    716.26619
    Pzz0_standard =       83.941557
    sumpzz0_standard =    83.941557
    Pxy0_standard =      -199.36292
    sumpxy0_standard =   -199.36292
    Pxz0_standard =       31.400221
    sumpxz0_standard =    31.400221
    Pyz0_standard =       48.176233 
    sumpyz0_standard =    48.176233
    PotEng1_standard =   -132836.07
    sumpe1_standard =    -132836.07
    Press1_standard =     1171.2733
    sumpress1_standard =  1171.2733
    Pxx1_standard =       1177.1297
    sumpxx1_standard =    1177.1297
    Pyy1_standard =       1337.6253
    sumpyy1_standard =    1337.6253
    Pzz1_standard =       999.06488
    sumpzz1_standard =    999.06488
    Pxy1_standard =      -59.272685
    sumpxy1_standard =   -59.272685
    Pxz1_standard =      -37.35268
    sumpxz1_standard =   -37.35268
    Pyz1_standard =       26.972408
    sumpyz1_standard =    26.972408

    energy_tolerance = 3
    pressure_tolerance = 12
   
    if ((PotEng[0]   <   PotEng0_standard +   energy_tolerance) and (PotEng[0]   >   PotEng0_standard -   energy_tolerance) and \
        (sumpe[0]    <    sumpe0_standard +   energy_tolerance) and (sumpe[0]    >    sumpe0_standard -   energy_tolerance) and \
        (Press [0]   <    Press0_standard + pressure_tolerance) and (Press [0]   >    Press0_standard - pressure_tolerance) and \
        (sumpress[0] < sumpress0_standard + pressure_tolerance) and (sumpress[0] > sumpress0_standard - pressure_tolerance) and \
        (Pxx[0]      <      Pxx0_standard + pressure_tolerance) and (Pxx[0]      >      Pxx0_standard - pressure_tolerance) and \
        (sumpxx[0]   <   sumpxx0_standard + pressure_tolerance) and (sumpxx[0]   >   sumpxx0_standard - pressure_tolerance) and \
        (Pyy[0]      <      Pyy0_standard + pressure_tolerance) and (Pyy[0]      >      Pyy0_standard - pressure_tolerance) and \
        (sumpyy[0]   <   sumpyy0_standard + pressure_tolerance) and (sumpyy[0]   >   sumpyy0_standard - pressure_tolerance) and \
        (Pzz[0]      <      Pzz0_standard + pressure_tolerance) and (Pzz[0]      >      Pzz0_standard - pressure_tolerance) and \
        (sumpzz[0]   <   sumpzz0_standard + pressure_tolerance) and (sumpzz[0]   >   sumpzz0_standard - pressure_tolerance) and \
        (Pxy[0]      <      Pxy0_standard + pressure_tolerance) and (Pxy[0]      >      Pxy0_standard - pressure_tolerance) and \
        (sumpxy[0]   <   sumpxy0_standard + pressure_tolerance) and (sumpxy[0]   >   sumpxy0_standard - pressure_tolerance) and \
        (Pxz[0]      <      Pxz0_standard + pressure_tolerance) and (Pxz[0]      >      Pxz0_standard - pressure_tolerance) and \
        (sumpxz[0]   <   sumpxz0_standard + pressure_tolerance) and (sumpxz[0]   >   sumpxz0_standard - pressure_tolerance) and \
        (Pyz[0]      <      Pyz0_standard + pressure_tolerance) and (Pyz[0]      >      Pyz0_standard - pressure_tolerance) and \
        (sumpyz[0]   <   sumpyz0_standard + pressure_tolerance) and (sumpyz[0]   >   sumpyz0_standard - pressure_tolerance) and \
        (PotEng[1]   <   PotEng1_standard +   energy_tolerance) and (PotEng[1]   >   PotEng1_standard -   energy_tolerance) and \
        (sumpe[1]    <    sumpe1_standard +   energy_tolerance) and (sumpe[1]    >    sumpe1_standard -   energy_tolerance) and \
        (Press [1]   <    Press1_standard + pressure_tolerance) and (Press [1]   >    Press1_standard - pressure_tolerance) and \
        (sumpress[1] < sumpress1_standard + pressure_tolerance) and (sumpress[1] > sumpress1_standard - pressure_tolerance) and \
        (Pxx[1]      <      Pxx1_standard + pressure_tolerance) and (Pxx[1]      >      Pxx1_standard - pressure_tolerance) and \
        (sumpxx[1]   <   sumpxx1_standard + pressure_tolerance) and (sumpxx[1]   >   sumpxx1_standard - pressure_tolerance) and \
        (Pyy[1]      <      Pyy1_standard + pressure_tolerance) and (Pyy[1]      >      Pyy1_standard - pressure_tolerance) and \
        (sumpyy[1]   <   sumpyy1_standard + pressure_tolerance) and (sumpyy[1]   >   sumpyy1_standard - pressure_tolerance) and \
        (Pzz[1]      <      Pzz1_standard + pressure_tolerance) and (Pzz[1]      >      Pzz1_standard - pressure_tolerance) and \
        (sumpzz[1]   <   sumpzz1_standard + pressure_tolerance) and (sumpzz[1]   >   sumpzz1_standard - pressure_tolerance) and \
        (Pxy[1]      <      Pxy1_standard + pressure_tolerance) and (Pxy[1]      >      Pxy1_standard - pressure_tolerance) and \
        (sumpxy[1]   <   sumpxy1_standard + pressure_tolerance) and (sumpxy[1]   >   sumpxy1_standard - pressure_tolerance) and \
        (Pxz[1]      <      Pxz1_standard + pressure_tolerance) and (Pxz[1]      >      Pxz1_standard - pressure_tolerance) and \
        (sumpxz[1]   <   sumpxz1_standard + pressure_tolerance) and (sumpxz[1]   >   sumpxz1_standard - pressure_tolerance) and \
        (Pyz[1]      <      Pyz1_standard + pressure_tolerance) and (Pyz[1]      >      Pyz1_standard - pressure_tolerance) and \
        (sumpyz[1]   <   sumpyz1_standard + pressure_tolerance) and (sumpyz[1]   >   sumpyz1_standard - pressure_tolerance)): 
      print "  PASSED"
      self.passes += 1
    else: 
      print "  FAILED"
      self.fails += 1

  # --------------------------------------------------------------------
  # write out new LAMMPS input script for SPC/E test

  def in_write_spce(self,infile,kspace_style,accuracy,kspace_modify):

    input_txt = """

    # SPC/E water box benchmark

units           real
atom_style      full

reset_timestep  0

pair_style      %s 15.0
kspace_style    %s %s
kspace_modify   %s

bond_style      harmonic
angle_style     harmonic
dihedral_style  none
improper_style  none

read_data data.spce

replicate       2 2 2

special_bonds   lj/coul 0.0 0.0 0.5

fix             1 all shake 0.0001 20 0 b 1 a 1

velocity        all create 300 432567 dist uniform

timestep        2.0
thermo          1

compute         peperatom all pe/atom
compute         sumpe all reduce sum c_peperatom

compute         pressperatom all stress/atom NULL
variable        myperatomp atom (c_pressperatom[1]+c_pressperatom[2]+c_pressperatom[3]+c_pressperatom[4]+c_pressperatom[5]+c_pressperatom[6])
compute         p all reduce sum c_pressperatom[1] c_pressperatom[2] c_pressperatom[3] c_pressperatom[4] c_pressperatom[5] c_pressperatom[6]
variable        sumpress equal -(c_p[1]+c_p[2]+c_p[3])/(3*vol)
variable        sumpxx equal -c_p[1]/vol
variable        sumpyy equal -c_p[2]/vol
variable        sumpzz equal -c_p[3]/vol
variable        sumpxy equal -c_p[4]/vol
variable        sumpxz equal -c_p[5]/vol
variable        sumpyz equal -c_p[6]/vol

thermo_style    custom step cpu pe c_sumpe press v_sumpress pxx v_sumpxx pyy v_sumpyy pzz v_sumpzz pxy v_sumpxy pxz v_sumpxz pyz v_sumpyz

run             1
""" 

    pair_style = "lj/cut/coul/long"
    if (kspace_style == "msm"): pair_style = "lj/cut/coul/msm"
    txt = input_txt % (pair_style, kspace_style, accuracy, kspace_modify)
    
    f = open(infile,'w')
    print >>f,txt
    f.close()

  # --------------------------------------------------------------------
  # execute LAMMPS

  def run(self,infile,logfile):
    
    lammpsargs = self.execcmd + " -in " + infile + \
        " -log " + logfile + " -screen none"  

    print
    print "Now running LAMMPS long-range electrostatics test #" + \
      str(self.tests) + " ..."
    print
    
    os.popen(lammpsargs, 'w')

  # --------------------------------------------------------------------
  # delete intermediate files

  def cleanup(self):

    delete_args = "rm test*.in test*.log"
    os.popen(delete_args, 'w')

  # --------------------------------------------------------------------
  # give user final stats

  def final_tally(self):

    print
    print "Completed LAMMPS long-range electrostatics testing."
    print "  Tests : ", self.tests
    print "  Passes: ", self.passes
    print "  Fails : ", self.fails
    print

  # --------------------------------------------------------------------

  def random(self):
    k = self.seed/IQ
    self.seed = IA*(self.seed-k*IQ) - IR*k
    if self.seed < 0:
      self.seed += IM
    return AM*self.seed

# --------------------------------------------------------------------
# random # generator constants

IM = 2147483647
AM = 1.0/IM
IA = 16807
IQ = 127773
IR = 2836    
