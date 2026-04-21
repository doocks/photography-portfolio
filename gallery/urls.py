from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gallery/<slug:category_slug>/', views.gallery_view, name='gallery_category'),
    path('api/gallery/', views.gallery_json, name='gallery_json'),
    path('booking/', views.booking_view, name='booking'),
    path('booking/success/', views.booking_success, name='booking_success'),
    path('contact/', views.contact_view, name='contact'),
    path('blog/', views.blog_list, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('client/gallery/', views.client_gallery_access, name='client_gallery_access'),
    path('client/gallery/<str:access_code>/', views.client_gallery_view, name='client_gallery_view'),
    path('client/gallery/logout/', views.logout_gallery, name='logout_gallery'),
    path('my/galleries/', views.my_galleries, name='my_galleries'),
    path('review/', views.submit_review, name='submit_review'),  # ← ADD THIS
    path('api/reviews/', views.get_reviews_api, name='get_reviews_api'), 
    path('check-admin/', views.check_admin, name='check_admin'), 
      # ← ADD THIS
]