from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


def validate_pdf(uploaded_file):
    content_type = getattr(uploaded_file, "content_type", None)
    if content_type and content_type != "application/pdf":
        raise ValidationError("Only PDF files are allowed.")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Representative(TimeStampedModel):
    image = models.FileField(upload_to="representatives/")
    full_name_ru = models.CharField(max_length=255)
    full_name_en = models.CharField(max_length=255)
    full_name_ky = models.CharField(max_length=255)
    role_ru = models.CharField(max_length=255)
    role_en = models.CharField(max_length=255)
    role_ky = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Представитель"
        verbose_name_plural = "Представители"

    def __str__(self):
        return self.full_name_ru


class DocumentCategory(TimeStampedModel):
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_ky = models.CharField(max_length=255)

    class Meta:
        ordering = ["id"]
        verbose_name = "Категория документа"
        verbose_name_plural = "Категории документов"

    def __str__(self):
        return self.title_ru


class Document(TimeStampedModel):
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_ky = models.CharField(max_length=255)
    file_ru = models.FileField(
        upload_to="documents/",
        validators=[FileExtensionValidator(["pdf"]), validate_pdf],
    )
    file_en = models.FileField(
        upload_to="documents/",
        validators=[FileExtensionValidator(["pdf"]), validate_pdf],
    )
    file_ky = models.FileField(
        upload_to="documents/",
        validators=[FileExtensionValidator(["pdf"]), validate_pdf],
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return self.title_ru


class Tender(TimeStampedModel):
    title_ru = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    title_ky = models.CharField(max_length=255)
    description_ru = models.TextField()
    description_en = models.TextField()
    description_ky = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateField()

    class Meta:
        ordering = ["deadline", "id"]
        verbose_name = "Тендер"
        verbose_name_plural = "Тендеры"

    def __str__(self):
        return self.title_ru

    @property
    def is_active(self):
        return self.deadline >= timezone.localdate()
