# SRD viscosity demo - ellipsoids

units		lj
atom_style	ellipsoid
atom_modify	first big
dimension	2

# create big ellipsoidal particles

lattice		sq 0.14
region		box block 0 10 0 10 -0.5 0.5
create_box	2 box
create_atoms	1 region box

set		type 1 mass 1.0
set		type 1 shape 3.0 1.0 1.0
group		big type 1
set		group big quat/random 29898

velocity	big create 1.44 87287 loop geom

# equilibrate big particles

pair_style      gayberne 1.0 3.0 1.0 4.0
pair_coeff      1 1 1.0 1.0 1 1 1 1 1 1
pair_coeff      1 2 1.0 1.0 1 1 1 1 1 1 0.0
pair_coeff      2 2 1.0 1.0 1 1 1 1 1 1 0.0

neighbor	0.3 bin
neigh_modify	delay 0 every 1 check yes

fix		1 big nve/asphere
fix		2 all enforce2d

compute		rot big temp/asphere

#dump		1 all custom 10 dump.ellipsoid.equil id type x y z &
#		  quatw quati quatj quatk

thermo_style	custom step temp c_rot epair etotal press
thermo		100

run		1000

#undump		1
unfix		1
unfix		2

# add small particles as hi density lattice

region		plane block INF INF INF INF -0.001 0.001 units box
lattice		sq 120.0
create_atoms	2 region plane

set		type 2 mass 0.01
group		small type 2
velocity	small create 1.0 593849 loop geom

# delete overlaps
# must set 1-2 cutoff to non-zero value

pair_style	lj/cut 2.5
pair_coeff	1 1 1.0 1.0
pair_coeff	2 2 0.0 1.0 0.0
pair_coeff	1 2 0.0 1.0 2.0

neigh_modify	one 10000

delete_atoms	overlap 1.6 small big

# SRD run

reset_timestep	0

neighbor	0.3 bin
neigh_modify	delay 0 every 1 check yes

comm_modify	mode multi group big vel yes
neigh_modify	include big

# no pairwise interactions with small particles

pair_style      gayberne 1.0 3.0 1.0 4.0
pair_coeff      1 1 1.0 1.0 1 1 1 1 1 1
pair_coeff      1 2 1.0 1.0 1 1 1 1 1 1 0.0
pair_coeff      2 2 1.0 1.0 1 1 1 1 1 1 0.0

# use fix SRD to push small particles out from inside big ones
# if comment out, big particles won't see SRD particles

timestep	0.0005

fix		1 big nve/asphere
fix	        2 small srd 20 big 1.0 0.25 49894 shift yes 54979 &
                  collision noslip search 0.2 inside ignore exact no bounce 50
fix		3 small viscosity 20 x y 50
fix		4 all enforce2d

# diagnostics

compute		tbig big temp/asphere
variable	pebig equal pe*atoms/count(big)
variable	ebig equal etotal*atoms/count(big)
thermo_style	custom step temp c_rot f_2[9] etotal v_pebig v_ebig press &
		f_2[1] f_2[2] f_2[3] f_2[4] f_2[5] &
		f_2[6] f_2[7] f_2[8] f_2[9] f_2[10] f_2[11] f_2[12]

thermo_modify	temp tbig
thermo		1000

#dump		1 all custom 500 dump.ellipsoid.mp id type x y z &
#                quatw quati quatj quatk

#dump		1 all image 500 image.*.jpg type type zoom 1.6
#dump_modify	1 pad 6 adiam 1 1 adiam 2 0.2

run		1000
