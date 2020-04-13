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

import yaml

from termcolor import colored

DEFAULT_CONFIG='serial'
DEFAULT_ENV='ubuntu_18.04'
DEFAULT_BUILDER='cmake'

LAMMPS_BUILDERS=('legacy', 'cmake')
LAMMPS_BUILD_MODES=('exe', 'shlib', 'shexe')

logger = logging.getLogger('lammps_test')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(ch)

def file_is_newer(a, b):
    return os.stat(a).st_mtime > os.stat(b).st_mtime

class Settings:
    def __init__(self):
        self.default_config = DEFAULT_CONFIG
        self.default_env    = DEFAULT_ENV

        if 'LAMMPS_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.info(f"Using LAMMPS_DIR:        {os.environ['LAMMPS_DIR']}")

        if 'LAMMPS_TESTING_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_TESTING_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.info(f"Using LAMMPS_TESTING_DIR: {os.environ['LAMMPS_TESTING_DIR']}")

        if 'LAMMPS_CACHE_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_CACHE_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.info(f"Using LAMMPS_CACHE_DIR:  {os.environ['LAMMPS_CACHE_DIR']}")

    @property
    def cache_dir(self):
        return os.environ['LAMMPS_CACHE_DIR']

    @property
    def container_dir(self):
        return os.path.join(os.environ['LAMMPS_CACHE_DIR'], 'containers')

    @property
    def container_definition_dir(self):
        return os.path.join(os.environ['LAMMPS_TESTING_DIR'], 'containers', 'singularity')

    @property
    def configuration_dir(self):
        return os.path.join(os.environ['LAMMPS_TESTING_DIR'], 'configurations')

    @property
    def lammps_dir(self):
        return os.environ['LAMMPS_DIR']

    @property
    def lammps_testing_dir(self):
        return os.environ['LAMMPS_TESTING_DIR']

class Container:
    def __init__(self, name, container, container_definition):
        self.name = name
        self.container = container
        self.container_definition =  container_definition

    def build(self):
        os.makedirs(os.path.dirname(self.container), exist_ok=True)
        if os.path.exists(self.container) and file_is_newer(self.container_definition, self.container):
            logger.info(f"Newer container definition found! Rebuilding container '{self.name}'...")
            os.unlink(self.container)
        elif not os.path.exists(self.container):
            logger.info(f"Building container '{self.name}'...")

        if not os.path.exists(self.container):
            subprocess.call(['sudo', 'singularity', 'build', self.container, self.container_definition])
        else:
            logger.info(f"Container '{self.name}' already exists and is up-to-date.")

    def clean(self):
        if self.exists:
            logger.info(f"Deleting container '{self.name}'...")
            os.unlink(self.container)

    @property
    def exists(self):
        return os.path.exists(self.container)


class LAMMPSConfiguration(object):
    def __init__(self, filename, lammps_dir):
        self.filename = filename
        self.lammps_dir = lammps_dir

        # set defaults
        self.mpi = False
        self.openmp = False
        self.shared = False
        self.binary = True
        self.library = False
        self.compiler = 'g++'
        self.cc = 'gcc'
        self.cxx = 'g++'
        self.sizes = 'smallbig'
        self.exceptions = False
        self.package_options = {}
        self.packages = []
        self.attributes_changed = set()

        # load values from configuration file
        with open(filename, 'r') as f:
            loaded_dict = yaml.load(f, Loader=yaml.FullLoader)

            for k, v in loaded_dict.items():
                setattr(self, k.lower(), v)
                self.attributes_changed.add(k)

    @property
    def name(self):
        return Path(self.filename).stem

    def __str__(self):
        s =  "LAMMPS Configuration\n"
        s += "--------------------\n"
        s += "  MPI:         {}\n".format("yes" if self.mpi else "no")
        s += "  OpenMP:      {}\n".format("yes" if self.openmp else "no")
        s += "  Shared:      {}\n".format("yes" if self.shared else "no")
        s += "  Binary:      {}\n".format("yes" if self.binary else "no")
        s += "  Library:     {}\n".format("yes" if self.library else "no")
        s += f"  Compiler:    {self.compiler}\n"
        s += f"  CC:          {self.cc}\n"
        s += f"  CXX:         {self.cxx}\n"
        s += f"  Sizes:       {self.sizes}\n"
        s += "  Exceptions:  {}\n".format("yes" if self.exceptions else "no")
        s += "--------------------\n"
        s += "  Packages:\n"
        s += "--------------------\n"

        for pkg in sorted(self.packages):
            s += f" - {pkg}\n"

        s += "--------------------\n"
        s += "  Packages Options:\n"
        s += "--------------------\n"

        for pkg in sorted(self.package_options.keys()):
            if pkg.upper() not in set([p.upper() for p in self.packages]):
                s += f" - {pkg}: ignored since not enabled\n"
                continue

            s += f" - {pkg}:\n"
            options = self.package_options[pkg]
            for k in sorted(options.keys()):
                s += f"     {k}: {options[k]}"

        return s

