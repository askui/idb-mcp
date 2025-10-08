import asyncio
import json
import os
import sys
from datetime import datetime, timezone

import bson

from idb_mcp.askui_chat.asst_avatar import ASSISTANT_AVATAR
from idb_mcp.askui_chat.prompt import SYSTEM_PROMPT
from idb_mcp.mcp.server import app


class AddMcpServerToAskUIChat:
    """Class handles"""

    def __init__(self, chat_directory_path: str | None = None) -> None:
        self.chat_directory_path = (
            chat_directory_path or AddMcpServerToAskUIChat._get_caesr_desktop_path()
        )
        if not os.path.exists(self.chat_directory_path):
            raise FileNotFoundError(
                f"AskUI Chat directory path does not exist at '{self.chat_directory_path}'."
            )
        self._mcp_server_config_directory_path = os.path.join(
            self.chat_directory_path, "mcp_configs"
        )
        self._assistant_config_directory_path = os.path.join(
            self.chat_directory_path, "assistants"
        )
        self._check_directories_exists()

        self._time_ordered_id = str(bson.ObjectId())
        self._created_at = int(datetime.now(tz=timezone.utc).timestamp())
        self._app_tool_list = asyncio.run(AddMcpServerToAskUIChat._get_app_tool_list())
        self._mcp_server_config_name = f"mcpcnf_{self._time_ordered_id}"
        self._assistant_config_name = f"asst_{self._time_ordered_id}"

    @classmethod
    def add_mcp_server_to_askui_chat(
        cls, chat_directory_path: str | None = None
    ) -> None:
        """
        Adds the MCP server config and assistant config to the AskUI chat directory.
        """
        add_mcp_server_to_askui_chat = cls(chat_directory_path)
        add_mcp_server_to_askui_chat.add_to_chat()

    def _check_directories_exists(self) -> None:
        """ "
        Checks if the directories exist.
        """
        if not os.path.exists(self.chat_directory_path):
            raise FileNotFoundError(
                f"AskUI Chat directory path does not exist at '{self.chat_directory_path}'."
            )

        if not os.path.exists(self._mcp_server_config_directory_path):
            raise FileNotFoundError(
                f"MCP server config directory path does not exist at '{self._mcp_server_config_directory_path}'."
            )
        if not os.path.exists(self._assistant_config_directory_path):
            raise FileNotFoundError(
                f"Assistant config directory path does not exist at '{self._assistant_config_directory_path}'."
            )

    def add_to_chat(self) -> None:
        """
        Adds the MCP server config and assistant config to the AskUI chat directory.
        """
        if not os.path.exists(self.chat_directory_path):
            raise FileNotFoundError(
                f"Chat directory path does not exist: {self.chat_directory_path}"
            )
        self._add_mcp_server_config()
        self._add_assistant_config()

    @staticmethod
    async def _get_app_tool_list() -> list:
        tools = await app.get_tools()
        return [tool.name for tool in tools.values()]

    @staticmethod
    def _get_caesr_desktop_path() -> str:
        if sys.platform == "darwin":
            return os.path.expanduser(
                "~/Library/Application Support/caesr-desktop/chat"
            )
        raise NotImplementedError(f"Platform {sys.platform} not supported")

    def _add_mcp_server_config(self) -> None:
        """
        Adds the MCP server config to the chat directory.
        """
        mcp_server_config_directory_path = os.path.join(
            self.chat_directory_path, "mcp_configs"
        )
        if not os.path.exists(mcp_server_config_directory_path):
            raise FileNotFoundError(
                f"MCP server config directory path does not exist at '{mcp_server_config_directory_path}'."
            )
        mcp_server_config_file_path = os.path.join(
            mcp_server_config_directory_path,
            f"{self._mcp_server_config_name}.json",
        )
        print(f"Adding MCP server config to '{mcp_server_config_file_path}' ...")
        with open(mcp_server_config_file_path, "w", encoding="utf-8") as f:
            json.dump(self._get_mcp_server_config(), f)
        print(f"MCP server was successfully added to '{mcp_server_config_file_path}'")

    def _add_assistant_config(self) -> None:
        """
        Adds the assistant config to the chat directory.
        """
        assistant_config_directory_path = os.path.join(
            self.chat_directory_path, "assistants"
        )
        if not os.path.exists(assistant_config_directory_path):
            raise FileNotFoundError(
                f"Assistant config directory path does not exist at '{assistant_config_directory_path}'."
            )
        assistant_config_file_path = os.path.join(
            assistant_config_directory_path, f"{self._assistant_config_name}.json"
        )
        print(f"Adding Assistant config to '{assistant_config_file_path}' ...")
        with open(assistant_config_file_path, "w", encoding="utf-8") as f:
            json.dump(self._get_assistant_config(), f)
        print(f"Assistant was successfully added to '{assistant_config_file_path}'")

    def _get_assistant_config(self) -> dict:
        return {
            "id": self._assistant_config_name,
            "workspace_id": None,
            "name": "IOS Automation Assistant",
            "description": "An assistant that can automate iOS simulators.",
            "avatar": ASSISTANT_AVATAR,
            "tools": self._app_tool_list,
            "system": SYSTEM_PROMPT,
            "object": "assistant",
            "created_at": self._created_at,
        }

    def _get_mcp_server_config(self) -> dict:
        return {
            "id": self._mcp_server_config_name,
            "name": "AskUI IDB MCP Server",
            "mcp_server": {
                "command": "uvx",
                "args": [
                    "idb-mcp",
                    "start",
                    "sse",
                    "--target-screen-size",
                    "1280",
                    "800",
                ],
            },
            "created_at": self._created_at,
        }
