from django.db import models
from django.db.models import Count

from eums.models import SalesOrder, DistributionPlanNode, PurchaseOrderItem


class PurchaseOrderManager(models.Manager):
    def for_direct_delivery(self):
        return self.model.objects.annotate(release_order_count=Count('release_orders')).filter(release_order_count=0)

    @staticmethod
    def for_consignee(consignee_id):
        order_item_ids = DistributionPlanNode.objects.filter(consignee__id=consignee_id).values_list('item', flat=True)
        order_ids = PurchaseOrderItem.objects.filter(id__in=order_item_ids).values_list('purchase_order')
        return PurchaseOrder.objects.filter(id__in=order_ids)


class PurchaseOrder(models.Model):
    order_number = models.IntegerField(unique=True)
    sales_order = models.ForeignKey(SalesOrder)
    date = models.DateField(auto_now=False, null=True)
    objects = PurchaseOrderManager()

    def has_plan(self):
        return DistributionPlanNode.objects.filter(item__in=self.purchaseorderitem_set.all()).exists()

    class Meta:
        app_label = 'eums'

    def __unicode__(self):
        return "%s - %s, %s %s" % (
            self.sales_order.programme.name, self.sales_order.description, self.order_number, str(self.date))
