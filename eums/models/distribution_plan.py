import logging

from django.db import models
from django.db.models import Q
from eums.models import MultipleChoiceAnswer, Flow, Question, TextQuestion, TextAnswer, \
    MultipleChoiceQuestion, NumericAnswer, NumericQuestion, Run
from eums.models import Runnable, DistributionPlanNode
from eums.models.answers import Answer
from eums.models.programme import Programme
import eums.models

logger = logging.getLogger(__name__)


class DistributionPlan(Runnable):
    programme = models.ForeignKey(Programme)
    confirmed = models.BooleanField(default=False, null=False)
    time_limitation_on_distribution = models.IntegerField(null=True)
    tracked_date = models.DateTimeField(null=True)

    class Meta:
        app_label = 'eums'

    def save(self, *args, **kwargs):
        super(DistributionPlan, self).save(*args, **kwargs)
        DistributionPlanNode.objects.filter(distribution_plan=self,
                                            tree_position=Flow.Label.IMPLEMENTING_PARTNER).update(track=self.track)
        if self.track:
            self.update_purchase_order()
            self.update_release_order()

    def update_purchase_order(self):
        purchase_order = eums.models.PurchaseOrder.objects.filter(
                purchaseorderitem__distributionplannode__distribution_plan_id=self.id).first()

        if purchase_order is None:
            return

        last_shipment_data_need_updated = purchase_order.last_shipment_date is None \
                                          or self.delivery_date > purchase_order.last_shipment_date
        if last_shipment_data_need_updated:
            purchase_order.last_shipment_date = self.delivery_date

        tracked_need_updated = purchase_order.tracked_date is None
        if tracked_need_updated:
            purchase_order.tracked_date = self.tracked_date

        purchase_order.save() if last_shipment_data_need_updated or tracked_need_updated else None

    def update_release_order(self):
        release_order = eums.models.ReleaseOrder.objects.filter(
                purchase_order__purchaseorderitem__releaseorderitem__distributionplannode__distribution_plan_id=self.id).first()

        if release_order is None:
            return

        release_order.tracked_date = self.tracked_date
        release_order.save()

    def has_existing_run(self):
        return Run.objects.filter(runnable=self).exists()

    def update_total_value_and_ip(self, ip):
        self.ip = ip
        self.total_value = self._get_total_value()
        self.save()

    def _get_total_value(self):
        delivery_root_nodes = DistributionPlanNode.objects.root_nodes_for(delivery=self)
        return reduce(lambda total, node: total + node.total_value, delivery_root_nodes, 0)

    def __unicode__(self):
        return "%s, %s" % (self.programme.name, str(self.delivery_date))

    def shipment_received(self):
        delivery_answer = self._shipment_received_answer()

        return True if delivery_answer and delivery_answer.value.text == 'Yes' else False

    def is_received(self):
        delivery_answer = self._shipment_received_answer()

        delivery_nodes = DistributionPlanNode.objects.filter(distribution_plan=self)

        items_received = DistributionPlan._has_received_all_items(delivery_nodes)

        return None if not delivery_answer else delivery_answer.value.text == 'Yes' and items_received

    def is_partially_received(self):
        delivery_answer = self._shipment_received_answer()
        return None if not delivery_answer else delivery_answer.value.text == 'Yes'

    def _shipment_received_answer(self):
        delivery_answer = MultipleChoiceAnswer.objects.filter(Q(run__runnable__id=self.id),
                                                              Q(question__label=Question.LABEL.deliveryReceived),
                                                              ~ Q(run__status='cancelled')).first()
        return delivery_answer

    def _is_confirmed(self):
        delivery_nodes = DistributionPlanNode.objects.filter(distribution_plan=self)
        for node in delivery_nodes:
            node_answers = MultipleChoiceAnswer.objects.filter(Q(run__runnable__id=node.id),
                                                               Q(question__label='itemReceived'),
                                                               ~ Q(run__status='cancelled'))
            if not node_answers.exists():
                return False
        return True

    def confirm(self):
        if self._is_confirmed():
            self.confirmed = True
            self.save()

    @staticmethod
    def _has_received_all_items(delivery_nodes):
        node_answers = []
        for node in delivery_nodes:
            answer = MultipleChoiceAnswer.objects.filter(Q(run__runnable__id=node.id),
                                                         Q(question__label='itemReceived'),
                                                         ~ Q(run__status='cancelled')).first()
            if answer:
                node_answers.append(answer.value.text == 'Yes')

        all_nodes_have_answers = len(node_answers) == len(delivery_nodes)
        all_answers_are_true = all(True == answer for answer in node_answers)
        has_received_items = True if all_nodes_have_answers and all_answers_are_true else False

        return has_received_items

    def _first_node(self):
        return DistributionPlanNode.objects.filter(distribution_plan=self).first()

    def type(self):
        delivery_node = self._first_node()
        if delivery_node:
            return delivery_node.type()
        return 'Unknown'

    def number(self):
        delivery_node = self._first_node()
        return delivery_node.number() if delivery_node else 'Unknown'

    def number_of_items(self):
        return DistributionPlanNode.objects.filter(distribution_plan=self).count()

    def answers(self):
        ip_flow = Flow.objects.get(label=Flow.Label.IMPLEMENTING_PARTNER)
        text_questions = TextQuestion.objects.filter(flow=ip_flow)
        multiple_choice_questions = MultipleChoiceQuestion.objects.filter(flow=ip_flow)
        numeric_questions = NumericQuestion.objects.filter(flow=ip_flow)

        text_answers = Answer.build_answer(self, text_questions, TextAnswer)
        multiple_choice_answers = Answer.build_answer(self, multiple_choice_questions, MultipleChoiceAnswer)
        numeric_answers = Answer.build_answer(self, numeric_questions, NumericAnswer)

        answers = text_answers + multiple_choice_answers + numeric_answers
        return sorted(answers, key=lambda field: field['position'])

    def received_date(self):
        answers = filter(lambda answer: answer['question_label'] == Question.LABEL.dateOfReceipt, self.answers())
        if len(answers) > 0:
            return answers[0]['value']
        return ''

    def node_answers(self):
        node_answers = []
        web_flow = Flow.objects.get(label=Flow.Label.WEB)
        text_questions = TextQuestion.objects.filter(flow=web_flow)
        multiple_choice_questions = MultipleChoiceQuestion.objects.filter(flow=web_flow)
        numeric_questions = NumericQuestion.objects.filter(flow=web_flow)
        nodes = DistributionPlanNode.objects.filter(distribution_plan=self)

        for node in nodes:
            text_answers = Answer.build_answer(node, text_questions, TextAnswer)
            multiple_choice_answers = Answer.build_answer(node, multiple_choice_questions, MultipleChoiceAnswer)
            numeric_answers = Answer.build_answer(node, numeric_questions, NumericAnswer)

            answers = text_answers + multiple_choice_answers + numeric_answers
            node_answers.append({'id': node.id, 'answers': sorted(answers, key=lambda field: field['position'])})

        return node_answers

    def contact_person_id(self):
        return DistributionPlanNode.objects.filter(distribution_plan=self).first().contact_person_id

    @classmethod
    def flow(cls):
        return Flow.objects.get(label=Flow.Label.IMPLEMENTING_PARTNER)
