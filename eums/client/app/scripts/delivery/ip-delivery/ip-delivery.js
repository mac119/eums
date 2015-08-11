'use strict';

angular.module('IpDelivery', ['eums.config', 'ngTable', 'siTable', 'Delivery', 'Loader', 'User', 'Answer', 'EumsFilters'])
    .controller('IpDeliveryController', function ($scope, $location, DeliveryService, LoaderService,
                                                  UserService, AnswerService) {
        $scope.deliveries = [];
        $scope.answers = [];
        $scope.activeDelivery = undefined;
        $scope.hasReceivedDelivery = undefined;
        var questionLabel = 'deliveryReceived';
        $scope.searchFields = ['number', 'date'];

        function loadDeliveries() {
            LoaderService.showLoader();
            DeliveryService.all()
                .then(function (deliveries) {
                    $scope.deliveries = deliveries;
                    LoaderService.hideLoader();
                });
        }

        loadDeliveries();

        UserService.retrieveUserPermissions()
            .then(function (userPermissions) {
                $scope.canConfirm = _isSubarray(userPermissions, [
                    'auth.can_view_distribution_plans',
                    'auth.can_add_textanswer',
                    'auth.change_textanswer',
                    'auth.add_nimericanswer',
                    'auth.change_nimericanswer'
                ]);
            });

        $scope.confirm = function (delivery) {
            LoaderService.showLoader();
            $scope.activeDelivery = delivery;
            DeliveryService.getDetail(delivery, 'answers')
                .then(function (answers) {
                    LoaderService.hideLoader();
                    $scope.activeDelivery = delivery;
                    $scope.answers = answers;
                    LoaderService.showModal('ip-acknowledgement-modal');
                });
        };

        $scope.saveAnswers = function () {
            var answers;
            LoaderService.showLoader();
            answers = _isDeliveryReceived(questionLabel, $scope.answers) ? $scope.answers : [$scope.answers.first()];
            AnswerService.createWebAnswer($scope.activeDelivery, answers)
                .then(function () {
                    if (_isDeliveryReceived(questionLabel, $scope.answers)) {
                        $location.path('/ip-delivery-items/' + $scope.activeDelivery.id);
                    }
                    $scope.answers = [];
                    $scope.activeDelivery = undefined;
                    LoaderService.hideLoader();
                });
        };

        $scope.$watch('answers', function () {
            $scope.hasReceivedDelivery = $scope.answers && _isDeliveryReceived(questionLabel, $scope.answers);

            if ($scope.answers.length > 0) {
                $scope.isValidChoice = _isValidChoice($scope.answers);
            } else {
                $scope.isValidChoice = false;
            }
        }, true);

        function _isDeliveryReceived(questionLabel, answers) {
            var received = answers.find(function (answer) {
                return answer.question_label === questionLabel && answer.value === 'Yes';
            });

            return received ? true : false;
        }

        function _isSubarray(mainArray, testArray) {
            var found = [];
            testArray.forEach(function (element) {
                if (mainArray.indexOf(element) != -1) {
                    found.add(element)
                }
            });

            return found.length === testArray.length;
        }

        function _isValidChoice(answers) {
            var isValid = [];
            answers.forEach(function (answer) {
                if (answer.type == 'multipleChoice') {
                    isValid.add(answer.options.indexOf(answer.value) > -1);
                } else if (answer.type == 'text') {
                    isValid.add(answer.value != '');
                }
            });
            return isValid.indexOf(false) <= -1;
        }
    });


