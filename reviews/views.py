import base64
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import ReviewComment

def get_photos_list():
    return [
        {
            "filename": "1.png",
            "title": "ทัศนียภาพเกาะกลางน้ำ",
            "subtitle": "บรรยากาศโดยรอบเกาะกลางน้ำ ล้อมรอบด้วยธรรมชาติอันร่มรื่น",
            "category": "จุดท่องเที่ยวหลัก",
            "rating": "4.9",
            "year": "2026",
            "location": "ศูนย์ท่องเที่ยวเกาะกลางน้ำ"
        },
        {
            "filename": "ปลา1.png",
            "title": "จุดให้อาหารปลา 1",
            "subtitle": "ฝูงปลาธรรมชาติแหวกว่ายริมตลิ่งอย่างหนาแน่น",
            "category": "กิจกรรมสัตว์น้ำ",
            "rating": "4.8",
            "year": "2026",
            "location": "ริมตลิ่งทิศตะวันออก"
        },
        {
            "filename": "ปลา2.png",
            "title": "จุดให้อาหารปลา 2",
            "subtitle": "ความสนุกสนานของการให้อาหารฝูงปลาคาร์ฟและปลาเกาะ",
            "category": "กิจกรรมสัตว์น้ำ",
            "rating": "4.7",
            "year": "2026",
            "location": "แพหน้าศาลา"
        },
        {
            "filename": "ปลา3.png",
            "title": "จุดให้อาหารปลา 3",
            "subtitle": "ชมความอุดมสมบูรณ์ของระบบนิเวศทางน้ำประจำเกาะ",
            "category": "กิจกรรมสัตว์น้ำ",
            "rating": "4.8",
            "year": "2026",
            "location": "สะพานไม้ให้อาหารปลา"
        },
        {
            "filename": "ปลา4.png",
            "title": "จุดให้อาหารปลา 4",
            "subtitle": "มุมถ่ายรูปฝูงปลาแหวกว่ายยอดนิยมของนักท่องเที่ยว",
            "category": "กิจกรรมสัตว์น้ำ",
            "rating": "4.9",
            "year": "2026",
            "location": "ระเบียงชมปลา"
        },
        {
            "filename": "ศาลา1.png",
            "title": "ศาลากลางน้ำทรงไทย 1",
            "subtitle": "สถาปัตยกรรมศาลาพักผ่อนกลางน้ำ บรรยากาศเงียบสงบ",
            "category": "จุดพักผ่อน",
            "rating": "4.9",
            "year": "2026",
            "location": "ใจกลางเกาะกลางน้ำ"
        },
        {
            "filename": "ศาลา2.png",
            "title": "ศาลากลางน้ำทรงไทย 2",
            "subtitle": "ศาลาชมทัศนียภาพรอบเกาะ เหมาะสำหรับการนั่งพักผ่อนรับลม",
            "category": "จุดพักผ่อน",
            "rating": "4.8",
            "year": "2026",
            "location": "โซนริมน้ำทิศใต้"
        },
        {
            "filename": "สะพาน1.png",
            "title": "สะพานเชื่อมเกาะกลางน้ำ 1",
            "subtitle": "สะพานเดินข้ามน้ำเชื่อมต่อแผ่นดินใหญ่เข้าสู่ตัวเกาะ",
            "category": "สถาปัตยกรรม",
            "rating": "4.9",
            "year": "2026",
            "location": "ทางเข้าเกาะทิศเหนือ"
        },
        {
            "filename": "สะพาน2.png",
            "title": "สะพานเชื่อมเกาะกลางน้ำ 2",
            "subtitle": "มุมมองสะพานทอดยาวตัดกับสายน้ำ สวยงามทั้งเช้าและเย็น",
            "category": "สถาปัตยกรรม",
            "rating": "4.8",
            "year": "2026",
            "location": "จุดเชื่อมเกาะฝั่งตะวันตก"
        },
        {
            "filename": "หอคอย1.png",
            "title": "หอคอยชมวิว 1",
            "subtitle": "หอคอยสูงสำหรับขึ้นไปชมวิวทิวทัศน์แบบ 360 องศา",
            "category": "จุดชมวิวสูง",
            "rating": "5.0",
            "year": "2026",
            "location": "ยอดหอคอยเกาะกลางน้ำ"
        },
        {
            "filename": "หอคอย3.png",
            "title": "หอคอยชมวิว 3",
            "subtitle": "บรรยากาศยามแสงแดดส่องกระทบตัวหอคอย สวยงามตระการตา",
            "category": "จุดชมวิวสูง",
            "rating": "4.9",
            "year": "2026",
            "location": "จุดชมทัศนียภาพหอคอย"
        },
        {
            "filename": "หอคอย4.png",
            "title": "หอคอยชมวิว 4",
            "subtitle": "สัญลักษณ์แลนด์มาร์คสำคัญของเกาะกลางน้ำที่ต้องมาเยือน",
            "category": "แลนด์มาร์ค",
            "rating": "5.0",
            "year": "2026",
            "location": "ลานกิจกรรมหอคอย"
        }
    ]

