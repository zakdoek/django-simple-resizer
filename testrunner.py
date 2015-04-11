#!/usr/bin/env python

import os
import sys
from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
        },
    },
    ROOT_URLCONF="resizer.urls",
    INSTALLED_APPS=(
        "resizer",
        "resizer.tests",
    ))

from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(pattern="*.py",
                             interactive=False)

failures = test_runner.run_tests(["resizer",])
if failures:
    sys.exit(failures)
