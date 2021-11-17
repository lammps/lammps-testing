#!/usr/bin/python
import argparse
import glob
import os
import re
import sys

from .common import logger, Settings, get_containers, get_configurations, get_container
from .tests import RunTest, RegressionTest, UnitTest

from .commands.env import init_command as init_env_command
from .commands.config import init_command as init_config_command
from .commands.build import init_command as init_build_command
from .commands.compile import init_command as init_compile_command
from .commands.runtest import init_command as init_runtest_command
from .commands.unit import init_command as init_unit_command
from .commands.reg import init_command as init_reg_command

def container_build_status(value):
    return "[X]" if value else "[ ]"

def status(args, settings):
    print()
    print("Environments:")
    containers = get_containers(settings)
    print(container_build_status(True), "local")
    for c in containers:
        print(container_build_status(c.exists), c.name)

    containers = [None] + containers

    print()
    print("Configurations:")
    configurations = get_configurations(settings)

    for config in configurations:
        print()
        print(f' {config.name} '.center(120, "+"))

        if hasattr(config, "builds"):
            print()
            print("Builds:")
            for build in config.builds:
                print(" ", f"{build:<40}")


        if hasattr(config, 'unit_tests'):
            print()
            print("Unit Tests:")

            for unit in config.unit_tests:
                print(" ", f"{unit:<40}")

        if hasattr(config, 'run_tests'):
            print()
            print("Run Tests:")

            for run in config.run_tests:
                print(" ", f"{run:<40}")

        if hasattr(config, 'regression_tests'):
            print()
            print("Regression Tests:")

            for regtest in config.regression_tests:
                print(" ", f"{regtest:<40}")

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

def regression_test(args, settings):
    selected_config = args.config
    selected_builds = args.builds
    configurations = get_configurations(settings)

    for config in configurations:
        if 'ALL' not in selected_config and config.name not in selected_config:
            continue

        container = get_container(config.container_image, settings)

        if not container.exists:
            logger.error(f"Can not find container: {container}")
            sys.exit(1)

        regTest = RegressionTest(container, settings, args.ignore_commit)

        for build_name in config.regression_tests:
            if 'ALL' not in selected_builds and build_name not in selected_builds:
                continue

            if not args.test_only and not regTest.build(build_name):
                print(f"Compilation of '{build_name}' on '{container.name}' FAILED!")
                sys.exit(1)

            if not args.build_only and not regTest.test(build_name):
                print(f"Regression test of '{build_name}' on '{container.name}' FAILED!")
                sys.exit(1)

def run_test(args, settings):
    selected_config = args.config
    selected_builds = args.builds
    configurations = get_configurations(settings)

    for config in configurations:
        if 'ALL' not in selected_config and config.name not in selected_config:
            continue

        container = get_container(config.container_image, settings)

        if not container.exists:
            logger.error(f"Can not find container: {container}")
            sys.exit(1)

        runTest = RunTest(container, settings, args.ignore_commit)

        if hasattr(config, 'run_tests'):
            for build_name in config.run_tests:
                if 'ALL' not in selected_builds and build_name not in selected_builds:
                    continue

                if not args.test_only and not runTest.build(build_name):
                    print(f"Compilation of '{build_name}' on '{container.name}' FAILED!")
                    sys.exit(1)

                if not args.build_only and not runTest.test(build_name):
                    print(f"Run test of '{build_name}' on '{container.name}' FAILED!")
                    sys.exit(1)

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
    parser_status.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
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
