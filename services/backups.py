import os
import shutil
import zipfile
from datetime import datetime
from django.conf import settings

def create_system_backup():
    """
    Creates a backup of the database and media files.
    Saves it as a .zip file in the 'backups' directory.
    """
    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"nebras_backup_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Backup database (SQLite)
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            zipf.write(db_path, arcname=os.path.basename(db_path))
            
        # Backup media files
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, settings.BASE_DIR)
                    zipf.write(file_path, arcname=arcname)
                    
    return backup_path

def cleanup_old_backups(days=30):
    """Deletes backups older than X days."""
    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    if not os.path.exists(backup_dir):
        return
        
    now = datetime.now().timestamp()
    for file in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, file)
        if os.path.isfile(file_path):
            if os.path.getmtime(file_path) < now - (days * 86400):
                os.remove(file_path)
