import io
import json
import platform

import mcp
from fastmcp import FastMCP
from fastmcp.server.server import Transport
from fastmcp.utilities.types import Image as FastMcpImage
from PIL import Image

from idb_mcp.idb import DeviceButton, IDBController
from idb_mcp.utils import scale_coordinates, scale_image_to_fit


class MCPServerHandler:
    """Handler for the MCP server."""

    def __init__(self) -> None:
        self.controller = IDBController()
        self.target_screen_size: tuple[int, int] | None = None

    def set_target_screen_size(self, target_screen_size: tuple[int, int]) -> None:
        """Set the target screen size."""
        self.target_screen_size = target_screen_size

    def image_handler(self, image: Image.Image) -> Image.Image:
        """Scale image to the target screen size."""
        if self.target_screen_size is not None:
            image = scale_image_to_fit(image, self.target_screen_size)
        return image

    def coordinates_handler(self, coordinates: tuple[int, int]) -> tuple[int, int]:
        """Scale coordinates to the target screen size."""
        if self.target_screen_size is not None:
            coordinates = scale_coordinates(
                coordinates=coordinates,
                target_size=self.target_screen_size,
                original_size=self.controller.get_selected_device().get_screen_size(),
                inverse=True,
            )
        return coordinates


app = FastMCP("AskUI IDB MCP Server")
mcp_server_handler = MCPServerHandler()


@app.tool()
def ios_list_devices() -> str:
    """List available iOS devices (simulators and devices). that can be selected and used for actions."""
    devices = mcp_server_handler.controller.list_devices()
    if len(devices) == 0:
        return "No devices connected"
    device_list = ", ".join([str(device) for device in devices])
    return f"devices target list: [{device_list}]"


@app.tool()
def ios_select_device_by_udid(udid: str) -> str:
    """
    Select a device by UDID, to be used for actions.

    Args:
        udid (str): The UDID of the device to select.
    """
    device = mcp_server_handler.controller.select_device_by_udid(udid)
    return f"Selected device: {device}"


@app.tool()
def ios_select_device_by_name(name: str) -> str:
    """
    Select a device by name, to be used for actions.

    Args:
        name (str): The name of the device to select.
    """
    device = mcp_server_handler.controller.select_device_by_name(name)
    return f"Selected device: {device}"


@app.tool()
def ios_idb_kill() -> str:
    """Kill the IDB server and reset state. Useful in case of persistent issues."""
    mcp_server_handler.controller.idb_kill()
    return "IDB server killed"


@app.tool()
def ios_get_selected_device() -> str:
    """Get the currently selected device."""
    device = mcp_server_handler.controller.get_selected_device()
    return f"the currently selected device is: {str(device)}"


@app.tool()
def ios_manually_connect_to_companion_by_tap(tcp_address: str, tcp_port: int) -> str:
    """
    Manually connect to IDB companion by tapping the device.
    In case the device is hosted on a different machine than the one running the controller mcp

    Args:
        tcp_address (str): The address of the TCP server.
        tcp_port (int): The port of the TCP server.
    """
    mcp_server_handler.controller.manually_connect_to_companion_by_tap(
        tcp_address, tcp_port
    )
    return f"Connected to IDB companion on {tcp_address}:{tcp_port}"


@app.tool()
def ios_boot_device() -> str:
    """Boot the selected device."""
    mcp_server_handler.controller.get_selected_device().boot()
    return "Booted the selected device"


@app.tool()
def ios_shutdown_device() -> str:
    """Shutdown the selected device."""
    mcp_server_handler.controller.get_selected_device().shutdown()
    return "Shutdown the selected device"


@app.tool()
def ios_type_text(text: str) -> str:
    """
    Type text on the selected device.

    Args:
        text (str): The text to type.
    """
    mcp_server_handler.controller.get_selected_device().type_text(text)
    return "Typed text on the selected device"


@app.tool()
def ios_tap_with_viewport_coordinates(
    x: int, y: int, duration_in_milliseconds: int = 1
) -> str:
    """
    Tap on the selected device.
    The coordinates are in the viewport coordinate system.
    Use this tool, if the coordinates are not extracted from the screen screenshot but from the device.

    Args:
        x (int): The x coordinate of the tap in viewport coordinates.
        y (int): The y coordinate of the tap in viewport coordinates.
        duration_in_milliseconds (int): The duration of the tap in milliseconds.
    """
    mcp_server_handler.controller.get_selected_device().tap(
        x, y, duration_in_milliseconds
    )
    return f"Tapped at {x}, {y} for {duration_in_milliseconds} milliseconds"


