LAMMPS (4 Jan 2019)
# Pure Cu crystal, structure created by LAMMPS, qeq off

units		metal
atom_style	charge
dimension       3
boundary        p p p

lattice  	fcc 3.615
Lattice spacing in x,y,z = 3.615 3.615 3.615
region		box block 0 4 0 4 0 4
create_box	1 box
Created orthogonal box = (0 0 0) to (14.46 14.46 14.46)
  2 by 2 by 2 MPI processor grid
create_atoms	1 box
Created 256 atoms
  Time spent = 0.00083376 secs
mass		1 63.54

pair_style	comb
pair_coeff	* * ffield.comb Cu
Reading potential file ffield.comb with DATE: 2011-02-22

neighbor	0.5 bin
neigh_modify	every 1 delay 1 check yes

fix		1 all nve
timestep        0.00020

thermo_style	custom step temp etotal pe evdwl ecoul press vol lx ly lz xz
thermo_modify	norm yes
velocity	all create 10.1 2398378
thermo	  	1

#dump		1 all custom 10 tmp.dump id type xs ys zs q vx vy vz fx fy fz
#dump_modify	1 append yes element Cu

#dump		2 all image 10 image.*.jpg element element #		axes yes 0.8 0.02 view 60 -30
#dump_modify	2 pad 2 element Cu

#dump		3 all movie 10 movie.mpg element element #		axes yes 0.8 0.02 view 60 -30
#dump_modify	3 pad 2 element Cu

run  		10
Neighbor list info ...
  update every 1 steps, delay 1 steps, check yes
  max neighbors/atom: 2000, page size: 100000
  master list distance cutoff = 12.5
  ghost atom cutoff = 12.5
  binsize = 6.25, bins = 3 3 3
  1 neighbor lists, perpetual/occasional/extra = 1 0 0
  (1) pair comb, perpetual
      attributes: full, newton on
      pair build: full/bin/atomonly
      stencil: full/bin/3d
      bin: standard
Per MPI rank memory allocation (min/avg/max) = 6.807 | 6.807 | 6.807 Mbytes
Step Temp TotEng PotEng E_vdwl E_coul Press Volume Lx Ly Lz Xz 
       0         10.1   -3.5063151   -3.5076155   -3.5076155            0    27.496055    3023.4645        14.46        14.46        14.46            0 
       1    10.099639   -3.5063151   -3.5076155   -3.5076155            0     27.51357    3023.4645        14.46        14.46        14.46            0 
       2    10.098554   -3.5063151   -3.5076153   -3.5076153            0    27.566113    3023.4645        14.46        14.46        14.46            0 
       3    10.096747   -3.5063151   -3.5076151   -3.5076151            0    27.653671    3023.4645        14.46        14.46        14.46            0 
       4    10.094218   -3.5063151   -3.5076148   -3.5076148            0     27.77623    3023.4645        14.46        14.46        14.46            0 
       5    10.090967   -3.5063151   -3.5076144   -3.5076144            0    27.933766    3023.4645        14.46        14.46        14.46            0 
       6    10.086994   -3.5063151   -3.5076139   -3.5076139            0    28.126248    3023.4645        14.46        14.46        14.46            0 
       7    10.082301   -3.5063151   -3.5076132   -3.5076132            0    28.353642    3023.4645        14.46        14.46        14.46            0 
       8    10.076888   -3.5063151   -3.5076126   -3.5076126            0    28.615905    3023.4645        14.46        14.46        14.46            0 
       9    10.070756   -3.5063151   -3.5076118   -3.5076118            0    28.912987    3023.4645        14.46        14.46        14.46            0 
      10    10.063906   -3.5063151   -3.5076109   -3.5076109            0    29.244835    3023.4645        14.46        14.46        14.46            0 
Loop time of 0.0305132 on 8 procs for 10 steps with 256 atoms

Performance: 5.663 ns/day, 4.238 hours/ns, 327.727 timesteps/s
100.0% CPU use with 8 MPI tasks x no OpenMP threads

MPI task timing breakdown:
Section |  min time  |  avg time  |  max time  |%varavg| %total
---------------------------------------------------------------
Pair    | 0.025743   | 0.026944   | 0.028076   |   0.6 | 88.30
Neigh   | 0          | 0          | 0          |   0.0 |  0.00
Comm    | 0.0020651  | 0.0031892  | 0.0043906  |   1.7 | 10.45
Output  | 0.00028491 | 0.00029322 | 0.00032504 |   0.0 |  0.96
Modify  | 8.0754e-06 | 8.5511e-06 | 9.065e-06  |   0.0 |  0.03
Other   |            | 7.845e-05  |            |       |  0.26

Nlocal:    32 ave 32 max 32 min
Histogram: 8 0 0 0 0 0 0 0 0 0
Nghost:    2425 ave 2425 max 2425 min
Histogram: 8 0 0 0 0 0 0 0 0 0
Neighs:    0 ave 0 max 0 min
Histogram: 8 0 0 0 0 0 0 0 0 0
FullNghs:  21568 ave 21568 max 21568 min
Histogram: 8 0 0 0 0 0 0 0 0 0

Total # of neighbors = 172544
Ave neighs/atom = 674
Neighbor list builds = 0
Dangerous builds = 0
Total wall time: 0:00:00
