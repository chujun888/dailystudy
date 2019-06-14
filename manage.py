#!/usr/bin/env python
import os
import sys
# chujun88 123456
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freshstudy.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
