import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trip.settings')
django.setup()

from django.contrib.auth.models import User
from reviews.models import ReviewComment

def seed():
    sample_users = [
        ("Nattapong_Trip", "Pass1234!"),
        ("Somchai_Traveler", "Pass1234!"),
        ("Kanjana_Explorer", "Pass1234!"),
        ("Ananda_Vibe", "Pass1234!"),
        ("Ploy_Reviewer", "Pass1234!"),
        ("Tanawat_Sightseeing", "Pass1234!"),
        ("Waraporn_Green", "Pass1234!"),
    ]

    users = []
    for uname, pword in sample_users:
        u, created = User.objects.get_or_create(username=uname)
        if created:
            u.set_password(pword)
            u.save()
        users.append(u)

    sample_comments = [
        (users[0], "บรรยากาศดีมากกก! ฝูงปลาเยอะสุดๆ เด็กๆ ชอบใจใหญ่เลยครับ ศาลากลางน้ำก็ลมเย็นสบายมากๆ", 5, "จุดให้อาหารปลา 1"),
        (users[1], "หอคอยชมวิวตระการตามาก มองเห็นรอบเกาะแบบ 360 องศา แนะนำให้มาช่วง 5 โมงเย็น พระอาทิตย์ตกสวยมากครับ", 5, "หอคอยชมวิว 1"),
        (users[2], "สะพานเดินข้ามเกาะถ่ายรูปสวยมากๆ ถ่ายมุมไหนก็รอด โทนสีน้ำทะเลกับสะพานเข้ากันดีสุดๆ", 4, "สะพานเชื่อมเกาะกลางน้ำ 1"),
        (users[3], "ศาลากลางน้ำทรงไทยสวยงาม ลมพัดเย็นตลอดวัน เหมาะกับการมานั่งพักผ่อน อ่านหนังสือ หรือถ่ายรูปชิวๆ", 5, "ศาลากลางน้ำทรงไทย 1"),
        (users[4], "ไปให้อาหารปลาคาร์ฟตรงระเบียงมารสนุกมาก ปลาตัวโตและเชื่องมาก อากาศร่มรื่น ให้ 5 ดาวเลยค่ะ", 5, "จุดให้อาหารปลา 4"),
        (users[5], "สถานที่สะอาด การเดินทางสะดวก มีจุดพักผ่อนเยอะมาก ร่มรื่นสุดๆ คุ้มค่ากับการมาเที่ยว", 5, "ทัศนียภาพเกาะกลางน้ำ"),
        (users[6], "มุมถ่ายรูปเยอะมาก โดยเฉพาะบริเวณสะพานและหอคอย แนะนำเตรียมชุดสวยๆ มาถ่ายรูปเลยค่ะ", 4, "หอคอยชมวิว 4"),
    ]

    for user, text, rating, photo in sample_comments:
        if not ReviewComment.objects.filter(user=user, comment_text=text).exists():
            ReviewComment.objects.create(
                user=user,
                comment_text=text,
                rating=rating,
                photo_title=photo
            )
            print(f"Created comment for {user.username}")

if __name__ == '__main__':
    seed()
    print("Seeding completed successfully on Neon PostgreSQL DB!")
