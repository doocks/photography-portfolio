from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import hashlib
from datetime import timedelta
from .models import Category, Photograph, Package, Booking, Review, Testimonial, BlogPost, SiteSetting, ClientGallery, ClientPhoto, AccessAttempt
from .forms import BookingForm, ContactForm, ClientGalleryAccessForm, ReviewForm

def get_settings():
    return SiteSetting.objects.first()

def index(request):
    settings_obj = get_settings()
    categories = Category.objects.all()
    featured_photos = Photograph.objects.filter(featured=True)[:8]
    packages = Package.objects.all().order_by('order')
    testimonials = Testimonial.objects.filter(featured=True)[:6]
    recent_blogs = BlogPost.objects.filter(published=True)[:3]
    
    context = {
        'settings': settings_obj,
        'categories': categories,
        'featured_photos': featured_photos,
        'packages': packages,
        'testimonials': testimonials,
        'recent_blogs': recent_blogs,
    }
    return render(request, 'gallery/index.html', context)

def gallery_view(request, category_slug=None):
    settings_obj = get_settings()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        photos = Photograph.objects.filter(category=category)
    else:
        category = None
        photos = Photograph.objects.all()
    
    categories = Category.objects.all()
    context = {
        'settings': settings_obj,
        'photos': photos,
        'categories': categories,
        'current_category': category,
    }
    return render(request, 'gallery/gallery.html', context)

def gallery_json(request):
    photos = Photograph.objects.all().values('id', 'title', 'description', 'image', 'category__name', 'location', 'camera_settings')
    return JsonResponse(list(photos), safe=False)

def booking_view(request):
    settings_obj = get_settings()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            try:
                send_mail(
                    f'New Booking Request - {booking.client_name}',
                    f"Name: {booking.client_name}\nEmail: {booking.client_email}\nPhone: {booking.client_phone}\nDate: {booking.event_date}\nPackage: {booking.package.name if booking.package else 'Not selected'}\nMessage: {booking.message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@example.com'],
                    fail_silently=True,
                )
            except:
                pass
            messages.success(request, 'Your booking request has been sent! We will contact you within 24 hours.')
            return redirect('booking_success')
    else:
        form = BookingForm()
    
    packages = Package.objects.all()
    context = {
        'settings': settings_obj,
        'form': form,
        'packages': packages,
    }
    return render(request, 'gallery/booking.html', context)

def booking_success(request):
    settings_obj = get_settings()
    return render(request, 'gallery/booking_success.html', {'settings': settings_obj})

def contact_view(request):
    settings_obj = get_settings()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                send_mail(
                    f"Contact Form: {form.cleaned_data['subject']}",
                    f"From: {form.cleaned_data['name']} ({form.cleaned_data['email']})\n\nMessage: {form.cleaned_data['message']}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@example.com'],
                    fail_silently=True,
                )
            except:
                pass
            messages.success(request, 'Your message has been sent! I will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'settings': settings_obj,
        'form': form,
    }
    return render(request, 'gallery/contact.html', context)

def blog_list(request):
    settings_obj = get_settings()
    posts = BlogPost.objects.filter(published=True).order_by('-created_at')
    return render(request, 'gallery/blog.html', {'settings': settings_obj, 'posts': posts})

