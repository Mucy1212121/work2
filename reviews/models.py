from django.db import models
from django.contrib.auth.models import User

class Place(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="ชื่อสถานที่/วัด")
    category = models.CharField(max_length=100, default='วัด/ศาสนสถาน', verbose_name="หมวดหมู่")
    description = models.TextField(blank=True, verbose_name="รายละเอียด")
    highlight = models.CharField(max_length=255, blank=True, verbose_name="จุดเด่นไฮไลท์")
    image = models.CharField(max_length=255, default='1.png', verbose_name="รูปภาพประกอบ")
    latitude = models.FloatField(default=15.1186, verbose_name="ละติจูด")
    longitude = models.FloatField(default=104.3220, verbose_name="ลองจิจูด")
    address = models.CharField(max_length=300, blank=True, verbose_name="ที่อยู่/ตำบล")
    opening_hours = models.CharField(max_length=100, default='08:00 - 17:00 น.', verbose_name="เวลาเปิด-ปิด")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ReviewComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    photo_title = models.CharField(max_length=200, blank=True, null=True, default='สถานที่ท่องเที่ยว')
    category = models.CharField(max_length=100, default='จุดท่องเที่ยวหลัก')
    comment_text = models.TextField()
    rating = models.IntegerField(default=5)
    image = models.TextField(blank=True, null=True, verbose_name="รูปภาพแนบ")
    image2 = models.TextField(blank=True, null=True, verbose_name="รูปภาพแนบ 2")
    image3 = models.TextField(blank=True, null=True, verbose_name="รูปภาพแนบ 3")
    image4 = models.TextField(blank=True, null=True, verbose_name="รูปภาพแนบ 4")
    latitude = models.FloatField(default=13.7466)
    longitude = models.FloatField(default=100.5347)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.photo_title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_replies(self):
        return self.replies.count()


class ReviewLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_likes')
    review = models.ForeignKey(ReviewComment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')

    def __str__(self):
        return f"{self.user.username} liked #{self.review.id}"


class ReviewReply(models.Model):
    review = models.ForeignKey(ReviewComment, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_replies')
    reply_text = models.TextField()
    image = models.TextField(blank=True, null=True, verbose_name="รูปภาพแนบในคอมเมนต์ย่อย")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} replied on #{self.review.id}: {self.reply_text[:20]}"
