from django.core.management.base import BaseCommand
from gallery.models import ClientGallery, ClientPhoto
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = 'Create demo client gallery with sample photos'

    def handle(self, *args, **options):
        # Create or get admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'is_superuser': True, 'is_staff': True, 'email': 'admin@example.com'}
        )
        if not admin_user.password:
            admin_user.set_password('admin123')
            admin_user.save()
        
        # Create demo gallery
        gallery, created = ClientGallery.objects.get_or_create(
            access_code='DEMO123',
            defaults={
                'client': admin_user,
                'title': 'Demo Wedding Photography Gallery',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f"✅ Created demo gallery with access code: DEMO123")
            
            # Create sample photos
            colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 200, 100), (200, 100, 255), (100, 200, 255)]
            captions = ['Wedding Ceremony', 'Bride Portrait', 'First Dance', 'Reception', 'Family Photo', 'Cake Cutting']
            
            for i, (color, caption) in enumerate(zip(colors, captions)):
                img = Image.new('RGB', (800, 600), color=color)
                buffer = BytesIO()
                img.save(buffer, format='JPEG')
                photo = ClientPhoto(
                    gallery=gallery,
                    caption=f'{caption} - Sample from demo gallery',
                    is_downloadable=True
                )
                photo.image.save(f'demo_photo_{i+1}.jpg', ContentFile(buffer.getvalue()), save=True)
                self.stdout.write(f"  - Created photo: {caption}")
        else:
            self.stdout.write(f"ℹ️ Demo gallery already exists with code: DEMO123")
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Demo Access Code: DEMO123"))
        self.stdout.write(self.style.SUCCESS(f"📍 URL: http://localhost:8000/client/gallery/"))