from ..common import get_configurations

def config_list(args, settings):
    for c in get_configurations(settings):
        print(c.name)


def init_command(parser):
    subparsers = parser.add_subparsers(help='sub-command help')

    clist = subparsers.add_parser('list', help='list all configurations')
    clist.set_defaults(func=config_list)