def home_view(request):
    photos = get_photos_list()
    comments = ReviewComment.objects.select_related('user').all()[:15]
    total_comments = ReviewComment.objects.count()
    context = {
        'photos': photos,
        'comments': comments,
        'total_comments': total_comments
    }
    return render(request, '1.home.html', context)

def add_comment_view(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'กรุณาเข้าสู่ระบบก่อนแสดงความคิดเห็น')
            return redirect('login')
        
        comment_text = request.POST.get('comment_text', '').strip()
        rating = request.POST.get('rating', 5)
        photo_title = request.POST.get('photo_title', 'เกาะกลางน้ำ')
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                rating = 5
        except ValueError:
            rating = 5
            
        if comment_text:
            ReviewComment.objects.create(
                user=request.user,
                comment_text=comment_text,
                rating=rating,
                photo_title=photo_title
            )
            messages.success(request, 'ขอบคุณสำหรับความคิดเห็นของคุณ!')
        else:
            messages.warning(request, 'กรุณากรอกข้อความแสดงความคิดเห็น')
            
    return redirect('home')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'ยินดีต้อนรับกลับ คุณ {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            error_message = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง'
            
    return render(request, '2.login.html', {'error_message': error_message})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not username or not password:
            error_message = 'กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน'
        elif password != confirm_password:
            error_message = 'รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน'
        else:
            existing_user = User.objects.filter(username__iexact=username).first()
            if existing_user:
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f'เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับ คุณ {user.username}')
                    return redirect('home')
                else:
                    error_message = f'ชื่อผู้ใช้ "{username}" ถูกใช้งานไปแล้ว ไม่สามารถใช้ชื่อนี้ได้อีก'
            else:
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                messages.success(request, f'สมัครสมาชิกสำเร็จ! ยินดีต้อนรับ คุณ {username}')
                return redirect('home')
            
    return render(request, 'register.html', {'error_message': error_message})

@csrf_exempt
def google_login_view(request):
    """ Dedicated Google Account login handler saving email to Django Admin & Neon PostgreSQL DB """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        name = request.POST.get('name', '').strip()
        credential = request.POST.get('credential', '').strip()

        if credential and len(credential.split('.')) >= 2:
            try:
                parts = credential.split('.')
                padding = '=' * (-len(parts[1]) % 4)
                payload_json = base64.b64decode(parts[1] + padding).decode('utf-8')
                payload = json.loads(payload_json)
                email = payload.get('email') or email
                name = payload.get('name') or name
            except Exception:
                pass

        if not email:
            if username and '@' in username:
                email = username
                username = username.split('@')[0]
            elif username:
                email = f"{username}@gmail.com"
            else:
                email = "manggomny@gmail.com"
                username = "manggomny"

        if not username:
            username = email.split('@')[0] if '@' in email else email

        username = username.replace(' ', '_')

        # Check existing user by username or email in Neon DB
        user = User.objects.filter(username__iexact=username).first()
        if not user:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=f"Google_{username}_Secured2026!"
            )
            if name:
                user.first_name = name
                user.save()
        else:
            # Ensure email is updated & saved in Django DB
            if user.email != email:
                user.email = email
                user.save()

        login(request, user)
        messages.success(request, f'เข้าสู่ระบบด้วย Google ({user.email}) สำเร็จ! ยินดีต้อนรับ คุณ {user.username}')
        return redirect('home')

    # If GET request, render google_callback.html which parses hash parameters and automatically POSTs
    return render(request, 'google_callback.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'ออกจากระบบเรียบร้อยแล้ว')
    return redirect('home')
