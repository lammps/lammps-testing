#!/usr/bin/python
import argparse
import subprocess
import sys
import os
import yaml
import glob
from termcolor import colored
from pathlib import Path
import threading
import time
import logging

DEFAULT_CONFIG="serial"
DEFAULT_ENV="ubuntu_18.04"

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
            logger.info("Using LAMMPS_DIR:        ", os.environ['LAMMPS_DIR'])

        if 'LAMMPS_TESTING_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_TESTING_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.info("Using LAMMPS_TESTING_DIR:", os.environ['LAMMPS_TESTING_DIR'])

        if 'LAMMPS_CACHE_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_CACHE_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.info("Using LAMMPS_CACHE_DIR:  ", os.environ['LAMMPS_CACHE_DIR'])

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
    def __init__(self, container, config, settings):
        self.container = container
        self.config = config
        self.settings = settings

    @property
    def working_dir(self):
        return os.path.join(self.settings.cache_dir, self.name)

    @property
    def build_log(self):
        return os.path.join(self.working_dir, 'build.log')

    @property
    def exists(self):
        return os.path.exists(self.working_dir)

    def build(self):
        pass

    @property
    def commit(self):
        commit_file = os.path.join(self.working_dir, 'COMMIT')
        if os.path.exists(commit_file):
            with open(os.path.join(self.working_dir, 'COMMIT')) as f:
                return f.read().strip()[:8]
        return "TBD"

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
                print('\r' + " "*120, end='')
                print(f"\r⚙️  {colored(self.name, attrs=['bold']):<60}    Commit: {self.commit}    Status: Building" + '.'*i, end='')
                time.sleep(1)
                i = (i + 1) % 4

        t = threading.Thread(target=heartbeat, daemon=True)
        t.start()

        with open(self.build_log, 'wb') as build_log:
            subprocess.call(command, env=env, cwd=self.working_dir, stdout=build_log, stderr=subprocess.STDOUT)

        running = False
        t.join()
        print('\r' + " "*120, end='\r')

        if self.success:
            print(f"\r✅ {colored(self.name, attrs=['bold']):<60}    Commit: {self.commit}    Status: OK")
        else:
            print(f"\r❌ {colored(self.name, attrs=['bold']):<60}    Commit: {self.commit}    Status: Failed")
            print(f"   See build log at {self.build_log}")
            

class CMakeBuild(LAMMPSBuild):
    def __init__(self, container, config, settings, mode='exe'):
        super().__init__(container, config, settings)
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
    def __init__(self, container, config, settings, mode='exe'):
        super().__init__(container, config, settings)
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
        build_env["LAMMPS_MODE"] = self.mode
        build_env["LAMMPS_MACH"] = self.mach
        build_env["LAMMPS_TARGET"] = self.target
        build_env["LAMMPS_COMPILER"] = self.config.compiler
        build_env["CC"] = self.config.cc
        build_env["CXX"] = self.config.cxx
        build_env["LAMMPS_PACKAGES"] = self.get_lammps_packages()

        logger.info("Building with Legacy...")
        logger.info("Workdir:", self.working_dir)
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
        assert(self.container.exists)
        assert(os.path.exists(self.lammps_build_dir))
        logger.info(f"LAMMPS Build: {self.builder.working_dir}")
        logger.info(f"Workdir: {self.working_dir}")
        os.makedirs(self.working_dir, exist_ok=True)
        build_env = os.environ.copy()
        build_env["LAMMPS_BUILD_DIR"] = self.lammps_build_dir
        build_env["LAMMPS_TESTS"] = "tests/test_commands.py"
        build_env["LAMMPS_TESTING_NPROC"] = "1"
        scripts_dir = os.path.join(self.settings.lammps_testing_dir, 'scripts')
        run_tests_script = os.path.join(scripts_dir, 'RunTests.sh')
        subprocess.call(['singularity', 'run', '-B', f'{self.settings.lammps_dir}/:{self.settings.lammps_dir}/', '-B', f'{scripts_dir}/:{scripts_dir}/', self.container.container, run_tests_script], env=build_env, cwd=self.working_dir)

class LocalRunner():
    def __init__(self, builder, settings):
        self.builder = builder
        self.container = builder.container
        self.settings = settings

    @property
    def working_dir(self):
        return os.getcwd()

    @property
    def lammps_build_dir(self):
        return self.builder.working_dir

    def run(self, args):
        assert(self.container.exists)
        print(self.lammps_build_dir)
        assert(os.path.exists(self.lammps_build_dir))
        print("LAMMPS Build:", self.builder.working_dir)
        print("Workdir:", self.working_dir)
        build_env = os.environ.copy()
        build_env["LAMMPS_BUILD_DIR"] = self.lammps_build_dir
        scripts_dir = os.path.join(self.settings.lammps_testing_dir, 'scripts')
        run_tests_script = os.path.join(scripts_dir, 'Run.sh')
        subprocess.call(['singularity', 'run', '-B', f'{self.settings.lammps_dir}/:{self.settings.lammps_dir}/', '-B', f'{scripts_dir}/:{scripts_dir}/', self.container.container, run_tests_script, args], env=build_env, cwd=self.working_dir)

