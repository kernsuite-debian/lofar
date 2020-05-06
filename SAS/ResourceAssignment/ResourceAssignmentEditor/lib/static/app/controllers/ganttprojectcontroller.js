// $Id: ganttprojectcontroller.js 32761 2015-11-02 11:50:21Z schaap $

var ganttProjectControllerMod = angular.module('GanttProjectControllerMod', [
                                        'gantt',
                                        'gantt.sortable',
                                        'gantt.movable',
                                        'gantt.drawtask',
                                        'gantt.tooltips',
                                        'gantt.bounds',
                                        'gantt.progress',
                                        'gantt.table',
                                        'gantt.tree',
                                        'gantt.groups',
                                        'gantt.dependencies',
                                        'gantt.overlap',
                                        'gantt.resizeSensor',
                                        'gantt.contextmenu']).config(['$compileProvider', function($compileProvider) {
    $compileProvider.debugInfoEnabled(false); // Remove debug info (angularJS >= 1.3)
}]);

ganttProjectControllerMod.controller('GanttProjectController', ['$scope', 'dataService', function($scope, dataService) {

    var self = this;
    self.doInitialCollapse = true;

    $scope.dataService = dataService;
    $scope.ganttData = [];
    $scope.enabled = true;

    self.taskStatusColors = dataService.taskStatusColors;

    $scope.options = {
        mode: 'custom',
        viewScale: '1 hours',
        currentDate: 'line',
        currentDateValue: $scope.dataService.lofarTime,
        columnMagnet: '1 minutes',
        timeFramesMagnet: false,
        sideMode: 'Table',
        autoExpand: 'both',
        taskOutOfRange: 'truncate',
        dependencies: false,
        api: function(api) {
            // API Object is used to control methods and events from angular-gantt.
            $scope.api = api;

            api.core.on.ready($scope, function () {
                    api.tasks.on.moveEnd($scope, moveHandler);
                    api.tasks.on.resizeEnd($scope, moveHandler);
                }
            );

            api.directives.on.new($scope, function(directiveName, directiveScope, directiveElement) {
                if (directiveName === 'ganttRow' || directiveName === 'ganttRowLabel' ) {
                    directiveElement.bind('click', function(event) {
                        if(directiveScope.row.model.project) {
                            $scope.dataService.selected_project_id = directiveScope.row.model.project.id;
                        }
                    });
                } else if (directiveName === 'ganttTask') {
                    directiveElement.bind('click', function(event) {
                        if(directiveScope.task.model.raTask) {
                            if(event.ctrlKey) {
                                $scope.dataService.toggleTaskSelection(directiveScope.task.model.raTask.id);
                            } else {
                                $scope.dataService.setSelectedTaskId(directiveScope.task.model.raTask.id);
                            }
                        }
                    });
                    directiveElement.bind('dblclick', function(event) {
                        if(directiveScope.task.model.raTask) {
                            $scope.dataService.setSelectedTaskId(directiveScope.task.model.raTask.id);
                            $scope.jumpToSelectedTasks();
                        }
                    });
                }
            });

            api.directives.on.destroy($scope, function(directiveName, directiveScope, directiveElement) {
                if (directiveName === 'ganttRow' || directiveName === 'ganttRowLabel' || directiveName === 'ganttTask') {
                    directiveElement.unbind('click');
                }
                if (directiveName === 'ganttTask') {
                    directiveElement.unbind('dblclick');
                }
            });
        }
    };

    function moveHandler(item)
    {
        var task_id = item.model.id;

        if(task_id) {
            var task = $scope.dataService.taskDict[task_id];
            var updatedTask = {
                id: task.id,
                starttime: item.model.from._d,
                endtime: item.model.to._d
            };
            $scope.dataService.putTask(updatedTask);
        }
    };

    function updateGanttDataAsync() {
        $scope.$evalAsync(updateGanttData);
    };

    function updateGanttData() {
        if(!$scope.enabled) {
            return;
        }

        if(!dataService.initialLoadComplete) {
            return;
        }

        var projectsDict = $scope.dataService.momProjectsDict;
        var numProjecs = $scope.dataService.momProjects.length;

        if(numProjecs == 0) {
            $scope.ganttData = [];
            return;
        }

        var taskDict = $scope.dataService.taskDict;
        var tasks = $scope.dataService.filteredTasks;
        var numTasks = tasks.length;

        //only enable dependencies (arrows between tasks) in detailed view
        $scope.options.dependencies = false;
        var has_any_task_with_dependencies = false;

        var ganttRows = [];

        if(numProjecs > 0 && numTasks > 0) {
            var lowerViewBound = $scope.dataService.viewTimeSpan.from;
            var upperViewBound = $scope.dataService.viewTimeSpan.to;
            $scope.options.fromDate = lowerViewBound;
            $scope.options.toDate = upperViewBound;
            var fullTimespanInMinutes = (upperViewBound - lowerViewBound) / (60 * 1000);

            $scope.options.dependencies = (fullTimespanInMinutes <= 6*60 && numTasks <= 100) || numTasks < 20;

            if(fullTimespanInMinutes > 28*24*60) {
                $scope.options.viewScale = '7 days';
            } else if(fullTimespanInMinutes > 14*24*60) {
                $scope.options.viewScale = '1 day';
            } else if(fullTimespanInMinutes > 7*24*60) {
                $scope.options.viewScale = '6 hours';
            } else if(fullTimespanInMinutes > 2*24*60) {
                $scope.options.viewScale = '3 hours';
            } else if(fullTimespanInMinutes > 12*60) {
                $scope.options.viewScale = '1 hours';
            } else if(fullTimespanInMinutes > 3*60) {
                $scope.options.viewScale = '30 minutes';
            } else {
                $scope.options.viewScale = '15 minutes';
            }

            //start with aggregating all tasks per type,
            //and plot these in the upper rows,
            //so we can see the observartion and pipeline scheduling usage/efficiency
            for(var type of ['observation', 'pipeline', 'reservation']) {
                var typeTasks = tasks.filter(function(t) { return t.type == type;}).sort(function(a, b) { return a.starttime.getTime() -  b.starttime.getTime(); });;
                var numTypeTasks = typeTasks.length;

                if(numTypeTasks > 0) {
                    var typeAggregateRow = {
                            id: type + 's_aggregated',
                            name: ('All ' + type + 's').toUpperCase(),
                            tasks: []
                        };
                    ganttRows.push(typeAggregateRow);

                    var task = typeTasks[0];

                    var rowTask = {
                        id: typeAggregateRow.id + '_task_' + typeAggregateRow.tasks.length,
                        from: task.starttime,
                        color: '#cceecc',
                        movable: false
                    };

                    if(rowTask.from < lowerViewBound) {
                        rowTask.from = lowerViewBound;
                    }

                    for(var i = 1; i < numTypeTasks; i++) {
                        var prev_task = task;
                        task = typeTasks[i];

                        if(task.starttime > prev_task.endtime) {
                            rowTask.to = prev_task.endtime;

                            if(rowTask.to > upperViewBound) {
                                rowTask.to = upperViewBound;
                            }

                            typeAggregateRow.tasks.push(rowTask);

                            rowTask = {
                                id: typeAggregateRow.id + '_task_' + typeAggregateRow.tasks.length,
                                from: task.starttime,
                                color: '#cceecc',
                                movable: false
                            };

                            if(rowTask.from < lowerViewBound) {
                                rowTask.from = lowerViewBound;
                            }
                        }
                    }

                    if(!rowTask.to) {
                        rowTask.to = task.endtime;

                        if(rowTask.to > upperViewBound) {
                            rowTask.to = upperViewBound;
                        }
                    }

                    typeAggregateRow.tasks.push(rowTask);
                    var aggTaskTotalDuration = 0.0 + typeAggregateRow.tasks.map(function(t) { return t.to - t.from;}).reduce(function(a, b) { return a+b; });
                    var usage = aggTaskTotalDuration / (upperViewBound - lowerViewBound);
                    var usagePerc = parseFloat(Math.round(100.0 * usage * 10.0) / 10.0).toFixed(1);
                    typeAggregateRow.name += ' (' + usagePerc + '%)';
                }
            }

            var editableTaskStatusIds = $scope.dataService.editableTaskStatusIds;
            var ganttRowsDict = {};

            for(var i = 0; i < numTasks; i++) {
                var task = tasks[i];
                var project = projectsDict[task.project_mom_id];

                if(!project) {
                    continue;
                }

                var projectTypeRowsId = 'project_' + task.project_mom_id + '_type_' + task.type_id;
                var ganttProjectTypeRows = ganttRowsDict[projectTypeRowsId];

                if(!ganttProjectTypeRows) {
                    ganttProjectTypeRows = [];
                    ganttRowsDict[projectTypeRowsId] = ganttProjectTypeRows;
                }

                var availableRow = ganttProjectTypeRows.find(function(row) {
                    var overlappingTasks = row.tasks.filter(function(t) {
                        return (t.from >= task.starttime && t.from <= task.endtime) ||
                               (t.to >= task.starttime && t.to <= task.endtime) ||
                               (t.from <= task.starttime && t.to >= task.endtime);
                    });
                    return overlappingTasks.length == 0;
                });

                if(!availableRow)
                {
                    availableRow = {
                        id: projectTypeRowsId + '_' + (ganttProjectTypeRows.length+1),
                        name: project.name + ' ' + task.type,
                        project: project,
                        tasks: []
                    };

                    if(task.type == 'reservation' && project.name.toLowerCase().includes('reservation')) {
                        availableRow.name = project.name;
                    }

                    ganttProjectTypeRows.push(availableRow);
                    ganttRows.push(availableRow);
                }

                // Scheduled tasks that are blocked tasks are shown differently and use a tooltip
                var css_class = "task-status-";
                if (task.blocked_by_ids.length > 0) {
                    css_class += "blocked";
                }
                else {
                    css_class += task.status;
                }

                var rowTask = {
                    id: task.id.toString(),
                    name: task.name,
                    from: task.starttime,
                    to: task.endtime,
                    raTask: task,

                    // Leave color property undefined; it is now defined by CSS
                    //color: self.taskStatusColors[task.status],

                    classes: css_class,
                    movable: $.inArray(task.status_id, editableTaskStatusIds) > -1
                };

                if(dataService.isTaskIdSelected(task.id)) {
                    rowTask.classes += ' task-selected-task';
                }

                if($scope.options.dependencies && task.predecessor_ids && task.predecessor_ids.length > 0) {
                    rowTask['dependencies'] = [];
                    for(var predId of task.predecessor_ids) {
                            rowTask['dependencies'].push({'from': predId});
                            has_any_task_with_dependencies = true;
                    }
                }

                availableRow.tasks.push(rowTask);
            }
        }

        //only enable dependencies (arrows between tasks) if there are any tasks with dependencies
        $scope.options.dependencies &= has_any_task_with_dependencies;

        $scope.ganttData = ganttRows;
    };

    $scope.$watch('dataService.initialLoadComplete', updateGanttDataAsync);
    $scope.$watch('dataService.selected_task_ids', updateGanttDataAsync, true);
    $scope.$watch('dataService.viewTimeSpan', updateGanttDataAsync, true);
    $scope.$watch('dataService.filteredTaskChangeCntr', updateGanttDataAsync);
    $scope.$watch('enabled', function() { setTimeout(updateGanttDataAsync, 500); } );
    $scope.$watch('dataService.lofarTime', function() {
        $scope.$evalAsync(function() {
            if($scope.dataService.lofarTime.getSeconds() % 10 == 0) {
                $scope.options.currentDateValue= $scope.dataService.lofarTime;}
        });
    });
}
]);
