import re

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
                elif re.match(r"^-------\+ Step",line):
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
