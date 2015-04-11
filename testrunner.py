#!/usr/bin/env python

import os
import sys
from django.conf import settings
from django.conf import global_settings

settings.configure(
    DEBUG=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "PATH": os.path.join(os.path.dirname(__file__), "db.sqlite3"),
        },
    },
    ROOT_URLCONF="simple_resizer.urls",
    INSTALLED_APPS=(
        "simple_resizer",
        "simple_resizer.tests",
    ),
    # Suppress a warning from the checks system
    MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES,
)

from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(pattern="*.py",
                             interactive=False)

try:
    import django
    django.setup()
except AttributeError:
    print("Running tests in legacy mode!")

failures = test_runner.run_tests(["simple_resizer"])
if failures:
    sys.exit(failures)
