import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify


def generate_unique_slug(model_class, title, slug_field='slug'):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
    return slug


def generate_qr_code(data: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return File(buffer, name=f'qr_{uuid.uuid4().hex}.png')


def paginate_queryset(queryset, request, page_size=20):
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    result_page = paginator.paginate_queryset(queryset, request)
    return result_page, paginator


def format_currency(amount, currency='USD'):
    return f'{currency} {amount:,.2f}'