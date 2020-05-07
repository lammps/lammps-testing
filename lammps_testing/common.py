import os
import sys
import glob
import logging
import subprocess

logger = logging.getLogger('lammps_test')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(ch)

def file_is_newer(a, b):
    return os.stat(a).st_mtime > os.stat(b).st_mtime

class Settings(object):
    def __init__(self):
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
        return os.path.join(os.environ['LAMMPS_TESTING_DIR'], 'scripts', 'simple')

    @property
    def build_scripts_dir(self):
        return os.path.join(self.configuration_dir, 'builds')

    @property
    def run_tests_scripts_dir(self):
        return os.path.join(self.configuration_dir, 'run_tests')

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


def discover_tests(test_dir, skip_list=[]):
    for name in os.listdir(test_dir):
        path = os.path.join(test_dir, name)

        if name in skip_list:
            continue

        if os.path.isdir(path):
            scripts = list(map(os.path.basename, glob.glob(os.path.join(path, 'in.*'))))
            if len(scripts) > 0:
                yield name, scripts