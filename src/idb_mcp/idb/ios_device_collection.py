from .idb_wrapper import IDBWrapper
from .ios_device import IOSDevice


class IOSDeviceCollection:
    def __init__(self, devices: list[IOSDevice] | None = None) -> None:
        self.devices: list[IOSDevice] = devices if devices is not None else []
        self._idb_wrapper = IDBWrapper()

    @classmethod
    def build(cls) -> "IOSDeviceCollection":
        """Create an IOSDeviceCollection from a list of JSON strings."""
        collection = cls()
        for json_str in collection._idb_wrapper.run_command(
            ["list-targets", "--json"]
        ).splitlines():
            collection.add_device(IOSDevice.from_json(json_str))
        return collection

    def add_device(self, device: IOSDevice) -> None:
        """Check if the device is already in the collection."""
        if device in self.devices:
            return
        """Add a device to the collection."""
        self.devices.append(device)

    def get_device_by_udid(self, udid: str) -> IOSDevice | None:
        """Get a device by UDID from the collection."""
        for device in self.devices:
            if device.udid == udid:
                return device
        return None

    def is_empty(self) -> bool:
        """Check if the collection is empty."""
        return len(self.devices) == 0

    def get_booted_devices(self) -> "IOSDeviceCollection":
        """Get all booted devices from the collection."""
        booted_devices = []
        for device in self.devices:
            if device.state == "Booted":
                booted_devices.append(device)
        return IOSDeviceCollection(booted_devices)

    def get_all_devices_with_companion(self) -> "IOSDeviceCollection":
        """Get all devices with a companion from the collection."""
        devices_with_companion = []
        for device in self.devices:
            if device.has_companion():
                devices_with_companion.append(device)
        return IOSDeviceCollection(devices_with_companion)

    def get_device_by_name(self, name: str) -> IOSDevice | None:
        """Get a device by name from the collection."""
        for device in self.devices:
            if device.name == name:
                return device
        return None

    def includes_device(self, device: IOSDevice) -> bool:
        """Check if the collection includes a device."""
        return device in self.devices
