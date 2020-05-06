(function(){
    'use strict';
    angular.module('gantt.contextmenu', ['gantt', 'gantt.contextmenu.templates']).directive('ganttContextmenu', ['$compile', '$document', '$window', function($compile, $document, $window) {
        return {
            restrict: 'E',
            require: '^gantt',
            scope: {
                enabled: '=?'
            },
            link: function(scope, element, attrs, ganttCtrl) {
                var api = ganttCtrl.gantt.api;

                // Load options from global options attribute.
                if (scope.options && typeof(scope.options.contextmenu) === 'object') {
                    for (var option in scope.options.contextmenu) {
                        scope[option] = scope.options[option];
                    }
                }

                if (scope.enabled === undefined) {
                    scope.enabled = true;
                }

                api.directives.on.new(scope, function(dName, dScope, dElement, dAttrs, dController) {
                    //for each new ganttTask
                    if (dName === 'ganttTask') {
                        dElement.bind('contextmenu', function(event) {
                            //TODO: remove link to dataService in this generic plugin
                            var dataService = dScope.scope.dataService;
                            var dataCtrlScope = dScope.scope.$parent.$parent;
                            var cleanupCtrl = dScope.scope.$parent.cleanupCtrl;
                            var docElement = angular.element($document);

                            var task = dScope.task.model.raTask;

                            if(!task)
                                return;

                            if(!dataService.isTaskIdSelected(task.id)) {
                                dataService.setSelectedTaskId(task.id);
                            }

                            //search for already existing contextmenu element
                            while($document.find('#gantt-context-menu').length) {
                                //found, remove it, so we can create a fresh one
                                $document.find('#gantt-context-menu')[0].remove();

                                //unbind document close event handlers
                                docElement.unbind('click', closeContextMenu);
                                docElement.unbind('contextmenu', closeContextMenu);
                            }

                            //create contextmenu element
                            //with list of menu items,
                            //each with it's own action
                            var contextmenuElement = angular.element('<div id="gantt-context-menu"></div>');
                            var ulElement = angular.element('<ul  class="dropdown-menu" role="menu" style="left:' + event.clientX + 'px; top:' + event.clientY + 'px; z-index: 100000; display:block;"></ul>');
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
                                var liContent = '<li><a href="#">Select blocking predecessors</a></li>'
                                var liElement = angular.element(liContent);
                                ulElement.append(liElement);
                                liElement.on('click', function() {
                                    closeContextMenu();

                                    var blocking_predecessors = []
                                    for(var task of blocked_selected_cep4_tasks) {
                                        blocking_predecessors = blocking_predecessors.concat(task.blocked_by_ids);
                                    }

                                    dataCtrlScope.loadTasksSelectAndJumpIntoView(blocking_predecessors);
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
                                        setTimeout(function(url_arg) {
                                            $window.open(url_arg, '_blank');
                                        }, window_cntr*750, url);
                                        window_cntr += 1;
                                    }
                                });
                            }

                            var liContent = completed_selected_cep4_tasks.length > 0 ? '<li><a href="#">Show disk usage</a></li>' : '<li><a href="#" style="color:#aaaaaa">Show disk usage</a></li>'
                            var liElement = angular.element(liContent);
                            ulElement.append(liElement);
                            if(completed_selected_cep4_tasks.length > 0) {
                                liElement.on('click', function() {
                                    closeContextMenu();
                                    if(selected_cep4_tasks.length == 1) {
                                        cleanupCtrl.showTaskDiskUsage(task);
                                    } else {
                                        cleanupCtrl.showTaskDiskUsage(completed_selected_cep4_tasks);
                                    }
                                });
                            }

                            var liContent = completed_selected_cep4_tasks.length > 0 ? '<li><a href="#">Delete data</a></li>' : '<li><a href="#" style="color:#aaaaaa">Delete data</a></li>'
                            var liElement = angular.element(liContent);
                            ulElement.append(liElement);
                            if(completed_selected_cep4_tasks.length > 0) {
                                liElement.on('click', function() {
                                    closeContextMenu();
                                    cleanupCtrl.deleteTasksDataWithConfirmation(completed_selected_cep4_tasks);
                                });
                            }

                            var approved_selected_cep4_tasks = selected_cep4_tasks.filter(function(t) { return t.status == 'approved'; });

                            if(approved_selected_cep4_tasks.length > 0) {
                                var liContent = '<li><a href="#">Schedule approved CEP4 task(s)</a></li>'
                                var liElement = angular.element(liContent);
                                ulElement.append(liElement);
                                liElement.on('click', function() {
                                    closeContextMenu();
                                    for(var pl of approved_selected_cep4_tasks) {
                                        var newTask = { id: pl.id, status: 'prescheduled' };
                                        dataService.putTask(newTask);
                                    }
                                });
                            }

                            var scheduled_selected_cep4_tasks = selected_cep4_tasks.filter(function(t) { return (t.status == 'prescheduled' || t.status == 'scheduled' || t.status == 'queued'); });

                            if(scheduled_selected_cep4_tasks.length > 0) {
                                var liContent = '<li><a href="#">Unschedule (pre)scheduled/queued CEP4 task(s)</a></li>'
                                var liElement = angular.element(liContent);
                                ulElement.append(liElement);
                                liElement.on('click', function() {
                                    closeContextMenu();
                                    for(var t of scheduled_selected_cep4_tasks) {
                                        if(t.status == 'queued') {
                                            var newTask = { id: t.id, status: 'aborted' };
                                            dataService.putTask(newTask);
                                        }

                                        var newTask = { id: t.id, status: 'approved' };
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

                            var closeContextMenu = function() {
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
                        });
                    }
                });

                api.directives.on.destroy(scope, function(dName, dScope, dElement, dAttrs, dController) {
                    //for each destroyed ganttTask
                    if (dName === 'ganttTask') {
                        dElement.unbind('contextmenu');
                    }
                });
            }
        };
    }]);
}());

angular.module('gantt.contextmenu.templates', []).run(['$templateCache', function($templateCache) {

}]);