class LAMMPSBuild:
    def __init__(self, container, config, settings, commit):
        self.container = container
        self.config = config
        self.settings = settings
        self.commit = commit

    @property
    def name(self):
        raise NotImplementedError()

    @property
    def working_dir(self):
        return os.path.join(self.settings.cache_dir, f"builds_{self.commit}", self.name)

    def clean(self):
        if os.path.exists(self.working_dir):
            print(f"Deleting {self.working_dir}...")
            shutil.rmtree(self.working_dir)

    @property
    def build_log(self):
        return os.path.join(self.working_dir, 'build.log')

    @property
    def exists(self):
        return os.path.exists(self.working_dir)

    def build(self):
        pass

    @property
    def success(self):
        lammps_binary = os.path.join(self.working_dir, 'pyenv', 'bin', 'lmp')
        lammps_shared_library = os.path.join(self.working_dir, 'pyenv', 'lib', 'liblammps.so')
        return os.path.exists(lammps_binary) or os.path.exists(lammps_shared_library)

    def run_command(self, command, env):
        running = True

        def heartbeat():
            i = 0
            while(running):
                sys.stdout.write(f"⚙️  {colored(self.name, attrs=['bold']):<60}    Commit: {self.commit[:8]}    Status: Building" + '.'*i + ' '*(3-i) + '\r')
                time.sleep(1)
                i = (i + 1) % 4

        t = threading.Thread(target=heartbeat, daemon=True)
        t.start()

        with open(self.build_log, 'wb') as build_log:
            subprocess.call(command, env=env, cwd=self.working_dir, stdout=build_log, stderr=subprocess.STDOUT)

        running = False
        t.join()

        if self.success:
            print(f"✅ {colored(self.name, attrs=['bold']):<60}    Commit: {self.commit[:8]}    Status: OK          ")
        else:
            print(f"❌ {colored(self.name, attrs=['bold']):<60}    Commit: {self.commit[:8]}    Status: Failed      ")
            print(f"   See build log at {self.build_log}")


