from django.core.management.base import BaseCommand
from services.backups import create_system_backup, cleanup_old_backups

class Command(BaseCommand):
    help = 'Creates a zip backup of the database and media files'

    def add_arguments(self, parser):
        parser.add_argument('--cleanup', action='store_true', help='Clean up backups older than 30 days')

    def handle(self, *args, **options):
        self.stdout.write("Starting system backup...")
        path = create_system_backup()
        self.stdout.write(self.style.SUCCESS(f"Backup created successfully: {path}"))
        
        if options['cleanup']:
            self.stdout.write("Cleaning up old backups...")
            cleanup_old_backups()
            self.stdout.write(self.style.SUCCESS("Cleanup completed."))
