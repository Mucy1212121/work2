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

def home_view(request):
    search_query = request.GET.get('search', '').strip()
    
    # Query reviews and order by latest (select_related user to prevent N+1)
    reviews_qs = ReviewComment.objects.select_related('user').prefetch_related(
        'likes', 'replies__user'
    ).defer('image', 'image2', 'image3', 'image4')
    
    if search_query:
        reviews_qs = reviews_qs.filter(
            Q(photo_title__icontains=search_query) |
            Q(comment_text__icontains=search_query)
        )
        
    # Limit to latest 40 reviews for blazing speed
    reviews_qs = list(reviews_qs.order_by('-created_at')[:40])
    
    # Fetch image fields only for the displayed reviews
    review_ids = [r.id for r in reviews_qs]
    images_map = {
        r['id']: r for r in ReviewComment.objects.filter(id__in=review_ids).values(
            'id', 'image', 'image2', 'image3', 'image4'
        )
    }

    # Prepare review list with user like status
    reviews_list = []
    user_id = request.user.id if request.user.is_authenticated else None
    
    for r in reviews_qs:
        user_has_liked = False
        if user_id:
            user_has_liked = any(like.user_id == user_id for like in r.likes.all())
        
        # Attach image data
        img_data = images_map.get(r.id, {})
        r.image = img_data.get('image')
        r.image2 = img_data.get('image2')
        r.image3 = img_data.get('image3')
        r.image4 = img_data.get('image4')
        
        reviews_list.append({
            'obj': r,
            'user_has_liked': user_has_liked,
            'likes_count': r.likes.count(),
            'replies': r.replies.all(),
            'replies_count': r.replies.count(),
        })
    
    total_comments = ReviewComment.objects.count()
    total_likes = ReviewLike.objects.count()
    
    context = {
        'reviews': reviews_list,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'search_query': search_query,
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
        user_lat_val = request.POST.get('user_lat', '').strip()
        user_lng_val = request.POST.get('user_lng', '').strip()
        share_location = request.POST.get('share_location', '').strip()
        image_data = request.POST.get('image', '').strip()
        image2_data = request.POST.get('image2', '').strip()
        image3_data = request.POST.get('image3', '').strip()
        image4_data = request.POST.get('image4', '').strip()
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                rating = 5
        except ValueError:
            rating = 5
            
        lat = None
        lng = None
        if user_lat_val and user_lng_val:
            try:
                lat = float(user_lat_val)
                lng = float(user_lng_val)
            except ValueError:
                lat = None
                lng = None
                
        if comment_text or image_data:
            ReviewComment.objects.create(
                user=request.user,
                photo_title='โพสต์รีวิว',
                category='รีวิวทั่วไป' if not (lat and lng) else 'แชร์พิกัด',
                comment_text=comment_text,
                rating=rating,
                image=image_data if image_data else None,
                image2=image2_data if image2_data else None,
                image3=image3_data if image3_data else None,
                image4=image4_data if image4_data else None,
                latitude=lat if lat is not None else 0,
                longitude=lng if lng is not None else 0
            )
            messages.success(request, 'โพสต์รีวิวของคุณสำเร็จแล้ว!')
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
            next_url = request.POST.get('next') or request.GET.get('next', '')
            if not next_url or not next_url.startswith('/'):
                next_url = 'home'
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
