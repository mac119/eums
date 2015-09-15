from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from eums.models import ReleaseOrder


class ReleaseOrderSerialiser(serializers.ModelSerializer):
    programme = serializers.CharField(read_only=True, source='sales_order.programme.name')
    consignee_name = serializers.CharField(read_only=True, source='consignee.name')

    class Meta:
        model = ReleaseOrder
        fields = ('id', 'order_number', 'sales_order', 'purchase_order', 'programme', 'consignee', 'waybill',
                  'delivery_date', 'items', 'delivery', 'consignee_name')


class ReleaseOrderViewSet(ModelViewSet):
    queryset = ReleaseOrder.objects.all().order_by('order_number')
    serializer_class = ReleaseOrderSerialiser

    def list(self, request, *args, **kwargs):
        consignee_id = request.GET.get('consignee', None)
        delivered = request.GET.get('delivered', None)
        if consignee_id:
            orders = ReleaseOrder.objects.for_consignee(consignee_id).order_by('waybill')
        else:
            if delivered:
                orders = ReleaseOrder.objects.delivered().order_by('waybill')
            else:
                orders = self.get_queryset()

        orders = self._apply_filters_on(orders, request)

        return Response(self.get_serializer(orders, many=True).data)

    def _apply_filters_on(self, orders, request):
        query = request.GET.get('query')
        from_date = request.GET.get('from')
        to_date = request.GET.get('to')

        if query:
            orders = orders.filter(waybill__icontains=query)
        if from_date:
            orders = orders.filter(delivery_date__gte=from_date)
        if to_date:
            orders = orders.filter(delivery_date__lte=to_date)
        return orders

    def get_queryset(self):
        delivery_is_null = self.request.GET.get('delivery__isnull', None)
        if delivery_is_null == 'true':
            return self.queryset.filter(delivery__isnull=True)
        if delivery_is_null == 'false':
            return self.queryset.filter(delivery__isnull=False)
        return self.queryset._clone()

releaseOrderRouter = DefaultRouter()
releaseOrderRouter.register(r'release-order', ReleaseOrderViewSet)