from datetime import date, datetime
from unittest import TestCase
from eums.models import Alert
from eums.test.factories.alert_factory import AlertFactory
from eums.test.factories.delivery_factory import DeliveryFactory
from eums.test.factories.delivery_node_factory import DeliveryNodeFactory
from eums.test.factories.purchase_order_item_factory import PurchaseOrderItemFactory


class AlertTest(TestCase):

    def test_should_provide_display_name_for_issue_type_of_not_received(self):
        alert = AlertFactory(issue=Alert.ISSUE_TYPES.not_received)
        self.assertEqual(alert.issue_display_name(), Alert.ISSUE_TYPES[alert.issue])

    def test_should_provide_display_name_for_issue_type_of_bad_condition(self):
        alert = AlertFactory(issue=Alert.ISSUE_TYPES.bad_condition)
        self.assertEqual(alert.issue_display_name(), Alert.ISSUE_TYPES[alert.issue])

    def test_should_provide_total_value_of_the_runnable(self):
        po_item_one = PurchaseOrderItemFactory(value=400, quantity=200)
        po_item_two = PurchaseOrderItemFactory(value=600, quantity=100)

        delivery = DeliveryFactory()
        node = DeliveryNodeFactory(distribution_plan=delivery, item=po_item_one, quantity=50)
        DeliveryNodeFactory(distribution_plan=delivery, item=po_item_two, quantity=30)

        node_alert = AlertFactory(runnable=node)
        delivery_alert = AlertFactory(runnable=delivery)

        self.assertEqual(node_alert.total_value(), 100)
        self.assertEqual(delivery_alert.total_value(), 280)

    def test_should_provide_quantity_delivered_for_node_alert(self):
        node = DeliveryNodeFactory(quantity=20)
        alert = AlertFactory(runnable=node)
        delivery_alert = AlertFactory(runnable=DeliveryFactory())

        self.assertEqual(alert.quantity_delivered(), 20)
        self.assertEqual(delivery_alert.quantity_delivered(), None)

    def test_should_provide_location_for_runnable(self):
        node_location = "Kampala"
        node = DeliveryNodeFactory(location=node_location)

        delivery_location = "Wakiso"
        delivery = DeliveryNodeFactory(location=("%s" % delivery_location))

        alert = AlertFactory(runnable=node)
        delivery_alert = AlertFactory(runnable=delivery)

        self.assertEqual(alert.location(), node_location)
        self.assertEqual(delivery_alert.location(), delivery_location)

    def test_should_provide_delivery_date_for_runnable(self):
        node_date = datetime.strptime('24052010', "%d%m%Y").date()
        node = DeliveryNodeFactory(delivery_date=node_date)

        delivery_date = datetime.strptime('24052011', "%d%m%Y").date()
        delivery = DeliveryNodeFactory(location=delivery_date)

        alert = AlertFactory(runnable=node)
        delivery_alert = AlertFactory(runnable=delivery)

        self.assertEqual(alert.date_shipped(), node_date)
        self.assertEqual(delivery_alert.location(), delivery_date)