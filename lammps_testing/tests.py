import os
import re
import json
import yaml
import glob
from xml.etree import ElementTree as ET

class LAMMPSExampleRun(object):
    def __init__(self, name, input_script, configuration):
        self.name = name
        self.input_script = input_script
        self.configuration = configuration

    def __str__(self):
        if "mpi" in self.configuration:
            return f"{self.name} (MPI: {self.configuration['mpi']['nprocs']} procs)"
        return f"{self.name} (Serial)"


def config_from_logfile(logfile):
    """This converts the logfile filename into a configuration"""
    parts = os.path.basename(logfile).split('.')
    ref_date =  parts[1]
    compiler = parts[-2]
    nprocs = int(parts[-1])

    config = {
        "reference" : {
            "logfile": logfile,
            "date": ref_date
        }
    }

    config['compiler'] = compiler

    if nprocs > 1:
        config['mpi'] = {'nprocs': nprocs}

    return config


class LAMMPSExample(object):
    def __init__(self, name, scripts, logfiles):
        self.name = name
        self.testcases = {}
        self.folder = os.path.dirname(scripts[0])

        for script in scripts:
            script_name = os.path.basename(script)
            testcase_name = script_name[3:]
            logfile_pattern = re.compile(r"log.(?P<date>[0-9]+[a-zA-Z]{3}[0-9]{2})\." + testcase_name + r"\.(?P<config>(g\+\+|clang)\.[1-9]*)")
            run = LAMMPSExampleRun(testcase_name, script, {'mpi': {'nprocs': 8}})
            self.testcases[testcase_name] = [run]

            for logfile in logfiles:
                m = logfile_pattern.match(os.path.basename(logfile))
                if m is not None:
                    try:
                        configuration = config_from_logfile(logfile)
                        run = LAMMPSExampleRun(testcase_name, script, configuration)
                        self.testcases[testcase_name].append(run)
                    except ValueError:
                        pass

    def save_config(self):
        config_file = os.path.join(self.folder, '.testing', 'config.yaml')
        config = []

        for testcase_name, runs in self.testcases.items():
            run_list = []

            for run in runs:
                logfile = os.path.basename(run.configuration['logfile'])
                if 'mpi' in run.configuration:
                    run_list.append({'logfile': logfile, 'mpi': {'nprocs': run.configuration['mpi']['nprocs']}})
                else:
                    run_list.append({'logfile': logfile})

            testcase = {"input_script": f"in.{testcase_name}", "runs": run_list}
            config.append(testcase)

        os.makedirs(os.path.dirname(config_file),exist_ok=True)
        with open(config_file, "w") as f:
            yaml.dump(config, f)


class Build(object):
    def __init__(self, name, container, settings, commit=None):
        self.name = name
        self.container = container
        self.settings = settings
        self.commit = commit

    @property
    def build_base_dir(self):
        if self.commit is not None:
            return os.path.join(self.settings.cache_dir, f'builds_{self.commit}')
        return os.path.join(self.settings.cache_dir, f'builds')

    @property
    def build_dir(self):
        return os.path.join(self.build_base_dir, self.container.name, self.name)

    @property
    def build_script(self):
        return os.path.join(self.settings.build_scripts_dir, f"{self.name}.sh")

    @property
    def build_result_file(self):
        return os.path.join(self.build_dir, "build_result.json")

    @property
    def state(self):
        if os.path.exists(self.build_result_file):
            with open(self.build_result_file, "r") as f:
                result = json.load(f)

            if result["return_code"] == 0:
                return "success"
            return "failure"
        else:
            return "not executed"


class CompilationTest(Build):
    def __init__(self, name, container, settings, commit=None):
        super(CompilationTest, self).__init__(name, container, settings, commit)

    def build(self):
        workdir = self.build_dir
        build_script = self.build_script

        os.makedirs(workdir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir

        try:
            return_code = self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=build_script,
                                   cwd=workdir)
        except KeyboardInterrupt:
            return_code = -1

        with open(self.build_result_file, "w") as f:
            result = {
                'return_code': return_code
            }
            json.dump(result, f)

        return return_code == 0


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


class UnitTest(Build):
    def __init__(self, name, container, settings, commit=None):
        super(UnitTest, self).__init__(name, container, settings, commit)

    @property
    def build_script(self):
        return os.path.join(self.settings.unit_tests_scripts_dir, self.name, "build.sh")

    @property
    def test_script(self):
        return os.path.join(self.settings.unit_tests_scripts_dir, self.name, "test.sh")

    @property
    def test_result_file(self):
        return os.path.join(self.build_dir, "test_result.json")

    def build(self):
        os.makedirs(self.build_dir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        try:
            return_code = self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=self.build_script,
                                   cwd=self.build_dir)
        except KeyboardInterrupt:
            return_code = -1

        with open(self.build_result_file, "w") as f:
            result = {
                'return_code': return_code
            }
            json.dump(result, f)

        return return_code == 0

    def test(self):
        os.makedirs(self.build_dir, exist_ok=True)
        LAMMPS_DIR = self.settings.lammps_dir
        BUILD_SCRIPTS_DIR = self.settings.build_scripts_dir
        try:
            return_code = self.container.exec(options=['-B', f'{LAMMPS_DIR}/:{LAMMPS_DIR}/', '-B', f'{BUILD_SCRIPTS_DIR}/:{BUILD_SCRIPTS_DIR}/'],
                                   command=self.test_script,
                                   cwd=self.build_dir)
        except KeyboardInterrupt:
            return_code = -1

        with open(self.test_result_file, "w") as f:
            result = {
                'return_code': return_code
            }
            json.dump(result, f)

        return return_code == 0

    @property
    def state(self):
        build_state = super(UnitTest, self).state

        if os.path.exists(self.test_result_file):
            with open(self.test_result_file, "r") as f:
                result = json.load(f)

            if build_state == "success" and result["return_code"] == 0 and len(self.result["failed"]) == 0:
                return "success"
            return "failure"
        elif build_state == "success":
            return "pending"
        else:
            return "not executed"

    @property
    def result(self):
        test_files = glob.glob(os.path.join(self.build_dir, "**", "**", "**", "Test.xml"))
        result_dict = {'passed': [], 'failed': [], "skipped": []}

        for result_file in test_files:
            doc = ET.parse(result_file).getroot()
            tests = doc.find("Testing").findall("Test")
            for test in tests:
                full_name = test.find("FullName").text
                status = test.attrib["Status"]
                if status not in result_dict:
                    result_dict[status] = [full_name]
                else:
                    result_dict[status].append(full_name)
        return result_dict


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
