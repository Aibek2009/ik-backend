from rest_framework.routers import DefaultRouter

from .views import (
    DocumentCategoryViewSet,
    DocumentViewSet,
    RepresentativeViewSet,
    TenderViewSet,
)

router = DefaultRouter()
router.register("representatives", RepresentativeViewSet, basename="representative")
router.register("document-categories", DocumentCategoryViewSet, basename="document-category")
router.register("documents", DocumentViewSet, basename="document")
router.register("tenders", TenderViewSet, basename="tender")

urlpatterns = router.urls
