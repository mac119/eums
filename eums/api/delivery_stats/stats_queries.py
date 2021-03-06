import datetime
from django.db.models import Q
from eums import settings

from eums.api.delivery_stats.stats_structure import BaseQuerySets
from eums.models import MultipleChoiceQuestion, Option, MultipleChoiceAnswer, Run

GRACE_PERIOD = settings.NON_RESPONSE_GRACE_PERIOD


def get_product_received_base_query_sets(stats_search_data):
    was_product_received = MultipleChoiceQuestion.objects.get(label=stats_search_data.received_label,
                                                              flow=stats_search_data.flow)
    product_was_received = Option.objects.get(text='Yes', question=was_product_received)
    product_was_not_received = Option.objects.get(text='No', question=was_product_received)

    successful_delivery_answers = MultipleChoiceAnswer.objects.filter(
        question=was_product_received, value=product_was_received, run__runnable__in=stats_search_data.nodes).filter(
        Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed))

    unsuccessful_delivery_answers = MultipleChoiceAnswer.objects.filter(
        question=was_product_received, value=product_was_not_received,
        run__runnable__in=stats_search_data.nodes).filter(
        Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed))

    runs_with_answers = MultipleChoiceAnswer.objects.filter(
        question=was_product_received, run__runnable__in=stats_search_data.nodes).values_list('run_id')

    non_response_nodes = _get_non_responses_nodes(runs_with_answers, stats_search_data.nodes)

    return BaseQuerySets(successful_delivery_answers, unsuccessful_delivery_answers, non_response_nodes)


def _get_non_responses_nodes(runs_with_answers, nodes):
    grace_period_deadline = datetime.datetime.now() - datetime.timedelta(days=GRACE_PERIOD)
    return nodes.exclude(run__id__in=runs_with_answers).filter(delivery_date__lte=grace_period_deadline).distinct()


def get_quality_of_product_base_query_sets(stats_search_data):
    quality_of_product_qn = MultipleChoiceQuestion.objects.get(label=stats_search_data.quality_label,
                                                               flow=stats_search_data.flow)
    was_good = Option.objects.get(text=stats_search_data.quality_yes_text, question=quality_of_product_qn)

    good_quality_delivery_answers = MultipleChoiceAnswer.objects.filter(
        question=quality_of_product_qn, value=was_good, run__runnable__in=stats_search_data.nodes).filter(
        Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed))

    bad_order_delivery_answers = MultipleChoiceAnswer.objects.filter(
        question=quality_of_product_qn, run__runnable__in=stats_search_data.nodes).filter(~Q(value=was_good)).filter(
        Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed))

    runs_with_answers = MultipleChoiceAnswer.objects.filter(
        question=quality_of_product_qn, run__runnable__in=stats_search_data.nodes).values_list('run_id')

    non_response_nodes = _get_non_responses_nodes(runs_with_answers, stats_search_data.nodes)

    return BaseQuerySets(good_quality_delivery_answers, bad_order_delivery_answers, non_response_nodes)


def get_satisfied_with_product_base_query_sets(stats_search_data):
    satisfied_with_product_qn = MultipleChoiceQuestion.objects.get(label=stats_search_data.satisfied_label,
                                                                   flow=stats_search_data.flow)
    satisfied = Option.objects.get(text='Yes', question=satisfied_with_product_qn)
    unsatisfied = Option.objects.get(text='No', question=satisfied_with_product_qn)

    satisfied_with_product_answers = MultipleChoiceAnswer.objects.filter(
        question=satisfied_with_product_qn, value=satisfied, run__runnable__in=stats_search_data.nodes).filter(
        Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed))

    unsatisfied_with_product_answers = MultipleChoiceAnswer.objects.filter(
        question=satisfied_with_product_qn, value=unsatisfied, run__runnable__in=stats_search_data.nodes).filter(
        Q(run__status=Run.STATUS.scheduled) | Q(run__status=Run.STATUS.completed))

    runs_with_answers = MultipleChoiceAnswer.objects.filter(
        question=satisfied_with_product_qn, run__runnable__in=stats_search_data.nodes).values_list('run_id')

    non_response_nodes = _get_non_responses_nodes(runs_with_answers, stats_search_data.nodes)

    return BaseQuerySets(satisfied_with_product_answers, unsatisfied_with_product_answers, non_response_nodes)
