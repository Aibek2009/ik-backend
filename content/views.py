from rest_framework import viewsets

from .models import Document, DocumentCategory, Representative, Tender
from .serializers import (
    DocumentCategorySerializer,
    DocumentSerializer,
    RepresentativeSerializer,
    TenderSerializer,
)


class LanguageMixin:
    allowed_languages = {"ru", "en", "ky"}
    default_language = "ru"

    def get_language(self):
        lang = self.request.query_params.get("lang", self.default_language)
        if lang not in self.allowed_languages:
            lang = self.default_language
        return lang

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lang"] = self.get_language()
        return context


class RepresentativeViewSet(LanguageMixin, viewsets.ModelViewSet):
    queryset = Representative.objects.all()
    serializer_class = RepresentativeSerializer


class DocumentCategoryViewSet(LanguageMixin, viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer


class DocumentViewSet(LanguageMixin, viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects.select_related("category").all()

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class TenderViewSet(LanguageMixin, viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
