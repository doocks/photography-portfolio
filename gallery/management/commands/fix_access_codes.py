from django.core.management.base import BaseCommand
from gallery.models import ClientGallery

class Command(BaseCommand):
    help = 'Fix existing access codes to uppercase and ensure uniqueness'

    def handle(self, *args, **options):
        galleries = ClientGallery.objects.all()
        fixed_count = 0
        
        for gallery in galleries:
            old_code = gallery.access_code
            new_code = old_code.strip().upper()
            
            if old_code != new_code:
                # Check if new code already exists
                if ClientGallery.objects.filter(access_code=new_code).exclude(pk=gallery.pk).exists():
                    # Append random suffix
                    import uuid
                    new_code = f"{new_code}_{uuid.uuid4().hex[:4].upper()}"
                    self.stdout.write(f"⚠️ Conflict: {old_code} → {new_code}")
                
                gallery.access_code = new_code
                gallery.save()
                fixed_count += 1
                self.stdout.write(f"✓ Fixed: {old_code} → {new_code}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Fixed {fixed_count} access codes"))
        self.stdout.write("\n📋 Current galleries:")
        for gallery in ClientGallery.objects.filter(is_active=True):
            self.stdout.write(f"   • {gallery.title}: {gallery.access_code}")