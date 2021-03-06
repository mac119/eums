'use strict';

angular.module('SupplyEfficiencyReportFilters', ['Directives', 'Item', 'Programme', 'SystemSettingsService'])
    .controller('SupplyEfficiencyReportFiltersController', function ($scope, SystemSettingsService) {
        $scope.filters = {startDate: new moment(1, "MM").toDate(), endDate: new moment("Dec 31", "MMM DD").toDate()};

        $scope.clearFilters = function () {
            $scope.$broadcast('clear-list');
            $scope.$broadcast('clear-programme');
            $scope.$broadcast('clear-item');
            $scope.$broadcast('clear-consignee');
            $scope.filters = {startDate: new moment(1, "MM").toDate(), endDate: new moment("Dec 31", "MMM DD").toDate()};
        };

        init();

        $scope.$watch('filters', function (newFilters) {
            var cleanFilters = {};
            Object.each(newFilters, function (name, val) {
                if (val) cleanFilters[name] = val;
            });
            $scope.$emit('filters-changed', cleanFilters);
        }, true);

        function init() {
            loadSystemSettings();
        }

        function loadSystemSettings() {
            SystemSettingsService.getSettingsWithDefault().then(function (settings) {
                $scope.systemSettings = settings;
            });
        }
    });
