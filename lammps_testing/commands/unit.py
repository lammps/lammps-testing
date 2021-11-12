from ..common import get_configuration, logger, get_configurations_by_selector, get_container, state_icon, expand_selected_config_and_unittests, get_configurations
from ..tests import UnitTest
import sys

def unittest_list(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)
        for config in configs:
            if hasattr(config, "unit_tests"):
                for unit_test in config.unit_tests:
                    print(f"{config.name}/{unit_test}")
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)


def print_unittest_status(config, unittest):
    icon = state_icon(unittest.state)
    commit_info = ""

    if unittest.commit is not None:
        commit_info = f" ({unittest.commit[:8]:8s})"

    print(f" {icon} {config.name}/{unittest.name}{commit_info}")


def unittest_status(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)

        for config in configs:
            container = get_container(config.container_image, settings)

            if hasattr(config, "unit_tests"):
                for build in config.unit_tests:
                    if args.ignore_commit:
                        unitTest = UnitTest(build, container, settings)
                    else:
                        unitTest = UnitTest(build, container, settings, settings.current_lammps_commit)
                    print_unittest_status(config, unitTest)
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)

def unittest_report(args, settings):
    configuration_name, unittest_name = args.build.split('/')
    config = get_configuration(configuration_name, settings)
    container = get_container(config.container_image, settings)

    if args.ignore_commit:
        unitTest = UnitTest(unittest_name, container, settings)
    else:
        unitTest = UnitTest(unittest_name, container, settings, settings.current_lammps_commit)

    print(f"{configuration_name}/{unittest_name}\n")
    print("Build Directory:")
    print(unitTest.build_dir)
    print()

    result = unitTest.result

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


def run_unit_test(args, settings):
    selected_builds = args.builds
    selected_builds = expand_selected_config_and_unittests(args.builds, settings)
    configurations = get_configurations(settings)

    for config in configurations:
        if config.name in selected_builds.keys():
            container = get_container(config.container_image, settings)

            if not container.exists:
                logger.error(f"Can not find container: {container}")
                sys.exit(1)

            for unittest_name in config.unit_tests:
                    if args.ignore_commit:
                        unitTest = UnitTest(unittest_name, container, settings)
                    else:
                        unitTest = UnitTest(unittest_name, container, settings, settings.current_lammps_commit)

                    if not args.test_only and not unitTest.build():
                        print(f"Compilation of '{unittest_name}' on '{container.name}' FAILED!")
                        sys.exit(1)

                    if not args.build_only and not unitTest.test():
                        print(f"Run unit tests of '{unittest_name}' on '{container.name}' FAILED!")
                        sys.exit(1)


def init_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    ulist = subparsers.add_parser('list', help='list all unit test runs')
    ulist.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    ulist.set_defaults(func=unittest_list)

    status = subparsers.add_parser('status', help='show status of all unit test runs')
    status.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    status.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    status.set_defaults(func=unittest_status)

    report = subparsers.add_parser('report', help='show report of unit test run')
    report.add_argument('build', help='name of unit test run')
    report.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    report.set_defaults(func=unittest_report)

    run = subparsers.add_parser('run', help='list all unit test runs')
    run.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    run.add_argument('builds', metavar='build', nargs='*', default=['ALL'], help='list of builds that should be compiled')
    run_group = run.add_mutually_exclusive_group()
    run_group.add_argument('--build-only', default=False, action='store_true', help='Only build run binary')
    run_group.add_argument('--test-only', default=False, action='store_true', help='Only run test on existing binary')
    run.set_defaults(func=run_unit_test)
