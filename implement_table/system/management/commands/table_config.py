from django.core.management.base import BaseCommand

from  system import db_management



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            dest='path',
            default=False,
            help='the file name to execute',
        )

        parser.add_argument(
            '--name',
            dest='name',
            default=False,
            help='the file name to execute',
            required=True
        )

    def handle(self, *args, **options):
        if options.get('path'):
            db_management.insert_tables_config(name=options.get('name'), path=options.get('path'))
        else:
            db_management.insert_tables_config(name=options.get('name'))