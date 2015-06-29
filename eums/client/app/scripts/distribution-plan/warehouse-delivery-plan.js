'use strict';

angular.module('WarehouseDeliveryPlan', ['DistributionPlan', 'ngTable', 'siTable', 'DistributionPlanNode', 'ui.bootstrap',
    'ReleaseOrder', 'ReleaseOrderItem', 'eums.ip', 'ngToast', 'Contact'])
    .controller('WarehouseDeliveryPlanController', function ($scope, $location, $q, $routeParams, DistributionPlanService,
                                                             DistributionPlanNodeService, ReleaseOrderService, ReleaseOrderItemService,
                                                             IPService, ngToast, ContactService) {
        $scope.datepicker = {};
        $scope.districts = [];
        $scope.contact = {};
        $scope.selectedDate = '';
        $scope.selectedLocationId = '';
        $scope.deliveryNodes = [];
        $scope.delivery = {};
        $scope.releaseOrderItems = [];
        $scope.districtsLoaded = false;

        function createToast(message, klass) {
            ngToast.create({
                content: message,
                class: klass,
                maxNumber: 1,
                dismissOnTimeout: true
            });
        }

        function showLoadingModal(show) {
            if (show && !angular.element('#loading').hasClass('in')) {
                angular.element('#loading').modal();
            }
            else if (!show) {
                angular.element('#loading').modal('hide');
                angular.element('#loading.modal').removeClass('in');
            }
        }

        $scope.addContact = function () {
            $('#add-contact-modal').modal();
        };

        $scope.saveContact = function () {
            ContactService.create($scope.contact)
                .then(function (contact) {
                    $('#add-contact-modal').modal('hide');

                    var contactInput = $('#contact-select');
                    var contactSelect2Input = contactInput.siblings('div').find('a span.select2-chosen');
                    contactSelect2Input.text(contact.firstName + ' ' + contact.lastName);

                    contactInput.val(contact._id);

                    $scope.contact = {};
                }, function (response) {
                    createToast(response.data.error, 'danger');
                });
        };

        $scope.invalidContact = function (contact) {
            return !(contact.firstName && contact.lastName && contact.phone);
        };

        showLoadingModal(true);

        IPService.loadAllDistricts().then(function (response) {
            $scope.districts = response.data.map(function (district) {
                return {id: district, name: district};
            });
            $scope.districtsLoaded = true;
        });

        ReleaseOrderService.get($routeParams.releaseOrderId,
            ['consignee', 'sales_order.programme', 'delivery', 'items.item.unit']).then(function (releaseOrder) {
                $scope.selectedReleaseOrder = releaseOrder;
                $scope.selectedReleaseOrder.totalValue = 0.0;
                $scope.releaseOrderItems = releaseOrder.items;
                $scope.selectedReleaseOrder.totalValue = $scope.releaseOrderItems.sum(function (orderItem) {
                    return parseFloat(orderItem.value);
                });
                $scope.delivery = releaseOrder.delivery;
                if ($scope.delivery) {
                    DistributionPlanNodeService.getNodesByDelivery($scope.delivery.id)
                        .then(function (response) {
                            $scope.deliveryNodes = response.data;
                            $scope.selectedLocationId = response.data[0].location
                            $scope.selectedDate = response.data[0].plannedDistributionDate;
                            $scope.contact.id = response.data[0].contactPersonId;
                        });
                }
                showLoadingModal(false);
            });

        var formatDateForSave = function (date) {
            return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
        };

        var saveDeliveryNodes = function () {
            $scope.releaseOrderItems.forEach(function (releaseOrderItem) {
                saveDeliveryNode(releaseOrderItem);
            });
            var message = 'Warehouse Delivery Saved!';
            createToast(message, 'success');
        };

        $scope.saveDelivery = function () {
            if ($scope.delivery) {
                saveDeliveryNodes();
            }
            else {
                DistributionPlanService.createPlan({programme: $scope.selectedReleaseOrder.salesOrder.programme.id})
                    .then(function (createdDelivery) {
                        $scope.delivery = createdDelivery;
                        saveDeliveryNodes();
                    });
            }
        };

        var getNodeForItem = function (releaseOrderitem) {
            return $scope.deliveryNodes.find(function (deliveryNode) {
                return deliveryNode.item === releaseOrderitem.id
            });
        };

        var saveDeliveryNode = function (releaseOrderItem) {
            var deliveryDate = new Date($scope.selectedDate);

            if (deliveryDate.toString() === 'Invalid Date') {
                var planDate = $scope.selectedDate.split('/');
                deliveryDate = new Date(planDate[2], planDate[1] - 1, planDate[0]);
            }

            var node = getNodeForItem(releaseOrderItem);
            if (node) {
                node.location = $scope.selectedLocation.id;
                node.contact_person_id = $scope.contact.id;
                node.planned_distribution_date = formatDateForSave(deliveryDate);
                DistributionPlanNodeService.update(node);
            } else {
                node = {
                    consignee: $scope.selectedReleaseOrder.consignee.id,
                    location: $scope.selectedLocationId,
                    contact_person_id: $scope.contact.id,
                    distribution_plan: $scope.delivery,
                    tree_position: 'IMPLEMENTING_PARTNER',
                    item: releaseOrderItem,
                    targeted_quantity: parseInt(releaseOrderItem.quantity),
                    planned_distribution_date: formatDateForSave(deliveryDate),
                    track: false
                };
                var response = DistributionPlanNodeService.create(node);
                $scope.deliveryNodes.push(response.data);
            }

        };
    });