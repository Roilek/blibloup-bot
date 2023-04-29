from io import BytesIO

import pyqrcode


def vcard_from_dict(vcard_dict: dict) -> bytes:
    """Returns a qr code image a VCard from a dictionary"""
    vcard_str = 'BEGIN:VCARD\n' + '\n'.join([f'{key}:{value}' for key, value in vcard_dict.items()]) + '\nEND:VCARD'
    qr_code = pyqrcode.create(vcard_str)
    qr_code_buffer = BytesIO()
    qr_code.png(qr_code_buffer, scale=8)
    qr_code_buffer.seek(0)
    return qr_code_buffer.getvalue()


def qr_from_text(text: str) -> bytes:
    """Returns a qr code image from a text"""
    qr_code = pyqrcode.create(text)
    qr_code_buffer = BytesIO()
    qr_code.png(qr_code_buffer, scale=8)
    qr_code_buffer.seek(0)
    return qr_code_buffer.getvalue()
