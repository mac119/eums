from unittest import TestCase
from django.test import override_settings
from mock import patch
from eums import export_settings
from eums.export_settings import CSV_EXPIRED_HOURS
from eums.models import DistributionPlanNode, DistributionPlan
from eums.services.exporter.item_feedback_report_csv_exporter import ItemFeedbackReportExporter


class ItemFeedbackReportExporterTest(TestCase):
    HOSTNAME = 'http://ha.ha/'

    def tearDown(self):
        DistributionPlan.objects.all().delete()
        DistributionPlanNode.objects.all().delete()

    @patch('eums.services.exporter.delivery_csv_exporter.AbstractCSVExporter.generate_exported_csv_file_name')
    def test_generate_item_feedback_report_should_return_correct_notification_details(self,
                                                                                      generate_exported_csv_file_name):
        file_name = 'items_feedback_report_1448892495779.csv'
        generate_exported_csv_file_name.return_value = file_name
        item_feedback_report_csv_export = ItemFeedbackReportExporter(self.HOSTNAME)

        category = 'report/feedback'
        export_label = item_feedback_report_csv_export.export_label

        details = (export_settings.EMAIL_COMMON_SUBJECT,
                   export_settings.EMAIL_NOTIFICATION_CONTENT.format(export_label,
                                                                     'http://ha.ha/static/exports/' + category +
                                                                     '/' + file_name, CSV_EXPIRED_HOURS))
        self.assertEqual(item_feedback_report_csv_export.notification_details(), details)

    def test_assemble_csv_data(self):
        item_description = 'Cable binder black2.5x100mm'
        programme = {'id': 1, 'name': ''}
        tree_position = 'IMPLEMENTING_PARTNER'
        consignee = 'WAKISO DHO'
        implementing_partner = 'WAKISO DHO'
        order_number = 81020737
        quantity_shipped = 4
        value = 4.48
        answers = {'qualityOfProduct': 'Good', 'amountReceived': 4, 'itemReceived': 'Yes',
                   'satisfiedWithProduct': 'Yes', 'additionalDeliveryComments': ''}

        amount_received = 4
        quality_of_product = 'Good'
        satisfied_with_product = 'Yes'
        additional_delivery_comments = ''
        items_feedback = [{'tree_position': tree_position,
                           'additionalDeliveryComments': additional_delivery_comments,
                           'qualityOfProduct': quality_of_product,
                           'amountReceived': amount_received,
                           'consignee': consignee,
                           'answers': answers,
                           'satisfiedWithProduct': satisfied_with_product,
                           'implementing_partner': implementing_partner,
                           'value': value,
                           'programme': programme,
                           'order_number': order_number,
                           'item_description': item_description,
                           'quantity_shipped': quantity_shipped}, ]

        row_value = [
            item_description,
            programme.get('name'),
            implementing_partner,
            consignee,
            tree_position,
            order_number,
            quantity_shipped,
            value,
            answers.get('itemReceived'),
            answers.get('dateOfReceipt'),
            amount_received,
            quality_of_product,
            satisfied_with_product,
            additional_delivery_comments,

        ]
        csv_exporter = ItemFeedbackReportExporter(self.HOSTNAME)
        assembled_data = csv_exporter.assemble_csv_data(items_feedback)
        header = csv_exporter.config_headers()
        expect_data = [header, row_value]
        self.assertEqual(expect_data, assembled_data)
        self.assertTrue(len(assembled_data) is 2)