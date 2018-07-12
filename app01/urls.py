from django.urls import path,re_path
from app01 import views as app_views

urlpatterns = [
    # 文本编辑器上传图片url
    # re_path(r'upload/', app_views.upload),

    # 后台管理 url
    # re_path(r'blog_manage/$', app_views.blog_manage),
    # re_path(r'blog_manage/add_article/$', app_views.add_article),
    re_path(r'digg/', app_views.digg),
    re_path(r'comment/', app_views.comment),
    # re_path(r'get_comment_tree/', app_views.get_comment_tree),
    #
    re_path(r'^(?P<username>\w+)/articles/(?P<article_id>\d+)$', app_views.article_detail),
    re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', app_views.home_site),
    re_path(r'^(?P<username>\w+)/$', app_views.home_site),


]