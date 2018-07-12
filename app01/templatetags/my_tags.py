from django import template
from django.db.models import Count
from app01.models import *
register = template.Library()

@register.inclusion_tag('blog/classification.html')
def get_classification_style(user,blog):
    cate_list = Category.objects.filter(blog=blog).values('nid').annotate(c=Count('article__nid')).values_list('title', 'c')
    tag_list = Tag.objects.filter(blog=blog).values('nid').annotate(c=Count('article__nid')).values_list('title', 'c')
    date_list = Article.objects.filter(user=user).extra(select={'y_m_date': 'date_format(create_time, "%%Y/%%m")'}).values('y_m_date').annotate(c=Count('nid')).values_list('y_m_date', 'c')

    return {'user': user, 'cate_list': cate_list, 'date_list': date_list, 'tag_list': tag_list}
