from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class CashBox(models.Model):
	TYPE_INCOME = "ingreso"
	TYPE_EXPENSE = "egreso"
	TYPE_CHOICES = (
		(TYPE_INCOME, "Ingreso"),
		(TYPE_EXPENSE, "Egreso"),
	)

	REFERENCE_SALE = "venta"
	REFERENCE_PURCHASE = "compra"
	REFERENCE_EXPENSE = "gasto"
	REFERENCE_CHOICES = (
		(REFERENCE_SALE, "Venta"),
		(REFERENCE_PURCHASE, "Compra"),
		(REFERENCE_EXPENSE, "Gasto"),
	)

	PAYMENT_METHOD_CASH = "cash"
	PAYMENT_METHOD_QR = "qr"
	PAYMENT_METHOD_TRANSFER = "transferencia"
	PAYMENT_METHOD_NA = "no_aplica"
	PAYMENT_METHOD_CHOICES = (
		(PAYMENT_METHOD_CASH, "Efectivo"),
		(PAYMENT_METHOD_QR, "QR"),
		(PAYMENT_METHOD_TRANSFER, "Transferencia"),
		(PAYMENT_METHOD_NA, "No aplica"),
	)

	date = models.DateTimeField(default=timezone.now, verbose_name="Fecha")
	type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Tipo")
	amount = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		validators=[MinValueValidator(0.01)],
		verbose_name="Monto",
	)
	description = models.TextField(verbose_name="Descripcion")
	reference = models.CharField(max_length=20, choices=REFERENCE_CHOICES, verbose_name="Referencia")
	payment_method = models.CharField(
		max_length=20,
		choices=PAYMENT_METHOD_CHOICES,
		default=PAYMENT_METHOD_NA,
		verbose_name="Medio de pago",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date", "-id"]
		verbose_name = "Movimiento de caja"
		verbose_name_plural = "Movimientos de caja"

	def __str__(self):
		return f"{self.get_type_display()} - Bs {self.amount:.2f}"

	def clean(self):
		self.validate_day_open(self.date)

	@staticmethod
	def resolve_business_date(entry_date=None):
		entry_date = entry_date or timezone.now()
		if hasattr(entry_date, "hour"):
			if timezone.is_aware(entry_date):
				entry_date = timezone.localtime(entry_date)
			return entry_date.date()
		return entry_date

	@classmethod
	def validate_day_open(cls, entry_date=None):
		business_date = cls.resolve_business_date(entry_date)
		qs = CashBoxClosure.objects.filter(date=business_date, is_closed=True)
		if qs.exists():
			raise ValidationError(f"La caja del {business_date.strftime('%d/%m/%Y')} ya fue cerrada.")
		return business_date

	@classmethod
	def create_entry(cls, *, entry_type, amount, description, reference, date=None, payment_method=None):
		cls.validate_day_open(date)
		return cls.objects.create(
			date=date or timezone.now(),
			type=entry_type,
			amount=amount,
			description=description,
			reference=reference,
			payment_method=payment_method or cls.PAYMENT_METHOD_NA,
		)

	@classmethod
	def register_sale(cls, sale):
		return cls.create_entry(
			entry_type=cls.TYPE_INCOME,
			amount=sale.total,
			description=f"Ingreso por venta #{sale.pk} al cliente {sale.client.name}",
			reference=cls.REFERENCE_SALE,
			date=sale.date,
			payment_method=sale.payment_type,
		)

	@classmethod
	def register_sale_reversal(cls, sale):
		return cls.create_entry(
			entry_type=cls.TYPE_EXPENSE,
			amount=sale.total,
			description=f"Reversion de ingreso por eliminacion de venta #{sale.pk}",
			reference=cls.REFERENCE_SALE,
			payment_method=sale.payment_type,
		)

	@classmethod
	def register_purchase(cls, purchase):
		return cls.create_entry(
			entry_type=cls.TYPE_EXPENSE,
			amount=purchase.total,
			description=f"Egreso por compra #{purchase.pk} al proveedor {purchase.supplier}",
			reference=cls.REFERENCE_PURCHASE,
			date=purchase.date,
		)

	@classmethod
	def register_purchase_reversal(cls, purchase):
		return cls.create_entry(
			entry_type=cls.TYPE_INCOME,
			amount=purchase.total,
			description=f"Reversion de egreso por eliminacion de compra #{purchase.pk}",
			reference=cls.REFERENCE_PURCHASE,
		)


class CashBoxClosure(models.Model):
	date = models.DateField(verbose_name="Fecha")
	opening_balance = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		default=Decimal("0.00"),
		validators=[MinValueValidator(0)],
		verbose_name="Saldo inicial",
	)
	total_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Ingresos")
	total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Egresos")
	closing_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Saldo de cierre")
	is_closed = models.BooleanField(default=False, verbose_name="Cerrada")
	closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de cierre")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		verbose_name = "Cierre diario de caja"
		verbose_name_plural = "Cierres diarios de caja"
		unique_together = [("date",)]

	def __str__(self):
		return f"Caja {self.date.strftime('%d/%m/%Y')}"

	@property
	def current_balance(self):
		return self.opening_balance + self.total_income - self.total_expense

	@classmethod
	def get_suggested_opening_balance(cls, target_date):
		previous_closure = cls.objects.filter(date__lt=target_date, is_closed=True).order_by("-date").first()
		if previous_closure:
			return previous_closure.closing_balance

		previous_day = cls.objects.filter(date__lt=target_date).order_by("-date").first()
		if previous_day:
			return previous_day.closing_balance or previous_day.opening_balance

		return Decimal("0.00")

	@classmethod
	def get_day_summary(cls, target_date):
		closure = cls.objects.filter(date=target_date).first()
		opening_balance = closure.opening_balance if closure else cls.get_suggested_opening_balance(target_date)
		entries = CashBox.objects.filter(date__date=target_date)
		income_total = entries.filter(type=CashBox.TYPE_INCOME).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
		expense_total = entries.filter(type=CashBox.TYPE_EXPENSE).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
		current_balance = opening_balance + income_total - expense_total
		return {
			"closure": closure,
			"opening_balance": opening_balance,
			"income_total": income_total,
			"expense_total": expense_total,
			"current_balance": current_balance,
			"is_closed": closure.is_closed if closure else False,
			"closed_at": closure.closed_at if closure else None,
			"closing_balance": closure.closing_balance if closure else current_balance,
		}

	@classmethod
	def set_opening_balance(cls, *, target_date, opening_balance):
		closure, _ = cls.objects.get_or_create(
			date=target_date,
			defaults={
				"opening_balance": opening_balance,
				"closing_balance": opening_balance,
			},
		)
		if closure.is_closed:
			raise ValidationError(f"La caja del {target_date.strftime('%d/%m/%Y')} ya fue cerrada.")

		closure.opening_balance = opening_balance
		closure.refresh_totals(save=True)
		return closure

	def refresh_totals(self, save=False):
		summary = self.get_day_summary(self.date)
		self.total_income = summary["income_total"]
		self.total_expense = summary["expense_total"]
		self.closing_balance = summary["current_balance"]
		if save:
			self.save(update_fields=["opening_balance", "total_income", "total_expense", "closing_balance", "updated_at"])
		return self

	def perform_close(self):
		if self.is_closed:
			raise ValidationError(f"La caja del {self.date.strftime('%d/%m/%Y')} ya fue cerrada.")

		self.refresh_totals()
		self.is_closed = True
		self.closed_at = timezone.now()
		self.save(update_fields=["opening_balance", "total_income", "total_expense", "closing_balance", "is_closed", "closed_at", "updated_at"])
		return self
