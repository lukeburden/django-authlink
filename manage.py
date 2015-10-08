#!/usr/bin/env python
from django.core import management
import os


os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'
if __name__ == "__main__":
    management.execute_from_command_line()