class CMakeBuild(LAMMPSBuild):
    def __init__(self, container, config, settings, commit, mode='exe'):
        super().__init__(container, config, settings, commit)
        self.mode = mode

    @property
    def name(self):
        return f"{self.container.name}_cmake_{self.config.name}_{self.mode}"

    def build_options(self):
        options=[]

        if 'VORONOI' in self.config.packages or 'voronoi' in self.config.packages:
            options.append('-D DOWNLOAD_VORO=on')

        if 'MSCG' in self.config.packages or 'mscg' in self.config.packages:
            options.append('-D DOWNLOAD_MSCG=on')

        if 'USER-PLUMED' in self.config.packages or 'user-plumed' in self.config.packages:
            options.append('-D DOWNLOAD_PLUMED=on')

        if 'GPU' in self.config.packages or 'gpu' in self.config.packages:
            if 'gpu' in self.config.package_options:
                gpu_options = self.config.package_options['gpu']
            elif 'GPU' in self.config.packages_options:
                gpu_options = self.config.package_options['gpu']
            else:
                gpu_options = {'api': 'opencl'}

            if gpu_options['api'] == 'cuda':
                options.append('-D CMAKE_LIBRARY_PATH=/usr/local/cuda/lib64/stubs')

            options.append(f'-D GPU_API={gpu_options["api"]}')

        if self.config.mpi:
            options.append('-D BUILD_MPI=on')
        else:
            options.append('-D BUILD_MPI=off')

        if self.config.openmp:
            options.append('-D BUILD_OMP=on')
        else:
            options.append('-D BUILD_OMP=off')

        if self.mode == 'exe':
            options.append('-D BUILD_EXE=on')
        elif self.mode == 'shlib':
            options.append('-D BUILD_EXE=off')
            options.append('-D BUILD_LIB=on')
            options.append('-D BUILD_SHARED_LIBS=on')
        elif self.mode == 'shexe':
            options.append('-D BUILD_EXE=on')
            options.append('-D BUILD_LIB=on')
            options.append('-D BUILD_SHARED_LIBS=on')

        for pkg in self.config.packages:
            options.append(f'-D PKG_{pkg.upper()}=on')

        return options


    def build(self):
        logger.info("Building with CMake...")
        logger.debug(self.config)
        options = self.build_options()

        assert(self.container.exists)
        build_env = os.environ.copy()
        build_env["LAMMPS_COMMIT"] = self.commit
        build_env["LAMMPS_C_FLAGS"]   = "-Wall -Wextra -Wno-unused-result -Wno-maybe-uninitialized -Wreorder"
        build_env["LAMMPS_CXX_FLAGS"] = "-Wall -Wextra -Wno-unused-result -Wno-maybe-uninitialized -Wreorder"
        build_env["CC"] = self.config.cc
        build_env["CXX"] = self.config.cxx
        build_env["LAMMPS_CMAKE_OPTIONS"] = " ".join(options)

        logger.debug(f"Workdir: {self.working_dir}")
        os.makedirs(self.working_dir, exist_ok=True)
        scripts_dir = os.path.join(self.settings.lammps_testing_dir, 'scripts')
        cmake_build_script = os.path.join(scripts_dir, 'CMakeBuild.sh')
        self.run_command(['singularity', 'run', '-B', f'{self.settings.lammps_dir}/:{self.settings.lammps_dir}/', '-B', f'{scripts_dir}/:{scripts_dir}/', self.container.container, cmake_build_script], env=build_env)

class LegacyBuild(LAMMPSBuild):
    def __init__(self, container, config, settings, commit, mode='exe'):
        super().__init__(container, config, settings, commit)
        self.mode = mode

        if config.mpi:
            self.mach = "mpi"
            self.target = "mpi"
        else:
            self.mach = "serial"
            self.target = "serial"

    @property
    def name(self):
        return f"{self.container.name}_legacy_{self.config.name}_{self.mode}"

    def get_lammps_packages(self):
        s = "no-all"
        for pkg in self.config.packages:
            s += f":yes-{pkg.lower()}"
        return s

    def build(self):
        logger.debug(self.config)
        assert(self.container.exists)
        build_env = os.environ.copy()
        build_env["LAMMPS_COMMIT"] = self.commit
        build_env["LAMMPS_MODE"] = self.mode
        build_env["LAMMPS_MACH"] = self.mach
        build_env["LAMMPS_TARGET"] = self.target
        build_env["LAMMPS_COMPILER"] = self.config.compiler
        build_env["CC"] = self.config.cc
        build_env["CXX"] = self.config.cxx
        build_env["LAMMPS_PACKAGES"] = self.get_lammps_packages()

        logger.info("Building with Legacy...")
        logger.info(f"Workdir: {self.working_dir}")
        os.makedirs(self.working_dir, exist_ok=True)
        scripts_dir = os.path.join(self.settings.lammps_testing_dir, 'scripts')
        legacy_build_script = os.path.join(scripts_dir, 'LegacyBuild.sh')
        self.run_command(['singularity', 'run', '-B', f'{self.settings.lammps_dir}/:{self.settings.lammps_dir}/', '-B', f'{scripts_dir}/:{scripts_dir}/', self.container.container, legacy_build_script], env=build_env)

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
            logger.error(f"Container '{self.container.name}' is missing! Build with 'lammps_test --env={self.container.name} buildenv' first!")
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
            logger.error(f"Container '{self.container.name}' is missing! Build with 'lammps_test --env={self.container.name} buildenv' first!")
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
    containers = get_names(os.path.join(settings.container_definition_dir, '*.def'))
    return [get_container(c, settings) for c in sorted(containers)]

