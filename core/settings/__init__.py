from __future__ import annotations

import os

SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE", __name__)

if SETTINGS_MODULE == __name__:
    DJANGO_ENV = os.getenv("DJANGO_ENV", "dev").lower()

    if DJANGO_ENV == "prod":
        from .prod import *  # noqa: F403
    elif DJANGO_ENV == "staging":
        from .staging import *  # noqa: F403
    elif DJANGO_ENV == "test":
        from .test import *  # noqa: F403
    else:
        from .dev import *  # noqa: F403
