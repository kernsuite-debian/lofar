// $Id: controller.js 32761 2015-11-02 11:50:21Z schaap $

function sizeFilterCondition(term, value, row, column) {
    if (term === 0)
        return value === 0;

    return (value >= term);
};


var gridControllerMod = angular.module('GridControllerMod', ['ui.grid',
                                                             'ui.grid.edit',
                                                             'ui.grid.selection',
                                                             'ui.grid.resizeColumns',
                                                             'ui.grid.autoResize']);

gridControllerMod.controller('GridController', ['$scope', '$window', 'dataService', 'uiGridConstants', function($scope, $window, dataService, uiGridConstants) {

    var self = this;

    $scope.dataService = dataService;

    $scope.sanitize_url = function(in_url) {
        var split_url = in_url.split("://");
        return split_url[0] + "://" + split_url[1].replace(/\/+/g, "/");
    }

    $scope.selectBlockingPredecessors = function(in_blocking_predecessors) {
        $scope.$parent.$parent.loadTasksSelectAndJumpIntoView(in_blocking_predecessors);
    };

    $scope.openLtaLocation = function(in_ingest_tasks) {
        var ingest_tasks = Array.isArray(in_ingest_tasks) ? in_ingest_tasks : [in_ingest_tasks];

        //example: http://lofar.target.rug.nl/Lofar?mode=query_result_page_user&product=AveragingPipeline&ObservationId=544965&project=LC6_015
        //map task.sub_type to url product parameter
        var project2project2product2tasksDict = {};

        for(var t of ingest_tasks) {
            var lta_product;
            switch(t.sub_type) {
                case 'averaging_pipeline': lta_product = 'AveragingPipeline'; break;
                case 'calibration_pipeline': lta_product = 'CalibrationPipeline'; break;
                case 'pulsar_pipeline': lta_product = 'PulsarPipeline'; break;
                case 'lofar_imaging_pipeline': lta_product = 'ImagingPipeline'; break;
                case 'imaging_pipeline_msss': lta_product = 'ImagingPipeline'; break;
                case 'long_baseline_pipeline': lta_product = 'LongBaselinePipeline'; break;
                case 'lofar_observation': lta_product = 'Observation'; break;
            }
            if(lta_product && (t.ingest_status != undefined) ) {
                if(!project2project2product2tasksDict.hasOwnProperty(t.project_name)) {
                    project2project2product2tasksDict[t.project_name] = {};
                }
                if(!project2project2product2tasksDict[t.project_name].hasOwnProperty(lta_product)) {
                    project2project2product2tasksDict[t.project_name][lta_product] = [];
                }
                project2project2product2tasksDict[t.project_name][lta_product].push(t);
            }
        }

        var window_cntr = 0;
        for(var project in project2project2product2tasksDict) {
            for(var product in project2project2product2tasksDict[project]) {
                var product_tasks = project2project2product2tasksDict[project][product];
                var otdb_ids = product_tasks.map(function(pt) { return pt.otdb_id; });
                var otdb_ids_string = otdb_ids.join(',');
                var url = dataService.config.lta_base_url + '/Lofar?mode=query_result_page_user&product=' + product + '&ObservationId=' + otdb_ids_string + '&project=' + project;
                url = $scope.sanitize_url(url);
                setTimeout(function(url_arg) {
                    $window.open(url_arg, '_blank');
                }, window_cntr*250, url);
                window_cntr += 1;
            }
        }
    }

    $scope.columns = [
    { field: 'name',
        enableCellEdit: false,
        cellTooltip: function(row, col) { return row.entity.description; },
        width: '*',
        minWidth: '100',
    },
    { field: 'project_name',
        displayName:'Project',
        enableCellEdit: false,
        cellTemplate:'<div style=\'padding-top:5px;\'>' +
                     '<a target="_blank" href="https://lofar.astron.nl/mom3/user/project/setUpMom2ObjectDetails.do?view=generalinfo&mom2ObjectId={{row.entity.project_mom2object_id}}"' +
                         ' title="{{row.grid.appScope.dataService.momProjectsDict[row.entity.project_mom_id].description}}"' +
                     '>{{row.entity[col.field]}}' +
                     '</a></div>',
        width: '*',
        minWidth: '80',
        filter: {
            type: uiGridConstants.filter.SELECT,
            selectOptions: []
        }
    },
    { field: 'starttime',
        displayName: 'Start',
        width: '120',
        type: 'date',
        enableCellEdit: false,
        enableCellEditOnFocus: false,
        cellTemplate:'<div style=\'text-align:center; padding-top:5px;\'>{{row.entity[col.field] | date:\'yyyy-MM-dd HH:mm:ss\'}}</div>',
        sort: { direction: uiGridConstants.ASC, priority: 3 }
    },
    { field: 'endtime',
        displayName: 'End',
        width: '120',
        type: 'date',
        enableCellEdit: false,
        enableCellEditOnFocus: false,
        cellTemplate:'<div style=\'text-align:center; padding-top:5px;\'>{{row.entity[col.field] | date:\'yyyy-MM-dd HH:mm:ss\'}}</div>'
    },
    { field: 'duration',
        displayName: 'Duration',
        width: '70',
        type: 'number',
        enableFiltering: false,
        enableCellEdit: false,
        enableCellEditOnFocus: false,
        cellTemplate:'<div style=\'text-align:center; padding-top:5px;\'>{{row.entity[col.field] | secondsToHHmmss}}</div>'
    },
    { field: 'status',
        enableCellEdit: false,
        width: '70',
        filter: {
            condition: uiGridConstants.filter.EXACT,
            type: uiGridConstants.filter.SELECT,
            selectOptions: []
        },
        cellClass: function(grid, row, col, rowRenderIndex, colRenderIndex) {
            return "grid-status-" + grid.getCellValue(row,col);
        }
        // Supposedly [1], select-box items can be formatted using:
        // headerCellFilter: 'statusFormatter'
        //
        // [1] http://stackoverflow.com/questions/37286945/ui-grid-setting-template-for-filter-options
    },
    {   field: 'info',
        displayName: 'Info',
        enableCellEdit: false,
        width: '45',
        filter: {
            condition: function(searchTerm, cellValue, row, column) {
                var do_include = false;
                switch(searchTerm) {
                    case 0: do_include = (row.entity.blocked_by_ids.length > 0);    break;
                    case 1: do_include = (row.entity.ingest_status=="ingesting");   break;
                    case 2: do_include = (row.entity.ingest_status=="ingested");    break;
                    case 3: do_include = (row.entity.ingest_status=="failed");      break;
                    case 4: do_include = row.entity.data_pinned;                    break;
                    default: break;
                };
                return do_include;
            },
            type: uiGridConstants.filter.SELECT,
            selectOptions: []
        },
        editableCellTemplate: 'ui-grid/dropdownEditor',
        editDropdownOptionsArray: [],
        headerTooltip: "Additional status information",
        cellTemplate:   '<div style="text-align: center" class="ui-grid-cell-contents">' +
                            '<span ng-if="row.entity.blocked_by_ids.length > 0"><img ng-click="row.grid.appScope.selectBlockingPredecessors(row.entity.blocked_by_ids)" ng-src="static/icons/blocked.png" title="Blocked by {{row.entity.blocked_by_ids.length.toString()}} predecessor(s) - Click to select" /></span>' +
                            '<span ng-if="row.entity.ingest_status==\'ingesting\'"><img ng-click="row.grid.appScope.openLtaLocation(row.entity)" ng-src="static/icons/ingest_in_progress.png" title="Ingest in progress - Click to open LTA catalog" /></span>' +
                            '<span ng-if="row.entity.ingest_status==\'ingested\'"><img ng-click="row.grid.appScope.openLtaLocation(row.entity)" ng-src="static/icons/ingest_successful.png" title="Ingest successful - Click to open LTA catalog" /></span>' +
                            '<span ng-if="row.entity.ingest_status==\'failed\'"><img ng-click="row.grid.appScope.openLtaLocation(row.entity)" ng-src="static/icons/ingest_failed.png" title="Ingest failed - Click to open LTA catalog" /></span>' +
                            '<span ng-if="row.entity.data_pinned"><img ng-src="static/icons/pinned.png" title="data is pinned and will not be deleted by (auto) cleanup service" /></span>' +
                        '</div>'
    },
    { field: 'type',
        enableCellEdit: false,
        width: '80',
        filter: {
            condition: uiGridConstants.filter.EXACT,
            type: uiGridConstants.filter.SELECT,
            selectOptions: []
        },
        sort: { direction: uiGridConstants.ASC, priority: 2 }
    },
    { field: 'disk_usage',
        displayName: 'Size',
        type: 'number',
        enableCellEdit: false,
        cellTemplate:'<div style=\'text-align:right; padding-top: 5px;\'>{{row.entity.disk_usage_readable}}</div>',
        width: '80',
        filter: {
            type: uiGridConstants.filter.SELECT,
            condition: sizeFilterCondition,
            selectOptions: [{ value:0, label: '0'}, { value:1, label: '> 0'}, { value:1e6, label: '> 1M'}, { value:1e9, label: '> 1G'}, { value:1e10, label: '> 10G'}, { value:1e11, label: '> 100G'}, { value:1e12, label: '> 1T'} ]
        }
    },
    { field: 'mom_object_group_id',
        displayName: 'Group ID',
        enableCellEdit: false,
        cellTemplate:'<div style=\'text-align: center; padding-top:5px;\'>' +
                        '<a target="_blank" href="https://lofar.astron.nl/mom3/user/project/setUpMom2ObjectDetails.do?view=generalinfo&mom2ObjectId={{row.entity.mom_object_group_mom2object_id}}"' +
                            'title="' +
                                'Group name: ' +           '{{row.entity.mom_object_group_name}}\n' +
                                'Parent group name: ' +    '{{row.entity.mom_object_parent_group_name}}\n' +
                                'Parent group ID: ' +      '{{row.entity.mom_object_parent_group_id}}' +
                            '">{{row.entity.mom_object_group_id}}</a></div>',
        width: '80',
        filter: {
            condition: uiGridConstants.filter.EXACT,
            type: uiGridConstants.filter.SELECT,
            selectOptions: []
        }
    },
    { field: 'mom_id',
        displayName: 'MoM ID',
        enableCellEdit: false,
        cellTemplate:'<div style=\'text-align: center; padding-top:5px;\'>' +
                        '<a target="_blank" href="https://lofar.astron.nl/mom3/user/project/setUpMom2ObjectDetails.do?view=generalinfo&mom2ObjectId={{row.entity.mom2object_id}}"' +
                            'title="' +
                                'Project description: ' +  '{{row.grid.appScope.dataService.momProjectsDict[row.entity.project_mom_id].description}}\n' +
                                'Task description: ' +     '{{row.entity.description}}\n' +
                                'Group name: ' +           '{{row.entity.mom_object_group_name}}\n' +
                                'Group ID: ' +             '{{row.entity.mom_object_group_id}}\n' +
                                'Parent group name: ' +    '{{row.entity.mom_object_parent_group_name}}\n' +
                                'Parent group ID: ' +      '{{row.entity.mom_object_parent_group_id}}' +
                            '">{{row.entity[col.field]}} </a></div>',
        width: '65'
    },
    { field: 'otdb_id',
        displayName: 'SAS ID',
        enableCellEdit: false,
        cellTemplate:'<div style=\'text-align:center; padding-top:5px;\'>{{row.entity.otdb_id}}</div>',
        width: '65'
    },
    { field: 'id',
        displayName: 'RADB ID',
        enableCellEdit: false,
        cellTemplate:'<div style=\'text-align:center; padding-top:5px;\'><a target="_blank" href="tasks/{{row.entity.id}}.html">{{row.entity[col.field]}}</a></div>',
        width: '72'
    },
    { field: 'cluster',
        displayName: 'Cluster',
        enableCellEdit: false,
        width: '75',
        filter: {
            condition: uiGridConstants.filter.EXACT,
            type: uiGridConstants.filter.SELECT,
            selectOptions: []
        },
        cellClass: function(grid, row, col, rowRenderIndex, colRenderIndex) {
            var value = grid.getCellValue(row,col);
            return "grid-cluster-" + value;
        },
        sort: { direction: uiGridConstants.ASC, priority: 1 }
    }];

    if($scope.dataService.projectMode) {
        $scope.columns.splice(1, 1);
    }

    $scope.gridOptions = {
        enableGridMenu: false,
        enableSorting: true,
        enableFiltering: true,
        enableCellEdit: false,
        enableColumnResize: true,
        enableHorizontalScrollbar: uiGridConstants.scrollbars.NEVER,
        enableRowSelection: true,
        enableRowHeaderSelection: true,
        enableFullRowSelection: false,
        modifierKeysToMultiSelect: true,
        multiSelect:true,
        enableSelectionBatchEvent:false,
        gridMenuShowHideColumns: false,
        columnDefs: $scope.columns,
        data: [],
//         rowTemplate: "<div ng-repeat=\"(colRenderIndex, col) in colContainer.renderedColumns track by col.uid\" ui-grid-one-bind-id-grid=\"rowRenderIndex + '-' + col.uid + '-cell'\" class=\"ui-grid-cell\" ng-class=\"{ 'ui-grid-row-header-cell': col.isRowHeader }\" role=\"{{col.isRowHeader ? 'rowheader' : 'gridcell'}}\" ui-grid-cell></div>"
        rowTemplate: "<div ng-repeat=\"(colRenderIndex, col) in colContainer.renderedColumns track by col.uid\" ui-grid-one-bind-id-grid=\"rowRenderIndex + '-' + col.uid + '-cell'\" class=\"ui-grid-cell\" ng-class=\"{ 'ui-grid-row-header-cell': col.isRowHeader }\" role=\"{{col.isRowHeader ? 'rowheader' : 'gridcell'}}\" ui-grid-cell context-menu>",
        onRegisterApi: function(gridApi){
            $scope.gridApi = gridApi;

            $scope.gridApi.core.on.rowsRendered($scope, function() {
                //on.rowsRendered is called whenever the data/filtering of the grid changed
                //update the filteredTasks in the dataService from the resulting new grid rows
                $scope.$evalAsync(function() {
                    var taskDict = $scope.dataService.taskDict;
                    $scope.dataService.filteredTasks = [];
                    var rows = $scope.gridApi.core.getVisibleRows(grid);
                    var numRows = rows.length;
                    for(var i = 0; i < numRows; i++) {
                        var row = rows[i];
                        if(row.visible)
                        {
                            var task_id = row.entity.id;
                            var task = taskDict[task_id];
                            if(task) {
                                $scope.dataService.filteredTasks.push(task);
                            }

                            row.setSelected($scope.dataService.selected_task_ids.indexOf(task_id) != -1);
                        }
                    }

                    $scope.dataService.filteredTaskChangeCntr++;

                    if($scope.dataService.filteredTasks.length == 0) {
                        var otdb_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'otdb_id'; });
                        if(otdb_col && otdb_col.filters.length && otdb_col.filters[0].hasOwnProperty('term')) {
                            var otdb_id = otdb_col.filters[0].term;
                            $scope.$parent.$parent.loadTaskByOTDBIdSelectAndJumpIntoView(otdb_id).then(function(loadedTask) {
                                if(loadedTask) {
                                    otdb_col.filters[0].term = null;
                                }
                            });
                        } else {
                            var mom_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'mom_id'; });

                            if(mom_col && mom_col.filters.length && mom_col.filters[0].hasOwnProperty('term')) {
                                var mom_id = mom_col.filters[0].term;
                                $scope.$parent.$parent.loadTaskByMoMIdSelectAndJumpIntoView(mom_id).then(function(task) {
                                    mom_col.filters[0].term = null;
                                    if(task == undefined) {
                                        //getting the task by mom_id did not find a task
                                        //maybe the entered id was a mom group_id?
                                        //let's try to loadTasksByMoMGroupIdSelectAndJumpIntoView
                                        $scope.$parent.$parent.loadTasksByMoMGroupIdSelectAndJumpIntoView(mom_id).then(function(tasks) {
                                            if(tasks == undefined || tasks.length == 0) {
                                                //getting the tasks by mom group id did not find any tasks
                                                //maybe the entered id was a mom parent group_id?
                                                //let's try to loadTasksByMoMParentGroupIdSelectAndJumpIntoView
                                                $scope.$parent.$parent.loadTasksByMoMParentGroupIdSelectAndJumpIntoView(mom_id).then(function(tasks) {
                                                    //pass
                                                });
                                            }
                                        });
                                    }
                                });
                            }
                        }
                    }
                });
            });

            gridApi.edit.on.afterCellEdit($scope,function(rowEntity, colDef, newValue, oldValue){
                var task = $scope.dataService.taskDict[rowEntity.id];
                var newTask = { id: task.id, status: task.status };
                $scope.dataService.putTask(newTask);
            });

            gridApi.selection.on.rowSelectionChanged($scope,function(row){
                if(row.entity.id) {
                    if(row.isSelected) {
                        $scope.dataService.addSelectedTaskId(row.entity.id);
                    } else if(!row.isSelected) {
                        $scope.dataService.removeSelectedTaskId(row.entity.id);
                    }
                }
            });
        }
    };

    function fillColumFilterSelectOptions(options, columnDef) {
        if (columnDef == undefined)
            return;

        var columnSelectOptions = [];
        if(options) {
            for(var i = 0; i < options.length; i++) {
                var option = options[i];
                if(option.hasOwnProperty('value') && option.hasOwnProperty('label')) {
                    columnSelectOptions.push({ value: option.value, label: option.label })
                }
                else {
                    columnSelectOptions.push({ value: option, label: option })
                }
            }
        }

        columnDef.filter.selectOptions = columnSelectOptions;
    };

    function populateListAsync() {
        $scope.$evalAsync(populateList);
    };

    function populateList() {
        if('tasks' in $scope.dataService && $scope.dataService.tasks.length > 0) {
            var viewFrom = $scope.dataService.viewTimeSpan.from;
            var viewTo = $scope.dataService.viewTimeSpan.to;

            var gridTasks = [];

            for(var task of $scope.dataService.tasks) {
                if(task.endtime >= viewFrom && task.starttime <= viewTo) {

                    var gridTask = {
                        blocked_by_ids: task.blocked_by_ids,
                        cluster: task.cluster,
                        description: task.description,
                        disk_usage: task.disk_usage,
                        disk_usage_readable: task.disk_usage_readable,
                        duration: task.duration,
                        endtime: task.endtime,
                        id: task.id,
                        ingest_status: task.ingest_status,
                        mom2object_id: task.mom2object_id,
                        mom_id: task.mom_id,
                        mom_object_group_id: task.mom_object_group_id,
                        mom_object_group_mom2object_id: task.mom_object_group_mom2object_id,
                        mom_object_group_name: task.mom_object_group_name,
                        mom_object_parent_group_id: task.mom_object_parent_group_id,
                        name: task.name,
                        nr_of_dataproducts: task.nr_of_dataproducts,
                        otdb_id: task.otdb_id,
                        predecessor_ids: task.predecessor_ids,
                        project_mom2object_id: task.project_mom2object_id,
                        project_mom_id: task.project_mom_id,
                        project_name: task.project_name,
                        specification_id: task.specification_id,
                        starttime: task.starttime,
                        status: task.status,
                        status_id: task.status_id,
                        sub_type: task.sub_type,
                        successor_ids: task.successor_ids,
                        type: task.type,
                        type_id: task.type_id,
                        data_pinned: task.data_pinned
                    };



                    gridTasks.push(task);
                }
            }

            $scope.gridOptions.data = gridTasks;
        } else
            $scope.gridOptions.data = []

        fillProjectsColumFilterSelectOptions()
        fillGroupsColumFilterSelectOptions();
    };

    function jumpToSelectedTaskRows() {
        var rowIndices = dataService.selected_task_ids.map(function(t_id) { return $scope.gridOptions.data.findIndex(function(row) {return row.id == t_id; } ); });
        rowIndices = rowIndices.filter(function(idx) {return idx > -1;}).sort();

        for(var rowIndex of rowIndices) {
            $scope.gridApi.core.scrollTo($scope.gridOptions.data[rowIndex], null);
        }
    };

    function onSelectedTaskIdsChanged() {
        var selected_task_ids = $scope.dataService.selected_task_ids;
        var rows = $scope.gridApi.grid.rows;

        for(var row of rows) {
            row.setSelected(selected_task_ids.indexOf(row.entity.id) != -1);
        }

        //find out if we have selected all tasks in a single mom group
        var selected_tasks = $scope.dataService.selected_task_ids.map(function(t_id) { return $scope.dataService.taskDict[t_id]; }).filter(function(t) { return t != undefined;});

        if(selected_tasks && selected_tasks.length > 1) {
            var selected_task_group_ids = selected_tasks.map(function(t) { return t.mom_object_group_id; });
            selected_task_group_ids = selected_task_group_ids.unique();

            if(selected_task_group_ids.length == 1) {
                //we have selected tasks in a single mom group
                //find out if we have selected all tasks within this mom group
                var mom_object_group_id = selected_task_group_ids[0];
                var all_group_tasks = $scope.dataService.tasks.filter(function(t) { return t.mom_object_group_id == mom_object_group_id; });

                if(all_group_tasks.length == selected_tasks.length) {
                    //we have selected all tasks in a single mom group
                    //apply filter on group column to see only tasks within this group
                    var group_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'mom_object_group_id'; });
                    if(group_col) {
                        var mom_object_group_name = all_group_tasks[0].mom_object_group_name;
                        var label = mom_object_group_id + ' ' + mom_object_group_name;

                        var groupSelectOptions = [ { value: mom_object_group_id, label: label} ];

                        fillColumFilterSelectOptions(groupSelectOptions, $scope.columns.find(function(c) {return c.field == 'mom_object_group_id'; }));
                        group_col.filters[0].term = mom_object_group_id;
                    }
                }
            }
        }


        $scope.$evalAsync(jumpToSelectedTaskRows);
    };

    $scope.$watch('dataService.taskChangeCntr', function() { populateListAsync(); });
    $scope.$watch('dataService.claimChangeCntr', function() { populateListAsync(); });
    $scope.$watch('dataService.viewTimeSpan', function() {
        populateListAsync();
        $scope.$evalAsync(jumpToSelectedTaskRows);
    }, true);

    function fillFilterSelectOptions() {
        if(dataService.initialLoadComplete) {
            fillStatusColumFilterSelectOptions();
            fillInfoColumFilterSelectOptions();
            fillTypeColumFilterSelectOptions();
            fillProjectsColumFilterSelectOptions();
            fillGroupsColumFilterSelectOptions();
            fillColumFilterSelectOptions(['CEP2', 'CEP4', 'DRAGNET'], $scope.columns.find(function(c) {return c.field == 'cluster'; }));
        }
    };

    $scope.$watch('dataService.filteredTaskChangeCntr', function()  { $scope.$evalAsync(fillFilterSelectOptions()); });
    $scope.$watch('dataService.initialLoadComplete',    function()  {
        populateListAsync();
        $scope.$evalAsync(fillFilterSelectOptions()); });

    function fillProjectsColumFilterSelectOptions() {
        var projectNames = [];
        var momProjectsDict = $scope.dataService.momProjectsDict;
        var tasks = $scope.dataService.filteredTasks;

        var project_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'project_name'; });
        if(project_col && project_col.filters.length && project_col.filters[0].term) {
            tasks = $scope.dataService.tasks;
        }

        //get unique projectIds from tasks
        var task_project_ids = tasks.map(function(t) { return t.project_mom_id; });
        task_project_ids = task_project_ids.unique();

        for(var project_id of task_project_ids) {
            if(momProjectsDict.hasOwnProperty(project_id)) {
                var projectName = momProjectsDict[project_id].name;
                if(!(projectName in projectNames)) {
                    projectNames.push(projectName);
                }
            }
        }
        projectNames.sort();
        fillColumFilterSelectOptions(projectNames, $scope.columns.find(function(c) {return c.field == 'project_name'; }));
    };

    function fillStatusColumFilterSelectOptions() {
        var tasks = $scope.dataService.filteredTasks;

        var status_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'status'; });
        if(status_col && status_col.filters.length && status_col.filters[0].term) {
            tasks = $scope.dataService.tasks;
        }

        //get unique statuses from tasks
        var task_statuses = tasks.map(function(t) { return t.status; });
        task_statuses = task_statuses.unique();
        task_statuses.sort();

        fillColumFilterSelectOptions(task_statuses, $scope.columns.find(function(c) {return c.field == 'status'; }));
    };

    function fillTypeColumFilterSelectOptions() {
        var tasks = $scope.dataService.filteredTasks;

        var type_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'type'; });
        if(type_col && type_col.filters.length && type_col.filters[0].term) {
            tasks = $scope.dataService.tasks;
        }

        //get unique types from tasks
        var task_types = tasks.map(function(t) { return t.type; });
        task_types = task_types.unique();
        task_types.sort();

        fillColumFilterSelectOptions(task_types, $scope.columns.find(function(c) {return c.field == 'type'; }));
    };

    function fillGroupsColumFilterSelectOptions() {
        var group_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'mom_object_group_id'; });
        if(!group_col || group_col.filter.term) {
            return;
        }

        var tasks = $scope.dataService.filteredTasks;

        //get unique groupNames from tasks
        var groupId2Name = {};
        var groupIds = [];

        for(var task of tasks) {
            if(task.mom_object_group_id) {
                if(!groupId2Name.hasOwnProperty(task.mom_object_group_id)) {
                    groupId2Name[task.mom_object_group_id] = task.mom_object_group_name;
                    groupIds.push(task.mom_object_group_id);
                }
            }
        }

        groupIds.sort();

        fillColumFilterSelectOptions(groupIds, $scope.columns.find(function(c) {return c.field == 'mom_object_group_id'; }));
    };

    function fillInfoColumFilterSelectOptions() {
        var tasks = $scope.dataService.filteredTasks;

        var info_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'info'; });
        if(info_col && info_col.filters.length && info_col.filters[0].term) {
            tasks = $scope.dataService.tasks;
        }

        // Generate a list of unique information items
        var task_info = [];
        var info_bit_flags = 0x00;
        for(var task of tasks) {
            if((task.blocked_by_ids.length > 0) && !(info_bit_flags & 0x01)) {
                task_info.push({ value: 0, label: 'Blocked tasks' });
                info_bit_flags |= 0x01;
            }

            if((task.ingest_status === 'ingesting') && !(info_bit_flags & 0x02)) {
                task_info.push({ value: 1, label: 'Ingests in progress' });
                info_bit_flags |= 0x02;
            }

            if((task.ingest_status === 'ingested') && !(info_bit_flags & 0x04)) {
                task_info.push({ value: 2, label: 'Successful ingests' });
                info_bit_flags |= 0x04;
            }

            if((task.ingest_status === 'failed') && !(info_bit_flags & 0x08)) {
                task_info.push({ value: 3, label: 'Failed ingests' });
                info_bit_flags |= 0x08;
            }

            if(task.data_pinned && !(info_bit_flags & 0x10)) {
                task_info.push({ value: 4, label: 'Pinned' });
                info_bit_flags |= 0x10;
            }
        };

        // sort on key values
        function keysrt(key,desc) {
          return function(a,b){
           return desc ? ~~(a[key] < b[key]) : ~~(a[key] > b[key]);
          }
        }

        task_info.sort(keysrt('value'));
        fillColumFilterSelectOptions(task_info, $scope.columns.find(function(c) {return c.field == 'info'; }));
    };

    $scope.$watch('dataService.selected_task_ids', onSelectedTaskIdsChanged, true);
    $scope.$watch('dataService.selected_project_id', function() {
        fillProjectsColumFilterSelectOptions();

        var project_col = $scope.gridApi.grid.columns.find(function(c) {return c.field == 'project_name'; });
        if(project_col && project_col.filters.length) {
            if(dataService.selected_project_id != undefined) {
                var projectName = dataService.momProjectsDict[dataService.selected_project_id].name;
                if(projectName != undefined) {
                    var project_names = project_col.filter.selectOptions.map(function(so) { return so.value;});
                    if(project_names.includes(projectName)) {
                        project_col.filters[0].term = projectName;
                    }
                }
            }
        }
    });
}]);