@app.tool()
def ios_tap_with_screen_coordinates(
    x: int, y: int, duration_in_milliseconds: int = 1
) -> str:
    """
    Tap on the selected device.
    The coordinates are in the screen coordinate system.
    Use this tool, if the coordinates are extracted from the screen screenshot.

    Args:
        x (int): The x coordinate of the tap in screen coordinates.
        y (int): The y coordinate of the tap in screen coordinates.
        duration_in_milliseconds (int): The duration of the tap in milliseconds.
    """
    (scaled_x, scaled_y) = mcp_server_handler.coordinates_handler((x, y))
    selected_device = mcp_server_handler.controller.get_selected_device()
    scale_factor = selected_device.get_scale_factor()
    x = int(scaled_x * scale_factor)
    y = int(scaled_y * scale_factor)
    selected_device.tap(x, y, duration_in_milliseconds)
    return f"Tapped at {x}, {y} for {duration_in_milliseconds} milliseconds"


@app.tool()
def ios_swipe_with_screen_coordinates(
    x1: int, y1: int, x2: int, y2: int, duration_in_milliseconds: int = 1
) -> str:
    """
    Swipes from the specified start point to the end.
    The coordinates are in the screen coordinate system.
    Must be used, if the coordinates are extracted from the screen screenshot.

    Args:
        x1 (int): The x coordinate of the start point in screen coordinates.
        y1 (int): The y coordinate of the start point in screen coordinates.
        x2 (int): The x coordinate of the end point in screen coordinates.
        y2 (int): The y coordinate of the end point in screen coordinates.
        duration_in_milliseconds (int): The duration of the swipe in milliseconds.
    """
    selected_device = mcp_server_handler.controller.get_selected_device()
    (x1, y1) = mcp_server_handler.coordinates_handler((x1, y1))
    (x2, y2) = mcp_server_handler.coordinates_handler((x2, y2))
    scale_factor = selected_device.get_scale_factor()
    x1 = int(x1 * scale_factor)
    y1 = int(y1 * scale_factor)
    x2 = int(x2 * scale_factor)
    y2 = int(y2 * scale_factor)
    mcp_server_handler.controller.get_selected_device().swipe(
        x1, y1, x2, y2, duration_in_milliseconds
    )
    return f"Swiped from {x1}, {y1} to {x2}, {y2} for {duration_in_milliseconds} milliseconds"


@app.tool()
def ios_swipe_with_viewport_coordinates(
    x1: int, y1: int, x2: int, y2: int, duration_in_milliseconds: int = 1
) -> str:
    """
    Swipes from the specified start point to the end.
    The coordinates are in the viewport coordinate system.
    Must be used, if the coordinates are not extracted from the screen screenshot but from the device.

    Args:
        x1 (int): The x coordinate of the start point in viewport coordinates.
        y1 (int): The y coordinate of the start point in viewport coordinates.
        x2 (int): The x coordinate of the end point in viewport coordinates.
        y2 (int): The y coordinate of the end point in viewport coordinates.
        duration_in_milliseconds (int): The duration of the swipe in milliseconds.
    """
    mcp_server_handler.controller.get_selected_device().swipe(
        x1, y1, x2, y2, duration_in_milliseconds
    )
    return f"Swiped from {x1}, {y1} to {x2}, {y2} for {duration_in_milliseconds} milliseconds"


@app.tool()
def ios_tap_button(
    button: DeviceButton,
    duration_in_milliseconds: int = 1,
) -> str:
    """Tap a button on the selected device."""
    mcp_server_handler.controller.get_selected_device().tap_button(
        button, duration_in_milliseconds
    )
    return f"Tapped the {button} button for {duration_in_milliseconds} milliseconds"


@app.tool()
def ios_tap_key(key_code: int, duration_in_milliseconds: int = 1) -> str:
    """
    Tap a key on the selected device.

    Args:
        key_code (int): The key code of the key to tap.
        duration_in_milliseconds (int): The duration of the tap in milliseconds.
    """
    mcp_server_handler.controller.get_selected_device().tap_key(
        key_code, duration_in_milliseconds
    )
    return f"Tapped the {key_code} key for {duration_in_milliseconds} milliseconds"


@app.tool()
def ios_tap_key_sequence(
    key_sequence: list[int], duration_in_milliseconds: int = 1
) -> str:
    """
    Inputs multiple key events sequentially.

    Args:
        key_sequence (list[int]): The sequence of key codes to tap.
        duration_in_milliseconds (int): The duration of the tap in milliseconds.
    """
    mcp_server_handler.controller.get_selected_device().tap_key_sequence(
        key_sequence, duration_in_milliseconds
    )
    return f"Tapped the {key_sequence} key sequence for {duration_in_milliseconds} milliseconds"


@app.tool()
def ios_screenshot() -> mcp.types.ImageContent:
    """
    Take a screenshot of the selected device.
    """
    selected_device = mcp_server_handler.controller.get_selected_device()
    image = selected_device.screenshot()
    image = mcp_server_handler.image_handler(image)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return FastMcpImage(data=img_byte_arr.getvalue(), format="png").to_image_content()


