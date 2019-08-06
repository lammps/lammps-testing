LAMMPS (4 Jan 2019)
# sample LAMMPS input script for thermal conductivity of liquid LJ
# Muller-Plathe method via fix thermal_conductivity

# settings

variable	x equal 10
variable	y equal 10
variable	z equal 20

variable	rho equal 0.6
variable        t equal 1.35
variable	rc equal 2.5

#variable	rho equal 0.85
#variable        t equal 0.7
#variable	rc equal 3.0

# setup problem

units		lj
atom_style	atomic

lattice		fcc ${rho}
lattice		fcc 0.6
Lattice spacing in x,y,z = 1.88207 1.88207 1.88207
region		box block 0 $x 0 $y 0 $z
region		box block 0 10 0 $y 0 $z
region		box block 0 10 0 10 0 $z
region		box block 0 10 0 10 0 20
create_box	1 box
Created orthogonal box = (0 0 0) to (18.8207 18.8207 37.6414)
  2 by 1 by 4 MPI processor grid
create_atoms	1 box
Created 8000 atoms
  Time spent = 0.0011959 secs
mass		1 1.0

velocity	all create $t 87287
velocity	all create 1.35 87287

pair_style	lj/cut ${rc}
pair_style	lj/cut 2.5
pair_coeff	1 1 1.0 1.0

neighbor	0.3 bin
neigh_modify	delay 0 every 1

# 1st equilibration run

fix		1 all nvt temp $t $t 0.5
fix		1 all nvt temp 1.35 $t 0.5
fix		1 all nvt temp 1.35 1.35 0.5
thermo		100
run		1000
Neighbor list info ...
  update every 1 steps, delay 0 steps, check yes
  max neighbors/atom: 2000, page size: 100000
  master list distance cutoff = 2.8
  ghost atom cutoff = 2.8
  binsize = 1.4, bins = 14 14 27
  1 neighbor lists, perpetual/occasional/extra = 1 0 0
  (1) pair lj/cut, perpetual
      attributes: half, newton on
      pair build: half/bin/atomonly/newton
      stencil: half/bin/3d/newton
      bin: standard
Per MPI rank memory allocation (min/avg/max) = 3.151 | 3.151 | 3.151 Mbytes
Step Temp E_pair E_mol TotEng Press 
       0         1.35   -4.1241917            0   -2.0994448   -3.1961612 
     100    1.1819832   -3.7640881            0    -1.991335   0.53985757 
     200    1.2578365   -3.7395333            0   -1.8530144   0.69591862 
     300    1.3282971   -3.7215427            0   -1.7293461   0.79036065 
     400    1.3714367   -3.7043826            0   -1.6474847   0.85873226 
     500    1.3590952   -3.6707735            0   -1.6323855   0.99602024 
     600    1.3575117   -3.7118244            0   -1.6758114   0.81454305 
     700    1.3284444   -3.7075488            0   -1.7151313   0.81136596 
     800    1.3419995   -3.7155648            0   -1.7028172   0.82925676 
     900    1.3562214   -3.6965609            0   -1.6624831   0.88908117 
    1000    1.3732017   -3.7100044            0   -1.6504594   0.83982701 
Loop time of 0.970362 on 8 procs for 1000 steps with 8000 atoms

Performance: 445194.895 tau/day, 1030.544 timesteps/s
97.1% CPU use with 8 MPI tasks x no OpenMP threads

MPI task timing breakdown:
Section |  min time  |  avg time  |  max time  |%varavg| %total
---------------------------------------------------------------
Pair    | 0.48908    | 0.50112    | 0.51286    |   1.1 | 51.64
Neigh   | 0.24536    | 0.25312    | 0.26581    |   1.2 | 26.08
Comm    | 0.16401    | 0.17537    | 0.18939    |   1.8 | 18.07
Output  | 0.00025719 | 0.00026755 | 0.0003096  |   0.0 |  0.03
Modify  | 0.030477   | 0.030699   | 0.030804   |   0.1 |  3.16
Other   |            | 0.009783   |            |       |  1.01

Nlocal:    1000 ave 1020 max 982 min
Histogram: 1 0 2 1 0 1 1 1 0 1
Nghost:    2299.5 ave 2331 max 2268 min
Histogram: 1 1 1 1 0 0 0 3 0 1
Neighs:    27122 ave 28382 max 26337 min
Histogram: 2 0 2 1 1 0 0 1 0 1

Total # of neighbors = 216976
Ave neighs/atom = 27.122
Neighbor list builds = 162
Dangerous builds = 0

velocity	all scale $t
velocity	all scale 1.35

