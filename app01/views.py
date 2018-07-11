from django.shortcuts import render,HttpResponse,redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app01.myform import *
from app01.models import *
from app01.page import *
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO

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
    article_list = Article.objects.all()
    paginator = CustomPagination(current_page, "", article_list, 5)
    return render(request, 'index.html', {'article_list': paginator.res_list, 'page_html': paginator.html})


def home_site(request, username, **kwargs):
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, '404.html')
    blog = user.blog
    article_list = Article.objects.filter(user=user)
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
    return render(request, 'home_site.html')