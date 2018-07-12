from django.shortcuts import render,HttpResponse,redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from app01.myform import *
from app01.models import *
from app01.page import *
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
import json

# Create your views here.


def get_valid_img(request):
    """
        生成动态验证码
    """
    def get_random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def get_random_char():
        random_num = str(random.randint(0, 9))
        random_upper_alph = chr(random.randint(65, 90))
        random_lowwer_alph = chr(random.randint(97, 122))
        random_char = random.choice([random_num, random_lowwer_alph, random_upper_alph])
        return random_char

    image = Image.new(mode='RGB', size=(260, 40), color=get_random_color())
    draw = ImageDraw.Draw(image, mode='RGB')
    font = ImageFont.truetype('static/font/kumo.ttf', 32)
    valid_code_str = ''
    for i in range(1, 6):
        char = get_random_char()
        valid_code_str += char
        draw.text([i * 40, 5], char, get_random_color(), font=font)
    f = BytesIO()
    image.save(f, 'png')
    data = f.getvalue()
    request.session['valid_code_str'] = valid_code_str
    return HttpResponse(data)


def log_in(request):
    if request.is_ajax():
        loginForm = LoginForm(request,request.POST)
        loginResponse = {'user': None,'error_msg': ''}
        if loginForm.is_valid():
            user = auth.authenticate(username=loginForm.cleaned_data.get('user'), password=loginForm.cleaned_data.get('pwd'))
            if user:
                auth.login(request,user)
                loginResponse['user'] = user.username
            else:
                loginResponse['error_msg'] = {'pwd':['密码错误！']}
        else:
            loginResponse['error_msg'] = loginForm.errors
        return JsonResponse(loginResponse)
    loginForm = LoginForm(request)
    request.get_full_path()
    next_url = request.GET.get('next', '/index/')
    return render(request, 'login.html', {'loginForm': loginForm, 'next_url': next_url})


@login_required
def log_out(request):
    auth.logout(request)
    return redirect('/login/')


def register(request):
    if request.is_ajax():
        regForm = RegForm(request, request.POST)
        regResponse = {'user': None, 'errors': None}
        if regForm.is_valid():
            reg_dict = {}
            reg_dict['username'] = regForm.cleaned_data.get('user')
            reg_dict['password'] = regForm.cleaned_data.get('pwd')
            reg_dict['email'] = regForm.cleaned_data.get('email')
            avatar_obj = request.FILES.get('file_img')
            if avatar_obj:
                reg_dict['avatar'] = avatar_obj
            UserInfo.objects.create_user(**reg_dict)
            regResponse['user'] = reg_dict['username']
        else:
            regResponse['errors'] = regForm.errors
        return JsonResponse(regResponse)
    regForm = RegForm(request)
    return render(request, 'register.html', {'regForm': regForm})


def index(request):
    current_page = int(request.GET.get('page',1))
    article_list = Article.objects.all().order_by('nid')
    paginator = CustomPagination(current_page, "", article_list, 5)
    return render(request, 'index.html', {'article_list': paginator.res_list, 'page_html': paginator.html})


def home_site(request, username, **kwargs):
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, '404.html')
    blog = user.blog
    article_list = Article.objects.filter(user=user).order_by('nid')
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category__title=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split('/')
            article_list = article_list.filter(create_time__year=year,create_time__month=month)
    current_page = int(request.GET.get('page', 1))
    paginator = CustomPagination(current_page, "", article_list, 5)
    return render(request, 'blog/home_site.html', {'user': user, 'blog': blog, 'article_list': paginator.res_list, 'page_html': paginator.html})


def article_detail(request, username, article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_obj = Article.objects.filter(nid=article_id).first()
    comment_list = Comment.objects.filter(article=article_obj)

    return render(request, 'blog/article_detail.html', {'user': user, 'blog': blog, 'article_obj': article_obj, 'comment_list': comment_list})


def digg(request):
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))
    user_id = request.user.pk
    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
    jsonResponse = {'state': True}
    if not obj:
        res_obj = ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        article_obj = Article.objects.filter(nid=article_id)
        if is_up:
            article_obj.update(up_count=F('up_count')+1)
        else:
            article_obj.update(down_count=F('down_count')+1)
    else:
        jsonResponse['state'] = False
        jsonResponse['handled'] = obj.is_up
    return JsonResponse(jsonResponse)


def comment(request):
    article_id = request.POST.get('article_id')
    pid = request.POST.get('pid')
    content = request.POST.get('content')
    user_id = request.user.pk
    article_obj = Article.objects.filter(nid=article_id).first()

    with transaction.atomic():
        comment_obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content, parent_comment_id=pid)
        Article.objects.filter(nid=article_id).update(comment_count=F('comment_count') + 1)
    jsonResponse = {}
    jsonResponse['create_time'] = comment_obj.create_time.strftime('%Y-%m-%d %X')
    jsonResponse['username'] = request.user.username
    jsonResponse['content'] = content
    jsonResponse['comment_id'] = comment_obj.nid

    # 发送邮件

    from django.core.mail import send_mail
    from blog import settings
    # send_mail(
    #     "您的文章%s新增了一条评论内容"%article_obj.title,
    #     content,
    #     settings.EMAIL_HOST_USER,
    #     ["916852314@qq.com"]
    # )
    import threading
    t = threading.Thread(target=send_mail, args=('您的文章%s新增了一条评论内容' % article_obj.title,
                                                 content,
                                                 settings.EMAIL_HOST_USER,
                                                 ['2580151116@qq.com']))
    t.start()
    return JsonResponse(jsonResponse)


