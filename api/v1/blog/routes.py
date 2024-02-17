from rest_framework import routers

from .views import AccountViewSet, NewsViewSet, CurrencyViewSet, CategoryViewSet, TagsViewSet

router = routers.SimpleRouter()
router.register(r'users', AccountViewSet)
router.register(r'news/list', NewsViewSet, basename='news')
router.register(r'currency', CurrencyViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'tags', TagsViewSet)
urlpatterns = router.urls