@app.tool()
def ios_get_screen_size() -> tuple[int, int]:
    """Get the screen size of the selected device."""
    return mcp_server_handler.controller.get_selected_device().get_screen_size()


@app.tool()
def ios_get_current_view_description() -> str:
    """
    Get the current view description of the selected device.
    Returns a JSON formatted list of all the elements currently on screen,
        including their bounds and accessibility information.
    """
    return mcp_server_handler.controller.get_selected_device().get_current_view_description()


@app.tool()
def ios_get_host_machine_platform() -> str:
    """Get the platform of the host machine."""
    return f"Host machine platform: {platform.platform()}"


@app.tool()
def ios_save_screenshot_to_disk(absolute_image_path: str) -> str:
    """Save a screenshot of the selected device to a file at the given path.

    The path must end with .png. Parent directories are created if needed.
    Fails if the file already exists.
    """
    mcp_server_handler.controller.get_selected_device().save_screenshot_to_disk(
        absolute_image_path
    )
    return f"Saved screenshot to {absolute_image_path}"


@app.tool()
def ios_open_url(url: str) -> str:
    """
    Open a URL on the selected device (e.g. https://example.com).

    Args:
        url (str): The URL to open.
    """
    mcp_server_handler.controller.get_selected_device().open_url(url)
    return f"Opened URL: {url}"


@app.tool()
def ios_set_location(latitude: float, longitude: float) -> str:
    """
    Set the simulator's GPS location. Only supported on simulators.

    Args:
        latitude (float): The latitude.
        longitude (float): The longitude.
    """
    mcp_server_handler.controller.get_selected_device().set_location(
        latitude, longitude
    )
    return f"Set location to ({latitude}, {longitude})"


@app.tool()
def ios_install_app(app_path: str) -> str:
    """
    Install an app on the selected device from a .app, .ipa, or .xcarchive path.

    Args:
        app_path (str): Absolute path to the app bundle (.app), .ipa, or .xcarchive.
    """
    mcp_server_handler.controller.get_selected_device().install_app(app_path)
    return f"Installed app from {app_path}"


@app.tool()
def ios_uninstall_app(bundle_id: str) -> str:
    """
    Uninstall an app from the selected device by bundle id.

    Args:
        bundle_id (str): The bundle identifier of the app to uninstall.
    """
    mcp_server_handler.controller.get_selected_device().uninstall_app(bundle_id)
    return f"Uninstalled app with bundle id: {bundle_id}"


@app.tool()
def ios_launch_app(bundle_id: str, args: list[str] | None = None) -> str:
    """
    Launch an app on the selected device by bundle id with optional arguments.

    Args:
        bundle_id (str): The bundle identifier of the app to launch.
        args (list[str] | None): Optional list of arguments to pass to the app.
    """
    output = mcp_server_handler.controller.get_selected_device().launch_app(
        bundle_id, args
    )
    return f"Launched app {bundle_id}. Output: {output}"


@app.tool()
def ios_terminate_app(bundle_id: str) -> str:
    """
    Terminate a running app on the selected device by bundle id.

    Args:
        bundle_id (str): The bundle identifier of the app to terminate.
    """
    mcp_server_handler.controller.get_selected_device().terminate_app(bundle_id)
    return f"Terminated app with bundle id: {bundle_id}"


@app.tool()
def ios_list_installed_apps() -> str:
    """List installed apps on the selected device. Returns JSON lines (one app per line)."""
    apps = mcp_server_handler.controller.get_selected_device().list_installed_apps()
    lines = [json.dumps(app) for app in apps]
    return "\n".join(lines) if lines else "No installed apps"


@app.tool()
def ios_approve_permissions(bundle_id: str, services: list[str]) -> str:
    """
    Approve permissions for an app. Only 'photos', 'location', 'camera', 'microphone' are supported.

    Args:
        bundle_id (str): The bundle identifier of the app.
        services (list[str]): List of services to approve, e.g. ['photos', 'location', 'camera', 'microphone'].
    """
    mcp_server_handler.controller.get_selected_device().approve_permissions(
        bundle_id, services
    )
    return f"Approved permissions {services} for app {bundle_id}"


def start_server(
    mode: Transport, port: int, target_screen_size: tuple[int, int] | None = None
) -> None:
    """
    Start the MCP server In either http or sse mode.
    If target_screen_size is provided, the images and coordinates will be scaled to the target screen size.
    If not provided, the images and coordinates will not be scaled.

    Args:
        mode (Transport): The mode to serve the MCP server in.
        target_screen_size (Optional[Tuple[int, int]]): The target screen size to scale the images and coordinates to.
    """
    mcp_server_handler.target_screen_size = target_screen_size
    if mode not in ["stdio", "http", "sse"]:
        raise ValueError(f"Invalid mode: {mode}")
    if mode == "stdio":
        app.run(mode, show_banner=False)
    else:
        print(f"Starting MCP server in {mode} mode on port {port}")
        app.run(mode, port=port)