def get_configurations(settings):
    configurations = get_names(os.path.join(settings.configuration_dir, '*.yml'))
    return [get_configuration(c, settings) for c in sorted(configurations)]

def get_commits(settings):
    commits = get_names(os.path.join(settings.cache_dir, 'builds_*'))
    return [c[7:] for c in sorted(commits)]

def get_configuration(name, settings):
    configfile = os.path.join(settings.configuration_dir, name + ".yml")
    if os.path.exists(configfile):
        return LAMMPSConfiguration(configfile, settings.lammps_dir)
    raise FileNotFoundError(configfile)

def get_configurations_by_selector(selector, settings):
    if 'all' in selector or 'ALL' in selector:
        return get_configurations(settings)
    return [get_configuration(c, settings) for c in sorted(selector)]

def get_modes_by_selector(selector, settings):
    if selector == 'all' or selector == 'ALL':
        return LAMMPS_BUILD_MODES
    return selector.split(',')

def get_lammps_build(builder, container, config, settings, commit, mode='exe'):
    if builder == 'cmake':
        return CMakeBuild(container, config, settings, commit, mode)
    elif builder == 'legacy':
        return LegacyBuild(container, config, settings, commit, mode)

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
    for c in containers:
        if c.name == DEFAULT_ENV:
            print(container_build_status(c.exists), colored(c.name, attrs=['bold']), colored("[default]", attrs=['bold']))
        else:
            print(container_build_status(c.exists), c.name)

    print()
    print("Commits:")
    commits = get_commits(settings)
    for c in commits:
        print("-", c)

    print()
    print("Configurations:")
    configurations = get_configurations(settings)

    for builder in LAMMPS_BUILDERS:
        print()
        print(f' {builder} '.center(120, "#"))
        for container in containers:
            show_configs = set()

            for config in configurations:
                for mode in LAMMPS_BUILD_MODES:
                    for commit in commits:
                        build = get_lammps_build(builder, container, config, settings, commit, mode)
                        if build.exists:
                            show_configs.add(config)

            if args.verbose or len(show_configs) > 0:
                print()
                print(f' {container.name} '.center(120, "+"))
                print()

                for commit in commits:
                    for config in configurations:
                        if not args.verbose and (config not in show_configs):
                            continue

                        if config.name == DEFAULT_CONFIG:
                            print(" ", colored(f"{config.name + ' [default]':<40}", attrs=['bold']), end="")
                        else:
                            print(" ", f"{config.name:<40}", end="")
                        for mode in LAMMPS_BUILD_MODES:
                                b = get_lammps_build(builder, container, config, settings, commit, mode)
                                print(build_status(b, mode), end=" ")

                    print()
    print()
    if not args.verbose:
        print("To see all possible configurations, use the -v option.")

def cleanall(args, settings):
    if args.env == 'all':
        containers = get_containers(settings)
    else:
        containers = [get_container(args.env, settings)]

    for builder in LAMMPS_BUILDERS:
        for container in containers:
            for config in get_configurations(settings):
                for mode in LAMMPS_BUILD_MODES:
                    b = get_lammps_build(builder, container, config, settings, mode)
                    b.clean()

    for container in containers:
        container.clean()

