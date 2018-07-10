from django.contrib import admin
from app01.models import *

# Register your models here.

admin.site.register(UserInfo)
admin.site.register(Blog)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(ArticleUpDown)
admin.site.register(Article2Tag)
admin.site.register(Comment)
