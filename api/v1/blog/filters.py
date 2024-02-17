from django_filters import rest_framework as filters

from blog.models import News


class NewsFilter(filters.FilterSet):
    # category_slug = filters.CharFilter(lookup_expr='icontains')
    # tags_slug = filters.NumberFilter(lookup_expr='gte')
    # status = filters.NumberFilter(lookup_expr='gte')
    # draft = filters.BooleanFilter(lookup_expr='lte')

    class Meta:
        model = News
        fields = ['category__slug', 'tags__slug', 'status', 'draft', ]
