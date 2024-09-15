#!/bin/env python
import os
import sys
import argparse
from lammps_testing.common import Settings, LocalRunner, MPIRunner
from lammps_testing.regression_testing import RegressionTest

def regression(args, settings):
    test_directory = os.path.realpath(os.path.dirname(args.input_script))
    input_script = os.path.basename(args.input_script)

    assert(input_script.startswith("in."))
    name = input_script[3:]

    if args.nprocs > 1:
        runner = MPIRunner(args.binary, nprocs=args.nprocs)
    else:
        runner = LocalRunner(args.binary)

    runner.working_dir = test_directory

    test = RegressionTest(name, test_directory, descriptor=args.descriptor, options=args.lammps_options.split())
    result = test.verify(runner, norm=args.norm, tolerance=args.tolerance, verbose=args.verbose, generate_plots=args.generate_plots)

    if args.output_attachements:
        print(f"[[ATTACHMENT|{result.current_log}]]")
        print(f"[[ATTACHMENT|{result.reference_log}]]")

        for img_path in result.generated_images:
            print(f"[[ATTACHMENT|{img_path}]]")

    if not result.passed:
        if result.error:
            print(result.error)
        print("FAILED!")
        sys.exit(1)

    print("OK.")

def main():
    s = Settings()

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='run_regression')
    parser.add_argument('--tolerance', default=1e-6, help='')
    parser.add_argument('--nprocs', default=8)
    parser.add_argument('--descriptor', type=str, default="8")
    parser.add_argument('--lammps-options', type=str, default="-v CORES 8")
    parser.add_argument('--norm', choices=('L1', 'L2', 'max'), default='max', help='')
    parser.add_argument('-v', '--verbose', action='store_true', help='Output thermo quantities that do not match')
    parser.add_argument('-g', '--generate-plots', action='store_true', help='Generate plots of thermo quantities that do not match')
    parser.add_argument('-j', '--output-attachements', action='store_true', help='Output attachement strings for Jenkins Attachment plugin')
    parser.add_argument('binary', help='LAMMPS binary that should run test')
    parser.add_argument('input_script', help='input script that should be tested')

    args = parser.parse_args()
    regression(args, s)

if __name__ == "__main__":
    main()
