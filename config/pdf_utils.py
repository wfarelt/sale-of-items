import logging

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

app_log = logging.getLogger('app')


def render_to_pdf(template_path, context, filename="documento.pdf", base_url=None):
    """Render a Django template to a PDF HttpResponse using WeasyPrint."""
    html_string = render_to_string(template_path, context)
    pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
