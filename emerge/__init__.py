from dataclasses import dataclass

from emerge.core.client import Z0RPCClient as Client

fs = Client("0.0.0.0", "5558")

__all__ = ["fs", "dataclass"]
