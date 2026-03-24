import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Document, DocumentCategory, Representative, Tender


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class RepresentativeApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    @staticmethod
    def make_image(name="photo.gif"):
        return SimpleUploadedFile(
            name,
            (
                b"GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
                b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
                b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
            ),
            content_type="image/gif",
        )

    def setUp(self):
        self.representative = Representative.objects.create(
            image=self.make_image(),
            full_name_ru="Иванов Иван Иванович",
            full_name_en="Ivanov Ivan Ivanovich",
            full_name_ky="Иванов Иван Иванович ky",
            role_ru="Полномочный представитель",
            role_en="Authorized Representative",
            role_ky="Ыйгарым укуктуу өкүл",
            order=1,
        )

    def test_list_returns_requested_language(self):
        response = self.client.get(reverse("representative-list"), {"lang": "en"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["full_name"], "Ivanov Ivan Ivanovich")
        self.assertEqual(response.data[0]["role"], "Authorized Representative")
        self.assertNotIn("full_name_ru", response.data[0])

    def test_invalid_language_falls_back_to_russian(self):
        response = self.client.get(reverse("representative-detail", args=[self.representative.id]), {"lang": "de"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "Иванов Иван Иванович")

    def test_ordering_works(self):
        Representative.objects.create(
            image=self.make_image("photo2.gif"),
            full_name_ru="Петров Петр Петрович",
            full_name_en="Petrov Petr Petrovich",
            full_name_ky="Петров Петр Петрович ky",
            role_ru="Заместитель",
            role_en="Deputy",
            role_ky="Орун басар",
            order=2,
        )

        response = self.client.get(reverse("representative-list"))

        self.assertEqual(response.data[0]["order"], 1)
        self.assertEqual(response.data[1]["order"], 2)

    def test_crud_for_representative(self):
        create_response = self.client.post(
            reverse("representative-list"),
            {
                "image": self.make_image("create.gif"),
                "full_name_ru": "Созданный Представитель",
                "full_name_en": "Created Representative",
                "full_name_ky": "Тузулгон екул",
                "role_ru": "Заместитель",
                "role_en": "Deputy",
                "role_ky": "Орун басар",
                "order": 3,
            },
            format="multipart",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        created_id = create_response.data["id"]
        patch_response = self.client.patch(
            reverse("representative-detail", args=[created_id]),
            {"role_ru": "Обновленная роль"},
            format="multipart",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Representative.objects.get(id=created_id).role_ru, "Обновленная роль")

        delete_response = self.client.delete(reverse("representative-detail", args=[created_id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class DocumentApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    @staticmethod
    def make_pdf(name):
        return SimpleUploadedFile(
            name,
            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
            content_type="application/pdf",
        )

    def setUp(self):
        self.category = DocumentCategory.objects.create(
            title_ru="Законы",
            title_en="Laws",
            title_ky="Мыйзамдар",
        )
        self.other_category = DocumentCategory.objects.create(
            title_ru="Приказы",
            title_en="Orders",
            title_ky="Буйруктар",
        )
        self.document = Document.objects.create(
            category=self.category,
            title_ru="Закон о бюджете",
            title_en="Budget Law",
            title_ky="Бюджет мыйзамы",
            file_ru=self.make_pdf("budget_ru.pdf"),
            file_en=self.make_pdf("budget_en.pdf"),
            file_ky=self.make_pdf("budget_ky.pdf"),
        )

    def test_document_list_returns_single_language_and_category(self):
        response = self.client.get(reverse("document-list"), {"lang": "ru"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Закон о бюджете")
        self.assertEqual(response.data[0]["category"]["title"], "Законы")
        self.assertTrue(response.data[0]["file"].endswith(".pdf"))
        self.assertNotIn("title_ru", response.data[0])

    def test_document_filter_by_category(self):
        Document.objects.create(
            category=self.other_category,
            title_ru="Приказ 1",
            title_en="Order 1",
            title_ky="Буйрук 1",
            file_ru=self.make_pdf("order_ru.pdf"),
            file_en=self.make_pdf("order_en.pdf"),
            file_ky=self.make_pdf("order_ky.pdf"),
        )

        response = self.client.get(reverse("document-list"), {"category": self.category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.document.id)

    def test_only_pdf_is_allowed(self):
        response = self.client.post(
            reverse("document-list"),
            {
                "category": self.category.id,
                "title_ru": "Текст",
                "title_en": "Text",
                "title_ky": "Текст ky",
                "file_ru": SimpleUploadedFile("bad.txt", b"abc", content_type="text/plain"),
                "file_en": self.make_pdf("ok_en.pdf"),
                "file_ky": self.make_pdf("ok_ky.pdf"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file_ru", response.data)

    def test_document_crud(self):
        create_response = self.client.post(
            reverse("document-list"),
            {
                "category": self.category.id,
                "title_ru": "Новый документ",
                "title_en": "New document",
                "title_ky": "Жаңы документ",
                "file_ru": self.make_pdf("new_ru.pdf"),
                "file_en": self.make_pdf("new_en.pdf"),
                "file_ky": self.make_pdf("new_ky.pdf"),
            },
            format="multipart",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        document_id = create_response.data["id"]
        update_response = self.client.patch(
            reverse("document-detail", args=[document_id]),
            {"title_en": "Updated document"},
            format="multipart",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.get(id=document_id).title_en, "Updated document")

        delete_response = self.client.delete(reverse("document-detail", args=[document_id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_category_crud_and_language(self):
        create_response = self.client.post(
            reverse("document-category-list"),
            {
                "title_ru": "Положения",
                "title_en": "Regulations",
                "title_ky": "Жоболор",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        category_id = create_response.data["id"]
        detail_response = self.client.get(reverse("document-category-detail", args=[category_id]), {"lang": "ky"})
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["title"], "Жоболор")

        delete_response = self.client.delete(reverse("document-category-detail", args=[category_id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)


class TenderApiTests(APITestCase):
    def setUp(self):
        self.tender = Tender.objects.create(
            title_ru="Закупка оборудования",
            title_en="Equipment procurement",
            title_ky="Жабдууларды сатып алуу",
            description_ru="Закупка компьютерной техники",
            description_en="Procurement of computer equipment",
            description_ky="Компьютердик техниканы сатып алуу",
            amount="500000.00",
            deadline=timezone.localdate() + timedelta(days=5),
        )

    def test_tender_returns_language_and_is_active(self):
        response = self.client.get(reverse("tender-list"), {"lang": "en"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Equipment procurement")
        self.assertEqual(response.data[0]["description"], "Procurement of computer equipment")
        self.assertTrue(response.data[0]["is_active"])

    def test_is_active_is_false_for_past_deadline(self):
        self.tender.deadline = timezone.localdate() - timedelta(days=1)
        self.tender.save()

        response = self.client.get(reverse("tender-detail", args=[self.tender.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])

    def test_tender_crud(self):
        create_response = self.client.post(
            reverse("tender-list"),
            {
                "title_ru": "Новый тендер",
                "title_en": "New tender",
                "title_ky": "Жаны тендер",
                "description_ru": "Описание",
                "description_en": "Description",
                "description_ky": "Сыпаттама",
                "amount": "1000.50",
                "deadline": str(timezone.localdate() + timedelta(days=10)),
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        tender_id = create_response.data["id"]
        update_response = self.client.put(
            reverse("tender-detail", args=[tender_id]),
            {
                "title_ru": "Новый тендер updated",
                "title_en": "New tender updated",
                "title_ky": "Жаны тендер updated",
                "description_ru": "Описание updated",
                "description_en": "Description updated",
                "description_ky": "Сыпаттама updated",
                "amount": "2000.00",
                "deadline": str(timezone.localdate() + timedelta(days=20)),
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(Tender.objects.get(id=tender_id).amount), "2000.00")

        delete_response = self.client.delete(reverse("tender-detail", args=[tender_id]))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)


class SwaggerTests(APITestCase):
    def test_schema_endpoint_is_available(self):
        response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_ui_endpoint_is_available(self):
        response = self.client.get(reverse("swagger-ui"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

# Create your tests here.
