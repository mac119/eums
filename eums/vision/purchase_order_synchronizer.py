from itertools import groupby
from operator import itemgetter

from django.core.exceptions import ObjectDoesNotExist

from eums.models import PurchaseOrder, SalesOrder, PurchaseOrderItem, Item
from eums.settings import VISION_URL
from eums.vision.order_synchronizer import OrderSynchronizer
from eums.vision.vision_data_synchronizer import VisionException


class PurchaseOrderSynchronizer(OrderSynchronizer):
    PURCHASE_ORDER_URL = VISION_URL + 'GetPurchaseOrderInfo_JSON/'
    REQUIRED_KEYS = ('PO_NUMBER', 'PO_ITEM', 'PO_TYPE', 'MATERIAL_CODE', 'MATERIAL_DESC', 'AMOUNT_USD',
                     'PO_ITEM_QTY', 'SO_NUMBER', 'PREQ_ITEM', 'UPDATE_DATE')
    SUPPORTED_PO_TYPE = ['NB', 'ZLC', 'ZUB', 'ZOC']

    def __init__(self, start_date, end_date=''):
        super(PurchaseOrderSynchronizer, self).__init__(PurchaseOrderSynchronizer.PURCHASE_ORDER_URL, start_date,
                                                        end_date)

    def _get_or_create_order(self, record):
        try:
            purchase_order = PurchaseOrder.objects.get(order_number=record['PO_NUMBER'])
            return self._update_order(purchase_order, record['UPDATE_DATE'], record['PO_TYPE'])
        except ObjectDoesNotExist:
            try:
                sales_order = SalesOrder.objects.get(order_number=record['SO_NUMBER'])
                return PurchaseOrder.objects.create(order_number=record['PO_NUMBER'],
                                                    sales_order=sales_order,
                                                    date=record['UPDATE_DATE'],
                                                    po_type=record['PO_TYPE'])
            except ObjectDoesNotExist:
                pass
        except Exception, e:
            raise VisionException(message='Get or create purchase order error: ' + e.message)

    def _update_or_create_item(self, record, order):
        sales_order_items = order.sales_order.salesorderitem_set.filter(item_number=record['PREQ_ITEM'])
        sales_order_item = sales_order_items[0] if sales_order_items else None
        try:
            purchase_order_item = PurchaseOrderItem.objects.get(purchase_order__order_number=order.order_number,
                                                                item_number=record['PO_ITEM'],
                                                                sales_order_item=sales_order_item)
            return self._update_item(purchase_order_item, record['PO_ITEM_QTY'], record['AMOUNT_USD'])
        except ObjectDoesNotExist:
            item, _ = Item.objects.get_or_create(material_code=record['MATERIAL_CODE'],
                                                 description=record['MATERIAL_DESC'])
            return PurchaseOrderItem.objects.get_or_create(purchase_order=order,
                                                           item=item,
                                                           item_number=record['PO_ITEM'],
                                                           sales_order_item=sales_order_item,
                                                           quantity=record['PO_ITEM_QTY'],
                                                           value=record['AMOUNT_USD'])
        except Exception, e:
            raise VisionException(message='Update or create purchase order item error: ' + e.message)

    @staticmethod
    def _update_order(order, po_date, po_type):
        order.date = po_date
        order.po_type = po_type
        order.save()
        return order

    @staticmethod
    def _update_item(item, quantity, value):
        item.quantity = quantity
        item.value = value
        item.save()
        return item

    @staticmethod
    def _filter_records(records):
        def is_valid_record(record):
            for key in PurchaseOrderSynchronizer.REQUIRED_KEYS:
                if not record[key] \
                        or key == 'PO_TYPE' and not record[key] in PurchaseOrderSynchronizer.SUPPORTED_PO_TYPE:
                    return False
            return True

        return filter(is_valid_record, records)

    @staticmethod
    def _format_records(records):
        def _to_dict(record_order, record_items):
            return {'PO_NUMBER': record_order[0],
                    'SO_NUMBER': record_order[1],
                    'PO_TYPE': record_order[2],
                    'UPDATE_DATE': record_order[3],
                    'ITEMS': list(record_items)}

        return [_to_dict(order, items) for order, items in groupby(records, key=itemgetter('PO_NUMBER',
                                                                                           'SO_NUMBER',
                                                                                           'PO_TYPE',
                                                                                           'UPDATE_DATE'))]
