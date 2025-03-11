"""module that standardizes the configuration of a sandbox"""

import typing
from dataclasses import dataclass
from functools import lru_cache as cache

import psutil


_max_mem_limit = int(psutil.virtual_memory().total * 0.99)
_max_cpu_quota = int(psutil.cpu_count(logical=True) * 100000 * 0.99)


@dataclass
class SandboxConfig:
    mem_limit: str
    cpu_quota: int


readymade = {
       "tiny": SandboxConfig(mem_limit="128m", cpu_quota=25000),
      "small": SandboxConfig(mem_limit="512m", cpu_quota=50000),
     "medium": SandboxConfig(mem_limit="1g",   cpu_quota=75000),
      "large": SandboxConfig(mem_limit="2g",   cpu_quota=100000),
     "xlarge": SandboxConfig(mem_limit="4g",   cpu_quota=150000),
    "2xlarge": SandboxConfig(mem_limit="8g",   cpu_quota=200000),
    "4xlarge": SandboxConfig(mem_limit="16g",  cpu_quota=300000),
    "8xlarge": SandboxConfig(mem_limit="32g",  cpu_quota=400000),
}


def _mem_limit_to_int(mem_limit: str) -> int:
    if mem_limit.isdigit():
        return int(mem_limit)
    
    LUT = {
        "k": 1024, 
        "m": 1024**2,
        "g": 1024**3
    }

    value, measure = mem_limit[:-1], mem_limit[-1]

    return int(value) * LUT[measure]


@cache(maxsize=1)
def filtering_available() -> typing.Tuple[typing.Set[str], str]:
    """available sandbox config based on system resources"""
    available = []
    max_available_config = "null"

    for naming, config in readymade.items():
        if _mem_limit_to_int(config.mem_limit) > _max_mem_limit:
            break

        if config.cpu_quota > _max_cpu_quota:
            break
        
        available.append(naming)

    if available:
        max_available_config = available[-1]

    return set(available), max_available_config


available, max_available_config = filtering_available()
