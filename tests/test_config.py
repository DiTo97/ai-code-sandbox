import pytest

from codegen_sandbox.config import (
    _mem_limit_to_int, available, readymade, _max_mem_limit, _max_cpu_quota
)


def test_mem_limit_to_int():
    assert _mem_limit_to_int("1")  == 1024**0
    assert _mem_limit_to_int("1k") == 1024**1
    assert _mem_limit_to_int("1m") == 1024**2
    assert _mem_limit_to_int("1g") == 1024**3

    with pytest.raises(KeyError):
        _mem_limit_to_int("1t")


def test_available():
    for naming in available:
        config = readymade[naming]

        assert _mem_limit_to_int(config.mem_limit) < _max_mem_limit
        assert config.cpu_quota < _max_cpu_quota
