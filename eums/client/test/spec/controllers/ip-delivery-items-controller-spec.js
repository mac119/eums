describe('IP Delivery Items Controller', function () {
    var mockDeliveryService, scope, location, mockLoaderService, q,
        mockDeliveryNodeService, controller, mockAnswerService;

    var deliveryNodes = [{
        id: 1,
        location: 'Kampala',
        consignee: {id: 10},
        track: true,
        deliveryDate: '2015-01-02',
        remark: 'some remarks',
        item: 1
    },
        {
            id: 2,
            location: 'Kampala',
            consignee: {id: 10},
            track: true,
            deliveryDate: '2015-01-02',
            remark: 'some other remarks',
            item: 2
        }];

    var activeDelivery = {
        id: 1,
        location: 'Kampala',
        consignee: {id: 10},
        track: true,
        deliveryDate: '2015-01-02',
        remark: 'some remarks',
        totalValue: 6000,
        distributionplannodeSet: deliveryNodes
    };

    var nodeAnswers = [{
        'question_label': 'itemReceived',
        'type': 'multipleChoice',
        'text': 'Was item received?',
        'value': 'Yes',
        'options': ['Yes'],
        'position': 0

    },
    {
        'question_label': 'additionalComments',
        'type': 'text',
        'text': 'Any additional comments?',
        'value': 'Answer1',
        'position': 1
    }];
    var emptyFunction = function () {
    };

    function initializeController() {
        controller('IpDeliveryItemsController', {
            $scope: scope,
            LoaderService: mockLoaderService,
            DeliveryService: mockDeliveryService,
            $routeParams: {activeDeliveryId: 1}
        });
    }

    beforeEach(function () {

        module('IpDeliveryItems');

        inject(function ($controller, $rootScope, $location, $q,
                         LoaderService, AnswerService, DeliveryService,
                         DeliveryNodeService) {
            controller = $controller;
            scope = $rootScope.$new();
            location = $location;
            q = $q;
            mockLoaderService = LoaderService;
            mockAnswerService = AnswerService;
            mockDeliveryService = DeliveryService;
            mockDeliveryNodeService = DeliveryNodeService;

            spyOn(mockLoaderService, 'showLoader');
            spyOn(mockLoaderService, 'hideLoader');
            spyOn(mockAnswerService, 'createWebAnswer');
            spyOn(mockDeliveryService, 'get');
            spyOn(mockDeliveryService, 'getDetail');
            spyOn(mockDeliveryNodeService, 'all');
            spyOn(location, 'path');

        });
    });

    describe('on load', function () {

        beforeEach(function () {
            mockDeliveryService.get.and.returnValue(q.when(activeDelivery));
            mockDeliveryService.getDetail.and.returnValue(q.when(nodeAnswers));
        });

        it('should show loader while loading', function () {
            initializeController();
            scope.$apply();

            expect(mockLoaderService.showLoader).toHaveBeenCalled();
            expect(mockLoaderService.showLoader.calls.count()).toBe(1);
        });

        it('should call the delivery service and set the shipment date and total value in the scope', function () {
            initializeController();
            scope.$apply();

            expect(mockDeliveryService.get).toHaveBeenCalledWith(1, ['distributionplannode_set']);
            expect(scope.shipmentDate).toBe('2015-01-02');
            expect(scope.totalValue).toBe(6000);
            expect(scope.deliveryNodes).toBe(deliveryNodes);
        });

        it('should get all the answers for all nodes belonging to a delivery', function () {
            initializeController();
            scope.$apply();

            expect(mockDeliveryService.getDetail).toHaveBeenCalledWith(activeDelivery, 'node_answers');
            expect(scope.nodeAnswers).toBe(nodeAnswers);
        });
    });
});

