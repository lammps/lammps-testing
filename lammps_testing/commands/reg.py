from ..common import discover_tests
from ..tests import LAMMPSExample
import os

def reg_list(args, settings):
    """List all examples and runs possible within the LAMMPS examples folder"""
    examples_dir = os.path.join(settings.lammps_dir, 'examples')
    testcase_count = 0
    run_count = 0
    mpi_run_count = 0
    for test, scripts, logfiles in discover_tests(examples_dir):
        example = LAMMPSExample(test, scripts, logfiles)
        if len(example.testcases) > 0:
            print(example.name)
            for testcase, runs in example.testcases.items():
                print(" -", testcase)
                testcase_count += 1
                for run in runs:
                    if "MPI" in str(run):
                        mpi_run_count += 1
                    print("    *", run)
                    run_count += 1
    print("Total testcases:", testcase_count)
    print("Total runs:", run_count)
    print("Total MPI runs:", mpi_run_count)


def reg_create_yaml(args, settings):
    """Generate YAML configuration files that describe the example runs"""
    examples_dir = os.path.join(settings.lammps_dir, 'examples')
    for test, scripts, logfiles in discover_tests(examples_dir):
        example = LAMMPSExample(test, scripts, logfiles)
        if len(example.testcases) > 0:
            example.save_config()


def init_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    blist = subparsers.add_parser('list', help='list all configurations')
    blist.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    blist.set_defaults(func=reg_list)

    create_yaml = subparsers.add_parser('create_yaml', help='generate yaml files for all cases')
    create_yaml.set_defaults(func=reg_create_yaml)