def clean(args, settings):
    c = get_container(args.env, settings)

    try:
        configurations = get_configurations_by_selector(args.config, settings)
        modes = get_modes_by_selector(args.mode, settings)
        for config in configurations:
            for mode in modes:
                builder = get_lammps_build(args.builder, c, config, settings, mode)
                builder.clean()
    except FileNotFoundError as e:
        logger.error("Configuration does not exist!")
        logger.error(e)
        sys.exit(1)

def buildenv(args, settings):
    c = get_container(args.env, settings)
    c.build()

def cleanenv(args, settings):
    c = get_container(args.env, settings)
    c.clean()

def build(args, settings):
    c = get_container(args.env, settings)

    if c.exists:
        try:
            configurations = get_configurations_by_selector(args.config, settings)
            modes = get_modes_by_selector(args.mode, settings)
            commit = get_lammps_commit(args.commit, settings)
            for config in configurations:
                for mode in modes:
                    builder = get_lammps_build(args.builder, c, config, settings, commit, mode)
                    builder.build()
        except FileNotFoundError as e:
            logger.error("Configuration does not exist!")
            logger.error(e)
            sys.exit(1)
    else:
        print(f"Missing container '{c.name}'\n")
        print("Build container environment first!\n")
        print(f"Usage: lammps_test --env={c.name} buildenv")
        sys.exit(1)

def run(args, settings):
    c = get_container(args.env, settings)
    config = get_configuration(args.config, settings)
    builder = get_lammps_build(args.builder, c, config, settings, args.mode)
    runner  = get_lammps_runner('local', builder, settings)
    runner.run(args.args.split())

def runtests(args, settings):
    c = get_container(args.env, settings)
    config = get_configuration(args.config, settings)
    builder = get_lammps_build(args.builder, c, config, settings, args.mode)
    runner  = get_lammps_runner('testing', builder, settings)
    runner.run()

class LammpsLog:
    STYLE_DEFAULT = 0
    STYLE_MULTI   = 1

    def __init__(self, filename):
        alpha = re.compile(r'[a-df-zA-DF-Z]') # except e or E for floating-point numbers
        kvpairs = re.compile(r'([a-zA-Z_0-9]+)\s+=\s*([0-9\.eE\-]+)')
        style = LammpsLog.STYLE_DEFAULT
        self.runs = []
        self.errors = []
        with open(filename, 'rt') as f:
            in_thermo = False
            for line in f:
                if "ERROR" in line or "exited on signal" in line:
                    self.errors.append(line)
                elif line.startswith('Step '):
                    in_thermo = True
                    keys = line.split()
                    current_run = {}
                    for k in keys:
                        current_run[k] = []
                elif line.startswith('---------------- Step'):
                    if not in_thermo:
                       current_run = {'Step': [], 'CPU': []}
                    in_thermo = True
                    style = LammpsLog.STYLE_MULTI
                    str_step, str_cpu = line.strip('-\n').split('-----')
                    step = float(str_step.split()[1])
                    cpu  = float(str_cpu.split('=')[1].split()[0])
                    current_run["Step"].append(step)
                    current_run["CPU"].append(cpu)
                elif line.startswith('Loop time of'):
                    in_thermo = False
                    self.runs.append(current_run)
                elif in_thermo:
                    if style == LammpsLog.STYLE_DEFAULT:
                        if alpha.search(line):
                            continue

                        for k, v in zip(keys, map(float, line.split())):
                            current_run[k].append(v)
                    elif style == LammpsLog.STYLE_MULTI:
                        if '=' not in line:
                            continue

                        for k,v in kvpairs.findall(line):
                            if k not in current_run:
                                current_run[k] = [float(v)]
                            else:
                                current_run[k].append(float(v))


