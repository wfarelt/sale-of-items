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


@register.filter(name="delivery_status_es")
def delivery_status_es(value):
    status = _normalize_status(value)
    return {"DELIVERED": "Entregada", "PENDING": "Pendiente"}.get(status, value)


@register.filter(name="delivery_status_badge_class")
def delivery_status_badge_class(value):
    return "text-bg-primary" if _normalize_status(value) == "DELIVERED" else "text-bg-secondary"


@register.filter(name="sale_status_es")
def sale_status_es(value):
    status = _normalize_status(value)
    mapping = {
        "PROFORMA": "Proforma",
        "EXECUTED": "Ejecutada",
        "CANCELLED": "Anulada",
        "RESERVED": "Reservada",
        "ORDERED": "Pedido",
    }
    return mapping.get(status, value)


@register.filter(name="sale_status_badge_class")
def sale_status_badge_class(value):
    status = _normalize_status(value)
    if status == "EXECUTED":
        return "text-bg-success"
    if status == "CANCELLED":
        return "text-bg-danger"
    if status == "PROFORMA":
        return "text-bg-warning text-dark"
    if status == "RESERVED":
        return "text-bg-info text-dark"
    if status == "ORDERED":
        return "text-bg-secondary"
    return "text-bg-secondary"
