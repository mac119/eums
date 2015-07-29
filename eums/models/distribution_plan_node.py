from django.db import models

from eums.models import DistributionPlan, Runnable


class DistributionPlanNode(Runnable):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    distribution_plan = models.ForeignKey(DistributionPlan)
    item = models.ForeignKey('OrderItem')
    targeted_quantity = models.IntegerField()
    tree_position = models.CharField(max_length=255,
                                     choices=((Runnable.MIDDLE_MAN, 'Middleman'), (Runnable.END_USER, 'End User'),
                                              (Runnable.IMPLEMENTING_PARTNER, 'Implementing Partner')))

    def __unicode__(self):
        return "%s %s %s %s" % (self.consignee.name, self.tree_position, str(self.distribution_plan), self.item)

    def quantity_in(self):
        return reduce(lambda total, arc: total + arc.quantity, self.arcs_in.all(), 0)

    def quantity_out(self):
        return reduce(lambda total, arc: total + arc.quantity, self.arcs_out.all(), 0)

    def balance(self):
        return self.quantity_in() - self.quantity_out()

    def get_ip(self):
        if not self.parent:
            return {'id': self.id, 'location': self.location}
        else:
            return self.parent.get_ip()

    def sender_name(self):
        if not self.parent:
            return "UNICEF"
        else:
            return self.parent.consignee.name

    def get_description(self):
        return self.item.item.description
