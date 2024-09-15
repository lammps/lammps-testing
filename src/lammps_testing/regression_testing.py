import glob
import math
import os
import platform
import shutil
from datetime import datetime

from lammps_testing.formats import LammpsLog


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


class RegressionTestResult(object):
    def __init__(self, current_log, reference_log, error, failed_fields, generated_images):
        self.current_log = current_log
        self.reference_log = reference_log
        self.error = error
        self.failed_fields = failed_fields
        self.generated_images = generated_images

    @property
    def passed(self):
        return self.error == None and len(self.failed_fields) == 0


class RegressionTest(object):
    def __init__(self, name, test_directory, descriptor, options=[]):
        self.test_directory = test_directory
        self.descriptor = descriptor
        self.name = name
        self.options = [str(x) for x in options]
        self.input_script = f'in.{name}'
        self.log_file     = f'log.{descriptor}.{name}'
        self.stdout_file  = f'stdout.{descriptor}.{name}'
        self.graphics_prefix = f'run.{descriptor}.{name}'

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
            lammps_options = ['-log', self.log_file] + self.options
            runner.working_directory = self.test_directory
            return_code = runner.run(input_script=self.input_script, options=lammps_options, stdout=f)

        if return_code != 0:
          raise Exception("LAMMPS run failed!")

        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(self.log_file_path)

        if is_reference:
            today = datetime.now()
            system_name = platform.system().lower()
            target_file_path = os.path.join(self.test_directory, f'log.{today:%d%b%y}.{system_name}.{self.descriptor}.{self.name}')
            shutil.copyfile(self.log_file_path, target_file_path)

    def verify(self, runner, norm='max', tolerance=1e-6, generate_plots=False, verbose=False):
        reference_file_path = self.gold_standard_file_path

        if not reference_file_path or not os.path.exists(reference_file_path):
            print("Reference run missing, creating new reference...")
            self.run(runner, is_reference=True)

        reference_file_path = self.gold_standard_file_path
        assert(reference_file_path and os.path.exists(reference_file_path))

        print("Running test case...")
        self.run(runner)

        current_file_path = self.log_file_path
        assert(current_file_path and os.path.exists(current_file_path))

        print("Current:", current_file_path)
        print("Reference:", reference_file_path)

        failed = []
        generated_images = []
        error = None

        current_log   = LammpsLog(current_file_path)
        reference_log = LammpsLog(reference_file_path)

        try:
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
                            img_path = os.path.join(self.test_directory, f'{self.graphics_prefix}.run.{index}.{field}.png')
                            plt.savefig(img_path)
                            generated_images.append(img_path)

                        failed.append((index, field))
        except Exception as e:
            error = e

        return RegressionTestResult(current_file_path, reference_file_path, error, failed, generated_images)
