// $Id: controller.js 32761 2015-11-02 11:50:21Z schaap $

var eventGridControllerMod = angular.module('EventGridControllerMod', ['ui.grid',
                                                                       'ui.grid.resizeColumns',
                                                                       'ui.grid.autoResize']);

eventGridControllerMod.controller('EventGridController', ['$scope', 'dataService', 'uiGridConstants', function($scope, dataService, uiGridConstants) {

    var self = this;

    $scope.dataService = dataService;
    
    $scope.columns = [
    { field: 'timestamp',
        displayName: 'Timestamp',
        width: '120',
        type: 'date',
        enableCellEdit: false,
        enableCellEditOnFocus: false,
        cellTemplate:'<div style=\'text-align:center; padding-top:5px;\'>{{row.entity[col.field] | date:\'yyyy-MM-dd HH:mm:ss\'}}</div>',
        sort: { direction: uiGridConstants.DESC }
    },
    { field: 'message',
        displayName: 'Message',
        enableCellEdit: false,
        width: '*',
        minWidth: '100',
    }];

    $scope.gridOptions = {
        enableGridMenu: false,
        enableSorting: true,
        enableFiltering: true,
        enableCellEdit: false,
        enableColumnResize: true,
        enableHorizontalScrollbar: uiGridConstants.scrollbars.NEVER,
        enableRowSelection: false,
        enableRowHeaderSelection: false,
        enableFullRowSelection: false,
        modifierKeysToMultiSelect: false,
        multiSelect:false,
        enableSelectionBatchEvent:false,
        gridMenuShowHideColumns: false,
        columnDefs: $scope.columns,
        data: dataService.events,
        rowTemplate: "<div ng-repeat=\"(colRenderIndex, col) in colContainer.renderedColumns track by col.uid\" ui-grid-one-bind-id-grid=\"rowRenderIndex + '-' + col.uid + '-cell'\" class=\"ui-grid-cell\" ng-class=\"{ 'ui-grid-row-header-cell': col.isRowHeader }\" role=\"{{col.isRowHeader ? 'rowheader' : 'gridcell'}}\" ui-grid-cell></div>"
    };
}]);