def L1_norm(seq):
    return sum([abs(x) for x in seq]) / len(seq)

def L2_norm(seq):
    return math.sqrt(sum([x*x for x in seq]) / len(seq))

def Max_norm(seq):
    return max([abs(x) for x in seq])

def compare(a, b, tolerance, norm='max'):
    if len(a) != len(b):
        raise Exception("Cannot compare columns")

    delta = [u - v for u, v in zip(a,b)]

    not_same_rows = [i for i, x in enumerate(delta) if abs(x) > tolerance]
    nsame_rows = len(a) - len(not_same_rows)

    if norm == "L1":
        norm_err = L1_norm(delta)
        norm_a = L1_norm(a)
        norm_b = L1_norm(b)
    elif norm == "L2":
        norm_err = L2_norm(delta)
        norm_a = L2_norm(a)
        norm_b = L2_norm(b)
    elif norm == "max":
        norm_err = Max_norm(delta)
        norm_a = Max_norm(a)
        norm_b = Max_norm(b)
    else:
        raise Exception("Invalid error norm")

    return norm_a, norm_b, norm_err, nsame_rows

class RegressionTest(object):
    def __init__(self, name, test_directory, descriptor, options=[]):
        self.test_directory = test_directory
        self.descriptor = descriptor
        self.name = name
        self.options = [str(x) for x in options]
        self.input_script = f'in.{name}'
        self.log_file     = f'log.{descriptor}.{name}'
        self.stdout_file  = f'stdout.{descriptor}.{name}'

    @property
    def log_file_path(self):
        return os.path.join(self.test_directory, self.log_file)

    @property
    def stdout_file_path(self):
        return os.path.join(self.test_directory, self.stdout_file)

    @property
    def completed(self):
        return os.path.exists(self.log_file_path) and os.path.exists(self.stdout_file_path)

    def clean(self):
        print("Removing log and stdout files...")
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

        if os.path.exists(self.stdout_file_path):
            os.remove(self.stdout_file_path)

    @property
    def gold_standard_file_path(self):
        system_name = platform.system().lower()
        gold_files = glob.glob(os.path.join(self.test_directory, f'log.*{system_name}.{self.descriptor}.{self.name}'))
        if len(gold_files) > 0:
            return gold_files[0]
        return None

    def run(self, runner, is_reference=False):
        self.clean()

        with open(self.stdout_file_path, 'w') as f:
            lammps_options = ['-in', self.input_script, '-log', self.log_file] + self.options
            runner.working_directory = self.test_directory
            runner.run(args=lammps_options, stdout=f)

        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(self.log_file_path)

        print(self.log_file_path)

        if is_reference:
            today = datetime.now()
            system_name = platform.system()
            target_file_path = os.path.join(self.test_directory, f'log.{today:%d%b%y}.{system_name}.{self.descriptor}.{self.name}')
            shutil.copyfile(self.log_file_path, target_file_path)

    def verify(self, runner, norm='max', tolerance=1e-6, generate_plots=False, verbose=False):
        reference_file_path = self.gold_standard_file_path

        if not reference_file_path or not os.path.exists(reference_file_path):
            self.run(runner, is_reference=True)

        reference_file_path = self.gold_standard_file_path
        assert(reference_file_path and os.path.exists(reference_file_path))

        self.run(runner)

        current_file_path = self.log_file_path
        assert(current_file_path and os.path.exists(current_file_path))

        print("Current:", current_file_path)
        print("Reference:", reference_file_path)
        failed = []
        has_error = False

        #try:
        current_log   = LammpsLog(current_file_path)
        reference_log = LammpsLog(reference_file_path)

        if len(current_log.runs) != len(reference_log.runs):
            raise Exception("Number of runs does not match between logs!")

        for index, (run, ref_run) in enumerate(zip(current_log.runs, reference_log.runs)):
            # sanity check, check for same data fields
            if sorted(run.keys()) != sorted(ref_run.keys()):
                raise Exception(f"Fields in run {index} do not match!")
            for field in run.keys():
                if field in ("CPU", "T/CPU", "S/CPU", "CPULeft"):
                    continue
                norm_current, norm_ref, norm_err, nsame_rows = compare(run[field], ref_run[field], tolerance, norm)
                nrows = len(ref_run[field])

                #if relative_error and norm > tolerance:
                #    norm_err /= norm_ref
                #    norm = 1.0

                if norm_err < tolerance:
                    print(f"✅ {field:<20}: norm_{norm}={norm_current}, reference_norm_{norm}={norm_ref}, norm_err_{norm}={norm_err}")
                    if nsame_rows != nrows:
                        print(f"   WARNING: Only {nsame_rows} out of {nrows} data points are identical")
                else:
                    print(f"❌ {field:<20}: norm_{norm}={norm_current}, reference_norm_{norm}={norm_ref}, norm_err_{norm}={norm_err} > {tolerance} !!!")

                    if verbose:
                        print()

                        if 'Step' in run:
                            print(f"   {'Step':12} | {'Current':30} | {'Reference':30} | {'Delta':30}")
                            print(f"   {'-'*12:12}-+-{'-'*30:30}-+-{'-'*30:30}-+-{'-'*30:30}")
                            for step, a, b in zip([int(s) for s in run['Step']], run[field], ref_run[field]):
                                print(f"   {step:12d} | {a:30} | {b:30} | {a-b:30}", end='')
                                if (a-b) > tolerance:
                                    print(f" >= {tolerance} !!!")
                                else:
                                    print()
                        else:
                            print(f"   {'Current':30} | {'Reference':30} | {'Delta':30}")
                            print(f"   {'-'*30:30}-+-{'-'*30:30}-+-{'-'*30:30}")
                            for step, a, b in zip(run[field], ref_run[field]):
                                print(f"   {a:30} | {b:30} | {a-b:30}", end='')
                                if (a-b) > tolerance:
                                    print(f" >= {tolerance} !!!")
                                else:
                                    print()
                        print()

                    if generate_plots:
                        import matplotlib
                        matplotlib.use('Agg')
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots()
                        fig.suptitle(field)
                        reference_line, = ax.plot(run['Step'], ref_run[field], label='Reference')
                        current_line, = ax.plot(run['Step'], run[field], label='Current')
                        ax.legend()
                        plt.savefig(os.path.join(self.test_directory,f'{field}.png'))

                    failed.append(field)
        #except Exception as e:
        #    print(e)
        #    has_error = True

