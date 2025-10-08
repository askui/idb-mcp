import sys

if sys.platform != "darwin":
    raise OSError("idb-mcp is only supported on macOS (Darwin).")

from idb_mcp.idb import (
    DeviceButton,
    IDBController,
    IDBError,
    IOSDevice,
    IOSDeviceCollection,
)

__all__ = [
    "IDBController",
    "IOSDevice",
    "IOSDeviceCollection",
    "IDBError",
    "DeviceButton",
]