unfix		1

# 2nd equilibration run

compute		ke all ke/atom
variable	temp atom c_ke/1.5

fix		1 all nve

compute         layers all chunk/atom bin/1d z lower 0.05 units reduced
fix		2 all ave/chunk 10 100 1000 layers v_temp file profile.mp

fix		3 all thermal/conductivity 10 z 20

variable        tdiff equal f_2[11][3]-f_2[1][3]
thermo_style	custom step temp epair etotal f_3 v_tdiff

thermo		1000
run		2000
Per MPI rank memory allocation (min/avg/max) = 3.405 | 3.405 | 3.405 Mbytes
Step Temp E_pair TotEng f_3 v_tdiff 
    1000         1.35   -3.7100044   -1.6852575            0            0 
    2000    1.3572899   -3.7210084   -1.6853282    873.12373   0.26058005 
    3000     1.359979   -3.7268343   -1.6871208    1750.6998   0.40845169 
Loop time of 2.01165 on 8 procs for 2000 steps with 8000 atoms

Performance: 429499.009 tau/day, 994.211 timesteps/s
98.5% CPU use with 8 MPI tasks x no OpenMP threads

MPI task timing breakdown:
Section |  min time  |  avg time  |  max time  |%varavg| %total
---------------------------------------------------------------
Pair    | 0.9464     | 1.0268     | 1.0825     |   5.3 | 51.04
Neigh   | 0.51611    | 0.53765    | 0.55928    |   2.1 | 26.73
Comm    | 0.30858    | 0.38456    | 0.47056    |  10.6 | 19.12
Output  | 5.9083e-05 | 6.1868e-05 | 7.3615e-05 |   0.0 |  0.00
Modify  | 0.039176   | 0.039904   | 0.040685   |   0.3 |  1.98
Other   |            | 0.02271    |            |       |  1.13

Nlocal:    1000 ave 1078 max 909 min
Histogram: 1 1 0 2 0 0 0 1 2 1
Nghost:    2288.62 ave 2426 max 2135 min
Histogram: 3 1 0 0 0 0 0 0 0 4
Neighs:    27250.5 ave 30566 max 22749 min
Histogram: 1 1 1 1 0 0 0 0 1 3

Total # of neighbors = 218004
Ave neighs/atom = 27.2505
Neighbor list builds = 334
Dangerous builds = 0

# thermal conductivity calculation
# reset fix thermal/conductivity to zero energy accumulation

fix		3 all thermal/conductivity 10 z 20

fix             ave all ave/time 1 1 1000 v_tdiff ave running
thermo_style	custom step temp epair etotal f_3 v_tdiff f_ave

run		2000
Per MPI rank memory allocation (min/avg/max) = 3.656 | 3.657 | 3.658 Mbytes
Step Temp E_pair TotEng f_3 v_tdiff f_ave 
    3000     1.359979   -3.7268343   -1.6871208            0   0.40845169   0.40845169 
    4000    1.3677422   -3.7394376   -1.6880807    815.10494   0.63828426   0.52336797 
    5000    1.3821981   -3.7619293   -1.6888913    1604.5574     0.698557   0.58176432 
Loop time of 2.18145 on 8 procs for 2000 steps with 8000 atoms

Performance: 396067.501 tau/day, 916.823 timesteps/s
98.7% CPU use with 8 MPI tasks x no OpenMP threads

MPI task timing breakdown:
Section |  min time  |  avg time  |  max time  |%varavg| %total
---------------------------------------------------------------
Pair    | 0.82718    | 1.023      | 1.2015     |  15.4 | 46.90
Neigh   | 0.47105    | 0.54127    | 0.60338    |   7.3 | 24.81
Comm    | 0.31432    | 0.55118    | 0.81285    |  27.7 | 25.27
Output  | 6.0974e-05 | 6.2633e-05 | 7.0981e-05 |   0.0 |  0.00
Modify  | 0.038005   | 0.040346   | 0.042704   |   0.9 |  1.85
Other   |            | 0.02557    |            |       |  1.17

Nlocal:    1000 ave 1121 max 876 min
Histogram: 2 1 0 1 0 0 0 0 3 1
Nghost:    2301.5 ave 2545 max 2073 min
Histogram: 2 2 0 0 0 0 0 2 0 2
Neighs:    27432.4 ave 33009 max 21276 min
Histogram: 3 0 0 1 0 0 0 0 1 3

Total # of neighbors = 219459
Ave neighs/atom = 27.4324
Neighbor list builds = 341
Dangerous builds = 0
Total wall time: 0:00:05
