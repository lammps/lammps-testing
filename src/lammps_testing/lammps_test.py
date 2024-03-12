import argparse
import glob
import os
import re
import sys

from lammps_testing.common import logger, Settings, get_containers, get_configurations, get_container
from lammps_testing.tests import RunTest, RegressionTest, UnitTest

from lammps_testing.commands.env import init_command as init_env_command
from lammps_testing.commands.config import init_command as init_config_command
from lammps_testing.commands.build import init_command as init_build_command
from lammps_testing.commands.compile import init_command as init_compile_command
from lammps_testing.commands.runtest import init_command as init_runtest_command
from lammps_testing.commands.unit import init_command as init_unit_command
from lammps_testing.commands.reg import init_command as init_reg_command

from lammps_testing.commands.build import build_status
from lammps_testing.commands.runtest import run_status
from lammps_testing.commands.unit import unittest_status
from lammps_testing.commands.reg import reg_status

def status(args, settings):
    args.config = ["ALL"]
    args.builds = ["ALL"]
    print("Compilation Tests:")
    build_status(args, settings)
    print()
    print("Run Tests:")
    run_status(args, settings)
    print()
    print("Regression Tests:")
    reg_status(args, settings)
    print()
    print("Unit Tests:")
    unittest_status(args, settings)
    print()


def checkstyle(args, settings):
    files = glob.glob(os.path.join(settings.lammps_dir, 'src', '**/*.cpp'), recursive=True)
    files.extend(glob.glob(os.path.join(settings.lammps_dir, 'src', '**/*.h'), recursive=True))
    trailing_spaces = re.compile(r'\s+$')

    for filename in files:
        if 'lammps/src/USER-MGPT' in filename:
            continue

        try:
            with open(filename, 'rt') as f:
                for lineno, line in enumerate(f):
                    if line == '\n':
                        continue
                    if trailing_spaces.match(line):
                        print(f"{filename}:{lineno+1}:found trailing whitespaces")
        except Exception as e:
            print(f"{filename}:exception while reading file:{e}")

def main():
    s = Settings()

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='lammps_test')
    subparsers = parser.add_subparsers(help='sub-command help')


    # create the parser for the "env" command
    parser_env = subparsers.add_parser('env', help='test environment commands')
    init_env_command(parser_env)

    # create the parser for the "config" command
    parser_config = subparsers.add_parser('config', help='test config commands')
    init_config_command(parser_config)

    # create the parser for the "build" command
    parser_build = subparsers.add_parser('build', help='test build commands')
    init_build_command(parser_build)

    # create the parser for the "compile" command
    parser_compile = subparsers.add_parser('compile', help='run compilation tests')
    init_compile_command(parser_compile)

    # create the parser for the "reg" command
    parser_build = subparsers.add_parser('reg', help='test reg commands')
    init_reg_command(parser_build)

    # create the parser for the "status" command
    parser_status = subparsers.add_parser('status', help='show status of testing environment')
    parser.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    parser_status.set_defaults(func=status)

    # create the parser for the "checkstyle" command
    parser_checkstyle = subparsers.add_parser('checkstyle', help='check current checkout for code style issues')
    parser_checkstyle.set_defaults(func=checkstyle)

    # create the parser for the "runtest" command
    parser_runtest = subparsers.add_parser('runtest', help='run tests')
    init_runtest_command(parser_runtest)

    # create the parser for the "unittests" command
    parser_unit_test = subparsers.add_parser('unit', help='run unit tests')
    init_unit_command(parser_unit_test)

    #try:
    args = parser.parse_args()
    args.func(args, s)
    #except Exception as e:
    #    print(e)
    #    parser.print_help()

if __name__ == "__main__":
    main()