def blog_detail(request, slug):
    settings_obj = get_settings()
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    post.views += 1
    post.save()
    return render(request, 'gallery/blog_detail.html', {'settings': settings_obj, 'post': post})

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_protect
@never_cache
@require_http_methods(['GET', 'POST'])
def client_gallery_access(request):
    """Secure client gallery access with rate limiting"""
    settings_obj = get_settings()
    client_ip = get_client_ip(request)
    
    # REMOVED: Auto-redirect for existing session
    # Now always show the access form
    
    # Check rate limiting
    if AccessAttempt.is_rate_limited(client_ip):
        messages.error(request, 'Too many failed attempts. Please try again after 15 minutes.')
        return render(request, 'gallery/gallery_access.html', {'settings': settings_obj, 'form': ClientGalleryAccessForm()})
    
    if request.method == 'POST':
        form = ClientGalleryAccessForm(request.POST)
        if form.is_valid():
            access_code = form.cleaned_data['access_code'].strip().upper()
            
            # Find gallery by code (using hash comparison)
            code_hash = hashlib.sha256(access_code.encode()).hexdigest()
            
            try:
                gallery = ClientGallery.objects.get(access_code_hash=code_hash, is_active=True)
                
                # Check if gallery is still valid
                if not gallery.is_valid():
                    AccessAttempt.record_attempt(client_ip, access_code, False)
                    if gallery.expires_at and gallery.expires_at < timezone.now():
                        messages.error(request, 'This gallery has expired. Please contact your photographer.')
                    elif not gallery.is_active:
                        messages.error(request, 'This gallery is no longer active.')
                    else:
                        messages.error(request, 'Invalid access code.')
                    return render(request, 'gallery/gallery_access.html', {'settings': settings_obj, 'form': form})
                
                # Successful access - record success and store in session
                AccessAttempt.record_attempt(client_ip, access_code, True)
                gallery.record_access()
                
                # Store in session
                request.session['gallery_access'] = gallery.access_code
                request.session['gallery_access_code'] = access_code  # Store the actual code
                request.session.set_expiry(3600)  # 1 hour session
                
                messages.success(request, f'Access granted! Welcome to {gallery.title}')
                return redirect('client_gallery_view', access_code=gallery.access_code)
                
            except ClientGallery.DoesNotExist:
                AccessAttempt.record_attempt(client_ip, access_code, False)
                messages.error(request, 'Invalid access code. Please check and try again.')
    else:
        form = ClientGalleryAccessForm()
        
        # Optional: Clear session if user wants to logout
        # Uncomment the line below to clear session when visiting access page
        # if 'gallery_access' in request.session:
        #     del request.session['gallery_access']
    
    context = {
        'settings': settings_obj,
        'form': form,
    }
    return render(request, 'gallery/gallery_access.html', context)

@never_cache
def client_gallery_view(request, access_code):
    """Secure gallery view with session verification"""
    settings_obj = get_settings()
    
    # Verify session has access to this gallery
    session_code = request.session.get('gallery_access')
    if not session_code or session_code != access_code.upper():
        messages.error(request, 'Your session has expired. Please enter your access code again.')
        return redirect('client_gallery_access')
    
    # Find gallery using hash for security
    code_hash = hashlib.sha256(access_code.upper().encode()).hexdigest()
    gallery = get_object_or_404(ClientGallery, access_code_hash=code_hash, is_active=True)
    
    # Double-check validity
    if not gallery.is_valid():
        # Clear session and redirect
        if 'gallery_access' in request.session:
            del request.session['gallery_access']
        messages.error(request, 'This gallery is no longer available.')
        return redirect('client_gallery_access')
    
    photos = gallery.photos.all()
    
    context = {
        'settings': settings_obj,
        'gallery': gallery,
        'photos': photos,
    }
    return render(request, 'gallery/client_gallery.html', context)

def logout_gallery(request):
    """Logout from gallery view"""
    if 'gallery_access' in request.session:
        del request.session['gallery_access']
    if 'gallery_access_code' in request.session:
        del request.session['gallery_access_code']
    messages.info(request, 'You have been logged out of the gallery.')
    return redirect('client_gallery_access')

@login_required
def my_galleries(request):
    settings_obj = get_settings()
    galleries = ClientGallery.objects.filter(client=request.user)
    return render(request, 'gallery/my_galleries.html', {'settings': settings_obj, 'galleries': galleries})

def submit_review(request):
    """Client review submission page"""
    settings_obj = get_settings()
    
    # Get approved reviews for display
    approved_reviews = Review.objects.filter(is_approved=True)[:10]
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False  # Requires admin approval
            review.save()
            
            # Send email notification to admin
            try:
                send_mail(
                    f'New Review Submitted - {review.client_name}',
                    f"""
                    New Client Review!
                    
                    Client: {review.client_name}
                    Email: {review.client_email}
                    Rating: {review.rating}★
                    Event Type: {review.get_event_type_display() if review.event_type else 'Not specified'}
                    
                    Review:
                    {review.review_text}
                    
                    Approve this review at: /admin/gallery/review/
                    """,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@example.com'],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {e}")
            
            messages.success(request, 'Thank you for your review! It will be published after admin approval.')
            return redirect('submit_review')
    else:
        form = ReviewForm()
    
    # Calculate average rating
    total_rating = sum([r.rating for r in approved_reviews])
    avg_rating = round(total_rating / len(approved_reviews), 1) if approved_reviews else 0
    
    context = {
        'settings': settings_obj,
        'form': form,
        'approved_reviews': approved_reviews,
        'avg_rating': avg_rating,
        'total_reviews': len(approved_reviews),
    }
    return render(request, 'gallery/review.html', context)


def get_reviews_api(request):
    """API endpoint for fetching approved reviews"""
    reviews = Review.objects.filter(is_approved=True).values(
        'client_name', 'rating', 'review_text', 'event_type', 'created_at'
    )
    return JsonResponse(list(reviews), safe=False)
