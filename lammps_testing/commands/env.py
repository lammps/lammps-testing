from ..common import logger, get_containers_by_selector, get_containers, state_icon

def env_clean(args, settings):
    containers = get_containers_by_selector(args.images, settings)

    print("Selected Containers:")

    for container in containers:
        print("-", container.name)

    if not args.force:
        answer = input('Delete all these containers? (y/N):')
        if answer not in ['Y', 'y']:
            logger.info('Aborting clean...')
            return

    for container in containers:
        logger.info(f'Removing {container.name}...')
        container.clean()


def env_build_container(args, settings):
    for c in get_containers_by_selector(args.images, settings):
        c.build(force=args.force)


def env_list(args, settings):
    containers = get_containers(settings)
    print("local")
    for c in containers:
        print(c.name)


def env_status(args, settings):
    containers = get_containers(settings)
    print(f" {state_icon('success')} local")
    for c in containers:
        if c.exists:
            icon = state_icon("success")
        else:
            icon = state_icon("")

        print(f" {icon} {c.name}")


def init_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    elist = subparsers.add_parser('list', help='list all test environments')
    elist.set_defaults(func=env_list)

    status = subparsers.add_parser('status', help='show build status of all test environments')
    status.set_defaults(func=env_status)

    build = subparsers.add_parser('build', help='build container image(s)')
    build.add_argument('images', metavar='image_name', nargs='+', help='container image names')
    build.add_argument('-f', '--force', default=False, action='store_true', help="Force rebuild")
    build.set_defaults(func=env_build_container)

    clean = subparsers.add_parser('clean', help='remove container image(s)')
    clean.add_argument('images', metavar='image_name', nargs='+', help='container image names')
    clean.add_argument('-f', '--force', default=False, action='store_true', help="Clean without asking")
    clean.set_defaults(func=env_clean)
