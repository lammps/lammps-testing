#!/usr/bin/python
import argparse
import glob
import os
import re
import subprocess
import sys

from termcolor import colored
from .common import logger, Settings, Container, get_containers, get_configurations, get_container, get_configuration
from .tests import RunTest, RegressionTest, UnitTest

from .commands.env import init_command as init_env_command
from .commands.config import init_command as init_config_command
from .commands.build import init_command as init_build_command
from .commands.compile import init_command as init_compile_command
from .commands.reg import init_command as init_reg_command

class TestRunner():
    def __init__(self, builder, settings):
        self.builder = builder
        self.container = builder.container
        self.settings = settings

    @property
    def name(self):
        return self.builder.name + "_testing"

    @property
    def working_dir(self):
        return os.path.join(self.settings.cache_dir, self.name)

    @property
    def lammps_build_dir(self):
        return self.builder.working_dir

    def run(self):
        if not self.container.exists:
            logger.error(f"Container '{self.container.name}' is missing! Build with 'lammps_test build_container {self.container.name}' first!")
            sys.exit(-1)
        if not self.builder.exists:
            logger.error(f"LAMMPS build '{self.builder.name}' is missing! Build with 'lammps_test build' first!")
            sys.exit(-1)

        logger.info(f"LAMMPS Build: {self.builder.working_dir}")
        logger.info(f"Workdir: {self.working_dir}")
        os.makedirs(self.working_dir, exist_ok=True)
        build_env = os.environ.copy()
        build_env["LAMMPS_BUILD_DIR"] = self.lammps_build_dir
        build_env["LAMMPS_TESTS"] = "tests/test_commands.py tests/test_examples.py"
        build_env["LAMMPS_TESTING_NPROC"] = "1"
        build_env["LAMMPS_TEST_MODES"] = "omp"
        scripts_dir = os.path.join(self.settings.lammps_testing_dir, 'scripts')
        run_tests_script = os.path.join(scripts_dir, 'RunTests.sh')
        subprocess.call(['singularity', 'run', '-B', f'{self.settings.lammps_dir}/:{self.settings.lammps_dir}/', '-B', f'{scripts_dir}/:{scripts_dir}/', self.container.container, run_tests_script], env=build_env, cwd=self.working_dir)

class LocalRunner(object):
    def __init__(self, builder, settings):
        self.builder = builder
        self.container = builder.container
        self.settings = settings
        self.working_dir = os.getcwd()

    @property
    def lammps_build_dir(self):
        return self.builder.working_dir

    def run_command(self, command, env, cwd, stdout=None):
        if stdout:
            subprocess.call(command, env=env, cwd=self.working_dir, stdout=stdout, stderr=subprocess.STDOUT)
        else:
            subprocess.call(command, env=env, cwd=self.working_dir)

    @property
    def build_env(self):
        env = os.environ.copy()
        env["LAMMPS_BUILD_DIR"] = self.lammps_build_dir
        return env

    def run(self, args, stdout=None):
        if not self.container.exists:
            logger.error(f"Container '{self.container.name}' is missing! Build with 'lammps_test build_container {self.container.name}' first!")
            sys.exit(-1)
        if not self.builder.exists:
            logger.error(f"LAMMPS build '{self.builder.name}' is missing! Build with 'lammps_test build' first!")
            sys.exit(-1)
        print(self.lammps_build_dir)
        print("LAMMPS Build:", self.builder.working_dir)
        print("Workdir:", self.working_dir)
        scripts_dir = os.path.join(self.settings.lammps_testing_dir, 'scripts')
        run_script = os.path.join(scripts_dir, 'Run.sh')
        self.run_command(['singularity', 'run', '-B', f'{self.settings.lammps_dir}/:{self.settings.lammps_dir}/', '-B', f'{scripts_dir}/:{scripts_dir}/', self.container.container, run_script] + args, env=self.build_env, cwd=self.working_dir, stdout=stdout)

class MPIRunner(LocalRunner):
    def __init__(self, builder, settings, nprocs=1):
        super().__init__(builder, settings)
        self.nprocs = nprocs

    @property
    def build_env(self):
        env = super().build_env
        env["LAMMPS_LAUNCHER"] = f'mpirun -np {self.nprocs} '
        return env



def get_lammps_runner(runner, builder, settings):
    if runner == 'testing':
        return TestRunner(builder, settings)
    elif runner == 'local':
        return LocalRunner(builder, settings)
    elif runner == 'mpi':
        return MPIRunner(builder, settings, nprocs=8)

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

def ensure_container_exists(container):
    if not container.exists:
        print(f"Missing container '{container.name}'\n")
        print("Build container environment first!\n")
        print(f"Usage: lammps_test buildenv --env={container.name}")
        sys.exit(1)

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

def unit_test(args, settings):
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

        unitTest = UnitTest(container, settings, args.ignore_commit)

        if hasattr(config, 'unit_tests'):
            for build_name in config.unit_tests:
                if 'ALL' not in selected_builds and build_name not in selected_builds:
                    continue

                if not args.test_only and not unitTest.build(build_name):
                    print(f"Compilation of '{build_name}' on '{container.name}' FAILED!")
                    sys.exit(1)

                if not args.build_only and not unitTest.test(build_name):
                    print(f"Run unit tests of '{build_name}' on '{container.name}' FAILED!")
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

    # create the parser for the "run" command
    parser_run_test = subparsers.add_parser('run', help='run tests')
    parser_run_test.add_argument('--builds', metavar='build', nargs='+', default=['ALL'], help='comma separated list of builds that should run')
    parser_run_test.add_argument('--config', metavar='config', nargs='+', default=['ALL'], help='name of configuration')
    parser_run_test.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    run_test_group = parser_run_test.add_mutually_exclusive_group()
    run_test_group.add_argument('--build-only', default=False, action='store_true', help='Only build run binary')
    run_test_group.add_argument('--test-only', default=False, action='store_true', help='Only run test on existing binary')
    parser_run_test.set_defaults(func=run_test)

    # create the parser for the "unittests" command
    parser_unit_test = subparsers.add_parser('unit', help='run unit tests')
    parser_unit_test.add_argument('--builds', metavar='build', nargs='+', default=['ALL'], help='comma separated list of builds that should run')
    parser_unit_test.add_argument('--config', metavar='config', nargs='+', default=['ALL'], help='name of configuration')
    parser_unit_test.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    unit_test_group = parser_unit_test.add_mutually_exclusive_group()
    unit_test_group.add_argument('--build-only', default=False, action='store_true', help='Only build run binary')
    unit_test_group.add_argument('--test-only', default=False, action='store_true', help='Only run test on existing binary')
    parser_unit_test.set_defaults(func=unit_test)

    # create the parser for the "regression" command
    parser_regression_test = subparsers.add_parser('regression', help='run regression tests')
    parser_regression_test.add_argument('--builds', metavar='build', nargs='+', default=['ALL'], help='comma separated list of builds that should run')
    parser_regression_test.add_argument('--config', metavar='config', nargs='+', default=['ALL'], help='name of configuration')
    parser_regression_test.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    regression_test_group = parser_regression_test.add_mutually_exclusive_group()
    regression_test_group.add_argument('--build-only', default=False, action='store_true', help='Only build run binary')
    regression_test_group.add_argument('--test-only', default=False, action='store_true', help='Only run test on existing binary')
    parser_regression_test.set_defaults(func=regression_test)

    #try:
    args = parser.parse_args()
    args.func(args, s)
    #except Exception as e:
    #    print(e)
    #    parser.print_help()

if __name__ == "__main__":
    main()
