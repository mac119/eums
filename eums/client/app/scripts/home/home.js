'use strict';

angular.module('Home', ['GlobalStats', 'Delivery', 'DeliveryNode', 'PurchaseOrderItem', 'PurchaseOrder', 'eums.map',
    'Loader', 'map.layers'])
    .controller('HomeController', function ($rootScope, $scope, $location, UserService, MapService, LoaderService) {
        $scope.filter = {programme: '', ip: '', from: '', to: ''};
        $scope.deliveryStatus = {mapReceivedWithIssues: true, mapNonResponse: true, mapReceived: true,
                                    mapNotReceived: true};

        $scope.datepicker = {from: false, to: false};
        $scope.data = {totalStats: {}, district: '', ipView: false};
        $scope.deliveryStatusCollapsed = false;

        $scope.directiveValues = {};

        UserService.getCurrentUser().then(function (user) {
            $scope.user = user;
        });

        $scope.showDetailedResponses = function () {
            var end_user_url = '/response-details/' + $scope.data.district;
            var ip_url = '/ip-feedback-report-by-delivery/' + $scope.data.district;
            var url = $scope.data.ipView? ip_url : end_user_url;
            $location.path(url);
        };

        $scope.toggleIpView = function (value) {
            $scope.data.ipView = value;
            redrawMapColors();
        };

        var redrawMapColors = function () {
            LoaderService.showLoader();
            MapService.addHeatMap($scope);
            $scope.data.district && MapService.clickLayer($scope.data.district);
        };

        $scope.$watchCollection('filter', function (newFilter, oldFilter) {
            if (!Object.equal(newFilter, oldFilter)) {
                redrawMapColors();
            }
        }, true);

        $scope.tmp = {mapReceivedAll: true};

        $scope.updateAllReceived = function () {
            $scope.tmp.mapReceivedAll = ($scope.deliveryStatus.mapReceived && $scope.deliveryStatus.mapReceivedWithIssues);
        };

        $scope.updateReceivedDeliveryStatus = function () {
            $scope.deliveryStatus.mapReceived = $scope.tmp.mapReceivedAll;
            $scope.deliveryStatus.mapReceivedWithIssues = $scope.tmp.mapReceivedAll;
        };

        $scope.$watchCollection('deliveryStatus', function (newDeliveryStatus, oldDeliveryStatus) {
            if (!Object.equal(newDeliveryStatus, oldDeliveryStatus)) {
                redrawMapColors();
            }
        }, true);
    })
    .controller('ResponseController', function ($scope, $q, $routeParams, DeliveryService, PurchaseOrderService,
                                                DeliveryNodeService, PurchaseOrderItemService) {
        function getAllResponsesByDate() {
            return DeliveryService.orderAllResponsesByDate($routeParams.district).then(function (allResponses) {
                var nodePromises = [];
                var poItemPromises = [];

                allResponses.forEach(function (response) {
                    if (response.node) {
                        nodePromises.push(
                            DeliveryNodeService.get(response.node, ['contact_person_id']).then(function (planNode) {
                                response.contactPerson = planNode.contactPerson;
                                var purchaseOrderItemId = planNode.item;
                                poItemPromises.push(
                                    PurchaseOrderItemService.get(purchaseOrderItemId).then(function (purchaseOrderItem) {
                                        return PurchaseOrderService.get(purchaseOrderItem.purchaseOrder).then(function (order) {
                                            response.purchaseOrder = order;
                                        });
                                    })
                                );
                            })
                        );
                    }
                });

                return $q.all(nodePromises).then(function () {
                    return $q.all(poItemPromises).then(function () {
                        return allResponses;
                    });
                });

            });
        }

        getAllResponsesByDate().then(function (allResponses) {
            $scope.allResponses = allResponses;
        });
    })
    .directive('customPopover', function () {
        return {
            restrict: 'A',
            link: function (scope, el, attrs) {
                $(el).popover({
                    trigger: 'hover',
                    html: true,
                    content: attrs.popoverHtml
                });
            }
        };
    });
