from django.core.management.base import BaseCommand
from gallery.models import ClientGallery
import hashlib  # ← MAKE SURE THIS IS HERE

class Command(BaseCommand):
    help = 'Hash existing access codes for security'

    def handle(self, *args, **options):
        galleries = ClientGallery.objects.all()
        
        if not galleries.exists():
            self.stdout.write(self.style.WARNING("No galleries found to hash."))
            return
        
        hashed_count = 0
        for gallery in galleries:
            if gallery.access_code and not gallery.access_code_hash:
                gallery.access_code_hash = hashlib.sha256(gallery.access_code.encode()).hexdigest()
                gallery.save(update_fields=['access_code_hash'])
                hashed_count += 1
                self.stdout.write(f"✅ Hashed code for: {gallery.title} ({gallery.access_code})")
            elif gallery.access_code and gallery.access_code_hash:
                self.stdout.write(f"ℹ️ Already hashed: {gallery.title}")
            else:
                self.stdout.write(f"⚠️ No access code for: {gallery.title}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Hashed {hashed_count} access codes successfully!"))
        
        # Display all galleries
        self.stdout.write("\n📋 Current Galleries:")
        for gallery in ClientGallery.objects.filter(is_active=True):
            hash_preview = gallery.access_code_hash[:20] if gallery.access_code_hash else "None"
            self.stdout.write(f"   • {gallery.title} - Code: {gallery.access_code} (Hash: {hash_preview}...)")