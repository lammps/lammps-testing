
from ..common import get_configuration, logger, get_configurations_by_selector, get_container, state_icon, expand_selected_config_and_runs, get_configurations
from ..tests import RunTest
import sys

def run_list(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)
        for config in configs:
            if hasattr(config, "run_tests"):
                for run_test in config.run_tests:
                    print(f"{config.name}/{run_test}")
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)


def print_run_status(config, run):
    icon = state_icon(run.state)
    commit_info = ""

    if run.commit is not None:
        commit_info = f" ({run.commit[:8]:8s})"

    print(f" {icon} {config.name}/{run.name}{commit_info}")


def run_status(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)

        for config in configs:
            container = get_container(config.container_image, settings)

            if hasattr(config, "run_tests"):
                for build in config.run_tests:
                    if args.ignore_commit:
                        runTest = RunTest(build, container, settings)
                    else:
                        runTest = RunTest(build, container, settings, settings.current_lammps_commit)
                    print_run_status(config, runTest)
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)

def run_report(args, settings):
    configuration_name, run_name = args.build.split('/')
    config = get_configuration(configuration_name, settings)
    container = get_container(config.container_image, settings)

    if args.ignore_commit:
        runTest = RunTest(run_name, container, settings)
    else:
        runTest = RunTest(run_name, container, settings, settings.current_lammps_commit)

    print(f"{configuration_name}/{run_name}\n")
    print("Build Directory:")
    print(runTest.build_dir)
    print()

    result = runTest.result

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


def run_test(args, settings):
    selected_builds = args.builds
    selected_builds = expand_selected_config_and_runs(args.builds, settings)
    configurations = get_configurations(settings)

    for config in configurations:
        if config.name in selected_builds.keys():
            container = get_container(config.container_image, settings)

            if not container.exists:
                logger.error(f"Can not find container: {container}")
                sys.exit(1)

            for run_name in config.run_tests:
                if run_name in selected_builds[config.name]:
                    if args.ignore_commit:
                        runTest = RunTest(run_name, container, settings)
                    else:
                        runTest = RunTest(run_name, container, settings, settings.current_lammps_commit)

                    if not args.test_only and not runTest.build():
                        print(f"Compilation of '{run_name}' on '{container.name}' FAILED!")
                        sys.exit(1)

                    if not args.build_only and not runTest.test():
                        print(f"Run tests of '{run_name}' on '{container.name}' FAILED!")
                        sys.exit(1)


def init_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    rlist = subparsers.add_parser('list', help='list all run tests')
    rlist.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    rlist.set_defaults(func=run_list)

    status = subparsers.add_parser('status', help='show status of all run tests')
    status.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    status.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    status.set_defaults(func=run_status)

    report = subparsers.add_parser('report', help='show report of run test')
    report.add_argument('build', help='name of run test')
    report.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    report.set_defaults(func=run_report)

    run = subparsers.add_parser('run', help='list all run tests')
    run.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    run.add_argument('builds', metavar='build', nargs='*', default=['ALL'], help='list of builds that should be compiled')
    run_group = run.add_mutually_exclusive_group()
    run_group.add_argument('--build-only', default=False, action='store_true', help='Only build run binary')
    run_group.add_argument('--test-only', default=False, action='store_true', help='Only run test on existing binary')
    run.set_defaults(func=run_test)
