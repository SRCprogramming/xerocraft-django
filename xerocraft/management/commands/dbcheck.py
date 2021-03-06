
# Standard

import unittest
import sys

# Third Party
from django.core.management.base import NoArgsCommand
from django.apps import apps
from django.core.exceptions import ValidationError

# Local


__author__ = 'adrian'


class Command(NoArgsCommand):

    help = "Runs validation for each model in the database."

    def handle_noargs(self, **options):
        suite = unittest.TestLoader().loadTestsFromTestCase(DbCheck)
        unittest.TextTestRunner().run(suite)


class DbCheck(unittest.TestCase):

    def test_models(self):

        count = 0
        problems = []

        for appname in ['tasks', 'books', 'inventory', 'members', 'xerocraft']:
            print(appname)
            app = apps.get_app_config(appname)
            for modelname, model in app.models.items():
                print("   {} ({}) ".format(modelname, model.objects.count()), end="")
                obj_count = 0
                for obj in model.objects.all():
                    try:
                        obj.full_clean()
                        if hasattr(obj, "dbcheck"): obj.dbcheck()
                        obj_count += 1
                        if obj_count % 100 == 0:
                            print(".", end="")
                            sys.stdout.flush()
                    except ValidationError as e:
                        print("E", end="")
                        problems.append("{} {} {}".format(obj.pk, obj, e))
                        count += 1
                        continue
                print("")

        if count > 0:
            print("DBCheck found the following issues:")
            for problem in problems:
                print("   "+problem)
            sys.stdout.flush()
