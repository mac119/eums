from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

from eums.models.system_settings import SystemSettings


class SystemSettingsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ('auto_track',)


class SystemSettingsViewSet(ModelViewSet):
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerialiser


system_settings_routers = DefaultRouter()
system_settings_routers.register(r'system-settings', SystemSettingsViewSet)
