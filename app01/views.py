from django.shortcuts import render,HttpResponse
from django.contrib import auth
from django.http import JsonResponse
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
    font = ImageFont.truetype('book_app/static/kumo.ttf', 32)
    valid_code_str = ''
    for i in range(1, 6):
        char = get_random_char()
        valid_code_str += char
        draw.text([i * 40, 5], char, get_random_color(), font=font)
    f = BytesIO()
    image.save(f, 'png')
    data = f.getvalue()
    print(valid_code_str)
    request.session['valid_code_str'] = valid_code_str
    return HttpResponse(data)

def log_in(request):
    pass

def log_out(request):
    pass

def register(request):
    pass


