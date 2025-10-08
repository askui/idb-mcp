import argparse
import sys

from idb_mcp.askui_chat import AddMcpServerToAskUIChat
from idb_mcp.mcp import start_server


def main() -> None:
    if sys.platform != "darwin":
        raise SystemExit("idb-mcp CLI is only supported on MacOS (Darwin).")
    parser = argparse.ArgumentParser(prog="idb_mcp", description="AskUI IDB MCP")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start MCP server")
    start_parser.add_argument(
        "mode",
        choices=["http", "sse"],
        help="Transport to serve: http or sse",
    )
    start_parser.add_argument(
        "--target-screen-size",
        type=int,
        nargs=2,
        help="Target screen size to scale the images and coordinates to",
        default=None,
    )

    add_mcp_server_to_askui_chat_parser = subparsers.add_parser(
        "add-to-caesr", help="Add MCP server to AskUI Caesr Chat"
    )
    add_mcp_server_to_askui_chat_parser.add_argument(
        "--chat-dir",
        dest="chat_directory_path",
        type=str,
        nargs="?",
        help="Path to the chat directory",
        default=None,
    )

    args = parser.parse_args()
    if args.command == "start":
        start_server(args.mode, args.target_screen_size)
    elif args.command == "add-to-caesr":
        AddMcpServerToAskUIChat.add_mcp_server_to_askui_chat(args.chat_directory_path)
    else:
        raise ValueError(f"Invalid command: {args.command}")


if __name__ == "__main__":
    main()
