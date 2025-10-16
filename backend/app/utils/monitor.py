from __future__ import annotations

import psutil
from typing import Dict, Any, List


def collect_system_metrics() -> Dict[str, Any]:
    cpu_percent = psutil.cpu_percent(interval=0.1)
    virtual_mem = psutil.virtual_memory()
    mem_percent = virtual_mem.percent
    net = psutil.net_io_counters()
    processes: List[Dict[str, Any]] = []
    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        info = proc.info
        processes.append(
            {
                "pid": info.get("pid"),
                "name": info.get("name"),
                "cpu_percent": info.get("cpu_percent"),
                "memory_percent": info.get("memory_percent"),
            }
        )
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": mem_percent,
        "net_bytes_sent": getattr(net, "bytes_sent", 0),
        "net_bytes_recv": getattr(net, "bytes_recv", 0),
        "processes": processes,
    }
