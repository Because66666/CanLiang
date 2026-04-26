"""非 Windows 环境下的 winreg 兼容桩。"""

HKEY_LOCAL_MACHINE = object()
HKEY_CLASSES_ROOT = object()


class _DummyKey:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def OpenKey(*args, **kwargs):  # pragma: no cover
    return _DummyKey()


def QueryInfoKey(*args, **kwargs):  # pragma: no cover
    return (0, 0, 0)


def EnumKey(*args, **kwargs):  # pragma: no cover
    raise OSError('winreg is unavailable on this platform')


def QueryValueEx(*args, **kwargs):  # pragma: no cover
    raise OSError('winreg is unavailable on this platform')


def CloseKey(*args, **kwargs):  # pragma: no cover
    return None
