import base64
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from .models import Place, ReviewComment, ReviewLike, ReviewReply

def get_photos_list():
    places = Place.objects.all()
    if places.exists():
        return [
            {
                "id": p.id,
                "filename": p.image if p.image else "1.png",
                "title": p.name,
                "subtitle": p.highlight or (p.description[:60] + "..." if p.description else ""),
                "category": p.category or "สถานที่ท่องเที่ยว",
                "rating": "4.9",
                "year": "2026",
                "location": p.address or p.name,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "description": p.description or "",
                "opening_hours": p.opening_hours or "เปิดให้บริการทุกวัน",
            }
            for p in places
        ]
    return []

def home_view(request):
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    
    # Query all places
    places = Place.objects.all()
    
    # Query reviews and order by latest (รีวิวใหม่ล่าสุด)
    reviews_qs = ReviewComment.objects.select_related('user', 'place').prefetch_related('likes', 'replies__user').all()
    
    if search_query:
        reviews_qs = reviews_qs.filter(
            Q(photo_title__icontains=search_query) |
            Q(comment_text__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(place__name__icontains=search_query)
        )
        
    if category_filter and category_filter != 'ทั้งหมด':
        reviews_qs = reviews_qs.filter(category=category_filter)
        
    # Order strictly by latest
    reviews_qs = reviews_qs.order_by('-created_at')
    
    # Prepare reviews with user like status
    reviews_list = []
    user_id = request.user.id if request.user.is_authenticated else None
    
    for r in reviews_qs:
        user_has_liked = False
        if user_id:
            user_has_liked = any(like.user_id == user_id for like in r.likes.all())
        
        reviews_list.append({
            'obj': r,
            'user_has_liked': user_has_liked,
            'likes_count': r.likes.count(),
            'replies': r.replies.all(),
            'replies_count': r.replies.count(),
        })

    # Prepare places JSON for Leaflet.js Interactive Map
    places_json = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category or "สถานที่ท่องเที่ยว",
            "image": p.image if p.image else "/static/1.png",
            "latitude": p.latitude,
            "longitude": p.longitude,
            "address": p.address or p.name,
            "opening_hours": p.opening_hours or "เปิดให้บริการทุกวัน",
            "highlight": p.highlight or "",
            "description": p.description or "",
            "reviews_count": p.reviews.count()
        }
        for p in places
    ]
    
    # Derive categories dynamically from existing DB records only
    place_cats = list(Place.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct())
    review_cats = list(ReviewComment.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct())
    all_cats = []
    for c in place_cats + review_cats:
        c_clean = c.strip() if c else ''
        if c_clean and c_clean not in all_cats:
            all_cats.append(c_clean)
            
    categories = ['ทั้งหมด'] + all_cats
    
    photos = get_photos_list()
    total_comments = ReviewComment.objects.count()
    total_likes = ReviewLike.objects.count()
    
    context = {
        'photos': photos,
        'places': places,
        'places_json': json.dumps(places_json, ensure_ascii=False),
        'reviews': reviews_list,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, '1.home.html', context)

def toggle_like_view(request, review_id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'success': False, 'message': 'กรุณาเข้าสู่ระบบก่อนกดถูกใจ'}, status=401)
        messages.error(request, 'กรุณาเข้าสู่ระบบก่อนกดถูกใจ')
        return redirect('login')
        
    review = get_object_or_404(ReviewComment, id=review_id)
    like_obj = ReviewLike.objects.filter(user=request.user, review=review).first()
    
    if like_obj:
        like_obj.delete()
        liked = False
    else:
        ReviewLike.objects.create(user=request.user, review=review)
        liked = True
        
    total_likes = review.likes.count()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': total_likes
        })
        
    return redirect('home')

