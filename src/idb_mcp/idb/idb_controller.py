from .idb_error import IDBError
from .idb_wrapper import IDBWrapper
from .ios_device import IOSDevice
from .ios_device_collection import IOSDeviceCollection


class IDBController:
    def __init__(self) -> None:
        self.idb_wrapper = IDBWrapper()
        self.selected_device_udid: str | None = None

    def select_device_by_udid(self, udid: str) -> IOSDevice:
        """Select a device by UDID."""
        device_collection = IOSDeviceCollection.build()
        selected_device = device_collection.get_device_by_udid(udid)
        if selected_device is None:
            raise IDBError(f"Device with UDID {udid} is not connected")
        self.selected_device_udid = selected_device.udid
        return selected_device

    def select_device_by_name(self, name: str) -> IOSDevice:
        """Select a device by name."""
        device_collection = IOSDeviceCollection.build()
        selected_device = device_collection.get_device_by_name(name)
        if selected_device is None:
            raise IDBError(f"Device with name {name} is not connected")
        self.selected_device_udid = selected_device.udid
        return selected_device

    def list_devices(self) -> list[IOSDevice]:
        """List all devices."""
        return IOSDeviceCollection.build().devices

    def idb_kill(self) -> None:
        """Kill the IDB server. Reset all state."""
        self.idb_wrapper.run_command(["kill"])

    def manually_connect_to_companion_by_tap(
        self, tcp_address: str, tcp_port: int
    ) -> None:
        """Manually connect to the companion by tapping on the device.
        Useful in case the device is hosted on a different machine than the one running the controller.
        IOS emulator are only supported on macOS.
        """
        self.idb_wrapper.run_command(["connect", tcp_address, f"{tcp_port}"])

    def get_selected_device(self) -> IOSDevice:
        """Get the selected device."""
        if self.selected_device_udid is None:
            raise IDBError("No device selected, Select a device first")
        return self.select_device_by_udid(self.selected_device_udid)
