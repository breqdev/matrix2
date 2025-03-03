from dataclasses import dataclass
from functools import cache
import subprocess


@dataclass
class NetworkInfo:
    ssid: str
    ip_addr: str


def get_ip_addr() -> str:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    addr = s.getsockname()[0]
    s.close()
    return addr


def get_ssid() -> str:
    result = subprocess.run(["iw", "dev", "wlan0", "link"], capture_output=True)
    lines = result.stdout.decode().splitlines()
    for line in lines:
        if line.strip().startswith("SSID: "):
            return line.strip().removeprefix("SSID: ")
    raise ValueError("command failed")


@cache
def get_network_info() -> NetworkInfo:
    return NetworkInfo(
        ssid=get_ssid(),
        ip_addr=get_ip_addr(),
    )
