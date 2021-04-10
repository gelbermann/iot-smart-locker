from django import template

from iot_smart_locker_no_docker.lockers.models import QR

register = template.Library()


@register.filter(name="svg_inline")
def qr_svg_inline(qr: QR, scale: int):
    return qr.qr.svg_inline(scale=scale)
