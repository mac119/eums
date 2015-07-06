from eums.models import ReleaseOrder, SalesOrder, PurchaseOrder, Consignee
from eums.test.api.api_test_helpers import create_release_order
from eums.test.api.authenticated_api_test_case import AuthenticatedAPITestCase
from eums.test.config import BACKEND_URL
from eums.test.factories.consignee_factory import ConsigneeFactory
from eums.test.factories.release_order_factory import ReleaseOrderFactory
from eums.test.factories.sales_order_factory import SalesOrderFactory
from eums.test.factories.purchase_order_factory import PurchaseOrderFactory
from mock import patch


ENDPOINT_URL = BACKEND_URL + 'release-order/'


class ReleaseOrderEndPointTest(AuthenticatedAPITestCase):
    def tearDown(self):
        ReleaseOrder.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        SalesOrder.objects.all().delete()
        Consignee.objects.all().delete()

    def test_should_get_release_orders(self):
        sales_order = SalesOrderFactory()
        purchase_order = PurchaseOrderFactory()
        consignee = ConsigneeFactory()

        release_order_details = {'order_number': 232345434, 'delivery_date': '2014-10-05',
                                 'sales_order': sales_order.id, 'purchase_order': purchase_order.id,
                                 'consignee': consignee.id, 'waybill': 234256}

        created_release_order, _ = create_release_order(self, release_order_details=release_order_details)

        # print 'CREATED RO', created_release_order
        self.assertDictContainsSubset(release_order_details, created_release_order)
        self.assertDictContainsSubset({'items': []}, created_release_order)
        self.assertDictContainsSubset({'programme': sales_order.programme.name}, created_release_order)

    @patch('eums.models.release_order.ReleaseOrder.objects.for_consignee')
    def test_should_provide_purchase_orders_that_have_deliveries_for_a_specific_consignee(self, mock_for_consignee):
        consignee_id = u'10'
        order = ReleaseOrderFactory()
        mock_for_consignee.return_value = ReleaseOrder.objects.all()

        response = self.client.get('%s?consignee=%s' % (ENDPOINT_URL, consignee_id))

        mock_for_consignee.assert_called_with(consignee_id)
        self.assertDictContainsSubset({'id': order.id}, response.data[0])
