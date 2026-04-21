from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import hashlib  # ← ADD THIS IMPORT
import secrets
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, default='fa-camera')
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class Photograph(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/')
    watermark_image = models.ImageField(upload_to='watermarked/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    location = models.CharField(max_length=200, blank=True)
    camera_settings = models.CharField(max_length=200, blank=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', '-created_at']


class Package(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    features = models.TextField(help_text="Comma-separated features")
    hours = models.IntegerField(default=4)
    edited_photos = models.IntegerField(default=50)
    popular = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def get_features_list(self):
        return [f.strip() for f in self.features.split(',')]

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    event_date = models.DateField()
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.event_date}"


class Testimonial(models.Model):
    client_name = models.CharField(max_length=200)
    client_photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    review = models.TextField()
    rating = models.IntegerField(default=5)
    event_type = models.CharField(max_length=100, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.rating}★"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField()
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    views = models.IntegerField(default=0)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ClientGallery(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='galleries', null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, default="My Gallery")
    access_code = models.CharField(max_length=50, unique=True, db_index=True)
    access_code_hash = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_views = models.IntegerField(default=0)
    current_views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.access_code}"
    
    def save(self, *args, **kwargs):
        # Convert access code to UPPERCASE and hash it
        if self.access_code:
            original_code = self.access_code.strip().upper()
            self.access_code = original_code
            # Store a hash of the code for secure verification
            self.access_code_hash = hashlib.sha256(original_code.encode()).hexdigest()
        else:
            # Generate secure random code
            import secrets
            self.access_code = secrets.token_urlsafe(8).upper().replace('-', '').replace('_', '')
            self.access_code_hash = hashlib.sha256(self.access_code.encode()).hexdigest()
        
        # Set default expiry (6 months from now)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=180)
        
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if gallery is still valid"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.max_views > 0 and self.current_views >= self.max_views:
            return False
        return True
    
    def record_access(self):
        """Record gallery access"""
        self.current_views += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['current_views', 'last_accessed'])
    
    def verify_code(self, input_code):
        """Securely verify access code using hash"""
        input_hash = hashlib.sha256(input_code.strip().upper().encode()).hexdigest()
        return self.access_code_hash == input_hash
    
    class Meta:
        ordering = ['-created_at']


class AccessAttempt(models.Model):
    """Track failed access attempts for rate limiting"""
    ip_address = models.GenericIPAddressField()
    access_code = models.CharField(max_length=50, blank=True)
    success = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['ip_address', 'attempted_at']),
        ]
    
    @classmethod
    def is_rate_limited(cls, ip_address, limit=5, window_minutes=15):
        """Check if IP is rate limited"""
        window = timezone.now() - timedelta(minutes=window_minutes)
        recent_failures = cls.objects.filter(
            ip_address=ip_address,
            success=False,
            attempted_at__gte=window
        ).count()
        return recent_failures >= limit
    
    @classmethod
    def record_attempt(cls, ip_address, access_code, success):
        cls.objects.create(
            ip_address=ip_address,
            access_code=access_code,
            success=success
        )
        # Clean up old records (keep last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        cls.objects.filter(attempted_at__lt=week_ago).delete()


class ClientPhoto(models.Model):
    gallery = models.ForeignKey(ClientGallery, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='client_galleries/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    is_downloadable = models.BooleanField(default=True)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.gallery.title}"


class SiteSetting(models.Model):
    site_title = models.CharField(max_length=100, default="Lens & Light Photography")
    hero_title = models.CharField(max_length=200, default="Capturing Your Beautiful Moments")
    hero_subtitle = models.TextField(default="Professional Photography Services")
    hero_image = models.ImageField(upload_to='settings/', blank=True, null=True)
    photographer_name = models.CharField(max_length=100, default="Jane Mitchell")
    photographer_bio = models.TextField(default="Award-winning photographer with 8+ years of experience.")
    photographer_experience = models.IntegerField(default=8)
    behind_scene_image = models.ImageField(upload_to='settings/', blank=True, null=True)
    email = models.EmailField(default="hello@example.com")
    phone = models.CharField(max_length=20, default="+1 (555) 123-4567")
    address = models.TextField(default="New York, NY")
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    google_map_embed = models.TextField(blank=True)

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name_plural = "Site Settings"

class Review(models.Model):
    """Client review and rating system"""
    EVENT_CHOICES = [
        ('wedding', 'Wedding'),
        ('portrait', 'Portrait'),
        ('event', 'Event'),
        ('commercial', 'Commercial'),
        ('other', 'Other'),
    ]
    
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    review_text = models.TextField()
    event_type = models.CharField(max_length=100, blank=True, choices=EVENT_CHOICES)
    is_approved = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client_name} - {self.rating}★ - {'Approved' if self.is_approved else 'Pending'}"
    
    class Meta:
        ordering = ['-created_at']