import json
import string
import tempfile
from enum import Enum

from PIL import Image

from .idb_error import IDBError
from .idb_wrapper import IDBWrapper


class DeviceButton(str, Enum):
    APPLE_PAY = "APPLE_PAY"
    HOME = "HOME"
    LOCK = "LOCK"
    POWER = "POWER"
    SIDE_BUTTON = "SIDE_BUTTON"
    SIRI = "SIRI"


class IOSDevice:
    """A class representing an iOS device."""

    def __init__(
        self,
        udid: str,
        name: str,
        state: str,
        device_type: str,
        os_version: str,
        architecture: str,
        companion: str | None = None,
    ) -> None:
        self.udid = udid
        self.name = name
        self.state = state
        self.device_type = device_type
        self.os_version = os_version
        self.architecture = architecture
        self.companion = companion
        self._idb_wrapper = IDBWrapper()
        self.screen_size: tuple[int, int] | None = None
        self.scale_factor: float | None = (
            None  # ViewPort Resolution / Device Resolution
        )

    def __str__(self) -> str:
        """Return a string representation of the device."""
        return f"UDID: {self.udid}, Name: {self.name}, State: {self.state}, Type: {self.device_type}, OS Version: {self.os_version}, Architecture: {self.architecture}"

    def __eq__(self, other: object) -> bool:
        """Check if the device is equal to another device."""
        if not isinstance(other, IOSDevice):
            return False
        return (
            self.udid == other.udid
            and self.name == other.name
            and self.state == other.state
            and self.device_type == other.device_type
            and self.os_version == other.os_version
            and self.architecture == other.architecture
            and self.companion == other.companion
        )

    @classmethod
    def from_json(cls, json_str: str) -> "IOSDevice":
        """Create an IOSDevice from a JSON string."""
        data = json.loads(json_str)
        return cls(
            udid=data["udid"],
            name=data["name"],
            state=data["state"],
            device_type=data["type"],
            os_version=data["os_version"],
            architecture=data["architecture"],
            companion=data.get("companion"),
        )

    def is_booted(self) -> bool:
        """Check if the device is booted."""
        return self.state == "Booted"

    def has_companion(self) -> bool:
        """Check if the device has a companion."""
        return self.companion is not None

    def run_command_on_device(self, command: list[str]) -> str:
        """Run a command on the device."""
        return self._idb_wrapper.run_command(command + ["--udid", self.udid])

    def boot(self) -> None:
        """Boot the device."""
        self.__assert_is_simulator("Boot")

        self.run_command_on_device(["boot"])
        self.state = "Booted"

    def shutdown(self) -> None:
        """Disconnect from the device."""
        self.__assert_is_simulator("Shutdown")

        self.run_command_on_device(["shutdown"])
        self.state = "shutdown"

    def type_text(self, text: str) -> None:
        """Type text on the device."""
        self.__assert_booted_simulator("Type text")

        if any(c not in string.printable or ord(c) < 32 or ord(c) > 126 for c in text):
            error_msg_nonprintable: str = (
                f"Text contains non-printable characters: {text} "
                + "or special characters which are not supported by the device"
            )
            raise RuntimeError(error_msg_nonprintable)

        self.run_command_on_device(["ui", "text", f"{text}"])

    def tap(self, x: int, y: int, duration_in_milliseconds: int = 1) -> None:
        """Tap on the device."""
        (viewport_size_width, viewport_size_height) = self.get_viewport_size()
        if x > viewport_size_width or y > viewport_size_height:
            raise IDBError(
                f"Coordinates {x}, {y} are out of the viewport size {viewport_size_width}, {viewport_size_height}"
            )

        self.__assert_booted_simulator("Tap")
        duration_in_seconds = duration_in_milliseconds / 1000
        self.run_command_on_device(
            ["ui", "tap", f"{x}", f"{y}", "--duration", f"{duration_in_seconds}"]
        )

    def swipe(
        self, x1: int, y1: int, x2: int, y2: int, duration_in_milliseconds: int = 1
    ) -> None:
        """Swipe on the device."""
        self.__assert_booted_simulator("Swipe")

        (viewport_size_width, viewport_size_height) = self.get_viewport_size()
        if x1 > viewport_size_width or x2 > viewport_size_width:
            raise IDBError(
                f"X coordinate {x1} or {x2} is out of the viewport size {viewport_size_width}"
            )
        if y1 > viewport_size_height or y2 > viewport_size_height:
            raise IDBError(
                f"Y coordinate {y1} or {y2} is out of the viewport size {viewport_size_height}"
            )

        duration_in_seconds = duration_in_milliseconds / 1000
        self.run_command_on_device(
            [
                "ui",
                "swipe",
                f"{x1}",
                f"{y1}",
                f"{x2}",
                f"{y2}",
                "--duration",
                f"{duration_in_seconds}",
            ]
        )

    def tap_button(
        self, button: DeviceButton, duration_in_milliseconds: int = 1
    ) -> None:
        """Press a button on the device."""
        self.__assert_booted_simulator("Tap button")

        if button not in DeviceButton:
            raise IDBError(
                f"Invalid button '{button.value}'. Only 'APPLE_PAY', 'HOME', 'LOCK', 'POWER', 'SIDE_BUTTON', 'SIRI' are supported"
            )

        duration_in_seconds = duration_in_milliseconds / 1000
        self.run_command_on_device(
            ["ui", "button", button, "--duration", f"{duration_in_seconds}"]
        )

    def tap_key(self, key_code: int, duration_in_milliseconds: int = 1) -> None:
        """Tap a key on the device."""
        self.__assert_booted_simulator("Tap key")

        duration_in_seconds = duration_in_milliseconds / 1000
        self.run_command_on_device(
            ["ui", "key", f"{key_code}", "--duration", f"{duration_in_seconds}"]
        )

    def tap_key_sequence(
        self, key_sequence: list[int], duration_in_milliseconds: int = 1
    ) -> None:
        """Tap a key sequence on the device."""
        self.__assert_booted_simulator("Tap key sequence")

        if len(key_sequence) < 2:
            raise IDBError("Key sequence must contain at least 2 keys")

        key_sequence_str = " ".join(map(str, key_sequence))
        duration_in_seconds = duration_in_milliseconds / 1000
        self.run_command_on_device(
            [
                "ui",
                "key-sequence ",
                f"{key_sequence_str}",
                "--duration",
                f"{duration_in_seconds}",
            ]
        )

    def get_current_view_description(self) -> str:
        """Get the description of the current view."""
        self._assert_is_booted()
        return self.run_command_on_device(["ui", "describe-all", "--json"])

    def screenshot(self) -> Image.Image:
        """Take a screenshot of the device."""
        self._assert_is_booted()

        with tempfile.NamedTemporaryFile(
            delete=True, suffix=".png", prefix="temp_ios_screenshot_"
        ) as temp_file:
            self.run_command_on_device(["screenshot", temp_file.name])
            return Image.open(temp_file.name)

    def connect_to_idb_companion(self) -> None:
        """Connect to the device to IDB Companion."""
        self._idb_wrapper.run_command(["connect", self.udid])
        self.state = "Connected"

    def disconnect_from_idb_companion(self) -> None:
        """Disconnect from the device."""
        if not self.has_companion():
            raise IDBError("Device does not have a companion, cannot disconnect")
        self._idb_wrapper.run_command(["disconnect", self.udid])
        self.state = "Disconnected"

    def open_url(self, url: str) -> None:
        """Open a URL on the device."""
        self._assert_is_booted()
        self.run_command_on_device(["open", url])

    def set_location(self, latitude: float, longitude: float) -> None:
        """Set the simulator's GPS location."""
        self.__assert_booted_simulator("Set location")
        self.run_command_on_device(["set-location", f"{latitude}", f"{longitude}"])

    def install_app(self, app_path: str) -> None:
        """Install an application from a .app, .ipa, or .xcarchive path."""
        self._assert_is_booted()
        self.run_command_on_device(["install", app_path])

    def uninstall_app(self, bundle_id: str) -> None:
        """Uninstall an application by bundle id."""
        self._assert_is_booted()
        self.run_command_on_device(["uninstall", bundle_id])

    def launch_app(self, bundle_id: str, args: list[str] | None = None) -> str:
        """Launch an app by bundle id with optional arguments. Returns launch output."""
        self._assert_is_booted()
        cmd = ["launch", bundle_id]
        if args:
            cmd += ["--args"] + args
        return self.run_command_on_device(cmd)

    def terminate_app(self, bundle_id: str) -> None:
        """Terminate a running app by bundle id."""
        self._assert_is_booted()
        self.run_command_on_device(["terminate", bundle_id])

    def list_installed_apps(self) -> list[dict]:
        """List installed apps; returns a list of JSON objects."""
        self._assert_is_booted()
        output = self.run_command_on_device(["list-apps", "--json"])
        apps: list[dict] = []
        for line in output.splitlines():
            if not line.strip():
                continue
            try:
                apps.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return apps

    def approve_permissions(self, bundle_id: str, services: list[str]) -> None:
        """Approve permissions for a given app. Services examples: 'photos', 'location', etc."""
        self._assert_is_booted()

        for service in services:
            if service not in ["photos", "location", "camera", "microphone"]:
                raise IDBError(
                    f"Invalid service '{service}'. Only 'photos', 'location', 'camera', 'microphone' are supported"
                )
        self.run_command_on_device(["approve", bundle_id] + services)

    def get_screen_size(self) -> tuple[int, int]:
        """Get the screen size of the device."""
        if self.screen_size is None:
            image = self.screenshot()
            self.screen_size = image.size
        return self.screen_size

    def get_viewport_size(self) -> tuple[int, int]:
        """Get the viewport size of the device."""
        try:
            json_string = self.get_current_view_description()
            json_data = json.loads(json_string)
            viewport_size = json_data[0]["frame"]
            return viewport_size["width"], viewport_size["height"]
        except json.JSONDecodeError as e:
            raise IDBError(f"Failed to get viewport size: Error {e}") from e

    def get_scale_factor(self) -> float:
        """Get the scale factor of the device. The scale factor is the ratio of the viewport size to the screen size."""
        if self.scale_factor is None:
            device_resolution = self.get_screen_size()
            viewport_resolution = self.get_viewport_size()
            self.scale_factor = viewport_resolution[0] / device_resolution[0]
        return self.scale_factor

    def _assert_is_booted(self) -> None:
        """Assert that the device is booted."""
        if not self.is_booted():
            raise IDBError(
                f"Device {self.name} with UDID {self.udid} is not booted, boot the device first"
            )

    def __assert_is_simulator(self, action_name: str) -> None:
        """Assert that the device is a simulator."""
        if self.device_type != "simulator":
            raise IDBError(
                f"Device {self.name} with UDID {self.udid} is not a simulator, {action_name} is only supported on simulator devices"
            )

    def __assert_booted_simulator(self, action_name: str) -> None:
        """Assert that the device is a booted simulator."""
        self._assert_is_booted()
        self.__assert_is_simulator(action_name)
