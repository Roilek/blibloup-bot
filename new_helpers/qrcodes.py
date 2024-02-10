from io import BytesIO

import pyqrcode



def qr_from_text(text: str) -> bytes:
    """Returns a qr code image from a text"""
    qr = pyqrcode.create(text)
    img = BytesIO()
    qr.png(img, scale=8)
    return img.getvalue()


def vcard_from_dict(vcard_dict: dict) -> bytes:
    """Returns a qr code image a VCard from a dictionary"""
    vcard_str = 'BEGIN:VCARD\n' + '\n'.join([f'{key}:{value}' for key, value in vcard_dict.items()]) + '\nEND:VCARD'
    qr = pyqrcode.create(vcard_str)
    img = BytesIO()
    qr.png(img, scale=8)
    return img.getvalue()


def wifi_qr(ssid: str, password: str, security: str = 'WPA') -> bytes:
    """Returns a qr code image for a wifi connection"""
    wifi_str = f'WIFI:T:{security};S:{ssid};P:{password};;'
    qr = pyqrcode.create(wifi_str)
    img = BytesIO()
    qr.png(img, scale=8)
    return img.getvalue()


