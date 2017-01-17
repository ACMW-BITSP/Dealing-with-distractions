#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Use development platform if not set
    platform = os.getenv('DWD_PLATFORM', 'dev')

    if platform == 'dev':
        settings = 'dwd.settings.dev'
    elif platform == 'heroku':
        settings = 'dwd.settings.heroku'
    else:
        settings = 'dwd.settings.prod'

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
