#!/bin/env python
from __future__ import print_function
import os
import nose
import xml.etree.ElementTree as ET
import argparse
import subprocess
import glob
from multiprocessing import Pool

__author__ = 'Richard Berger'
__email__ = "richard.berger@temple.edu"


def load_tests(filename):
    print("Loading tests from %s..." % filename)
    tests = []

    loader = nose.loader.TestLoader()
    ctx = loader.loadTestsFromName(filename)

    for tc in list(ctx):
        for testname in list(tc):
            parts = testname.id().split('.')
            classname = '.'.join(parts[0:-1])
            name = parts[-1]
            selector = "{0}.{1}:{2}.{3}".format(*parts)
            tests.append({'classname': classname, 'name': name, 'time': 1.0, 'selector' : selector})

    return tests


def load_test_timing(tests, filename):
    """ load test runtimes from xunit result file and save to corresponding test """
    print("Loading timing information from %s..." % filename)

    def find_test(classname, name):
        for x in tests:
            if x['classname'] == classname and x['name'] == name:
                return x
        return None

    tree = ET.parse(filename)
    testcases = [x.attrib for x in tree.getroot()]

    for test_result in testcases:
        test = find_test(test_result['classname'], test_result['name'])
        if test:
            test['time'] = float(test_result['time'])


def create_job_queues(tests, nprocesses):
    queues = []
    for q in range(nprocesses):
        queues.append([])

    sorted_tests = sorted(tests, key=lambda x: float(x['time']), reverse=True)

    for t in sorted_tests:
        work_assignment = sorted([(sum([float(x['time']) for x in q]), i) for i,q in enumerate(queues)])

        # select queue with lowest work assignment
        selected_queue = work_assignment[0][1]

        queues[selected_queue].append(t)

    return queues

def print_list(x):
    for elem in x:
        print(" - ", elem['classname'], elem['name'], elem['time'])

def run_nose(args):
    pid, tests = args

    cpu_set = list(os.sched_getaffinity(0))

    if len(cpu_set) > 4:
        offset = (pid*4) % len(cpu_set)
        os.sched_setaffinity(0, set(cpu_set[offset:offset+4]))

    xunitfile = "nosetests-{0:02}.xml".format(pid)
    print(pid, ": Running nose with", len(tests), "tests...", xunitfile)
    selected_tests = [x['selector'] for x in tests]
    call = ['nosetests', '-v', '--with-xunit', '--xunit-file=' + xunitfile] + selected_tests
    subprocess.call(call)

def main():
    parser = argparse.ArgumentParser(description='run nosetests in parallel and load balance using timning information')
    parser.add_argument('files', metavar='FILE', nargs='+', help='python module file(s) containing tests')
    parser.add_argument('-p', '--processes', type=int, help='number of parallel processes', default=1)
    parser.add_argument('-d', '--dry-run', action='store_true', help='do not run nosetests, but output schedule', default=False)

    args = parser.parse_args()

    # load tests

    tests = []

    for f in args.files:
      tests += load_tests(f)

    timing_files = glob.glob('nosetests-*.xml')

    for tf in timing_files:
        load_test_timing(tests, tf)
        os.remove(tf)

    queues = create_job_queues(tests, args.processes)

    for i, q in enumerate(queues):
        print(i, len(q), sum([float(x['time']) for x in q]))
        print_list(q)

    if not args.dry_run:
        pool = Pool(processes=args.processes)
        pool.map(run_nose, enumerate(queues))


if __name__ == "__main__":
    main()
