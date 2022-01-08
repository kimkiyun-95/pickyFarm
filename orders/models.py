from django.db import models
from core.models import CompressedImageField
from core import url_encryption
from django.utils import timezone


# Create your models here.


class Order_Group(models.Model):

    STATUS = (
        ("wait", "결제대기"),
        ("wait_vbank", "결제대기(가상계좌)"),
        ("payment_complete", "결제완료"),
        ("cancel", "결제취소"),
        ("error_stock", "결제오류(재고부족)"),
        ("error_valid", "결제오류(검증)"),
        ("error_server", "결제오류(서버)"),
        ("error_price_match", "결제오류(총가격 불일치)"),
    )

    status = models.CharField(max_length=20, choices=STATUS, default="wait")
    order_management_number = models.CharField(max_length=1000, null=True, blank=True)
    receipt_number = models.CharField(max_length=60, null=True, blank=True)
    rev_address = models.TextField(null=True, blank=True)
    rev_name = models.CharField(max_length=50, null=True, blank=True)
    rev_phone_number = models.CharField(max_length=30, null=True, blank=True)
    rev_loc_at = models.CharField(max_length=20, null=True, blank=True)
    rev_loc_detail = models.TextField(null=True, blank=True)
    rev_message = models.TextField(null=True, blank=True)
    to_farm_message = models.TextField(null=True, blank=True)

    payment_type = models.CharField(max_length=20, null=True, blank=True)
    v_bank = models.CharField(max_length=200, null=True, blank=True, help_text="가상계좌 은행명")
    v_bank_account = models.CharField(max_length=500, null=True, blank=True, help_text="가상계좌 번호")
    v_bank_account_holder = models.CharField(
        max_length=500, null=True, blank=True, help_text="가삼계좌 예금주"
    )
    v_bank_expire_date = models.DateTimeField(null=True, blank=True, help_text="가상계좌 입금 마감기한")

    total_price = models.IntegerField(null=True, blank=True)
    total_quantity = models.IntegerField(null=True, blank=True)

    is_jeju_mountain = models.BooleanField(default=False)

    order_at = models.DateTimeField(null=True, blank=True)

    update_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    consumer = models.ForeignKey(
        "users.Consumer", related_name="order_groups", on_delete=models.CASCADE
    )

    def __str__(self):
        if self.order_at is None:
            order_at = ""
        else:
            datatime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            order_at = str(timezone.localtime(self.order_at))
            order_at += " 주문"
        title = f"수취인 : {self.rev_name} / 결제자 : {self.consumer.user.account_name} / {order_at}"
        return title


class Order_Detail(models.Model):

    STATUS = (
        ("wait", "결제대기"),
        ("payment_complete", "결제완료"),
        ("preparing", "배송 준비 중"),
        ("shipping", "배송 중"),
        ("delivery_complete", "배송완료"),
        ("cancel", "주문취소"),
        ("re_recept", "환불 접수"),
        ("ex_recept", "교환 접수"),
        ("re_ex_approve", "환불/교환 승인"),
        ("re_ex_deny", "환불/교환 거절"),
        ("error_stock", "결제오류(재고부족)"),
        ("error_valid", "결제오류(검증)"),
        ("error_server", "결제오류(서버)"),
        ("error_price_match", "결제오류(총가격 불일치)"),
    )

    PAYMENT_STATUS = (
        ("none", "결제 이전"),
        ("incoming", "정산예정"),
        ("progress", "정산 진행"),
        ("done", "정산 완료"),
    )

    COMPANY = (
        ("CJ", "CJ대한통운"),
        ("POST", "우체국택배"),
        ("LOGEN", "로젠택배"),
        ("KG", "KG로지스"),
        ("ILYANG", "일양로지스"),
        ("HYUNDAI", "현대택배"),
        ("GTX", "GTX로지스"),
        ("FedEx", "FedEx"),
        ("HANJIN", "한진택배"),
        ("KYUNG", "경동택배"),
        ("LOTTE", "롯데택배"),
        ("HAPDONG", "합동택배"),
    )

    status = models.CharField(max_length=20, choices=STATUS, default="wait", help_text="주문 상태")
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS, default="none", help_text="정산 상태"
    )
    order_management_number = models.CharField(
        max_length=1000, null=True, blank=True, help_text="주문관리번호"
    )

    delivery_service_company = models.CharField(
        max_length=100, choices=COMPANY, null=True, blank=True, help_text="택배회사"
    )
    invoice_number = models.CharField(max_length=30, null=True, blank=True, help_text="운송장 번호")

    quantity = models.IntegerField(help_text="수량")

    total_price = models.IntegerField(help_text="총금액")
    commision_rate = models.FloatField(help_text="수수료율")

    cancel_reason = models.CharField(max_length=30, null=True, blank=True, help_text="주문 취소 사유")

    update_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(
        "products.Product",
        related_name="order_details",
        on_delete=models.CASCADE,
        help_text="구매 상품",
    )
    order_group = models.ForeignKey(
        Order_Group,
        related_name="order_details",
        on_delete=models.SET_NULL,
        null=True,
        help_text="주문 정보 그룹",
    )

    def __str__(self):
        name = []
        name.append(str(self.product.title))
        name.append(str(self.quantity))
        name.append(str(self.status))
        return "-".join(name)

    def encrypt_odmn(self):
        return url_encryption.encode_string_to_url(self.order_management_number)

    def save(self, *args, **kwargs):
        if self.status == "cancel":
            self.payment_status = "none"

        super(Order_Detail, self).save(*args, **kwargs)


class RefundExchange(models.Model):
    TYPE = (
        ("refund", "환불"),
        ("exchange", "교환"),
    )
    STATUS = (
        ("recept", "환불/교환 접수"),
        ("approve", "환불/교환 승인"),
        ("deny", "환불/교환 거절"),
    )
    claim_type = models.CharField(max_length=20, choices=TYPE)
    claim_status = models.CharField(max_length=20, choices=STATUS)

    order_detail = models.ForeignKey(
        "Order_Detail", on_delete=models.PROTECT, related_name="refund_exchanges"
    )
    reason = models.TextField()
    image = CompressedImageField(upload_to="RefundExchange/%Y/%m/%d/", null=True, blank=True)

    farmer_answer = models.TextField(null=True, blank=True)

    rev_address = models.TextField(null=True, blank=True)
    rev_loc_at = models.CharField(max_length=20, null=True, blank=True)
    rev_loc_detail = models.TextField(null=True, blank=True)
    rev_message = models.TextField(null=True, blank=True)

    refund_exchange_delivery_fee = models.IntegerField(null=True, blank=True)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