gridControllerMod.directive('contextMenu', ['$document', '$window', function($document, $window) {
    return {
      restrict: 'A',
      scope: {
      },
      link: function($scope, $element, $attrs) {
        function handleContextMenuEvent(event) {
            //pragmatic 'hard-coded' way of getting the dataService and the rowEntity via scope tree.
            var dataService = $scope.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.dataService;
            var cleanupCtrl = $scope.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.cleanupCtrl;
            var dataCtrlScope = $scope.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent;
            var row = $scope.$parent.$parent.$parent.row;
            var rowEntity = row.entity;

            if(!dataService || !rowEntity)
                return true;

            var taskId = rowEntity.id;
            var task = dataService.taskDict[taskId];
            if(!task)
                return true;

            if(!dataService.isTaskIdSelected(taskId)) {
                dataService.setSelectedTaskId(taskId);
            }

            var docElement = angular.element($document);

            //search for already existing contextmenu element
            while($document.find('#grid-context-menu').length) {
                //found, remove it, so we can create a fresh one
                $document.find('#grid-context-menu')[0].remove();

                //unbind document close event handlers
                docElement.unbind('click', closeContextMenu);
                docElement.unbind('contextmenu', closeContextMenu);
            }

            //create contextmenu element
            //with list of menu items,
            //each with it's own action
            var contextmenuElement = angular.element('<div id="grid-context-menu"></div>');
            var ulElement = angular.element('<ul class="dropdown-menu" role="menu" style="left:' + event.clientX + 'px; top:' + event.clientY + 'px; z-index: 100000; display:block;"></ul>');
            contextmenuElement.append(ulElement);

            var selected_tasks = dataService.selected_task_ids.map(function(t_id) { return dataService.taskDict[t_id]; });
            selected_tasks = selected_tasks.filter(function(t) { return t != undefined; });
            var selected_cep4_tasks = selected_tasks.filter(function(t) { return t['cluster'] == 'CEP4'; });

//                             var liElement = angular.element('<li><a href="#">Copy Task</a></li>');
//                             ulElement.append(liElement);
//                             liElement.on('click', function() {
//                                 closeContextMenu();
//                                 //TODO: remove link to dataService in this generic plugin
//                                 dataService.copyTask(task);
//                             });

            var liElement = angular.element('<li><a href="#">Select group</a></li>');
            ulElement.append(liElement);
            liElement.on('click', function() {
                closeContextMenu();
                dataCtrlScope.loadTasksByMoMGroupIdSelectAndJumpIntoView(task.mom_object_group_id);
            });

            var liElement = angular.element('<li><a href="#">Select parent group</a></li>');
            ulElement.append(liElement);
            liElement.on('click', function() {
                closeContextMenu();
                dataCtrlScope.loadTasksByMoMParentGroupIdSelectAndJumpIntoView(task.mom_object_parent_group_id);
            });

            var blocked_selected_cep4_tasks = selected_cep4_tasks.filter(function(t) { return (t.blocked_by_ids.length > 0); });

            if(blocked_selected_cep4_tasks.length > 0) {
                var liContent = '<li><a href="#">Select blocking predecessor(s)</a></li>'
                var liElement = angular.element(liContent);
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();

                    var blocking_predecessors = []
                    for(var task of blocked_selected_cep4_tasks) {
                        blocking_predecessors = blocking_predecessors.concat(task.blocked_by_ids);
                    }
                    row.grid.appScope.selectBlockingPredecessors(blocking_predecessors);
                });
            }

            var completed_selected_cep4_tasks = selected_cep4_tasks.filter(function(t) { return t.status == 'finished' || t.status == 'aborted'; });
            var completed_selected_cep4_observations = completed_selected_cep4_tasks.filter(function(t) { return t.type == 'observation'; });

            if(completed_selected_cep4_observations.length > 0 && dataService.config.inspection_plots_base_url) {
                var liElement = angular.element('<li><a href="#">Inspection Plots</a></li>');
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();

                    var window_cntr = 0;
                    for(var obs of completed_selected_cep4_observations) {
                        var url = dataService.config.inspection_plots_base_url + '/' + obs.otdb_id;
                        url = row.grid.appScope.sanitize_url(url);
                        setTimeout(function(url_arg) {
                            $window.open(url_arg, '_blank');
                        }, window_cntr*750, url);
                        window_cntr += 1;
                    }
                });
            }

            var selected_post_approved_observations = selected_tasks.filter(function(t) { return t.type ==
'observation' && t.status != 'approved'; });

            if(selected_post_approved_observations.length > 0 && dataService.config.sky_view_base_url) {
                var liElement = angular.element('<li><a href="#">Sky view</a></li>');
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();

                    var window_cntr = 0;
                    for(var obs of selected_post_approved_observations) {
                        var url = dataService.config.sky_view_base_url + '/' + obs.otdb_id;
                        url = row.grid.appScope.sanitize_url(url);
                        setTimeout(function(url_arg) {
                            $window.open(url_arg, '_blank');
                        }, window_cntr*750, url);
                        window_cntr += 1;
                    }
                });
            }

            var ingest_tasks = selected_tasks.filter(function(t) { return t.ingest_status != undefined; });

            if(ingest_tasks.length > 0 && dataService.config.lta_base_url) {
                var liElement = angular.element('<li><a href="#">Open in LTA catalogue</a></li>');
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();
                    row.grid.appScope.openLtaLocation(ingest_tasks);
                });
            }

            var liContent = selected_tasks.length > 0 ? '<li><a href="#">Show parset</a></li>' : '<li><a href="#" style="color:#aaaaaa">Show parset</a></li>'
            var liElement = angular.element(liContent);
            ulElement.append(liElement);
            if(selected_tasks.length > 0) {
                liElement.on('click', function() {
                    closeContextMenu();

                    var window_cntr = 0;
                    for(var selected_task of selected_tasks) {
                        var url = 'rest/tasks/otdb/' + selected_task.otdb_id + '/parset';
                        setTimeout(function(url_arg) {
                            $window.open(url_arg, '_blank');
                        }, window_cntr*750, url);
                        window_cntr += 1;
                    }

                });
            }

            var liContent = selected_cep4_tasks.length > 0 ? '<li><a href="#">Show disk usage</a></li>' : '<li><a href="#" style="color:#aaaaaa">Show disk usage</a></li>'
            var liElement = angular.element(liContent);
            ulElement.append(liElement);
            if(selected_cep4_tasks.length > 0) {
                liElement.on('click', function() {
                    closeContextMenu();
                    if(selected_cep4_tasks.length == 1) {
                        cleanupCtrl.showTaskDiskUsage(task);
                    } else {
                        cleanupCtrl.showTaskDiskUsage(completed_selected_cep4_tasks);
                    }
                });
            }

            var unpinned_selected_cep4_tasks = selected_cep4_tasks.filter(function(t) { return !t.data_pinned; });

            var liContent = unpinned_selected_cep4_tasks.length > 0 ? '<li><a href="#">Delete data</a></li>' : '<li><a href="#" style="color:#aaaaaa">Delete data</a></li>'
            var liElement = angular.element(liContent);
            ulElement.append(liElement);
            if(unpinned_selected_cep4_tasks.length > 0) {
                liElement.on('click', function() {
                    closeContextMenu();
                    cleanupCtrl.deleteTasksDataWithConfirmation(unpinned_selected_cep4_tasks);
                });
            }

            if(unpinned_selected_cep4_tasks.length > 0) {
                var liContent = '<li><a href="#">Pin task data against (auto) cleanup</a></li>';
                var liElement = angular.element(liContent);
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();

                    for(var t of unpinned_selected_cep4_tasks) {
                        var newTask = { id: t.id, data_pinned: true };
                        dataService.putTask(newTask);
                    }
                });
            }

            var pinned_selected_cep4_tasks = selected_cep4_tasks.filter(function(t) { return t.data_pinned; });

            if(pinned_selected_cep4_tasks.length > 0) {
                var liContent = '<li><a href="#">Unpin task data (allow (auto) cleanup to delete)</a></li>';
                var liElement = angular.element(liContent);
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();

                    for(var t of pinned_selected_cep4_tasks) {
                        var newTask = { id: t.id, data_pinned: false };
                        dataService.putTask(newTask);
                    }
                });
            }

            var schedulable_tasks = selected_tasks.filter(function(t) { return t.status == 'approved' || t.status == 'conflict' || t.status == 'error'; });

            if(schedulable_tasks.length > 0) {
                var liContent = '<li><a href="#">(Re)schedule CEP4 task(s)</a></li>'
                var liElement = angular.element(liContent);
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();
                    for(var pl of schedulable_tasks) {
                        var newTask = { id: pl.id, status: 'prescheduled' };
                        dataService.putTask(newTask);
                    }
                });
            }

            var unschedulable_selected_tasks = selected_tasks.filter(function(t) { return t.status == 'prescheduled' || t.status == 'scheduled' || t.status == 'queued' || t.status == 'error' || t.status == 'conflict'; });

            if(unschedulable_selected_tasks.length > 0) {
                var liContent = '<li><a href="#">Unschedule (pre)scheduled/queued/error/conflict tasks</a></li>'
                var liElement = angular.element(liContent);
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();
                    for(var pl of unschedulable_selected_tasks) {
                        if(pl.status == 'queued') {
                            var newTask = { id: pl.id, status: 'aborted' };
                            dataService.putTask(newTask);
                        }

                        var newTask = { id: pl.id, status: 'approved' };
                        dataService.putTask(newTask);
                    }
                });
            }

            var active_selected_cep4_pipelines = selected_cep4_tasks.filter(function(t) { return (t.status == 'active' || t.status == 'completing') && t.type == 'pipeline'; });

            if(active_selected_cep4_pipelines.length > 0) {
                var liContent = '<li><a href="#">Abort active CEP4 pipelines</a></li>'
                var liElement = angular.element(liContent);
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();
                    for(var pl of active_selected_cep4_pipelines) {
                        var newTask = { id: pl.id, status: 'aborted' };
                        dataService.putTask(newTask);
                    }
                });
            }

            var aborted_selected_cep4_pipelines = selected_cep4_tasks.filter(function(t) { return (t.status == 'aborted' || t.status == 'error') && t.type == 'pipeline'; });

            if(aborted_selected_cep4_pipelines.length > 0) {
                var liContent = '<li><a href="#">Reschedule aborted/error CEP4 pipelines</a></li>'
                var liElement = angular.element(liContent);
                ulElement.append(liElement);
                liElement.on('click', function() {
                    closeContextMenu();
                    for(var pl of aborted_selected_cep4_pipelines) {
                        var newTask = { id: pl.id, status: 'prescheduled' };
                        dataService.putTask(newTask);
                    }
                });
            }

            var closeContextMenu = function(cme) {
                contextmenuElement.remove();

                //unbind document close event handlers
                docElement.unbind('click', closeContextMenu);
                docElement.unbind('contextmenu', closeContextMenu);
            };

            //click anywhere to remove the contextmenu
            docElement.bind('click', closeContextMenu);
            docElement.bind('contextmenu', closeContextMenu);

            //add contextmenu to body
            var body = $document.find('body');
            body.append(contextmenuElement);

            //prevent bubbling event upwards
            return false;
        }

        $element.bind('contextmenu', handleContextMenuEvent);

        $scope.$on('$destroy', function() {
            $element.unbind('contextmenu', handleContextMenuEvent);
        });
      }
    };
  }]);
