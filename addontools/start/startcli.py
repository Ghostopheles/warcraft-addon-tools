import argparse

# Start tools


def start_handler(args):
    if args.subcommand == "create":
        print("Creating new configuration...")
        print(args)
        print(f"Portal: {args.portal}")
        print(f"Branch: {args.branch}")
    else:
        print("Launching config with args: " + str(args))


def register_start_parser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser(
        "start",
        help="Helper tools for starting specific WoW versions. All arguments provided with -- are forwarded to the WoW executable.",
    )

    subcommand = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        metavar="subcommand",
    )

    create = subcommand.add_parser(
        "create",
        help="Create a new configuration.",
        metavar="create",
    )
    create.add_argument(
        "-p",
        "-portal",
        dest="portal",
        metavar="portal",
        type=str,
        default="US",
        help="Set the portal to use. Default: US",
    )
    create.add_argument(
        "-b",
        "-branch",
        dest="branch",
        metavar="branch",
        type=str,
        default="live",
        help="Set the branch to use. Default: live",
    )

    parser.set_defaults(func=start_handler)