def regression(args, settings):
    # lammps_test regression --builder=cmake --config=regression tests/examples/pour/in.pour.2d.molecule
    c = get_container(args.env, settings)
    config = get_configuration(args.config, settings)
    commit = get_lammps_commit(args.commit, settings)
    builder = get_lammps_build(args.builder, c, config, settings, commit, args.mode)
    runner  = get_lammps_runner('mpi', builder, settings)

    test_directory = os.path.realpath(os.path.dirname(args.input_script))
    input_script = os.path.basename(args.input_script)

    assert(input_script.startswith("in."))
    name = input_script[3:]

    runner.working_dir = test_directory

    test = RegressionTest(name, test_directory, descriptor="8", options=['-v', 'CORES', 8])
    test.verify(runner, norm=args.norm, tolerance=args.tolerance, verbose=args.verbose, generate_plots=args.generate_plots)

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
    parser.add_argument('--env', default=s.default_env, help=f'name of container environment (default: {DEFAULT_ENV})')
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "status" command
    parser_status = subparsers.add_parser('status', help='show status of testing environment')
    parser_status.add_argument('-v', '--verbose', action='store_true', help='show verbose output')
    parser_status.set_defaults(func=status)

    # create the parser for the "clean" command
    parser_clean = subparsers.add_parser('clean', help='clean up cache directory')
    parser_clean.add_argument('--builder', choices=LAMMPS_BUILDERS, default=DEFAULT_BUILDER, help='compilation builder')
    parser_clean.add_argument('--mode', type=str, default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both, all or any comma separated list)')
    parser_clean.add_argument('config', nargs='+', help='name of configuration file or all')
    parser_clean.set_defaults(func=clean)

    # create the parser for the "checkstyle" command
    parser_checkstyle = subparsers.add_parser('checkstyle', help='check current checkout for code style issues')
    parser_checkstyle.set_defaults(func=checkstyle)

    # create the parser for the "buildenv" command
    parser_buildenv = subparsers.add_parser('buildenv', help='build container environment')
    parser_buildenv.set_defaults(func=buildenv)

    # create the parser for the "cleanenv" command
    parser_cleanenv = subparsers.add_parser('cleanenv', help='clean container environment')
    parser_cleanenv.set_defaults(func=cleanenv)

    # create the parser for the "cleanall" command
    parser_cleanall = subparsers.add_parser('cleanall', help='clean container environment and all builds')
    parser_cleanall.set_defaults(func=cleanall)

    # create the parser for the "build" command
    parser_build = subparsers.add_parser('build', help='build LAMMPS using a predefined configuration')
    parser_build.add_argument('--builder', choices=LAMMPS_BUILDERS, default=DEFAULT_BUILDER, help='compilation builder')
    parser_build.add_argument('--mode', type=str, default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both, all or any comma separated list)')
    parser_build.add_argument('--commit', type=str, default='HEAD', help='name of commit (SHA or equivalent)')
    parser_build.add_argument('config', nargs='+', help='name of configuration file or all')
    parser_build.set_defaults(func=build)

    # create the parser for the "runtests" command
    parser_runtests = subparsers.add_parser('runtests', help='run LAMMPS test(s)')
    parser_runtests.add_argument('--builder', choices=('legacy', 'cmake'), default=DEFAULT_BUILDER, help='compilation builder')
    parser_runtests.add_argument('--config', default='serial', help='compilation configuration')
    parser_runtests.add_argument('--mode', choices=LAMMPS_BUILD_MODES, default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both)')
    parser_runtests.add_argument('test', help='name of tests or testsuite')
    parser_runtests.set_defaults(func=runtests)

    # create the parser for the "run" command
    parser_run = subparsers.add_parser('run', help='run LAMMPS in current working directory')
    parser_run.add_argument('--builder', choices=('legacy', 'cmake'), default=DEFAULT_BUILDER, help='compilation builder')
    parser_run.add_argument('--config', default='serial', help='compilation configuration')
    parser_run.add_argument('--mode', choices=('exe', 'shlib', 'shexe'), default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both)')
    parser_run.add_argument('args', help='arguments passed to LAMMPS binary')
    parser_run.set_defaults(func=run)

    # create the parser for the "regression" command
    parser_regression = subparsers.add_parser('regression', help='run regression test')
    parser_regression.add_argument('--builder', choices=('legacy', 'cmake'), default=DEFAULT_BUILDER, help='compilation builder')
    parser_regression.add_argument('--config', default='serial', help='compilation configuration')
    parser_regression.add_argument('--commit', type=str, default='HEAD', help='name of commit (SHA or equivalent)')
    parser_regression.add_argument('--mode', choices=('exe', 'shlib', 'shexe'), default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both)')
    parser_regression.add_argument('--tolerance', default=1e-6, help='')
    parser_regression.add_argument('--norm', choices=('L1', 'L2', 'max'), default='max', help='')
    parser_regression.add_argument('-v', '--verbose', action='store_true', help='')
    parser_regression.add_argument('-g', '--generate-plots', action='store_true', help='')
    parser_regression.add_argument('input_script', help='input script that should be tested')
    parser_regression.set_defaults(func=regression)

    #try:
    args = parser.parse_args()
    args.func(args, s)
    #except Exception as e:
    #    print(e)
    #    parser.print_help()

if __name__ == "__main__":
    main()
