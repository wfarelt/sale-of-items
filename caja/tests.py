from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import CashBox, CashBoxClosure


class CashBoxModelTests(TestCase):
	def test_create_entry_stores_amount_and_reference(self):
		entry = CashBox.create_entry(
			entry_type=CashBox.TYPE_INCOME,
			amount=Decimal("150.50"),
			description="Ingreso manual",
			reference=CashBox.REFERENCE_EXPENSE,
		)

		self.assertEqual(entry.amount, Decimal("150.50"))
		self.assertEqual(entry.reference, CashBox.REFERENCE_EXPENSE)


class CashBoxClosureTests(TestCase):
	def test_set_opening_balance_and_close_day(self):
		target_date = timezone.localdate()
		CashBoxClosure.set_opening_balance(target_date=target_date, opening_balance=Decimal("100.00"))
		CashBox.create_entry(
			entry_type=CashBox.TYPE_INCOME,
			amount=Decimal("50.00"),
			description="Ingreso manual",
			reference=CashBox.REFERENCE_SALE,
			date=timezone.now(),
		)

		closure = CashBoxClosure.objects.get(date=target_date)
		closure.perform_close()

		self.assertTrue(closure.is_closed)
		self.assertEqual(closure.closing_balance, Decimal("150.00"))

	def test_closed_day_blocks_new_entries(self):
		target_date = timezone.localdate()
		closure = CashBoxClosure.set_opening_balance(target_date=target_date, opening_balance=Decimal("0.00"))
		closure.perform_close()

		with self.assertRaisesMessage(ValidationError, "ya fue cerrada"):
			CashBox.create_entry(
				entry_type=CashBox.TYPE_INCOME,
				amount=Decimal("10.00"),
				description="Ingreso bloqueado",
				reference=CashBox.REFERENCE_SALE,
				date=timezone.now(),
			)
