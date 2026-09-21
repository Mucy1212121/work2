from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from reviews import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('google-login/', views.google_login_view, name='google_login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-comment/', views.add_comment_view, name='add_comment'),
    path('review/<int:review_id>/like/', views.toggle_like_view, name='toggle_like'),
    path('review/<int:review_id>/reply/', views.add_reply_view, name='add_reply'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
