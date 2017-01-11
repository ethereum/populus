import sys


if sys.version_info.major == 2:
    from .six_py2 import (
        queue,
    )
else:
    from .six_py3 import (  # noqa: #401
        queue,
    )
