from rest_framework import serializers

from .models import Document, DocumentCategory, Representative, Tender


class TranslatedFieldsMixin:
    default_language = "ru"

    def get_language(self):
        return self.context.get("lang", self.default_language)

    def translated_value(self, obj, field_name):
        return getattr(obj, f"{field_name}_{self.get_language()}")

    def absolute_file_url(self, field):
        if not field:
            return None
        request = self.context.get("request")
        url = field.url
        return request.build_absolute_uri(url) if request else url


class RepresentativeSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Representative
        fields = (
            "id",
            "image",
            "full_name_ru",
            "full_name_en",
            "full_name_ky",
            "role_ru",
            "role_en",
            "role_ky",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            "full_name_ru": {"write_only": True},
            "full_name_en": {"write_only": True},
            "full_name_ky": {"write_only": True},
            "role_ru": {"write_only": True},
            "role_en": {"write_only": True},
            "role_ky": {"write_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "image": self.absolute_file_url(instance.image),
            "full_name": self.translated_value(instance, "full_name"),
            "role": self.translated_value(instance, "role"),
            "order": instance.order,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }


class DocumentCategorySerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ("id", "title_ru", "title_en", "title_ky", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            "title_ru": {"write_only": True},
            "title_en": {"write_only": True},
            "title_ky": {"write_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": self.translated_value(instance, "title"),
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }


class DocumentSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "id",
            "category",
            "title_ru",
            "title_en",
            "title_ky",
            "file_ru",
            "file_en",
            "file_ky",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            "title_ru": {"write_only": True},
            "title_en": {"write_only": True},
            "title_ky": {"write_only": True},
            "file_ru": {"write_only": True},
            "file_en": {"write_only": True},
            "file_ky": {"write_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "category": {
                "id": instance.category_id,
                "title": self.translated_value(instance.category, "title"),
            },
            "title": self.translated_value(instance, "title"),
            "file": self.absolute_file_url(getattr(instance, f"file_{self.get_language()}")),
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }


class TenderSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = (
            "id",
            "title_ru",
            "title_en",
            "title_ky",
            "description_ru",
            "description_en",
            "description_ky",
            "amount",
            "deadline",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            "title_ru": {"write_only": True},
            "title_en": {"write_only": True},
            "title_ky": {"write_only": True},
            "description_ru": {"write_only": True},
            "description_en": {"write_only": True},
            "description_ky": {"write_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": self.translated_value(instance, "title"),
            "description": self.translated_value(instance, "description"),
            "amount": instance.amount,
            "deadline": instance.deadline,
            "is_active": instance.is_active,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
