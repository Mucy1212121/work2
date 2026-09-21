from django.test import TestCase, Client
from django.contrib.auth.models import User
from reviews.models import Place, ReviewComment, ReviewLike, ReviewReply
import json

class KohKlangNamReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='tester1', password='Password123!')
        self.user2 = User.objects.create_user(username='tester2', password='Password123!')
        
        self.place = Place.objects.create(
            name='หอศรีลำดวนเฉลิมพระเกียรติ (หอคอยเกาะกลางน้ำ)',
            category='จุดชมวิว & แหล่งเรียนรู้',
            description='หอคอยชมเมืองความสูง 84 เมตร ชมทัศนียภาพเมืองศรีสะเกษและเกาะกลางน้ำแบบ 360 องศา',
            latitude=15.1065,
            longitude=104.3335
        )
        
        self.review1 = ReviewComment.objects.create(
            user=self.user1,
            place=self.place,
            photo_title='หอศรีลำดวนเฉลิมพระเกียรติ (หอคอยเกาะกลางน้ำ)',
            category='จุดชมวิว & แหล่งเรียนรู้',
            comment_text='ขึ้นลิฟต์ไปชมวิวเมืองศรีสะเกษและเกาะกลางน้ำแบบ 360 องศา สวยงามมาก',
            rating=5
        )

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TripHub')
        self.assertContains(response, 'หอศรีลำดวน')

    def test_like_toggle_ajax(self):
        self.client.login(username='tester1', password='Password123!')
        response = self.client.post(
            f'/review/{self.review1.id}/like/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['liked'])
        self.assertEqual(data['total_likes'], 1)

        # Toggle again -> Unlike
        response2 = self.client.post(
            f'/review/{self.review1.id}/like/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertFalse(data2['liked'])
        self.assertEqual(data2['total_likes'], 0)

    def test_add_reply_with_image_ajax(self):
        self.client.login(username='tester2', password='Password123!')
        response = self.client.post(
            f'/review/{self.review1.id}/reply/',
            data=json.dumps({
                'reply_text': 'มุมถ่ายรูปบนหอคอยสวยมากครับ',
                'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['reply']['username'], 'tester2')
        self.assertTrue(data['reply']['image'].startswith('data:image/png;base64'))
        self.assertEqual(data['total_replies'], 1)
        self.assertEqual(ReviewReply.objects.count(), 1)

    def test_search_and_filter(self):
        response = self.client.get('/?search=หอศรีลำดวน')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'หอศรีลำดวน')

        response2 = self.client.get('/?category=จุดชมวิว & แหล่งเรียนรู้')
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'หอศรีลำดวน')

