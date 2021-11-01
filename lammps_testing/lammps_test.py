#!/usr/bin/python
import argparse
import glob
import logging
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from collections import namedtuple

import yaml

from termcolor import colored
from .common import logger, Settings, Container

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

def get_container(name, settings):
    if name == 'local':
        return None
    container = os.path.join(settings.container_dir, name + ".sif")
    container_definition = os.path.join(settings.container_definition_dir, name + ".def")
    return Container(name, container, container_definition)

def get_lammps_commit(commit, settings):
    return subprocess.check_output(['git', 'rev-parse', commit], cwd=settings.lammps_dir).decode().strip()

def get_names(search_pattern):
    names = []
    for path in glob.glob(search_pattern):
        base = os.path.basename(path)
        name = os.path.splitext(base)[0]
        names.append(name)
    return names

def get_containers(settings):
    containers  = get_names(os.path.join(settings.container_definition_dir, '*.def'))
    containers += get_names(os.path.join(settings.container_definition_dir, '**/*.def'))
    return [get_container(c, settings) for c in sorted(containers)]

def get_containers_by_selector(selector, settings):
    if 'all' in selector or 'ALL' in selector:
        return get_containers(settings)
    return [get_container(c, settings) for c in sorted(selector)]

def get_configurations(settings):
    configurations = get_names(os.path.join(settings.configuration_dir, '*.yml'))
    return [get_configuration(c, settings) for c in sorted(configurations)]

def get_commits(settings):
    commits = get_names(os.path.join(settings.cache_dir, 'builds_*'))
    return [c[7:] for c in sorted(commits)]

def get_configuration(name, settings):
    configfile = os.path.join(settings.configuration_dir, name + ".yml")
    if os.path.exists(configfile):
        with open(configfile) as f:
            config = yaml.full_load(f)
            return namedtuple("Configuration", ['name'] + list(config.keys()))(name, *config.values())
    raise FileNotFoundError(configfile)

def get_configurations_by_selector(selector, settings):
    if 'all' in selector or 'ALL' in selector:
        return get_configurations(settings)
    return [get_configuration(c, settings) for c in sorted(selector)]

def get_lammps_runner(runner, builder, settings):
    if runner == 'testing':
        return TestRunner(builder, settings)
    elif runner == 'local':
        return LocalRunner(builder, settings)
    elif runner == 'mpi':
        return MPIRunner(builder, settings, nprocs=8)

def container_build_status(value):
    return "[X]" if value else "[ ]"

def build_status(build, title):
    if build.exists:
        if build.success:
            return f"✅ {title:5s} ({colored(build.commit[:8], 'green'):8s})"
        else:
            return f"❌ {title:5s} ({colored(build.commit[:8], 'red'):8s})"
    return f"   {title:5s} (        )"

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

def cleanall(args, settings):
    containers = get_containers(settings)

    print("Containers:")

    for container in containers:
        print("-", container.name)

    if not args.force:
        answer = input('Delete all containers and build? (y/N):')
        if answer not in ['Y', 'y']:
            logger.info('Aborting cleanall...')
            return

    for container in containers:
        logger.info(f'Removing {container.name}...')
        container.clean()

def env_build_container(args, settings):
    for c in get_containers_by_selector(args.images, settings):
        c.build(force=args.force)

def env_clean_container(args, settings):
    for c in get_containers_by_selector(args.images, settings):
        c.clean()

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

class CompilationTest(object):
    def __init__(self, container, settings, ignore_lammps_commit=False):
        self.container = container
        self.settings = settings
        self.ignore_lammps_commit = ignore_lammps_commit

    @property
    def build_base_dir(self):
        if self.ignore_lammps_commit:
            return os.path.join(self.settings.cache_dir, f'builds')
        return os.path.join(self.settings.cache_dir, f'builds_{self.settings.current_lammps_commit}')

    def get_build_dir(self, build_name):
        return os.path.join(self.build_base_dir, self.container.name, build_name)

    def get_build_script(self, build_name):
        return os.path.join(self.settings.build_scripts_dir, f"{build_name}.sh")

    def build(self, build_name):
        workdir = self.get_build_dir(build_name)
        build_script = self.get_build_script(build_name)

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        return self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=build_script,
                                   cwd=workdir) == 0

class RunTest(object):
    def __init__(self, container, settings, ignore_lammps_commit=False):
        self.container = container
        self.settings = settings
        self.ignore_lammps_commit = ignore_lammps_commit

    @property
    def build_base_dir(self):
        if self.ignore_lammps_commit:
            return os.path.join(self.settings.cache_dir, f'builds')
        return os.path.join(self.settings.cache_dir, f'builds_{self.settings.current_lammps_commit}')

    def get_build_dir(self, build_name):
        return os.path.join(self.build_base_dir, self.container.name, build_name)

    def get_build_script(self, build_name):
        return os.path.join(self.settings.run_tests_scripts_dir, build_name, "build.sh")

    def get_test_script(self, build_name):
        return os.path.join(self.settings.run_tests_scripts_dir, build_name, "test.sh")

    def build(self, build_name):
        workdir = self.get_build_dir(build_name)
        build_script = self.get_build_script(build_name)

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        return self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=build_script,
                                   cwd=workdir) == 0

    def test(self, build_name):
        workdir = self.get_build_dir(build_name)
        test_script = self.get_test_script(build_name)

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        return self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=test_script,
                                   cwd=workdir) == 0

