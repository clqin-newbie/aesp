from .. import __version__
import argparse


workflow_subcommands = [
    "terminate",
    "stop",
    "suspend",
    "delete",
    "retry",
    "resume"
]

def args_setup():
    parser = argparse.ArgumentParser(
        'aesp', 
        description="aesp is a tool for structure prediction", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(title="Valid subcommands", dest="command")

    ##########################################
    # submit
    parser_submit = subparsers.add_parser(
        "submit",
        help="Submit aesp workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_submit.add_argument(
        "config", help="the config file in json format defining the workflow."
    )
    
    # -----------------------gui
    parser_gui = subparsers.add_parser(
        "gui",
        help="gui aesp workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # parser_gui.add_argument(
    #     "config", help="the config file in json format defining the workflow."
    # )
    parser_gui.add_argument(
        "-d",
        "--destination",
        type=str,
        nargs=1,
        default=["./results"],
        help="specify the path to the results folder",
    )
    
    ##########################################
    # resubmit
    parser_resubmit = subparsers.add_parser(
        "resubmit",
        help="Submiting aesp workflow resuing steps from an existing workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_resubmit.add_argument(
        "config", help="the config file in json format defining the workflow."
    )
    parser_resubmit.add_argument("id", nargs="+", type=str, default=None, help="the ID of the existing workflow.")
    parser_resubmit.add_argument(
        "-s",
        "--stepid",
        type=str,
        nargs="+",
        default=None,
        help="specify which Steps (id) to reuse.",
    )


    ##########################################
    # download
    parser_download = subparsers.add_parser(
        "download",
        help="Dwnloading aesp files from an existing workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_download.add_argument(
        "config", help="the config file in json format defining the workflow."
    )
    parser_download.add_argument("id", help="the ID of the existing workflow.")
    parser_download.add_argument(
        "-s",
        "--stepid",
        type=str,
        nargs="+",
        default=None,
        help="Determining which Steps will be downloaded.",
    )
    parser_download.add_argument(
        "-d",
        "--destination",
        type=str,
        nargs=1,
        default=["./downloads"],
        help="Specify the path to the downloaded file",
    )
    parser_download.add_argument('-i', '--input', help='Input', action='store_true')
    parser_download.add_argument('-o', '--output', help='Output', action='store_true')

    ##########################################
    # analysis
    parser_analysis = subparsers.add_parser(
        "analysis",
        help="Dwnload aesp workflow resuing steps from an existing workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_analysis.add_argument(
        "config", help="the config file in json format defining the workflow."
    )
    parser_analysis.add_argument("id", help="the ID of the existing workflow.")
    parser_analysis.add_argument('-i', '--init', help='init', action='store_true')
    parser_analysis.add_argument('-t', '--train', help='train', action='store_true')
    parser_analysis.add_argument(
        "-d",
        "--destination",
        type=str,
        nargs=1,
        default=["./results"],
        help="specify the path to the results folder",
    )

    ##########################################
    # status
    parser_status = subparsers.add_parser(
        "status",
        help="show the status of the aesp workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_status.add_argument("config", help="the config file in json format.")
    parser_status.add_argument("id", help="the ID of the existing workflow.")
    parser_status.add_argument('-s', '--step', help='show the status of each Step', action='store_true')

    parser_status.add_argument(
        "-d",
        "--destination",
        type=str,
        nargs=1,
        default=None,
        help="Determine the output path of the status file",
    )
    # watch
    parser_watch = subparsers.add_parser(
        "watch",
        help="Watch a aesp workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser_watch.add_argument("config", help="the config file in json format.")
    parser_watch.add_argument("id", help="the ID of the existing workflow.")
    parser_watch.add_argument(
        "-s",
        "--stepid",
        type=str,
        nargs="+",
        default=None,
        help="specify which Steps to watch.",
    )

    ##########################################
    # workflow subcommands
    for cmd in workflow_subcommands:
        parser_cmd = subparsers.add_parser(
            cmd,
            help=f"{cmd.capitalize()} a aesp workflow.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser_cmd.add_argument("config", help="the config file in json format.")
        parser_cmd.add_argument("id", help="the ID of the workflow.")

    # --version
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="aesp v%s" % __version__,
    )
    return parser

