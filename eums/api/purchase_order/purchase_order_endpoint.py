from rest_framework import serializers
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from rest_framework.viewsets import ModelViewSet

from eums.api.distribution_plan.distribution_plan_endpoint import DistributionPlanSerialiser
from eums.api.standard_pagination import StandardResultsSetPagination
from eums.models import PurchaseOrder


class PurchaseOrderSerialiser(serializers.ModelSerializer):
    programme_name = serializers.CharField(read_only=True, source='sales_order.programme.name')
    programme = serializers.IntegerField(read_only=True, source='sales_order.programme.id')

    class Meta:
        model = PurchaseOrder
        fields = ('id', 'order_number', 'date', 'sales_order', 'po_type', 'programme_name', 'purchaseorderitem_set',
                  'release_orders', 'programme', 'is_single_ip', 'has_plan', 'is_fully_delivered')


class PurchaseOrderViewSet(ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('order_number')
    serializer_class = PurchaseOrderSerialiser
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        consignee_id = request.GET.get('consignee', None)
        if consignee_id:
            orders = PurchaseOrder.objects.for_consignee(consignee_id).order_by('order_number')
        else:
            orders = self.get_queryset()
        return Response(self.get_serializer(orders, many=True).data)

    @list_route()
    def for_direct_delivery(self, request, *args, **kwargs):
        if request.GET.get('paginate', None) != 'true':
            self.paginator.page_size = 0

        queryset = self.filter_queryset(self.__get_direct_delivery())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def __get_direct_delivery(self):
        query = self.request.GET.get('query')
        from_date = self.request.GET.get('from')
        to_date = self.request.GET.get('to')
        return PurchaseOrder.objects.for_direct_delivery(search_term=query, from_date=from_date, to_date=to_date)

    @detail_route()
    def deliveries(self, request, pk=None):
        is_root = request.GET.get('is_root')
        purchase_order = self.get_object()
        deliveries = purchase_order.deliveries(is_root)
        return Response(DistributionPlanSerialiser(deliveries, many=True).data)

    @detail_route()
    def total_value(self, _, pk=None):
        return Response(self.get_object().total_value())


purchaseOrderRouter = DefaultRouter()
purchaseOrderRouter.register(r'purchase-order', PurchaseOrderViewSet)