class UnitTest(object):
    def __init__(self, container, settings, ignore_lammps_commit=False):
        self.container = container
        self.settings = settings
        self.ignore_lammps_commit = ignore_lammps_commit

    @property
    def build_base_dir(self):
        if self.ignore_lammps_commit:
            return os.path.join(self.settings.cache_dir, f'builds')
        return os.path.join(self.settings.cache_dir, f'builds_{self.settings.current_lammps_commit}')

    def get_build_dir(self, build_name):
        return os.path.join(self.build_base_dir, self.container.name, build_name)

    def get_build_script(self, build_name):
        return os.path.join(self.settings.unit_tests_scripts_dir, build_name, "build.sh")

    def get_test_script(self, build_name):
        return os.path.join(self.settings.unit_tests_scripts_dir, build_name, "test.sh")

    def build(self, build_name):
        workdir = self.get_build_dir(build_name)
        build_script = self.get_build_script(build_name)

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        return self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=build_script,
                                   cwd=workdir) == 0

    def test(self, build_name):
        workdir = self.get_build_dir(build_name)
        test_script = self.get_test_script(build_name)

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        return self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=test_script,
                                   cwd=workdir) == 0

class RegressionTest(object):
    def __init__(self, container, settings, ignore_lammps_commit=False):
        self.container = container
        self.settings = settings
        self.ignore_lammps_commit = ignore_lammps_commit

    @property
    def build_base_dir(self):
        if self.ignore_lammps_commit:
            return os.path.join(self.settings.cache_dir, f'builds')
        return os.path.join(self.settings.cache_dir, f'builds_{self.settings.current_lammps_commit}')

    def get_build_dir(self, build_name):
        return os.path.join(self.build_base_dir, self.container.name, build_name)

    def get_build_script(self, build_name):
        return os.path.join(self.settings.regression_scripts_dir, build_name, "build.sh")

    def get_test_script(self, build_name):
        return os.path.join(self.settings.regression_scripts_dir, build_name, "test.sh")

    def build(self, build_name):
        workdir = self.get_build_dir(build_name)
        build_script = self.get_build_script(build_name)

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        return self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=build_script,
                                   cwd=workdir) == 0

    def test(self, build_name):
        workdir = self.get_build_dir(build_name)
        test_script = self.get_test_script(build_name)

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        return self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=test_script,
                                   cwd=workdir) == 0

def compilation_test(args, settings):
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

        compTest = CompilationTest(container, settings, args.ignore_commit)

        for build_name in config.builds:
            if 'ALL' not in selected_builds and build_name not in selected_builds:
                continue

            if not compTest.build(build_name):
                print(f"Compilation of '{build_name}' on '{container.name}' FAILED!")
                sys.exit(1)

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

def env_list(args, settings):
    containers = get_containers(settings)
    print("local")
    for c in containers:
        print(c.name)

def env_status(args, settings):
    containers = get_containers(settings)
    print("Build Status | Name")
    print("-------------|---------------------------------------------")
    print(f"{container_build_status(True):>12} |", "local")
    for c in containers:
        print(f"{container_build_status(c.exists):>12} |", c.name)

def config_list(args, settings):
    for c in get_configurations(settings):
        print(c.name)

def build_list(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)
        for config in configs:
            if hasattr(config, "builds"):
                for build in config.builds:
                    print(build)
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)

def init_env_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    elist = subparsers.add_parser('list', help='list all test environments')
    elist.set_defaults(func=env_list)

    status = subparsers.add_parser('status', help='show build status of all test environments')
    status.set_defaults(func=env_status)

    build = subparsers.add_parser('build', help='build container image(s)')
    build.add_argument('images', metavar='image_name', nargs='+', help='container image names')
    build.add_argument('-f', '--force', default=False, action='store_true', help="Force rebuild")
    build.set_defaults(func=env_build_container)

    clean = subparsers.add_parser('clean', help='remove container image(s)')
    clean.add_argument('images', metavar='image_name', nargs='+', help='container image names')
    clean.set_defaults(func=env_clean_container)

def init_config_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    clist = subparsers.add_parser('list', help='list all configurations')
    clist.set_defaults(func=config_list)

def init_build_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    blist = subparsers.add_parser('list', help='list all configurations')
    blist.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    blist.set_defaults(func=build_list)

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

    # create the parser for the "status" command
    parser_status = subparsers.add_parser('status', help='show status of testing environment')
    parser_status.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
    parser_status.set_defaults(func=status)

    # create the parser for the "checkstyle" command
    parser_checkstyle = subparsers.add_parser('checkstyle', help='check current checkout for code style issues')
    parser_checkstyle.set_defaults(func=checkstyle)

    # create the parser for the "cleanall" command
    parser_cleanall = subparsers.add_parser('cleanall', help='clean container environment and all builds')
    parser_cleanall.add_argument('-f', '--force', default=False, action='store_true', help="Clean without asking")
    parser_cleanall.set_defaults(func=cleanall)

    # create the parser for the "compilation" command
    parser_compilation_test = subparsers.add_parser('compilation', help='run compilation tests')
    parser_compilation_test.add_argument('--builds', metavar='build', nargs='+', default=['ALL'], help='comma separated list of builds that should run')
    parser_compilation_test.add_argument('--config', metavar='config', nargs='+', default=['ALL'], help='name of configuration')
    parser_compilation_test.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    parser_compilation_test.set_defaults(func=compilation_test)

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
