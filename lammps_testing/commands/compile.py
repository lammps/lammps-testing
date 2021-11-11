from ..common import logger, get_configurations, get_container, get_configuration
from ..tests import CompilationTest
import sys


def expand_selected_config_and_builds(selected_builds, settings):
    builds = {}

    def add_build(config, build):
        if config not in builds:
            builds[config] = [build]
        elif build not in builds[config]:
            builds[config].append(build)

    if "ALL" in selected_builds or "all" in selected_builds:
        configurations = get_configurations(settings)
        for config in configurations:
            if hasattr(config, "builds"):
                builds[config.name] = config.builds
    else:
        for selected in selected_builds:
            parts = selected.split('/')

            if len(parts) == 1 or parts[1] == "*":
                config = get_configuration(parts[0], settings)
                for build in config.builds:
                    add_build(config.name, build)
            elif parts[1].endswith("*"):
                prefix = parts[1][:-1]
                config = get_configuration(parts[0], settings)
                for build in config.builds:
                    if build.startswith(prefix):
                        add_build(config.name, build)
            else:
                config = get_configuration(parts[0], settings)
                build = parts[1]
                add_build(config.name, build)
    return builds


def compilation_test(args, settings):
    selected_builds = args.builds
    selected_builds = expand_selected_config_and_builds(args.builds, settings)
    configurations = get_configurations(settings)

    for config in configurations:
        if config.name in selected_builds.keys():
            container = get_container(config.container_image, settings)

            if not container.exists:
                logger.error(f"Can not find container: {container}")
                sys.exit(1)

            for build_name in config.builds:
                if build_name in selected_builds[config.name]:
                    if args.ignore_commit:
                        compTest = CompilationTest(build_name, container, settings)
                    else:
                        compTest = CompilationTest(build_name, container, settings, settings.current_lammps_commit)

                    print(f"Compiling {config.name}/{build_name}")

                    if not compTest.build():
                        print(f"Compilation of '{build_name}' on '{container.name}' FAILED!")
                        sys.exit(1)

def init_command(parser):
    parser.add_argument('--ignore-commit', default=False, action='store_true', help='Ignore commit and do not create SHA specific build folder')
    parser.add_argument('builds', metavar='build', nargs='*', default=['ALL'], help='list of builds that should be compiled')
    parser.set_defaults(func=compilation_test)
