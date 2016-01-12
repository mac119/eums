import datetime

from mock import patch

from eums.models import PurchaseOrder, Programme, DistributionPlan, PurchaseOrderItem, DistributionPlanNode, SalesOrder, \
    SalesOrderItem, Consignee, Item
from eums.test.api.api_test_helpers import create_release_order
from eums.test.api.authenticated_api_test_case import AuthenticatedAPITestCase
from eums.test.config import BACKEND_URL
from eums.test.factories.consignee_factory import ConsigneeFactory
from eums.test.factories.delivery_factory import DeliveryFactory
from eums.test.factories.delivery_node_factory import DeliveryNodeFactory
from eums.test.factories.item_factory import ItemFactory
from eums.test.factories.programme_factory import ProgrammeFactory
from eums.test.factories.purchase_order_factory import PurchaseOrderFactory
from eums.test.factories.purchase_order_item_factory import PurchaseOrderItemFactory
from eums.test.factories.sales_order_factory import SalesOrderFactory

ENDPOINT_URL = BACKEND_URL + 'purchase-order/'


class PurchaseOrderEndPointTest(AuthenticatedAPITestCase):
    def setUp(self):
        super(PurchaseOrderEndPointTest, self).setUp()
        PurchaseOrder.objects.all().delete()

    def test_should_get_purchase_orders_without_release_orders(self):
        purchase_order = PurchaseOrderFactory()
        create_release_order(self)

        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertListEqual([purchase_order.id], [order['id'] for order in response.data])

        response = self.client.get(ENDPOINT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_should_get_purchase_orders_by_multi_search_fields(self):
        po_one, po_two, programme, consignee = self.create_purchase_orders()
        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/?'
                                                  'purchaseOrder=40141010&'
                                                  'itemDescription=HEK2013&'
                                                  'fromDate=2014-07-08&'
                                                  'toDate=2014-07-10&'
                                                  'programmeId=%s&'
                                                  'selectedLocation=Wakiso&'
                                                  'ipId=%s' % (programme.id, consignee.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], po_two.id)

    def test_should_get_purchase_orders_by_date_range(self):
        date = datetime.date(2014, 07, 9)
        PurchaseOrderFactory()
        po_two = PurchaseOrderFactory(last_shipment_date=date)
        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/?'
                                                  'fromDate=2014-07-6&'
                                                  'toDate=2016-07-16')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], po_two.id)

    def test_should_get_purchase_orders_by_purchase_order_number(self):
        po_one, po_two, programme, consignee = self.create_purchase_orders()
        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/?'
                                                  'purchaseOrder=40141010')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], po_two.id)

    def test_should_get_purchase_orders_by_programme_id(self):
        po_one, po_two, programme, consignee = self.create_purchase_orders()
        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/?'
                                                  'programmeId=%s' % programme.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], po_two.id)

    def test_should_get_purchase_orders_by_item_description(self):
        po_one, po_two, programme, consignee = self.create_purchase_orders()
        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/?'
                                                  'itemDescription=HEK2013')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], po_two.id)

    def test_should_get_purchase_orders_by_location(self):
        po_one, po_two, programme, consignee = self.create_purchase_orders()
        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/?'
                                                  'selectedLocation=Wakiso')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], po_two.id)

    def test_should_get_purchase_orders_by_ip(self):
        po_one, po_two, programme, consignee = self.create_purchase_orders()
        response = self.client.get(ENDPOINT_URL + 'for_direct_delivery/?'
                                                  'ipId=%s' % consignee.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], po_two.id)

    def test_fetched_purchase_orders_should_have_programme_name_and_programme_id(self):
        programme = ProgrammeFactory()
        purchase_order = PurchaseOrderFactory(sales_order=SalesOrderFactory(programme=programme))
        response = self.client.get('%s%s/' % (ENDPOINT_URL, purchase_order.id))
        self.assertDictContainsSubset({'programme': programme.id, 'programme_name': programme.name}, response.data)

    @patch('eums.models.purchase_order.PurchaseOrder.objects.for_consignee')
    def test_should_provide_purchase_orders_that_have_deliveries_for_a_specific_consignee(self, mock_for_consignee):
        consignee_id = u'10'
        order = PurchaseOrderFactory()
        mock_for_consignee.return_value = PurchaseOrder.objects.all()

        response = self.client.get('%s?consignee=%s' % (ENDPOINT_URL, consignee_id))

        mock_for_consignee.assert_called_with(consignee_id)
        self.assertDictContainsSubset({'id': order.id}, response.data[0])

    def test_should_return_serialized_response_of_deliveries_for_particular_purchase_order(self):
        purchase_order = PurchaseOrderFactory()
        purchase_order_item = PurchaseOrderItemFactory(purchase_order=purchase_order)
        delivery = DeliveryFactory()
        node = DeliveryNodeFactory(item=purchase_order_item, distribution_plan=delivery)

        response = self.client.get(ENDPOINT_URL + str(purchase_order.id) + '/deliveries/')

        self.assertEqual(response.status_code, 200)
        self.assertDictContainsSubset({'distributionplannode_set': [node.id]}, response.data[0])
        self.assertDictContainsSubset({'programme': delivery.programme_id}, response.data[0])

    def test_should_compute_purchase_order_total_value(self):
        order = PurchaseOrderFactory()
        PurchaseOrderItemFactory(purchase_order=order, value=100)
        total_value_route = '%s%d/total_value/' % (ENDPOINT_URL, order.id)
        response = self.client.get(total_value_route)
        self.assertEqual(response.data, 100)

        PurchaseOrderItemFactory(purchase_order=order, value=200)
        response = self.client.get(total_value_route)
        self.assertEqual(response.data, 300)

    def create_purchase_orders(self):
        programme = ProgrammeFactory(name='YP104 MANAGEMENT RESULTS')
        consignee = ConsigneeFactory(name='Wakiso DHO')
        date = datetime.date(2014, 07, 9)
        po_one = PurchaseOrderFactory(order_number=45143984)
        po_two = PurchaseOrderFactory(order_number=40141010,
                                      sales_order=SalesOrderFactory(programme=programme),
                                      last_shipment_date=date)
        po_item = PurchaseOrderItemFactory(purchase_order=po_two, item=ItemFactory(description="HEK2013"))
        distribution_plan = DeliveryFactory()
        DeliveryNodeFactory(item=po_item,
                            distribution_plan=distribution_plan,
                            location="Wakiso",
                            consignee=consignee)
        return po_one, po_two, programme, consignee
