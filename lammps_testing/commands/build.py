from ..common import get_configurations_by_selector, get_container, state_icon
from ..tests import CompilationTest
import sys

def build_list(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)
        for config in configs:
            if hasattr(config, "builds"):
                for build in config.builds:
                    print(f"{config.name}/{build}")
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)


def print_build_status(config, build):
    icon = state_icon(build.state)
    commit_info = ""

    if build.commit is not None:
        commit_info = f" ({build.commit[:8]:8s})"

    print(f" {icon} {config.name}/{build.name}{commit_info}")


def build_status(args, settings):
    try:
        configs = get_configurations_by_selector(args.config, settings)

        for config in configs:
            container = get_container(config.container_image, settings)

            if hasattr(config, "builds"):
                for build in config.builds:
                    if args.ignore_commit:
                        compTest = CompilationTest(build, container, settings)
                    else:
                        compTest = CompilationTest(build, container, settings, settings.current_lammps_commit)
                    print_build_status(config, compTest)
    except FileNotFoundError:
        print(f"Configuration with name '{args.config}' does not exist!")
        sys.exit(1)


def init_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    blist = subparsers.add_parser('list', help='list all configurations')
    blist.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    blist.set_defaults(func=build_list)

    status = subparsers.add_parser('status', help='show build status')
    status.add_argument('config', metavar='config', default=['ALL'], help='name of configuration', nargs='*')
    status.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    status.set_defaults(func=build_status)
