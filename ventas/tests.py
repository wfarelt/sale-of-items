from decimal import Decimal

from django.test import SimpleTestCase
from django.utils import timezone

from .models import Sale, SaleDetail


class SaleDetailSubtotalTests(SimpleTestCase):
	def test_subtotal_returns_zero_when_quantity_and_price_are_none(self):
		detail = SaleDetail(quantity=None, price=None, discount=None)

		self.assertEqual(detail.subtotal(), Decimal("0.00"))

	def test_subtotal_never_returns_negative_values(self):
		detail = SaleDetail(quantity=Decimal("1.00"), price=Decimal("10.00"), discount=Decimal("15.00"))

		self.assertEqual(detail.subtotal(), Decimal("0.00"))


class SaleStatusTests(SimpleTestCase):
	def test_normalize_status_value_converts_legacy_values(self):
		self.assertEqual(Sale.normalize_status_value("confirmada"), Sale.STATUS_EXECUTED)
		self.assertEqual(Sale.normalize_status_value("confirmed"), Sale.STATUS_EXECUTED)
		self.assertEqual(Sale.normalize_status_value("anulada"), Sale.STATUS_CANCELLED)
		self.assertEqual(Sale.normalize_status_value("delivered"), Sale.STATUS_EXECUTED)

	def test_delivery_status_is_pending_without_delivery_date(self):
		sale = Sale()

		self.assertEqual(sale.delivery_status, Sale.DELIVERY_STATUS_PENDING)

	def test_delivery_status_is_delivered_with_delivery_date(self):
		sale = Sale(delivered_at=timezone.now())

		self.assertEqual(sale.delivery_status, Sale.DELIVERY_STATUS_DELIVERED)
