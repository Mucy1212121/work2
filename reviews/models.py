from django.db import models
from django.contrib.auth.models import User

class ReviewComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    rating = models.IntegerField(default=5)
    photo_title = models.CharField(max_length=200, blank=True, null=True, default='เกาะกลางน้ำ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.comment_text[:20]} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
