from django.test import TestCase
from django.urls import reverse
from decimal import Decimal

from .models import Payment


class TestAddBill2Payment(TestCase):
    def test_correct_new_bill(self):
        url = reverse("one_payment", args=[77])
        data = {"card_number": "1111 2223",
                "sum_to_pay": 22.33}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status")
        self.assertContains(response, "order_number")
        payments = Payment.objects.all()
        self.assertEqual(payments.count(), 1)
        payment = payments.first()
        self.assertEqual(payment.order_number, 77)
        self.assertEqual(payment.card_number, "1111 2223")
        self.assertEqual(payment.sum_to_pay, Decimal("22.33"))
        self.assertEqual(payment.status, 0)

    def test_correct_new_bill_int_sum(self):
        url = reverse("one_payment", args=[34])
        data = {"card_number": "1234 5678",
                "sum_to_pay": 22}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "status")
        self.assertContains(response, "order_number")
        payments = Payment.objects.all()
        self.assertEqual(payments.count(), 1)
        payment = payments.first()
        self.assertEqual(payment.order_number, 34)
        self.assertEqual(payment.card_number, "1234 5678")
        self.assertEqual(payment.sum_to_pay, Decimal("22"))
        self.assertEqual(payment.status, 0)

    def test_incorrect_data(self):
        url = reverse("one_payment", args=[34])
        data = {"card_number": "1234 5678",
                "sum_to_pay": -22.4}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")
        self.assertEqual(Payment.objects.count(), 0)

        url = reverse("one_payment", args=[34])
        data = {"card_number": "1234 5678"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")
        self.assertEqual(Payment.objects.count(), 0)

        url = reverse("one_payment", args=[34])
        data = {"card_number": "1234 5678",
                "sum_to_pay": 22.498}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")
        self.assertEqual(Payment.objects.count(), 0)

        url = reverse("one_payment", args=[34])
        data = {"sum_to_pay": 22.4}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")
        self.assertEqual(Payment.objects.count(), 0)

    # запрос с дублирующимся номером счета - ошибка, если в предыдущей записи статус 0
    # или 1, запись добавляется, если статус другой
    def test_double_number_bill(self):
        tmp_bill = Payment.objects.create(order_number=29, card_number="1017 3334",
                                          sum_to_pay=52.6, status=0)
        url = reverse("one_payment", args=[29])
        data = {"card_number": "1111 2223",
                "sum_to_pay": 22.33}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")
        self.assertEqual(Payment.objects.count(), 1)  # tmp_bill

        tmp_bill.status = 1
        tmp_bill.save()
        response = self.client.post(url, data)
        self.assertContains(response, "error")
        self.assertEqual(Payment.objects.count(), 1)  # tmp_bill

        tmp_bill.status = 2
        tmp_bill.save()
        response = self.client.post(url, data)
        self.assertNotContains(response, "error")
        self.assertEqual(Payment.objects.count(), 2)


class TestCheckBill(TestCase):
    @classmethod
    def setUpTestData(cls):
        Payment.objects.create(order_number=29, card_number="8613 3334",
                               sum_to_pay=52.6, status=0)
        Payment.objects.create(order_number=77, card_number="9929 3334",
                               sum_to_pay=523, status=1)
        Payment.objects.create(order_number=34, card_number="7037 3399",
                               sum_to_pay=556.56, status=2)

    def test_existed_bill(self):
        url = reverse("one_payment", args=[29])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "error")
        self.assertContains(response, "status")
        self.assertContains(response, "0")

        url = reverse("one_payment", args=[77])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "error")
        self.assertContains(response, "status")
        self.assertContains(response, "1")

        url = reverse("one_payment", args=[34])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "error")
        self.assertContains(response, "status")
        self.assertContains(response, "2")

    def test_not_existed_bill(self):
        url = reverse("one_payment", args=[92])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")
