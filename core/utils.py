import os
from datetime import datetime

import qrcode
import barcode
from barcode.writer import ImageWriter
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone


def generate_tracking_id(prefix='CMS', country='TZ'):
    year = timezone.now().year
    table_name = 'core_trackingidsequence'

    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS %s (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix VARCHAR(10) NOT NULL,
                country VARCHAR(5) NOT NULL,
                year INTEGER NOT NULL,
                current_value INTEGER NOT NULL DEFAULT 0,
                UNIQUE(prefix, country, year)
            )
            """ % table_name
        )

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO %s (prefix, country, year, current_value)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT(prefix, country, year)
                DO UPDATE SET current_value = current_value + 1
                RETURNING current_value
                """ % table_name,
                [prefix, country, year],
            )
            row = cursor.fetchone()
            seq_number = row[0] if row else 1

    return f"{prefix}-{country}-{year}-{seq_number:08d}"


def generate_document_number(prefix, year=None):
    if year is None:
        year = timezone.now().year

    table_name = 'core_documentnumbersequence'

    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS %s (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefix VARCHAR(20) NOT NULL,
                year INTEGER NOT NULL,
                current_value INTEGER NOT NULL DEFAULT 0,
                UNIQUE(prefix, year)
            )
            """ % table_name
        )

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO %s (prefix, year, current_value)
                VALUES (%s, %s, 1)
                ON CONFLICT(prefix, year)
                DO UPDATE SET current_value = current_value + 1
                RETURNING current_value
                """ % table_name,
                [prefix, year],
            )
            row = cursor.fetchone()
            seq_number = row[0] if row else 1

    return f"{prefix}-{year}-{seq_number:07d}"


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def generate_qr_code(data, filename):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(upload_dir, exist_ok=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')

    file_path = os.path.join(upload_dir, filename)
    img.save(file_path)

    return os.path.join('qrcodes', filename)


def generate_barcode(code_string, filename):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'barcodes')
    os.makedirs(upload_dir, exist_ok=True)

    code_class = barcode.get_barcode_class('code128')
    code = code_class(code_string, writer=ImageWriter())

    file_path = os.path.join(upload_dir, filename)
    saved_path = code.save(file_path)

    relative_path = os.path.relpath(saved_path, settings.MEDIA_ROOT)
    return relative_path


def format_currency(amount, currency='TZS'):
    if amount is None:
        amount = 0

    formatted = f"{amount:,.2f}"

    currency_symbols = {
        'TZS': 'TZS',
        'USD': '$',
        'KES': 'KES',
        'UGX': 'UGX',
    }
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol} {formatted}"


def calculate_volumetric_weight(length, width, height, divisor=5000):
    if not all([length, width, height]):
        return 0.0
    if divisor <= 0:
        return 0.0
    return (length * width * height) / divisor
