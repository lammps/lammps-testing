from ..common import get_configuration, logger, get_configurations_by_selector, get_container, state_icon, expand_selected_config_and_runs, get_configurations, discover_tests
from ..tests import RegressionTest, RunTest, LAMMPSExample
import os
import sys

def reg_list(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)
        for config in configs:
            if hasattr(config, "regression_tests"):
                for regression_test in config.regression_tests:
                    print(f"{config.name}/{regression_test}")
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)


def print_reg_status(config, reg):
    icon = state_icon(reg.state)
    commit_info = ""

    if reg.commit is not None:
        commit_info = f" ({reg.commit[:8]:8s})"

    print(f" {icon} {config.name}/{reg.name}{commit_info}")


def reg_status(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)

        for config in configs:
            container = get_container(config.container_image, settings)

            if hasattr(config, "regression_tests"):
                for build in config.regression_tests:
                    if args.ignore_commit:
                        regTest = RegressionTest(build, container, settings)
                    else:
                        regTest = RegressionTest(build, container, settings, settings.current_lammps_commit)
                    print_reg_status(config, regTest)
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)

def reg_report(args, settings):
    configuration_name, reg_name = args.build.split('/')
    config = get_configuration(configuration_name, settings)
    container = get_container(config.container_image, settings)

    if args.ignore_commit:
        regTest = RegressionTest(reg_name, container, settings)
    else:
        regTest = RegressionTest(reg_name, container, settings, settings.current_lammps_commit)

    print(f"{configuration_name}/{reg_name}\n")
    print("Build Directory:")
    print(regTest.build_dir)
    print()

    result = regTest.result

    if result is not None:
        npassed = len(result["passed"])
        nfailed = len(result["failed"])
        nskipped = len(result["skipped"])
        print(f"Result:")
        print(f"{npassed} passed")
        print(f"{nfailed} failed")
        print(f"{nskipped} skipped")
    else:
        print("Result: not available")


def reg_run(args, settings):
    selected_builds = args.builds
    selected_builds = expand_selected_config_and_runs(args.builds, settings)
    configurations = get_configurations(settings)

    for config in configurations:
        if config.name in selected_builds.keys():
            container = get_container(config.container_image, settings)

            if not container.exists:
                logger.error(f"Can not find container: {container}")
                sys.exit(1)

            for reg_name in config.regression_tests:
                if reg_name in selected_builds[config.name]:
                    if args.ignore_commit:
                        regTest = RegressionTest(reg_name, container, settings)
                    else:
                        regTest = RegressionTest(reg_name, container, settings, settings.current_lammps_commit)

                    if not args.test_only and not regTest.build():
                        print(f"Compilation of '{reg_name}' on '{container.name}' FAILED!")
                        sys.exit(1)

                    if not args.build_only and not regTest.test():
                        print(f"Run tests of '{reg_name}' on '{container.name}' FAILED!")
                        sys.exit(1)


def reg_list_tests(args, settings):
    """List all examples and runs possible within the LAMMPS examples folder"""
    examples_dir = os.path.join(settings.lammps_dir, 'examples')
    testcase_count = 0
    run_count = 0
    mpi_run_count = 0
    for test, scripts, logfiles in discover_tests(examples_dir):
        example = LAMMPSExample(test, scripts, logfiles)
        if len(example.testcases) > 0:
            print(example.name)
            for testcase, runs in example.testcases.items():
                print(" -", testcase)
                testcase_count += 1
                for run in runs:
                    if "MPI" in str(run):
                        mpi_run_count += 1
                    print("    *", run)
                    run_count += 1
    print("Total testcases:", testcase_count)
    print("Total runs:", run_count)
    print("Total MPI runs:", mpi_run_count)


def reg_create_yaml(args, settings):
    """Generate YAML configuration files that describe the example runs"""
    examples_dir = os.path.join(settings.lammps_dir, 'examples')
    for test, scripts, logfiles in discover_tests(examples_dir):
        example = LAMMPSExample(test, scripts, logfiles)
        if len(example.testcases) > 0:
            example.save_config()


def init_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    #blist = subparsers.add_parser('list-tests', help='list all configurations')
    #blist.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    #blist.set_defaults(func=reg_list_tests)

    #create_yaml = subparsers.add_parser('create_yaml', help='generate yaml files for all cases')
    #create_yaml.set_defaults(func=reg_create_yaml)

    rlist = subparsers.add_parser('list', help='list all run tests')
    rlist.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    rlist.set_defaults(func=reg_list)

    status = subparsers.add_parser('status', help='show status of all run tests')
    status.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    status.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    status.set_defaults(func=reg_status)

    report = subparsers.add_parser('report', help='show report of run test')
    report.add_argument('build', help='name of run test')
    report.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    report.set_defaults(func=reg_report)

    run = subparsers.add_parser('run', help='run regression tests')
    run.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    run.add_argument('builds', metavar='build', nargs='*', default=['ALL'], help='list of builds that should be compiled')
    run_group = run.add_mutually_exclusive_group()
    run_group.add_argument('--build-only', default=False, action='store_true', help='Only build regression test binary')
    run_group.add_argument('--test-only', default=False, action='store_true', help='Only run regression test on existing binary')
    run.set_defaults(func=reg_run)
