import os
import sys
import glob
import logging
import subprocess
from nose.tools import nottest
from collections import namedtuple

import yaml

logger = logging.getLogger('lammps_test')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

def file_is_newer(a, b):
    return os.stat(a).st_mtime > os.stat(b).st_mtime

class Settings(object):
    def __init__(self):
        if 'LAMMPS_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.debug(f"Using LAMMPS_DIR:        {os.environ['LAMMPS_DIR']}")

        if 'LAMMPS_TESTING_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_TESTING_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.debug(f"Using LAMMPS_TESTING_DIR: {os.environ['LAMMPS_TESTING_DIR']}")

        if 'LAMMPS_CACHE_DIR' not in os.environ:
            logger.error("lammps_test requires the LAMMPS_CACHE_DIR environment variable to be set!")
            sys.exit(1)
        else:
            logger.debug(f"Using LAMMPS_CACHE_DIR:  {os.environ['LAMMPS_CACHE_DIR']}")

        if 'LAMMPS_CONTAINER_DIR' not in os.environ:
            os.environ['LAMMPS_CONTAINER_DIR'] = os.path.join(os.environ['LAMMPS_CACHE_DIR'], 'containers')
        else:
            logger.debug(f"Using LAMMPS_CONTAINER_DIR:  {os.environ['LAMMPS_CONTAINER_DIR']}")

    @property
    def cache_dir(self):
        return os.environ['LAMMPS_CACHE_DIR']

    @property
    def container_dir(self):
        return os.environ['LAMMPS_CONTAINER_DIR']

    @property
    def container_definition_dir(self):
        return os.path.join(os.environ['LAMMPS_TESTING_DIR'], 'containers', 'singularity')

    @property
    def configuration_dir(self):
        return os.path.join(os.environ['LAMMPS_TESTING_DIR'], 'scripts')

    @property
    def build_scripts_dir(self):
        return os.path.join(self.configuration_dir, 'builds')

    @property
    def unit_tests_scripts_dir(self):
        return os.path.join(self.configuration_dir, 'unit_tests')

    @property
    def run_tests_scripts_dir(self):
        return os.path.join(self.configuration_dir, 'run_tests')

    @property
    def regression_scripts_dir(self):
        return os.path.join(self.configuration_dir, 'regression_tests')

    @property
    def lammps_dir(self):
        return os.environ['LAMMPS_DIR']

    @property
    def lammps_testing_dir(self):
        return os.environ['LAMMPS_TESTING_DIR']

    @property
    def current_lammps_commit(self):
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.lammps_dir).decode().strip()



class Container(object):
    def __init__(self, name, container, container_definition):
        self.name = name
        self.container = container
        self.container_definition =  container_definition

    def build(self, force=False):
        os.makedirs(os.path.dirname(self.container), exist_ok=True)
        if os.path.exists(self.container) and file_is_newer(self.container_definition, self.container):
            logger.info(f"Newer container definition found! Rebuilding container '{self.name}'...")
            os.unlink(self.container)
        elif os.path.exists(self.container) and force:
            logger.info(f"Forcing rebuilding container '{self.name}'...")
            os.unlink(self.container)
        elif not os.path.exists(self.container):
            logger.info(f"Building container '{self.name}'...")

        if not os.path.exists(self.container):
            subprocess.call(['sudo', '-E', 'singularity', 'build', self.container, self.container_definition])
        else:
            logger.info(f"Container '{self.name}' already exists and is up-to-date.")

    def exec(self, options=[], command=[], cwd="."):
        test_env = os.environ.copy()
        test_env["LAMMPS_CI_RUNNER"] = "lammps_test"
        return subprocess.call(['singularity', 'exec'] + options + [self.container, command], cwd=cwd, env=test_env)

    def clean(self):
        if self.exists:
            logger.info(f"Deleting container '{self.name}'...")
            os.unlink(self.container)

    @property
    def exists(self):
        return os.path.exists(self.container)


class LocalRunner(object):
    def __init__(self, lammps_binary_path):
        self.lammps_binary_path = lammps_binary_path
        self.working_directory = os.getcwd()

    def get_full_command(self, input_script, options=[]):
        return [self.lammps_binary_path, "-in", input_script] + options

    def run(self, input_script, options, stdout=None):
        command = self.get_full_command(input_script, options)

        print(" ".join(command))

        if stdout:
            result = subprocess.call(command, cwd=self.working_directory, stdout=stdout, stderr=subprocess.STDOUT)
        else:
            result = subprocess.call(command, cwd=self.working_directory)
        return result


class MPIRunner(LocalRunner):
    def __init__(self, lammps_binary_path, nprocs=1):
        super().__init__(lammps_binary_path)
        self.nprocs = nprocs
        self.custom_mpi_options = []

        if 'LAMMPS_MPI_OPTIONS' in os.environ:
            logger.debug(f"Using LAMMPS_MPI_OPTIONS: {os.environ['LAMMPS_MPI_OPTIONS']}")
            self.custom_mpi_options = os.environ['LAMMPS_MPI_OPTIONS'].split()

    def get_full_command(self, input_script, options=[]):
        base_command = super().get_full_command(input_script, options)
        return  ["mpirun", "-np", str(self.nprocs)] + self.custom_mpi_options + base_command

@nottest
def discover_tests(test_dir, skip_list=[]):
    for path, _, files in os.walk(test_dir):
        name = os.path.relpath(path, test_dir)

        if(any([name.startswith(s) for s in skip_list])):
            continue

        scripts = [os.path.join(path, f) for f in files if f.startswith('in.')]
        logfiles = [os.path.join(path, f) for f in files if f.startswith('log.')]

        if len(scripts) > 0:
            yield name, scripts, logfiles


def get_container(name, settings):
    if name == 'local':
        return None
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
    containers  = get_names(os.path.join(settings.container_definition_dir, '*.def'))
    containers += get_names(os.path.join(settings.container_definition_dir, '**/*.def'))
    return [get_container(c, settings) for c in sorted(containers)]


def get_containers_by_selector(selector, settings):
    if 'all' in selector or 'ALL' in selector:
        return get_containers(settings)
    return [get_container(c, settings) for c in sorted(selector)]


def state_icon(state):
    if state == "success":
        return "✅"
    elif state == "failed":
        return "❌"
    else:
        return "⭕"


def get_configuration(name, settings):
    configfile = os.path.join(settings.configuration_dir, name + ".yml")
    if os.path.exists(configfile):
        with open(configfile) as f:
            config = yaml.full_load(f)
            return namedtuple("Configuration", ['name'] + list(config.keys()))(name, *config.values())
    raise FileNotFoundError(configfile)


def get_configurations(settings):
    configurations = get_names(os.path.join(settings.configuration_dir, '*.yml'))
    return [get_configuration(c, settings) for c in sorted(configurations)]


def get_configurations_by_selector(selector, settings):
    if 'all' in selector or 'ALL' in selector:
        return get_configurations(settings)
    return [get_configuration(c, settings) for c in sorted(selector)]


def get_lammps_commit(commit, settings):
    return subprocess.check_output(['git', 'rev-parse', commit], cwd=settings.lammps_dir).decode().strip()


def get_commits(settings):
    commits = get_names(os.path.join(settings.cache_dir, 'builds_*'))
    return [c[7:] for c in sorted(commits)]
