import argparse
import sys

from idb_mcp.mcp import start_server


def main() -> None:
    if sys.platform != "darwin":
        raise SystemExit("idb-mcp CLI is only supported on MacOS (Darwin).")
    parser = argparse.ArgumentParser(prog="idb_mcp", description="AskUI IDB MCP")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start MCP server")
    start_parser.add_argument(
        "mode",
        choices=["stdio", "http", "sse"],
        help="Transport to serve: http or sse",
    )
    start_parser.add_argument(
        "--port",
        dest="port",
        type=int,
        help="Port to serve the MCP server on",
        default=8000,
    )
    start_parser.add_argument(
        "--target-screen-size",
        type=int,
        nargs=2,
        help="Target screen size to scale the images and coordinates to",
        default=None,
    )

    args = parser.parse_args()
    if args.command == "start":
        start_server(args.mode, args.port, args.target_screen_size)
    else:
        raise ValueError(f"Invalid command: {args.command}")


if __name__ == "__main__":
    main()
