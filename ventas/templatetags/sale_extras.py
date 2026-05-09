from django import template

register = template.Library()


def _normalize_status(value):
    if value is None:
        return ""
    return str(value).strip().upper()


@register.filter(name="payment_status_es")
def payment_status_es(value):
    status = _normalize_status(value)
    mapping = {
        "PAID": "Pagado",
        "PARTIAL": "Parcial",
        "PENDING": "Pendiente",
    }
    return mapping.get(status, value)


@register.filter(name="payment_status_badge_class")
def payment_status_badge_class(value):
    status = _normalize_status(value)
    if status == "PAID":
        return "text-bg-success"
    if status == "PARTIAL":
        return "text-bg-warning text-dark"
    return "text-bg-secondary"


@register.filter(name="sale_status_es")
def sale_status_es(value):
    status = _normalize_status(value)
    mapping = {
        "PROFORMA": "Proforma",
        "DRAFT": "Proforma",
        "CONFIRMADA": "Confirmada",
        "CONFIRMED": "Confirmada",
        "ANULADA": "Anulada",
        "CANCELED": "Anulada",
        "CANCELLED": "Anulada",
        "RESERVED": "Reservada",
        "ORDERED": "Pedido",
        "DELIVERED": "Entregada",
    }
    return mapping.get(status, value)


@register.filter(name="sale_status_badge_class")
def sale_status_badge_class(value):
    status = _normalize_status(value)
    if status in {"CONFIRMADA", "CONFIRMED"}:
        return "text-bg-success"
    if status in {"ANULADA", "CANCELED", "CANCELLED"}:
        return "text-bg-danger"
    if status in {"PROFORMA", "DRAFT"}:
        return "text-bg-warning text-dark"
    if status == "RESERVED":
        return "text-bg-info text-dark"
    if status == "ORDERED":
        return "text-bg-secondary"
    if status == "DELIVERED":
        return "text-bg-primary"
    return "text-bg-secondary"
