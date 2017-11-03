from django.core.management.base import BaseCommand

from  implement_table.system import db_management


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        # Named (optional) arguments
        parser.add_argument(
            '--file',
            dest='file',
            default=False,
            help='the file name to execute',
        )

    def handle(self, *args, **options):
        db_management.reset_collection("billing_config")
        if options.get('file'):
            db_management.init_general_config(options.get('file'))
        else:
            db_management.init_general_config()
