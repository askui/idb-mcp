# IDB-MCP

![PyPI](https://img.shields.io/pypi/v/idb-mcp) ![Python Versions](https://img.shields.io/pypi/pyversions/idb-mcp) ![License](https://img.shields.io/github/license/askui/idb-mcp)

An open-source MCP server and Python library that wraps Facebook IDB to control iOS simulators for automation. Built by [AskUI](https://www.askui.com/).

This project is based on the Facebook IDB CLI (`fb-idb`). See the GitHub repository ([`facebook/idb`](https://github.com/facebook/idb)) and the Python package ([`fb-idb` on PyPI](https://pypi.org/project/fb-idb/)).

Welcome! 🚀 This repo helps you automate iOS simulators quickly and reliably, via MCP or directly in Python.

## What it is

- **MCP server**: Exposes a set of iOS automation tools (list/select device, screenshot, tap, swipe, type, etc.) over MCP transports (HTTP or SSE) using `fastmcp`.
- **Python module**: Import to manage and control iOS simulators programmatically.

## Table of contents

- [IDB-MCP](#idb-mcp)
  - [What it is](#what-it-is)
  - [Table of contents](#table-of-contents)
  - [Key features](#key-features)
  - [Limitations](#limitations)
  - [Requirements](#requirements)
  - [Install](#install)
  - [Quick start (CLI)](#quick-start-cli)
    - [Why MCP?](#why-mcp)
    - [Start MCP server](#start-mcp-server)
    - [Add MCP server to AskUI `Caesr` Chat](#add-mcp-server-to-askui-caesr-chat)
  - [Programmatic usage (Python)](#programmatic-usage-python)
  - [Add to your favorite tools](#add-to-your-favorite-tools)
  - [Configuration](#configuration)
  - [Troubleshooting](#troubleshooting)
  - [Development](#development)
  - [Contributing](#contributing)
  - [License](#license)
  - [Links](#links)

## Key features

- **Device management** 🔧: list devices, select by UDID or name, boot/shutdown, kill IDB.
- **Input control** 👆: tap, swipe, type text, tap keys, tap buttons.
- **Screen utilities** 🖼️: capture screenshots, query screen size, get view description.
- **Image/coord scaling** 📐: optional scaling to a target viewport for consistent coordinates.
- **AskUI integration** 🤝: helper to add this server to AskUI `Caesr` Chat.

## Limitations

⚠️ Only iOS simulators are supported for UI control. Due to iOS security constraints, `idb` cannot interact with or automate the UI on real, physical devices. AskUI offers a solution for real-device UI automation—contact `support@askui.com` for more information.

## Requirements

- Runs on macOS only.
- Python >= 3.10
- Xcode with iOS Simulators installed and configured.
  - Verify simulators are visible:

    ```bash
    xcrun xctrace list devices
    ```

- [Facebook IDB companion](https://fbidb.io/docs/installation#idb-companion) (using `brew`):

  ```bash
  brew tap facebook/fb
  brew install idb idb-companion
  ```

## Install

```bash
pip install idb-mcp
```

## Quick start (CLI)

### Why MCP?

Using MCP lets your favorite AI tools connect to `idb-mcp` seamlessly. The client handles launching and communicating with the server, so you can ask for screenshots, taps, swipes, and more—without leaving your workflow. ✨

### Start MCP server

The package installs an `idb-mcp` command.

```bash
# Start MCP server over HTTP (default host/port managed by fastmcp)
idb-mcp start http

```

```bash
# Or start over SSE
idb-mcp start sse

```

```bash
# Optionally scale images/coordinates to a given target viewport (width height)
idb-mcp start http --target-screen-size 1280 800

```

```bash
# Discover available options
idb-mcp --help
idb-mcp start --help
```

### Add MCP server to AskUI `Caesr` Chat

To make it easier to use the MCP server in AskUI `Caesr` Chat, you can add the MCP server and custom assistant to the Chat.

```bash
# Adds the MCP server and custom assistant to AskUI `Caesr` Chat.
idb-mcp add-to-caesr
```

Or to a specific Chat directory:

```bash
idb-mcp add-to-caesr --chat-dir /path/to/askui/caesr/chat
```

## Programmatic usage (Python)

```python
from idb_mcp import IDBController, IOSDevice

# Initialize the IDB controller
controller = IDBController()
# Select the device by name
selected_device: IOSDevice = controller.select_device_by_name("iPhone 17 Pro Max")
# Boot the selected device
selected_device.boot()
# Get the current view description of the selected device
current_view_description: str = selected_device.get_current_view_description()
print(current_view_description)
# Shutdown the selected device
selected_device.shutdown()
```

## Add to your favorite tools

You can use `idb-mcp` in any MCP-compatible client (e.g., Cursor, Claude Desktop) by adding a server entry to your client's MCP config. The client will launch the server on demand.

Steps:

- Open your client's MCP configuration file (location varies by client).
- Add an entry named `askui-idb-mcp` that starts the server over SSE and sets a recommended target screen size.

Example configuration:

```json
{
  "mcpServers": {
    "askui-idb-mcp": {
      "command": "uvx",
      "args": ["idb-mcp", "start", "sse", "--target-screen-size", "1280", "800"]
    }
  }
}
```

Alternative (if `idb-mcp` is directly on your PATH without `uv`):

```json
{
  "mcpServers": {
    "askui-idb-mcp": {
      "command": "idb-mcp",
      "args": ["start", "sse", "--target-screen-size", "1280", "800"]
    }
  }
}
```

Notes:

- SSE works well for interactive automation. You can also use `http` if your client prefers it.
- The `--target-screen-size 1280 800` setting improves coordinate reliability, especially for models like Claude.

## Configuration

- **Target screen size** 📐: You can scale screenshots and coordinate inputs to a target viewport when starting the MCP server via CLI (`--target-screen-size W H`) or programmatically (`target_screen_size=(W, H)`).

## Troubleshooting

- **Cannot see devices** 🔍: Make sure you have an iOS simulator or device connected and running. Verify with:
  
  ```bash
  xcrun xctrace list devices
  ```

  Example output:

  ```text
  iPhone 17 Simulator (26.0) (32E2219C-ED40-452F-9A4D-XXXXXXX)
  iPhone 17 Pro Simulator (26.0) (764CCCB7-D84D-46EC-B62D-XXXXXXX)
  iPhone 17 Pro Max Simulator (26.0) (065382B5-56B4-4864-8174-XXXXXXX)
  ```

- **High-resolution screenshots with some LLMs** 🧠: Some LLM backends struggle to process very high-resolution images, resulting in poor coordinate detection or tapping errors. Use rescaling via `--target-screen-size` (or `target_screen_size` in Python) to downscale screenshots and coordinates. For Claude models, we recommend `1280 800`.

## Development

This repository uses PDM and Ruff for dev tooling.

```bash
# Install dev deps
pip install pdm
pdm install --with dev

# Lint / Format
pdm run lint-check
pdm run format-check
# Type check
pdm run type-check
```

## Contributing

Contributions are welcome! 🙌 Please open an issue or pull request on GitHub. Questions? Email us at `support@askui.com`.

## License

MIT License

## Links

- Homepage: `https://github.com/askui/idb-mcp`
- AskUI: `https://www.askui.com`
