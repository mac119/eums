'use strict';

angular.module('StockReport', [
        'eums.config', 'ngTable', 'siTable', 'eums.ip', 'Consignee', 'Directives', 'SortBy', 'Loader', 'ReportService',
        'User', 'EumsErrorMessage', 'Sort', 'SortArrow', 'SysUtils', 'ngToast', 'SystemSettingsService'])
    .config(['ngToastProvider', function (ngToast) {
        ngToast.configure({maxNumber: 1, horizontalPosition: 'center'});
    }])
    .controller('StockReportController', function ($scope, $q, $compile, StockReportService, ConsigneeService, SortByService,
                                                   ReportService, IPService, LoaderService, UserService, ErrorMessageService,
                                                   SortService, SortArrowService, SysUtilsService, ngToast, SystemSettingsService) {
        var SUPPORTED_FIELD = ['last_shipment_date', 'last_received_date', 'total_value_received', 'total_value_dispensed', 'total_value_lost', 'balance'];
        $scope.reportParams = {};
        $scope.totals = {};
        $scope.isIpUser = false;
        $scope.sortTerm = {field: 'last_shipment_date', order: 'desc'};

        init();

        $scope.goToPage = function (page) {
            fetchReport({page: page});
        };

        $scope.sortBy = function (sortField) {
            if (SUPPORTED_FIELD.indexOf(sortField) !== -1) {
                $scope.sortTerm = SortService.sortBy(sortField, $scope.sortTerm);
                $scope.currentPage = 1;
                fetchReport()
            }
        };

        $scope.hasEmptyDataResponse = function () {
            return ($scope.reportData != undefined && $scope.reportData.length === 0);
        };

        $scope.$watch('reportParams.selectedIPId', function (newIPId, oldIPId) {
            if (newIPId != oldIPId)
                fetchReport();
        });

        $scope.$watch('reportParams.selectedLocation', function (newLocation, oldLocation) {
            if (newLocation != oldLocation)
                fetchReport();
        });

        $scope.$watch('reportParams.selectedOutcomeId', function (newOutcomeId, oldOutcomeId) {
            if (newOutcomeId != oldOutcomeId)
                fetchReport();
        });

        $scope.$watch('reportParams.selectedFromDate', function (newFromDate, oldFromDate) {
            if (newFromDate != oldFromDate)
                fetchReport();
        });

        $scope.$watch('reportParams.selectedToDate', function (newToDate, oldToDate) {
            if (newToDate != oldToDate)
                fetchReport();
        });

        $scope.toggleOpenDocument = function (documentId) {
            $scope.openDocument = $scope.openDocument === documentId ? undefined : documentId;
        };

        $scope.sortArrowClass = function (criteria) {
            return SortArrowService.setSortArrow(criteria, $scope.sortTerm);
        };

        $scope.formatDate = function (date) {
            return SysUtilsService.formatDate(date);
        };

        $scope.exportToCSV = function () {
            var allFilters = angular.extend({}, getSearchTerm());
            ReportService.exportStockReport(allFilters).then(function (response) {
                ngToast.create({content: response.message, class: 'info'});
            }, function () {
                var errorMessage = "Error while generating CSV. Please contact the system's admin.";
                ngToast.create({content: errorMessage, class: 'danger'})
            });
        };

        function init() {
            bindModalEvent();
            loadDistricts();
            loadSystemSettings();
            UserService.getCurrentUser().then(function (user) {
                if (user && user.consignee_id) {
                    $scope.isIpUser = true;
                    $scope.reportParams.selectedIPId = user.consignee_id;
                    ConsigneeService.get(user.consignee_id).then(function (ip) {
                        $scope.$broadcast('set-consignee', ip);
                    });
                }
                fetchReport();
            });
        }

        function loadSystemSettings() {
            SystemSettingsService.getSettingsWithDefault().then(function (settings) {
                $scope.systemSettings = settings;
            });
        }

        function loadDistricts() {
            IPService.loadAllDistricts().then(function (response) {
                $scope.districts = response.data.map(function (district) {
                    return {id: district, name: district};
                });
                $scope.districtsLoaded = true;
            });
        }

        function appendSortParam(requestParams) {
            return angular.extend({}, requestParams, $scope.sortTerm);
        }

        function fetchReport(params) {
            LoaderService.showLoader();
            var requestParams = {};
            if ($scope.reportParams.selectedLocation) {
                Object.merge(requestParams, {location: $scope.reportParams.selectedLocation});
            }
            if ($scope.reportParams.selectedIPId) {
                Object.merge(requestParams, {consignee: $scope.reportParams.selectedIPId});
            }
            if ($scope.reportParams.selectedOutcomeId) {
                Object.merge(requestParams, {outcome: $scope.reportParams.selectedOutcomeId});
            }
            if ($scope.reportParams.selectedFromDate) {
                Object.merge(requestParams, {fromDate: SysUtilsService.formatDateToYMD($scope.reportParams.selectedFromDate)});
            }
            if ($scope.reportParams.selectedToDate) {
                Object.merge(requestParams, {toDate: SysUtilsService.formatDateToYMD($scope.reportParams.selectedToDate)});
            }
            if (params) {
                Object.merge(requestParams, params);
            }
            requestParams = appendSortParam(requestParams);
            StockReportService.getStockReport(requestParams).then(function (response) {
                $scope.count = response.data.count;
                $scope.pageSize = response.data.pageSize;
                $scope.reportData = response.data.results;
                $scope.totals = response.data.totals;
                $scope.openDocument = undefined;
            }, function (error) {
                ErrorMessageService.showError('An error occurred. Please refresh and try again.');
            }).finally(function () {
                LoaderService.hideLoader();
            });
        }

        function getSearchTerm() {
            return $scope.reportParams;
        }

        function bindModalEvent() {
            $('#stock-report-lost-remarks-modal').on('show.bs.modal', function (event) {
                $scope.lostRemarks = $(event.relatedTarget).data('lost-remark');
                $scope.$apply();
            });
        }
    })
    .factory('StockReportService', function ($http, EumsConfig) {
        return {
            getStockReport: function (requestParams) {
                var url = EumsConfig.BACKEND_URLS.STOCK_REPORT;
                if (requestParams) {
                    url += '?' + $.param(requestParams);
                }
                return $http.get(url);
            }
        };
    })
    .directive('concatArray', ['$compile', function ($compile) {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                scope.$watch(function () {
                    return attrs.concatArray;
                }, function (content) {
                    if(!content) return;
                    var value = "";
                    var array = scope.$eval(content);
                    for (var i = 0; i < array.length; i++) {
                        value += '<div>' + array[i] + '</div>';
                    }
                    element.html(value);
                    $compile(element.contents())(scope);
                });
            }
        };
    }]);
