from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Perform a health check'

    def handle(self, *args, **kwargs):
        db_conn = connections['default']
        try:
            db_conn.cursor()
            self.stdout.write(self.style.SUCCESS('Health check passed'))
        except OperationalError:
            self.stdout.write(self.style.ERROR('Database is unavailable'))
            exit(1)
