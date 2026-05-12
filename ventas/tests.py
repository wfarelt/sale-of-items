from decimal import Decimal

from django.test import SimpleTestCase

from .models import SaleDetail


class SaleDetailSubtotalTests(SimpleTestCase):
	def test_subtotal_returns_zero_when_quantity_and_price_are_none(self):
		detail = SaleDetail(quantity=None, price=None, discount=None)

		self.assertEqual(detail.subtotal(), Decimal("0.00"))

	def test_subtotal_never_returns_negative_values(self):
		detail = SaleDetail(quantity=Decimal("1.00"), price=Decimal("10.00"), discount=Decimal("15.00"))

		self.assertEqual(detail.subtotal(), Decimal("0.00"))
