// $Id: controller.js 32761 2015-11-02 11:50:21Z schaap $

var cleanupControllerMod = angular.module('CleanupControllerMod', ['ui.bootstrap', 'ngMaterial', 'ngSanitize']);

cleanupControllerMod.controller('CleanupController', ['$scope', '$uibModal', '$mdDialog', '$http', '$q', 'dataService', function($scope, $uibModal, $mdDialog, $http, $q, dataService) {
    var self = this;

    self.getTaskDataPath = function(task) {
        var defer = $q.defer();

        $http.get('/rest/tasks/' + task.id + '/datapath').success(function(result) {
            defer.resolve(result);
        }).error(function(result) {
            console.log("Error. Could get data path for task " + task.id + ", " + result);
            alert(result);
        });

        return defer.promise;
    };

    self.deleteTasksDataWithConfirmation = function(tasks) {
        suc_tasks_promises = [];
        for(var task of tasks) {
            if(task.successor_ids) {
                for(var suc_id of task.successor_ids) {
                    suc_tasks_promises.push(dataService.getTask(suc_id));
                }
            }
        }

        $q.all(suc_tasks_promises).then(function(suc_tasks) {
            var unfinished_suc_tasks = suc_tasks.filter(function(t) { return t && !(t.status == 'finished' || t.status == 'obsolete') });

            if(unfinished_suc_tasks.length > 0) {
                var unfinished_ids = unfinished_suc_tasks.map(function(t) { return t.id; });
                var unfinished_otdb_ids = unfinished_suc_tasks.map(function(t) { return t.otdb_id; });

                var undeletable_predecessors = tasks.filter(function(t) {
                    for (var suc_id of t.successor_ids) {
                        if(unfinished_ids.includes(suc_id))
                            return true;
                    }
                    return false;
                });
                var undeletable_pred_otdb_ids = undeletable_predecessors.map(function(t) { return t.otdb_id; });

                $mdDialog.show($mdDialog.confirm()
                                .parent(angular.element(document.querySelector('#popupContainer')))
                                .title('Warning: Delete data which is needed by succesors?')
                                .htmlContent("Cannot delete data for " + undeletable_pred_otdb_ids + " because there are unfinished successors: " + unfinished_otdb_ids + "<br>Do you want to set the unfinished succesors to obsolete and proceed with the deletion of all data?")
                                .ariaLabel('Error')
                                .ok('Yes')
                                .cancel('No')).then(function() {

                                                        waiting_dialog = $mdDialog.show($mdDialog.alert()
                                                                                        .parent(angular.element(document.querySelector('#popupContainer')))
                                                                                        .title('Waiting...')
                                                                                        .textContent("Waiting for the unfinished succesors to become obsolete...")
                                                                                        .ariaLabel('Waiting')
                                                                                        .ok('Ok'));

                                                        for(var unfinished_suc_task of unfinished_suc_tasks) {
                                                            var newTask = { id: unfinished_suc_task.id, status: 'obsolete' };
                                                            dataService.putTask(newTask);
                                                        }

                                                        var waitForTasksToBecomeObsolete = function(tasks_to_be_obsolete) {
                                                            // polling for all tasks_to_be_obsolete
                                                            // if they are all obsolete, then the returned promise resolves
                                                            // else, we poll again, and again, until they are all obsolete
                                                            var defer = $q.defer();
                                                            var load_promises = tasks_to_be_obsolete.map(function(t) { return dataService.getTask(t.id, true); });

                                                            $q.all(load_promises).then(function(loaded_tasks) {
                                                                var loaded_obsolete_tasks = loaded_tasks.filter(function(t) { return t['status'] == 'obsolete';});
                                                                if(loaded_obsolete_tasks.length == loaded_tasks.length) {
                                                                    defer.resolve();
                                                                } else {
                                                                    waitForTasksToBecomeObsolete(tasks_to_be_obsolete).then(function() {
                                                                        defer.resolve();
                                                                    });
                                                                }
                                                            });
                                                            return defer.promise;
                                                        };

                                                        waitForTasksToBecomeObsolete(unfinished_suc_tasks).then(
                                                            function() {
                                                                $mdDialog.cancel(waiting_dialog);
                                                                self.deleteTasksDataWithConfirmation(tasks);
                                                            });
                                                    }, function() {
                                                    });
                return;
            }

            du_waiting_dialog = $mdDialog.show($mdDialog.alert()
                                              .parent(angular.element(document.querySelector('#popupContainer')))
                                              .title('Cleanup waiting...')
                                              .textContent("Gathering disk size and data type information about the selected tasks.")
                                              .ariaLabel('Cleanup waiting...')
                                              .ok('Ok'));

            du_promises = [];
            for(var task of tasks) {
                du_promises.push(dataService.getTaskDiskUsage(task));
            }

            $q.all(du_promises).then(function(du_results) {
                $mdDialog.cancel(du_waiting_dialog);

                var unfound_du_results = du_results.filter(function(r) { return !r || !r.found; });

                if(unfound_du_results.length == du_results.length) {
                    $mdDialog.show($mdDialog.alert()
                            .parent(angular.element(document.querySelector('#popupContainer')))
                            .title('Warning')
                            .textContent("Could not find any data to delete for the selected tasks.")
                            .ariaLabel('Warning')
                            .ok('Ok'));
                } else if(unfound_du_results.length > 0) {
                    $mdDialog.show($mdDialog.confirm()
                            .parent(angular.element(document.querySelector('#popupContainer')))
                            .title('Info')
                            .textContent("Could not find data to delete for one or more of the selected tasks.\nContinue to delete the rest?")
                            .ariaLabel('Info')
                            .ok('Yes')
                            .cancel('No')).then(function() {
                                openDeleteConfirmationDialog(du_results);
                            });
                } else {
                    openDeleteConfirmationDialog(du_results);
                }
            });
        });
    };

    function deleteTaskData(task, delete_is, delete_cs, delete_uv, delete_im, delete_img, delete_pulp, delete_scratch, force_delete=false) {
        var params = {delete_is:delete_is, delete_cs:delete_cs, delete_uv:delete_uv, delete_im:delete_im, delete_img:delete_img, delete_pulp:delete_pulp, delete_scratch:delete_scratch, force_delete:force_delete};
        $http.delete('/rest/tasks/' + task.id + '/cleanup', {data: params}).error(function(result) {
            console.log("Error. Could cleanup data for task " + task.id + ", " + result);
        }).success(function(result) {
            console.log(result.message);
        });
    };

    function openDeleteConfirmationDialog(du_results) {
        var modalInstance = $uibModal.open({
            animation: false,
            template: '<div class="modal-header">\
                            <h3 class="modal-title">Are you sure?</h3>\
                        </div>\
                        <div class="modal-body">\
                            <p>This will delete all selected data in: \
                            <ul><li ng-repeat="path in paths">{{path}}</li></ul>\
                            <br>Are you sure?</p>\
                            <label ng-if="has_is" style="margin-left:24px">IS: {{amount_is}}<input style="margin-left:8px" type="checkbox" ng-model="$parent.delete_is"></label>\
                            <label ng-if="has_cs" style="margin-left:24px">CS: {{amount_cs}}<input style="margin-left:8px" type="checkbox" ng-model="$parent.delete_cs"></label>\
                            <label ng-if="has_uv" style="margin-left:24px">UV: {{amount_uv}}<input style="margin-left:8px" type="checkbox" ng-model="$parent.delete_uv"></label>\
                            <label ng-if="has_im" style="margin-left:24px">IM: {{amount_im}}<input style="margin-left:8px" type="checkbox" ng-model="$parent.delete_im"></label>\
                            <label ng-if="has_img" style="margin-left:24px">Images: {{amount_img}}<input style="margin-left:8px" type="checkbox" ng-model="$parent.delete_img"></label>\
                            <label ng-if="has_pulp" style="margin-left:24px">Pulp: {{amount_pulp}}<input style="margin-left:8px" type="checkbox" ng-model="$parent.delete_pulp"></label>\
                            <label ng-if="has_scratch" style="margin-left:24px">scratch: {{amount_scratch}}<input style="margin-left:8px" type="checkbox" ng-model="$parent.delete_scratch"></label>\
                        </div>\
                        <div class="modal-footer">\
                            <label style="margin-right:24px" title="force delete action, even if data is (partially) un-ingested or needed by successor pipeline(s)">force\
                            <input style="margin-right:2px; margin-top:2px; float: left" type="checkbox" ng-model="$parent.force_delete"></label>\
                            <button class="btn btn-primary" type="button" ng-click="ok()">OK</button>\
                            <button class="btn btn-warning" type="button" autofocus ng-click="cancel()">Cancel</button>\
                        </div>',
            controller: function ($scope, $uibModalInstance) {
                du_results = du_results.filter(function(r) { return r && r.found; });

                $scope.paths = du_results.map(function(r) { return r.task_directory.path; });
                $scope.has_is = false;
                $scope.has_cs = false;
                $scope.has_uv = false;
                $scope.has_im = false;
                $scope.has_img = false;
                $scope.has_pulp = false;
                $scope.has_scratch = false;
                $scope.amount_is = 0;
                $scope.amount_cs = 0;
                $scope.amount_uv = 0;
                $scope.amount_im = 0;
                $scope.amount_img = 0;
                $scope.amount_pulp = 0;
                $scope.amount_scratch = 0;

                for(var du_result of du_results) {
                    var path = du_result.task_directory.path;
                    var has_is = du_result.sub_directories.hasOwnProperty(path + '/is');
                    var has_cs = du_result.sub_directories.hasOwnProperty(path + '/cs');
                    var has_uv = du_result.sub_directories.hasOwnProperty(path + '/uv');
                    var has_im = du_result.sub_directories.hasOwnProperty(path + '/im');
                    var has_img = du_result.sub_directories.hasOwnProperty(path + '/img');
                    var has_pulp = du_result.sub_directories.hasOwnProperty(path + '/pulp');
                    var has_scratch = du_result.task_directory.hasOwnProperty('scratch_paths');

                    $scope.has_is |= has_is;
                    $scope.has_cs |= has_cs;
                    $scope.has_uv |= has_uv;
                    $scope.has_im |= has_im;
                    $scope.has_img |= has_img;
                    $scope.has_pulp |= has_pulp;
                    $scope.has_scratch |= has_scratch;

                    $scope.amount_is += has_is ? du_result.sub_directories[path + '/is'].disk_usage : 0;
                    $scope.amount_cs += has_cs ? du_result.sub_directories[path + '/cs'].disk_usage : 0;
                    $scope.amount_uv += has_uv ? du_result.sub_directories[path + '/uv'].disk_usage : 0;
                    $scope.amount_im += has_im ? du_result.sub_directories[path + '/im'].disk_usage : 0;
                    $scope.amount_img += has_img ? du_result.sub_directories[path + '/img'].disk_usage : 0;
                    $scope.amount_pulp += has_pulp ? du_result.sub_directories[path + '/pulp'].disk_usage : 0;
                    if(has_scratch) {
                        for(var scratch_path in du_result.task_directory.scratch_paths) {
                            var scratch_path_du = du_result.task_directory.scratch_paths[scratch_path];
                            if(scratch_path_du.found) {
                                $scope.amount_scratch += scratch_path_du.disk_usage;
                            }
                        }
                    }
                }

                $scope.amount_is = dataService.humanreadablesize($scope.amount_is);
                $scope.amount_cs = dataService.humanreadablesize($scope.amount_cs);
                $scope.amount_uv = dataService.humanreadablesize($scope.amount_uv);
                $scope.amount_im = dataService.humanreadablesize($scope.amount_im);
                $scope.amount_img = dataService.humanreadablesize($scope.amount_img);
                $scope.amount_pulp = dataService.humanreadablesize($scope.amount_pulp);
                $scope.amount_scratch = dataService.humanreadablesize($scope.amount_scratch);

                $scope.delete_is = true;
                $scope.delete_cs = true;
                $scope.delete_uv = true;
                $scope.delete_im = true;
                $scope.delete_img = true;
                $scope.delete_pulp = true;
                $scope.delete_scratch = true;

                $scope.ok = function () {
                    $uibModalInstance.close();
                    for(var du_result of du_results) {
                        var task = du_result.task;
                        deleteTaskData(task, $scope.delete_is, $scope.delete_cs, $scope.delete_uv, $scope.delete_im, $scope.delete_img, $scope.delete_pulp, $scope.delete_scratch, $scope.force_delete);
                    }
                };

                $scope.cancel = function () {
                    $uibModalInstance.dismiss('cancel');
                };
            }
        });
    };

    self.showAllProjectsDiskUsage = function() {
        self.showTaskDiskUsage(undefined);
    }

    self.showTaskDiskUsage = function(task) {
        var modalInstance = $uibModal.open({
            animation: false,
            template: '<div class="modal-header">\
                            <h3 class="modal-title">Disk usage</h3>\
                        </div>\
                        <div class="modal-body" style="text-align:right">\
                            <highchart id="chart_total_disk_usage" config="totalDiskUsageChartConfig" style="width: 960px; height: 120px; margin-bottom: 20px;" ></highchart>\
                            <hr>\
                            <highchart id="chart_disk_usage" config="diskUsageChartConfig" style="width: 960px; height: 720px;" ></highchart>\
                            <p>\
                              <span style="margin-right:8px" title="You are looking at cached data which might be (too) old.\nClick refresh to update the cache.">Last updated at: {{leastRecentCacheTimestamp | date }}</span>\
                              <button class="btn btn-primary glyphicon glyphicon-refresh" type="button" ng-click="refresh()" \
                              ng-disabled="is_loading" \
                              title="Force a refresh of the disk usage scan.\nCan take a while..."></button>\
                            </p>\
                        </div>\
                        <div class="modal-footer">\
                            <span style="margin-right:8px">1KB=1000bytes</span>\
                            <button class="btn btn-primary glyphicon glyphicon-level-up" type="button" ng-click="up()" title="Up one level" ng-if="watchedObjectType!=\'projects\'"></button>\
                            <button class="btn btn-primary" type="button" autofocus ng-click="ok()">OK</button>\
                        </div>',
            controller: function ($scope, $uibModalInstance) {
                $scope.ok = function () {
                    $uibModalInstance.close();
                };

                const OBJECT_TYPE_TASK = 'task';
                const OBJECT_TYPE_TASKS = 'tasks';
                const OBJECT_TYPE_PROJECT = 'project';
                const OBJECT_TYPE_PROJECTS = 'projects';
                $scope.watchedObjectType = OBJECT_TYPE_TASK;

                $scope.is_loading = false;

                $scope.current_otdb_id = undefined;
                $scope.current_project_name = undefined;

                $scope.leastRecentCacheTimestamp = '';

                $scope.onPieClicked = function(event) {
                    switch($scope.watchedObjectType) {
                        case OBJECT_TYPE_TASKS:
                        case OBJECT_TYPE_PROJECT:
                            loadTaskDiskUsage(this.otdb_id); //this.otdb_id -> 'this' is the clicked pie
                            break;
                        case OBJECT_TYPE_PROJECTS:
                            loadProjectDiskUsage(this.project_name);
                            break;
                    }
                };

                $scope.up = function () {
                    switch($scope.watchedObjectType) {
                        case OBJECT_TYPE_TASK:
                            loadProjectDiskUsage($scope.diskUsageChartSeries[0].project_name);
                            break;
                        case OBJECT_TYPE_TASKS:
                        case OBJECT_TYPE_PROJECT:
                            loadAllProjectsDiskUsage();
                            break;
                    }
                };

                $scope.refresh = function () {
                    switch($scope.watchedObjectType) {
                        case OBJECT_TYPE_TASK:
                            loadTaskDiskUsage($scope.current_otdb_id, true);
                            break;
                        case OBJECT_TYPE_PROJECT:
                            loadProjectDiskUsage($scope.current_project_name, true);
                            break;
                        case OBJECT_TYPE_PROJECTS:
                            loadAllProjectsDiskUsage(true);
                            break;
                    }
                };

                $scope.diskUsageChartSeries = [{name:'Loading data...', data:[]}];

                $scope.diskUsageChartConfig = {
                    options: {
                        chart: {
                            type: 'pie',
                            animation: {
                                duration: 200
                            },
                            legend: {
                                enabled: false
                            }
                        },
                        legend: {
                            enabled: false
                        },
                        plotOptions: {
                            pie: {
                                allowPointSelect: true,
                                cursor: 'pointer',
                                dataLabels: {
                                    enabled: true
                                },
                                showInLegend: false
                            },
                            series: {
                                point: {
                                    events: {
                                        click: $scope.onPieClicked
                                    }
                                },
                                turboThreshold:0
                            }
                        },
                        tooltip: {
                            headerFormat: '{series.name}<br/>',
                            pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>'
                        }
                    },
                    series: $scope.diskUsageChartSeries,
                    title: {
                        text: 'Loading data...'
                    },
                    credits: {
                        enabled: false
                    },
                    loading: false
                }

                $scope.totalDiskUsageChartConfig = {
                    options: {
                        chart: {
                            type: 'bar',
                            animation: {
                                duration: 200
                            },
                            legend: {
                                enabled: false
                            }
                        },
                        navigation: {
                            buttonOptions: {
                                enabled: false
                            }

                        },
                        plotOptions: {
                            bar: {
                                allowPointSelect: false,
                                cursor: 'pointer',
                                dataLabels: {
                                    enabled: false
                                },
                                showInLegend: false,
                            },
                            series: {
                                stacking: 'normal',
                                pointWidth: 32,
                                turboThreshold:0
                            },
                        },
                        yAxis: {
                            visible: true,
                            title: {text:'Percentage'},
                            min: 0,
                            max: 100,
                            endOnTick: false
                        },
                        xAxis: {
                            visible: false
                        },
                        tooltip: {
                            headerFormat: '{series.name}<br/>',
                            pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>'
                        },
                    },
                    series: [],
                    title: {
                        text: 'CEP4 total disk usage'
                    },
                    credits: {
                        enabled: false
                    },
                    loading: false
                }

                var cep4storage_resource = dataService.resources.find(function(r) { return r.name == 'CEP4_storage:/data'; });
                if(cep4storage_resource) {
                    dataService.getProjectsDiskUsage().then(function(result) {
                        if(result.found) {
                            var projects_du = result.projectdir.disk_usage;
                            var misc_du = cep4storage_resource.used_capacity - projects_du;
                            var total_cap = cep4storage_resource.total_capacity;

                            $scope.totalDiskUsageChartConfig.series = [{name:'Free ' + dataService.humanreadablesize(cep4storage_resource.available_capacity, 1) + 'B',
                                                                        data:[100.0*cep4storage_resource.available_capacity/total_cap],
                                                                        color:'#66ff66'},
                                                                       {name:'Misc ' + dataService.humanreadablesize(misc_du, 1) + 'B',
                                                                        data:[100.0*misc_du/total_cap],
                                                                        color:'#aaaaff'},
                                                                       {name:'Projects ' + dataService.humanreadablesize(projects_du, 1) + 'B',
                                                                        data:[100.0*projects_du/total_cap],
                                                                        color:'#ff6666'}];
                        }
                    });
                }

                var loadTaskDiskUsage = function(otdb_id, force) {
                    $scope.current_otdb_id = otdb_id;
                    $scope.current_project_name = undefined;
                    $scope.is_loading = true;
                    dataService.getTaskDiskUsageByOTDBId(otdb_id, force).then(function(result) {
                        $scope.is_loading = false;
                        if(result.found) {
                            $scope.watchedObjectType = OBJECT_TYPE_TASK;
                            $scope.diskUsageChartConfig.title.text = result.task_directory.name + ' ' + result.task_directory.disk_usage_readable;
                            $scope.diskUsageChartSeries[0].name = $scope.diskUsageChartConfig.title.text;
                            var path_parts = result.task_directory.path.split('/');
                            $scope.diskUsageChartSeries[0].project_name = path_parts[path_parts.length-2];
                            $scope.diskUsageChartSeries[0].data.splice(0, $scope.diskUsageChartSeries[0].data.length);
                            $scope.leastRecentCacheTimestamp = dataService.convertDatestringToLocalUTCDate(result.task_directory.cache_timestamp);

                            var sub_directory_names = Object.keys(result.sub_directories);
                            sub_directory_names.sort(function(a, b) { return ((a.name < b.name) ? -1 : ((a.name > b.name) ? 1 : 0)); });
                            for(var sub_dir of sub_directory_names) {
                                var sub_dir_result = result.sub_directories[sub_dir];
                                $scope.diskUsageChartSeries[0].data.push({name:sub_dir_result.name + ' ' + sub_dir_result.disk_usage_readable,y:sub_dir_result.disk_usage || 0});
                            }
                        }else {
                            $scope.ok();
                            $scope.$evalAsync(function() { alert("Could not find disk usage for task " + otdb_id); });
                        }
                    });
                };

                var loadTasksDiskUsage = function(tasks, force) {
                    $scope.current_otdb_id = undefined;
                    $scope.current_project_name = undefined;
                    $scope.is_loading = true;
                    var du_promises = tasks.map(function(t) { return dataService.getTaskDiskUsageByOTDBId(t.otdb_id, force); });
                    $q.all(du_promises).then(function(du_results) {
                        $scope.is_loading = false;

                        var found_task_dus = du_results.filter(function(r) { return r.found;}).map(function(r) { return r.task_directory; });

                        if(found_task_dus.length > 0) {
                            $scope.watchedObjectType = OBJECT_TYPE_TASKS;

                            $scope.leastRecentCacheTimestamp = new Date(Math.min.apply(null, found_task_dus.map(function(tdu) { return dataService.convertDatestringToLocalUTCDate(tdu.cache_timestamp); })));

                            var total_usage = found_task_dus.map(function(tdu) { return tdu.disk_usage; }).reduce(function(a, b) { return a + b;});
                            var total_usage_readable = dataService.humanreadablesize(total_usage);

                            $scope.diskUsageChartConfig.title.text = 'Total size: ' + total_usage_readable;
                            $scope.diskUsageChartSeries[0].data.splice(0, $scope.diskUsageChartSeries[0].data.length);
                            $scope.diskUsageChartSeries[0].name = $scope.diskUsageChartConfig.title.text;

                            for(var task_du of found_task_dus) {
                                $scope.diskUsageChartSeries[0].data.push({name:task_du.name + ' ' + task_du.disk_usage_readable,
                                                                          y:task_du.disk_usage || 0,
                                                                          otdb_id: task_du.otdb_id });
                            }
                        }else {
                            $scope.ok();
                            $scope.$evalAsync(function() { alert("Could not find disk usage for task " + otdb_id); });
                        }
                    });
                };

                var loadProjectDiskUsage = function(project_name, force) {
                    $scope.current_otdb_id = undefined;
                    $scope.current_project_name = project_name;
                    $scope.is_loading = true;
                    dataService.getProjectDiskUsage(project_name, force).then(function(result) {
                        $scope.is_loading = false;

                        if(result.found) {
                            $scope.watchedObjectType = OBJECT_TYPE_PROJECT;
                            $scope.diskUsageChartConfig.title.text = result.projectdir.name + ' ' + result.projectdir.disk_usage_readable;
                            $scope.diskUsageChartSeries[0].name = $scope.diskUsageChartConfig.title.text;
                            $scope.diskUsageChartSeries[0].data.splice(0, $scope.diskUsageChartSeries[0].data.length);
                            $scope.leastRecentCacheTimestamp = dataService.convertDatestringToLocalUTCDate(result.projectdir.cache_timestamp);

                            var sub_directory_names = Object.keys(result.sub_directories);
                            sub_directory_names.sort(function(a, b) { return ((a.name < b.name) ? -1 : ((a.name > b.name) ? 1 : 0)); });
                            for(var sub_dir of sub_directory_names) {
                                var sub_dir_result = result.sub_directories[sub_dir];
                                $scope.diskUsageChartSeries[0].data.push({name:sub_dir_result.name + ' ' + sub_dir_result.disk_usage_readable,
                                                                        y:sub_dir_result.disk_usage || 0,
                                                                        otdb_id: parseInt(sub_dir_result.name.slice(1)) });
                            }
                        }else {
                            $scope.ok();
                            $scope.$evalAsync(function() { alert("Could not find disk usage for project " + project_name); });
                        }
                    });
                };

                var loadAllProjectsDiskUsage = function(force) {
                    $scope.current_otdb_id = undefined;
                    $scope.current_project_name = undefined;
                    dataService.getProjectsDiskUsage(force).then(function(result) {
                        if(result.found) {
                            $scope.watchedObjectType = OBJECT_TYPE_PROJECTS;
                            $scope.diskUsageChartConfig.title.text = result.projectdir.name + ' ' + result.projectdir.disk_usage_readable;
                            $scope.diskUsageChartSeries[0].name = $scope.diskUsageChartConfig.title.text;
                            $scope.diskUsageChartSeries[0].data.splice(0, $scope.diskUsageChartSeries[0].data.length);
                            $scope.leastRecentCacheTimestamp = dataService.convertDatestringToLocalUTCDate(result.projectdir.cache_timestamp);

                            var sub_directory_names = Object.keys(result.sub_directories);
                            sub_directory_names.sort(function(a, b) { return ((a.name < b.name) ? -1 : ((a.name > b.name) ? 1 : 0)); });
                            for(var sub_dir of sub_directory_names) {
                                var sub_dir_result = result.sub_directories[sub_dir];
                                $scope.diskUsageChartSeries[0].data.push({name:sub_dir_result.name + ' ' + sub_dir_result.disk_usage_readable,
                                                                        y:sub_dir_result.disk_usage || 0,
                                                                        project_name: sub_dir_result.name });
                            }
                        }else {
                            $scope.ok();
                            $scope.$evalAsync(function() { alert("Could not find disk usage for all projects"); });
                        }
                    });
                };

                if(task) {
                    if(task.constructor === Array) {
                        loadTasksDiskUsage(task);
                    } else {
                        loadTaskDiskUsage(task.otdb_id);
                    }
                } else {
                    loadAllProjectsDiskUsage();
                }
            }
        });
    };
}]);

