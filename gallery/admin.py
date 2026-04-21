from django.contrib import admin
from django import forms
from .models import Category, Photograph, Package, Booking, Testimonial, BlogPost, SiteSetting, ClientGallery, ClientPhoto, AccessAttempt, Review
from .forms import BookingForm, ContactForm, ClientGalleryAccessForm, ReviewForm
# Custom form for ClientGallery to ensure proper access code handling
class ClientGalleryForm(forms.ModelForm):
    class Meta:
        model = ClientGallery
        fields = '__all__'
    
    def clean_access_code(self):
        access_code = self.cleaned_data.get('access_code')
        if access_code:
            # Convert to uppercase and strip spaces
            access_code = access_code.strip().upper()
            
            # Check for duplicate (case-insensitive)
            existing = ClientGallery.objects.filter(access_code__iexact=access_code)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f'Access code "{access_code}" already exists. Please use a different code.')
        return access_code

@admin.register(ClientGallery)
class ClientGalleryAdmin(admin.ModelAdmin):
    form = ClientGalleryForm
    list_display = ('title', 'client', 'access_code', 'is_active', 'created_at', 'photo_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'access_code', 'client__username', 'client__email')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Gallery Information', {
            'fields': ('client', 'booking', 'title', 'access_code', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'
    
    def save_model(self, request, obj, form, change):
        # Ensure access code is uppercase before saving
        if obj.access_code:
            obj.access_code = obj.access_code.strip().upper()
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        # Show success message with access code
        self.message_user(request, f'✅ Gallery created! Access Code: {obj.access_code}')
        return super().response_add(request, obj, post_url_continue)

@admin.register(ClientPhoto)
class ClientPhotoAdmin(admin.ModelAdmin):
    list_display = ('gallery', 'caption', 'is_downloadable', 'created_at')
    list_filter = ('gallery', 'is_downloadable')
    search_fields = ('caption', 'gallery__title')

# Register other models
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)

@admin.register(Photograph)
class PhotographAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'featured', 'order', 'views')
    list_filter = ('category', 'featured')
    search_fields = ('title', 'description')
    list_editable = ('featured', 'order')

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'popular', 'order')
    list_editable = ('popular', 'order')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'event_date', 'package', 'status', 'created_at')
    list_filter = ('status', 'event_date')
    search_fields = ('client_name', 'client_email')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'rating', 'featured', 'created_at')
    list_editable = ('featured',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'views', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('published',)

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if SiteSetting.objects.exists():
            return False
        return True

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'rating', 'event_type', 'is_approved', 'featured', 'created_at')
    list_filter = ('rating', 'is_approved', 'featured', 'event_type')
    search_fields = ('client_name', 'review_text')
    list_editable = ('is_approved', 'featured')
    actions = ['approve_reviews', 'feature_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def feature_reviews(self, request, queryset):
        queryset.update(featured=True)
        self.message_user(request, f"{queryset.count()} reviews featured.")
    feature_reviews.short_description = "Feature selected reviews"