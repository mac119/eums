import factory

from eums.test.factories.purchase_order_item_factory import PurchaseOrderItemFactory
from eums.test.factories.release_order_item_factory import ReleaseOrderItemFactory
from eums.test.helpers.fake_datetime import FakeDate
from eums.models import DistributionPlanNode
from eums.test.factories.consignee_factory import ConsigneeFactory
from eums.test.factories.distribution_plan_factory import DistributionPlanFactory


class DistributionPlanNodeFactory(factory.DjangoModelFactory):
    class Meta:
        model = DistributionPlanNode

    parent = None
    distribution_plan = factory.SubFactory(DistributionPlanFactory)
    consignee = factory.SubFactory(ConsigneeFactory)
    tree_position = DistributionPlanNode.END_USER
    location = "Kampala"
    contact_person_id = factory.Sequence(lambda n: "{0}".format(n))
    mode_of_delivery = DistributionPlanNode.THROUGH_WAREHOUSE
    purchase_order_item = factory.SubFactory(PurchaseOrderItemFactory)
    release_order_item = factory.SubFactory(ReleaseOrderItemFactory)
    track = False
    targeted_quantity = 10
    planned_distribution_date = FakeDate.today()
    remark = "In good condition"