def add_reply_view(request, review_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'กรุณาเข้าสู่ระบบก่อนตอบกลับ'}, status=401)
            messages.error(request, 'กรุณาเข้าสู่ระบบก่อนแสดงความคิดเห็น')
            return redirect('login')
            
        review = get_object_or_404(ReviewComment, id=review_id)
        
        reply_text = ''
        image_data = None
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                reply_text = body.get('reply_text', '').strip()
                image_data = body.get('image', None)
            except Exception:
                pass
        else:
            reply_text = request.POST.get('reply_text', '').strip()
            image_data = request.POST.get('image', None)
            
        if reply_text or image_data:
            reply = ReviewReply.objects.create(
                review=review,
                user=request.user,
                reply_text=reply_text,
                image=image_data
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'reply': {
                        'id': reply.id,
                        'username': request.user.username,
                        'user_initial': request.user.username[0].upper() if request.user.username else 'U',
                        'reply_text': reply.reply_text,
                        'image': reply.image,
                        'created_at': reply.created_at.strftime('%d %b %Y, %H:%M น.')
                    },
                    'total_replies': review.replies.count()
                })
            messages.success(request, 'ส่งความคิดเห็นย่อยเรียบร้อยแล้ว')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': 'กรุณากรอกข้อความหรือแนบรูปภาพ'}, status=400)
            messages.warning(request, 'กรุณากรอกข้อความตอบกลับ')
            
    return redirect('home')

def add_comment_view(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'กรุณาเข้าสู่ระบบก่อนแสดงความคิดเห็น')
            return redirect('login')
        
        comment_text = request.POST.get('comment_text', '').strip()
        rating = request.POST.get('rating', 5)
        place_id = request.POST.get('place_id', '').strip()
        new_place_name = request.POST.get('new_place_name', '').strip()
        new_category = request.POST.get('new_category', '').strip()
        new_lat = request.POST.get('new_lat', '').strip()
        new_lng = request.POST.get('new_lng', '').strip()
        image_data = request.POST.get('image', '').strip()
        image2_data = request.POST.get('image2', '').strip()
        image3_data = request.POST.get('image3', '').strip()
        image4_data = request.POST.get('image4', '').strip()
        share_location = request.POST.get('share_location', '').strip()
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                rating = 5
        except ValueError:
            rating = 5
            
        place = None
        photo_title = 'สถานที่ท่องเที่ยว'
        cat = 'สถานที่ท่องเที่ยว'
        lat = 13.7563
        lng = 100.5018

        if share_location == 'true':
            photo_title = 'เช็คอินล่าสุดของฉัน'
            cat = 'ที่อยู่ปัจจุบัน'
            try:
                lat = float(request.POST.get('user_lat', ''))
                lng = float(request.POST.get('user_lng', ''))
            except ValueError:
                pass
        elif new_place_name:
            # User is creating/reviewing a new place
            photo_title = new_place_name
            cat = new_category if new_category else 'สถานที่ท่องเที่ยว'
            try:
                lat = float(new_lat) if new_lat else 13.7563
                lng = float(new_lng) if new_lng else 100.5018
            except ValueError:
                lat, lng = 13.7563, 100.5018
                
            place = Place.objects.filter(name__iexact=new_place_name).first()
            if not place:
                place = Place.objects.create(
                    name=new_place_name,
                    category=cat,
                    latitude=lat,
                    longitude=lng,
                    image=image_data if image_data else "/static/1.png",
                    description=comment_text[:120] if comment_text else new_place_name
                )
        elif place_id and place_id != 'new':
            place = Place.objects.filter(id=place_id).first()
            if place:
                photo_title = place.name
                lat = place.latitude
                lng = place.longitude
                cat = place.category
                
        if comment_text or image_data:
            ReviewComment.objects.create(
                user=request.user,
                place=place,
                photo_title=photo_title,
                category=cat,
                comment_text=comment_text,
                rating=rating,
                image=image_data if image_data else None,
                image2=image2_data if image2_data else None,
                image3=image3_data if image3_data else None,
                image4=image4_data if image4_data else None,
                latitude=lat,
                longitude=lng
            )
            messages.success(request, f'ขอบคุณสำหรับรีวิว "{photo_title}" ของคุณ!')
        else:
            messages.warning(request, 'กรุณากรอกข้อความแสดงความคิดเห็นหรือแนบรูปภาพ')
            
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




def delete_review_view(request, review_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'กรุณาเข้าสู่ระบบก่อน')
            return redirect('home')
        
        review = get_object_or_404(ReviewComment, id=review_id)
        if request.user == review.user or request.user.is_superuser or request.user.is_staff:
            review.delete()
            messages.success(request, 'ลบโพสต์สำเร็จแล้ว')
        else:
            messages.error(request, 'คุณไม่มีสิทธิ์ลบโพสต์นี้')
            
    return redirect('home')
