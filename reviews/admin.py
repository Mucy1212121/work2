from django.contrib import admin
from .models import Place, ReviewComment, ReviewLike, ReviewReply

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'latitude', 'longitude', 'opening_hours', 'created_at')
    search_fields = ('name', 'category', 'description', 'address')
    list_filter = ('category',)

class ReviewReplyInline(admin.TabularInline):
    model = ReviewReply
    extra = 1

class ReviewLikeInline(admin.TabularInline):
    model = ReviewLike
    extra = 0

@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo_title', 'category', 'rating', 'total_likes', 'total_replies', 'created_at')
    search_fields = ('user__username', 'photo_title', 'comment_text')
    list_filter = ('rating', 'category', 'created_at')
    inlines = [ReviewReplyInline, ReviewLikeInline]

@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'reply_text', 'created_at')
    search_fields = ('user__username', 'reply_text')

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'created_at')

