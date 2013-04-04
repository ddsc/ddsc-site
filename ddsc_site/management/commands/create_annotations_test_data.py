from django.core.management.base import BaseCommand
from ddsc_site.models import Annotation

class Command(BaseCommand):
    args = '[nothing]'
    help = 'Create a set of test annotations.'

    def handle(self, *args, **options):
        Annotation.create_test_data()