def get_container(name, settings):
    container = os.path.join(settings.container_dir, name + ".sif")
    container_definition = os.path.join(settings.container_definition_dir, name + ".def")
    return Container(name, container, container_definition)

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

def get_lammps_build(builder, container, config, settings, mode='exe'):
    if builder == 'cmake':
        return CMakeBuild(container, config, settings, mode)
    elif builder == 'legacy':
        return LegacyBuild(container, config, settings, mode)

def get_lammps_runner(runner, builder, settings):
    if runner == 'testing':
        return TestRunner(builder, settings)
    elif runner == 'local':
        return LocalRunner(builder, settings)

def container_build_status(value):
    return "[X]" if value else "[ ]"

def build_status(build, title):
    if build.exists:
        if build.success:
            return f"✅ {title:5s} ({colored(build.commit, 'green'):8s})"
        else:
            return f"❌ {title:5s} ({colored(build.commit, 'red'):8s})"
    return f"   {title:5s} (        )"

def show(args, settings):
    print()
    print("Environments:")
    containers = get_containers(settings)
    for c in containers:
        if c.name == DEFAULT_ENV:
            print(container_build_status(c.exists), colored(c.name, attrs=['bold']), colored("[default]", attrs=['bold']))
        else:
            print(container_build_status(c.exists), c.name)

    print()
    print("Configurations:")

    for builder in LAMMPS_BUILDERS:
        print()
        print("#"*120)
        print("#", f'{builder}'.center(116), "#")
        print("#"*120)
        for container in containers:
            print()
            print(f' {container.name} '.center(120, "+"))
            print()
            for config in get_configurations(settings):
                if config.name == DEFAULT_CONFIG:
                    print(" ", colored(f"{config.name + ' [default]':<40}", attrs=['bold']), end="")
                else:
                    print(" ", f"{config.name:<40}", end="")
                for mode in LAMMPS_BUILD_MODES:
                    b = get_lammps_build(builder, container, config, settings, mode)
                    print(build_status(b, mode), end=" ")

                print()
    print()

def buildenv(args, settings):
    c = get_container(args.env, settings)
    c.build()

def build(args, settings):
    c = get_container(args.env, settings)

    if c.exists:
        try:
            configurations = get_configurations_by_selector(args.config, settings)
            modes = get_modes_by_selector(args.mode, settings)
            for config in configurations:
                for mode in modes:
                    builder = get_lammps_build(args.builder, c, config, settings, mode)
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
    runner.run(args.args)

def runtests(args, settings):
    c = get_container(args.env, settings)
    config = get_configuration(args.config, settings)
    builder = get_lammps_build(args.builder, c, config, settings, args.mode)
    runner  = get_lammps_runner('testing', builder, settings)
    runner.run()

def main():
    s = Settings()

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='lammps_test')
    parser.add_argument('--env', default=s.default_env, help=f'name of container environment (default: {DEFAULT_ENV})')
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "show" command
    parser_show = subparsers.add_parser('show', help='show status of testing environment')
    parser_show.set_defaults(func=show)

    # create the parser for the "buildenv" command
    parser_buildenv = subparsers.add_parser('buildenv', help='build container environment')
    parser_buildenv.set_defaults(func=buildenv)

    # create the parser for the "build" command
    parser_build = subparsers.add_parser('build', help='build LAMMPS using a predefined configuration')
    parser_build.add_argument('--builder', choices=LAMMPS_BUILDERS, default='legacy', help='compilation builder')
    parser_build.add_argument('--mode', type=str, default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both, all or any comma separated list)')
    parser_build.add_argument('config', nargs='+', help='name of configuration file or all')
    parser_build.set_defaults(func=build)

    # create the parser for the "runtests" command
    parser_runtests = subparsers.add_parser('runtests', help='run LAMMPS test(s)')
    parser_runtests.add_argument('--builder', choices=('legacy', 'cmake'), default='legacy', help='compilation builder')
    parser_runtests.add_argument('--config', default='serial', help='compilation configuration')
    parser_runtests.add_argument('--mode', choices=LAMMPS_BUILD_MODES, default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both)')
    parser_runtests.add_argument('test', help='name of tests or testsuite')
    parser_runtests.set_defaults(func=runtests)

    # create the parser for the "run" command
    parser_run = subparsers.add_parser('run', help='run LAMMPS in current working directory')
    parser_run.add_argument('--builder', choices=('legacy', 'cmake'), default='legacy', help='compilation builder')
    parser_run.add_argument('--config', default='serial', help='compilation configuration')
    parser_run.add_argument('--mode', choices=('exe', 'shlib', 'shexe'), default='exe', help='compilation mode (exe = binary, shlib = shared library, shexe = both)')
    parser_run.add_argument('args', help='arguments passed to LAMMPS binary')
    parser_run.set_defaults(func=run)

    #try:
    args = parser.parse_args()
    args.func(args, s)
    #except Exception as e:
    #    print(e)
    #    parser.print_help()

if __name__ == "__main__":
    main()
