from django.core.management.base import BaseCommand
from gallery.models import Category, Photograph, Package, Testimonial, BlogPost, SiteSetting
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = 'Seed gallery with complete sample data'

    def handle(self, *args, **options):
        # Clear existing data
        Category.objects.all().delete()
        Photograph.objects.all().delete()
        Package.objects.all().delete()
        Testimonial.objects.all().delete()
        BlogPost.objects.all().delete()
        SiteSetting.objects.all().delete()

        # Create Categories
        categories = [
            {'name': 'Wedding', 'slug': 'wedding', 'icon': 'fa-heart', 'order': 1},
            {'name': 'Portrait', 'slug': 'portrait', 'icon': 'fa-user', 'order': 2},
            {'name': 'Nature', 'slug': 'nature', 'icon': 'fa-tree', 'order': 3},
            {'name': 'Events', 'slug': 'events', 'icon': 'fa-calendar', 'order': 4},
        ]
        
        category_objs = {}
        for cat in categories:
            category_objs[cat['name']] = Category.objects.create(**cat)

        # Create sample photos (with generated placeholder images)
        photos_data = [
            ('Elegant Wedding Ceremony', 'Beautiful outdoor wedding in the countryside', 'Wedding', True, 1),
            ('Romantic Bride Portrait', 'Stunning bridal portrait session', 'Portrait', True, 2),
            ('Mountain Sunset Magic', 'Breathtaking sunset over Rocky Mountains', 'Nature', True, 3),
            ('Corporate Gala Event', 'Annual awards ceremony coverage', 'Events', True, 4),
            ('Wedding Reception Dance', 'First dance captured beautifully', 'Wedding', False, 5),
            ('Family Outdoor Portrait', 'Natural family photos in golden hour', 'Portrait', False, 6),
            ('Forest Morning Fog', 'Mysterious atmosphere in the woods', 'Nature', False, 7),
            ('Music Festival Energy', 'Live concert photography', 'Events', False, 8),
        ]

        for idx, (title, desc, cat_name, featured, order) in enumerate(photos_data):
            photo = Photograph(
                title=title,
                description=desc,
                category=category_objs[cat_name],
                featured=featured,
                order=order,
                location='Sample Location',
                camera_settings=f'f/2.8, 1/{200 + idx*50}s, ISO {100 + idx*50}'
            )
            # Generate placeholder image
            img = Image.new('RGB', (800, 600), color=(int(200 + idx*20), int(100 + idx*30), int(150 + idx*10)))
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            photo.image.save(f'photo_{order}.jpg', ContentFile(buffer.getvalue()), save=True)
            self.stdout.write(f"Created photo: {title}")

        # Create Packages
        # In seed_gallery.py
        packages = [
            {
                'name': 'Basic', 'slug': 'basic', 'price': 499,
                'description': 'Perfect for small events and portrait sessions',
                'features': '4 hours coverage,50 edited photos,Online gallery,Print rights',
                'hours': 4, 'edited_photos': 50, 'popular': False, 'order': 1
            },
            {
                'name': 'Standard', 'slug': 'standard', 'price': 899,
                'description': 'Most popular package for weddings and events',
                'features': '8 hours coverage,150 edited photos,Online gallery,Print rights,USB drive',
                'hours': 8, 'edited_photos': 150, 'popular': True, 'order': 2
            },
            {
                'name': 'Premium', 'slug': 'premium', 'price': 1499,
                'description': 'Full coverage with premium inclusions',
                'features': '12 hours coverage,300 edited photos,Online gallery,Print rights,USB drive,Photo album',
                'hours': 12, 'edited_photos': 300, 'popular': False, 'order': 3
            },
        ]
        
        for pkg in packages:
            Package.objects.create(**pkg)
            self.stdout.write(f"Created package: {pkg['name']}")

        # Create Testimonials
        testimonials = [
            {'client_name': 'Sarah & John', 'review': 'Absolutely incredible photographer! Captured every special moment perfectly. Professional, creative, and so easy to work with.', 'rating': 5, 'event_type': 'Wedding', 'featured': True},
            {'client_name': 'Michael Chen', 'review': 'Best portrait photographer in the city! The photos came out amazing and the turnaround time was super fast.', 'rating': 5, 'event_type': 'Portrait', 'featured': True},
            {'client_name': 'Emily Davis', 'review': 'Booked for our corporate event and was blown away by the quality. Highly recommend!', 'rating': 5, 'event_type': 'Event', 'featured': True},
            {'client_name': 'David & Lisa Kim', 'review': 'Very professional and talented. The photos exceeded our expectations. Will book again!', 'rating': 5, 'event_type': 'Wedding', 'featured': False},
        ]
        
        for test in testimonials:
            Testimonial.objects.create(**test)
            self.stdout.write(f"Created testimonial: {test['client_name']}")

        # Create Blog Posts
        blog_posts = [
            {
                'title': '10 Tips for Perfect Wedding Photography', 'slug': 'wedding-photography-tips',
                'excerpt': 'Essential tips to make your wedding photos unforgettable. Learn from professional experience.',
                'content': 'Detailed guide about wedding photography tips including timing, lighting, and posing...',
                'category': 'Wedding', 'tags': 'wedding, tips, photography', 'published': True
            },
            {
                'title': 'How to Pose for Natural Portraits', 'slug': 'natural-portrait-posing',
                'excerpt': 'Learn how to look your best in photos with these simple posing techniques.',
                'content': 'Complete guide to natural portrait posing including body positioning, facial expressions, and more...',
                'category': 'Portrait', 'tags': 'portrait, posing, tips', 'published': True
            },
            {
                'title': 'The Best Time for Outdoor Photography', 'slug': 'golden-hour-photography',
                'excerpt': 'Why golden hour is every photographer\'s favorite time of day.',
                'content': 'Explanation of golden hour and how to use it effectively for stunning outdoor photos...',
                'category': 'Nature', 'tags': 'golden hour, nature, lighting', 'published': True
            },
        ]
        
        for post in blog_posts:
            BlogPost.objects.create(**post)
            self.stdout.write(f"Created blog: {post['title']}")

        # Create Site Settings
        SiteSetting.objects.create(
            site_title="Lens & Light Photography",
            hero_title="Capturing Your Beautiful Moments",
            hero_subtitle="Professional Photography Services for Weddings, Portraits & Events",
            photographer_name="Jane Mitchell",
            photographer_bio="I'm an award-winning photographer with over 8 years of experience. My passion is capturing authentic emotions and creating timeless memories that you'll cherish forever. Based in New York, I travel worldwide for assignments.",
            photographer_experience=8,
            email="hello@lensandlight.com",
            phone="+1 (555) 123-4567",
            address="123 Photography Street, New York, NY 10001",
            instagram="https://instagram.com/lensandlight",
            facebook="https://facebook.com/lensandlight",
            twitter="https://twitter.com/lensandlight",
        )

        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('   - 4 Categories created'))
        self.stdout.write(self.style.SUCCESS('   - 8 Sample photos created'))
        self.stdout.write(self.style.SUCCESS('   - 3 Packages created'))
        self.stdout.write(self.style.SUCCESS('   - 4 Testimonials created'))
        self.stdout.write(self.style.SUCCESS('   - 3 Blog posts created'))
        self.stdout.write(self.style.SUCCESS('   - Site settings configured'))