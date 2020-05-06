// $Id$

angular.module('raeApp').factory("dataService", ['$http', '$q', function($http, $q){
    var self = this;
    self.projectMode = false;
    self.tasks = [];
    self.resources = [];
    self.resourceGroups = [];
    self.resourceClaims = [];
    self.tasktypes = [];
    self.taskstatustypes = [];
    self.editableTaskStatusIds = [];

    self.taskDict = {};
    self.resourceDict = {};
    self.resourceGroupsDict = {};
    self.resourceGroupMemberships = {};
    self.resourceClaimDict = {};
    self.resourceUsagesForSelectedResource = {};
    self.tasktypesDict = {};

    self.momProjects = [];
    self.momProjectsDict = {};

    self.resourcesWithClaims = [];

    self.filteredTasks = [];
    self.filteredTasksDict = {};

    self.taskTimes = {};
    self.resourceClaimTimes = {};

    self.events = [];

    self.config = {};

    self.selected_resource_id;
    self.selected_resourceGroup_id;
    self.selected_task_ids = [];
    self.selected_project_id;
    self.selected_resourceClaim_id;

    self.selected_project = { name: 'Please select project', value: undefined };

    self.initialLoadComplete = false;
    self.taskChangeCntr = 0;
    self.filteredTaskChangeCntr = 0;
    self.claimChangeCntr = 0;

    self.loadedHours = {};
    self.loadingChunksQueue = [];

    //for progress tracking
    self.nrOfLoadableChunks = 0;
    self.nrOfLoadingChunks = 0;
    self.nrOfLoadedChunks = 0;

    self.viewTimeSpan = {from: new Date(), to: new Date() };
    self.autoFollowNow = true;

    //loadResourceClaims is enabled when any controller using resourceclaims is enabled
    self.loadResourceClaims = false;

    self.humanreadablesize = function(num, num_digits=3) {
        var units = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z'];
        for(unit of units) {
            if(Math.abs(num) < 1000.0) {
                return num.toFixed(num_digits).toString() + unit;
            }
            num /= 1000.0;
        }
        return num.toFixed(num_digits).toString() + 'Y';
    }

    self.isTaskIdSelected = function(task_id) {
        return self.selected_task_ids.includes(task_id);
    }

    self.toggleTaskSelection = function(task_id) {
        if(self.isTaskIdSelected(task_id)) {
            self.removeSelectedTaskId(task_id);
        } else {
            self.addSelectedTaskId(task_id);
        }
    }

    self.addSelectedTaskId = function(task_id) {
        if(self.selected_task_ids.indexOf(task_id) == -1) {
            self.selected_task_ids.push(task_id);
        }
    }

    self.removeSelectedTaskId = function(task_id) {
        var idx = self.selected_task_ids.indexOf(task_id);
        if(idx != -1) {
            self.selected_task_ids.splice(idx, 1);
        }
    }

    self.setSelectedTaskId = function(task_id) {
        self.selected_task_ids.splice(0, self.selected_task_ids.length);
        self.selected_task_ids.push(task_id);
    }

    self.setSelectedTaskIds = function(task_ids) {
        self.selected_task_ids.splice(0, self.selected_task_ids.length);
        for(var task_id of task_ids) {
            self.selected_task_ids.push(task_id);
        }
    }

    self.selectTasksInSameGroup = function(task) {
        self.selected_task_ids.splice(0, self.selected_task_ids.length);
        var groupTasks = self.filteredTasks.filter(function(t) { return t.mom_object_group_id == task.mom_object_group_id; });
        for(var t of groupTasks) {
            self.selected_task_ids.push(t.id);
        }
    }

    self.floorDate = function(date, hourMod=1, minMod=1) {
        var min = date.getMinutes();
        min = date.getMinutes()/minMod;
        min = Math.floor(date.getMinutes()/minMod);
        min = minMod*Math.floor(date.getMinutes()/minMod);
        return new Date(date.getFullYear(), date.getMonth(), date.getDate(), hourMod*Math.floor(date.getHours()/hourMod), minMod*Math.floor(date.getMinutes()/minMod));
    };

    self.ceilDate = function(date, hourMod=1, minMod=1) {
        return new Date(date.getFullYear(), date.getMonth(), date.getDate(), hourMod*Math.ceil(date.getHours()/hourMod), minMod*Math.ceil(date.getMinutes()/minMod));
    };

    self.resourceClaimStatusColors = {'tentative':'#ffa64d',
                                      'conflict':'#ff0000',
                                      'claimed': '#66ff66',
                                      'mixed': '#bfbfbf'}

    self.taskStatusColors = {'prepared':'#cccccc',
                             'approved':'#8cb3d9',
                             'on_hold':'#b34700',
                             'conflict':'#ff0000',
                             'prescheduled': '#6666ff',
                             'scheduled': '#0000ff',
                             'queued': '#ccffff',
                             'active': '#ffff00',
                             'completing': '#ffdd99',
                             'finished': '#00ff00',
                             'aborted': '#cc0000',
                             'error': '#990033',
                             'obsolete': '#555555',
                             'opened': '#d9e5f2',
                             'suspended': '#996666'};



    //-- IMPORTANT REMARKS ABOUT UTC/LOCAL DATE --
    //Dates (datetimes) across javascript/angularjs/3rd party modules are a mess!
    //every module uses their own parsing and displaying
    //some care about utc/local date, others don't
    //So, to be consistent in this schedular client app, we chose the following conventions:
    //1) All received/sent timestamps are strings in iso format 'yyyy-MM-ddTHH:mm:ssZ'
    //2) All displayed timestamps should display the time in UTC, regardless of the timezone of the client.
    //All javascript/angularjs/3rd party modules display local times correct and the same...
    //So, to make 1&2 happen, we convert all received timestamps to 'local-with-utc-diff-correction', and then treat them as local.
    //And if we send them to the web server, we convert them back to real utc.
    //It's a stupid solution, but it works.
    //-- IMPORTANT REMARKS ABOUT UTC/LOCAL DATE --

    self.convertDatestringToLocalUTCDate = function(dateString) {
        //first convert the dateString to proper Date
        var date = new Date(dateString)
        //then do our trick to offset the timestamp with the utcOffset, see explanation above.
        return new Date(date.getTime() - self.utcOffset)
    };

    self.convertLocalUTCDateToISOString = function(local_utc_date) {
        if(local_utc_date) {
            //reverse trick to offset the timestamp with the utcOffset, see explanation above.
            var real_utc = new Date(local_utc_date.getTime() + self.utcOffset)
            return real_utc.toISOString();
        }
        return undefined;
    };

    //local client time offset to utc in milliseconds
    self.utcOffset = moment().utcOffset()*60000;

    self.convertNullToUndefined = function(in_value) {
        return in_value === null ? undefined : in_value;
    };

    self.toIdBasedDict = function(list) {
        var dict = {}
        if(list) {
            for(var i = list.length-1; i >=0; i--) {
                var item = list[i];
                dict[item.id] = item;
            }
        }
        return dict;
    };

    self.applyChanges = function(existingObj, changedObj) {
        for(var prop in changedObj) {
            if(existingObj.hasOwnProperty(prop) &&
            changedObj.hasOwnProperty(prop) &&
            existingObj[prop] != changedObj[prop]) {
                if(existingObj[prop] instanceof Date && typeof changedObj[prop] === "string") {
                    existingObj[prop] = self.convertDatestringToLocalUTCDate(changedObj[prop]);
                } else {
                    existingObj[prop] = changedObj[prop];
                }
            }
        }
    };

    self.getTasksAndClaimsForViewSpan = function() {
        var from = self.floorDate(self.viewTimeSpan.from, 1, 60);
        var until = self.ceilDate(self.viewTimeSpan.to, 1, 60);
        var lowerTS = from.getTime();
        var upperTS = until.getTime();

        //reset list of chunks to load
        //only keep the currently loading chunks
        self.loadingChunksQueue = self.loadingChunksQueue.filter(function(c) { return c.loading; });

        var chunkFactor = self.projectMode ? 4 : 1;
        var hourInmsec = 3600000;
        var quartDayInmsec = 6*hourInmsec;

        for (var timestamp = lowerTS; timestamp < upperTS; ) {
            if(self.loadedHours.hasOwnProperty(timestamp)) {
                timestamp += hourInmsec;
            }
            else {
                var chuckUpperLimit = Math.min(upperTS, timestamp + chunkFactor*quartDayInmsec);
                for (var chunkTimestamp = timestamp; chunkTimestamp < chuckUpperLimit; chunkTimestamp += hourInmsec) {
                    if(self.loadedHours.hasOwnProperty(chunkTimestamp))
                        break;
                }

                var hourLower = new Date(timestamp);
                var hourUpper = new Date(chunkTimestamp);
                if(hourUpper > hourLower) {
                    var chunk = { lower: hourLower, upper: hourUpper, loaded: false, loading: false };
                    if(hourLower < self.lofarTime) {
                        //prepend at beginning of queue, so we load most recent data first
                        self.loadingChunksQueue.unshift(chunk);
                    } else {
                        self.loadingChunksQueue.push(chunk);
                    }
                }
                timestamp = chunkTimestamp;
            }
        }

        //load a few chunks in parallel, a little distributed in time,
        //so we have nice load distribution on the server
        //and we have parallel loads for faster data retreival here in the client
        for(var i = 0; i < Math.min(3, self.loadingChunksQueue.length); i++) {
            setTimeout(self.loadNextChunk, i*250);
        }

        //load the usages as well, if needed.
        if (self.loadResourceClaims) {
            self.getUsagesForSelectedResource();
        }
    };

    self.loadNextChunk = function() {
        var chunksToLoad = self.loadingChunksQueue.filter(function(c) { return !c.loaded && !c.loading; });
        var loadingChunks = self.loadingChunksQueue.filter(function(c) { return c.loading; });

        //for progress tracking
        self.nrOfLoadableChunks = self.loadingChunksQueue.length;
        self.nrOfLoadingChunks = loadingChunks.length;
        self.nrOfLoadedChunks = self.nrOfLoadableChunks - chunksToLoad.length - self.nrOfLoadingChunks;

        if(chunksToLoad.length > 0) {
            var chunk = chunksToLoad[0];
            chunk.loading = true;

            var load_promisses = [ self.getTasks(chunk.lower, chunk.upper) ];

            if(self.loadResourceClaims) {
                load_promisses.push(self.getResourceClaims(chunk.lower, chunk.upper));
            }

            $q.all(load_promisses).then(function() {
                chunk.loading = false;
                chunk.loaded = true;
                self.nrOfLoadingChunks -= 1;
                self.nrOfLoadedChunks += 1;

                for (var timestamp = chunk.lower.getTime(); timestamp < chunk.upper.getTime(); timestamp += 3600000) {
                    self.loadedHours[timestamp] = true;
                }

                self.loadNextChunk();
            });
        } else {
            if(self.nrOfLoadingChunks == 0) {
                self.loadingChunksQueue = [];
                self.nrOfLoadableChunks = 0;
            }
        }
    }

    self.clearTasksAndClaimsOutsideViewSpan = function() {
        var from = self.floorDate(self.viewTimeSpan.from, 1, 60);
        var until = self.ceilDate(self.viewTimeSpan.to, 1, 60);

        var numTasks = self.tasks.length;
        var visibleTasks = [];
        for(var i = 0; i < numTasks; i++) {
            var task = self.tasks[i];
            if(task.endtime >= from && task.starttime <= until) {
                visibleTasks.push(task);
            }
            else {
                if(self.isTaskIdSelected(task.id)) {
                    self.removeSelectedTaskId(task.id);
                }
            }
        }

        self.tasks = visibleTasks;
        self.taskDict = self.toIdBasedDict(visibleTasks);
        self.taskChangeCntr++;

        self.computeMinMaxTaskTimes();

        var numClaims = self.resourceClaims.length;
        var visibleClaims = [];
        for(var i = 0; i < numClaims; i++) {
            var claim = self.resourceClaims[i];
            if(claim.endtime >= from && claim.starttime <= until)
                visibleClaims.push(claim);
        }

        self.resourceClaims = visibleClaims;
        self.resourceClaimDict = self.toIdBasedDict(self.resourceClaims);

        self.computeMinMaxResourceClaimTimes();

        var newLoadedHours = {};
        var fromTS = from.getTime();
        var untilTS = until.getTime();
        for(var hourTS in self.loadedHours) {
            if(hourTS >= fromTS && hourTS <= untilTS)
                newLoadedHours[hourTS] = true;
        }
        self.loadedHours = newLoadedHours;
    };

    self.getTasks = function(from, until) {
        var defer = $q.defer();
        var url = '/rest/tasks';
        if(self.projectMode) {
            if(self.selected_project_id === undefined){
                defer.resolve([]);
                return defer;
            }

            url = '/rest/projects/' + self.selected_project_id + '/tasks';
        }

        if(from) {
            url += '/' + self.convertLocalUTCDateToISOString(from);

            if(until) {
                url += '/' + self.convertLocalUTCDateToISOString(until);
            }
        }

        $http.get(url).success(function(result) {
            //convert datetime strings to Date objects
            for(var i in result.tasks) {
                var task = result.tasks[i];
                task.starttime = self.convertDatestringToLocalUTCDate(task.starttime);
                task.endtime = self.convertDatestringToLocalUTCDate(task.endtime);
                task.ingest_status = self.convertNullToUndefined(task.ingest_status);
                task.disk_usage = self.convertNullToUndefined(task.disk_usage);
                task.disk_usage_readable = self.convertNullToUndefined(task.disk_usage_readable);
            }

            var initialTaskLoad = self.tasks.length == 0;

            var newTaskDict = self.toIdBasedDict(result.tasks);
            var newTaskIds = Object.keys(newTaskDict);

            for(var i = newTaskIds.length-1; i >= 0; i--) {
                var task_id = newTaskIds[i];

                if(!self.taskDict.hasOwnProperty(task_id)) {
                    var task = newTaskDict[task_id];
                    if(!self.projectMode || self.selected_project_id == task.project_mom_id) {
                        self.tasks.push(task);
                        self.taskDict[task_id] = task;
                    }
                }
            }

            self.taskChangeCntr++;
            self.computeMinMaxTaskTimes();

            if(initialTaskLoad && self.tasks.length > 0) {
                setTimeout(function() {
                    self.selected_task_ids.splice(0,self.selected_task_ids.length);

                    //try to select current task
                    var currentTasks = self.tasks.filter(function(t) { return t.starttime <= self.lofarTime && t.endtime >= self.lofarTime; });

                    if(currentTasks.length > 0) {
                        self.selected_task_ids.push(currentTasks[0].id);
                    } else {
                        //try to select next task
                        var nextTasks = self.tasks.filter(function(t) { return t.starttime >= self.lofarTime; }).sort();

                        if(nextTasks.length > 0) {
                            self.selected_task_ids.push(nextTasks[0].id);
                        } else {
                            //try to select most recent task
                            var prevTasks = self.tasks.filter(function(t) { return t.endtime <= self.lofarTime; }).sort();

                            if(prevTasks.length > 0) {
                                self.selected_task_ids.push(prevTasks[prevTasks.length-1].id);
                            } else {
                                self.selected_task_ids.push(self.tasks[0].id);
                            }
                        }
                    }
                }, 1000);
            }

            defer.resolve();
        }).error(function(result) {
            defer.resolve();
        });

        return defer.promise;
    };

    self.putTask = function(task) {
        var org_task = self.taskDict[task.id];
        if(org_task) {
            var org_starttime = org_task.starttime;
            var org_endtime = org_task.endtime;
            task.starttime = self.convertLocalUTCDateToISOString(task.starttime);
            task.endtime = self.convertLocalUTCDateToISOString(task.endtime);
            $http.put('/rest/tasks/' + task.id, task).error(function(result) {
                console.log("Error. Could not update task. " + result);

                //revert to old state
                org_task.starttime = org_starttime;
                org_task.endtime = org_endtime;

                self.filteredTaskChangeCntr++;
            })
        }
    };

    var _getTaskBy = function(id_name, id, force_reload) {
        var defer = $q.defer();

        if(typeof(id) === 'string') {
            id = parseInt(id);
        }

        var foundTask = id_name == 'id' ? self.taskDict[id] : self.tasks.find(function(t) { return t[id_name] == id; });

        if(foundTask && !force_reload) {
            defer.resolve(foundTask);
        } else {
            var url;
            switch(id_name) {
                case 'id': url = '/rest/tasks/' + id; break;
                case 'otdb_id': url = '/rest/tasks/otdb/' + id; break;
                case 'mom_id': url = '/rest/tasks/mom/' + id; break;
            }

            if(url) {
                $http.get(url).success(function(result) {
                    var task = result.task;
                    if(task) {
                        task.starttime = self.convertDatestringToLocalUTCDate(task.starttime);
                        task.endtime = self.convertDatestringToLocalUTCDate(task.endtime);
                        task.ingest_status = self.convertNullToUndefined(task.ingest_status);
                        task.disk_usage = self.convertNullToUndefined(task.disk_usage);
                        task.disk_usage_readable = self.convertNullToUndefined(task.disk_usage_readable);

                        if(!self.taskDict.hasOwnProperty(task.id)) {
                            self.tasks.push(task);
                            self.taskDict[task.id] = task;
                            self.taskChangeCntr++;
                        }
                    }
                    defer.resolve(task);
                }).error(function(result) {
                    defer.resolve(undefined);
                })
            } else {
                defer.resolve(undefined);
            }
        }

        return defer.promise;
    };

    self.getTask= function(id, force_reload) {
        return _getTaskBy('id', id, force_reload);
    };

    self.getTaskByOTDBId = function(otdb_id, force_reload) {
        return _getTaskBy('otdb_id', otdb_id, force_reload);
    };

    self.getTaskByMoMId = function(mom_id, force_reload) {
        return _getTaskBy('mom_id', mom_id, force_reload);
    };

    self.getTasksByMoMGroupId = function(mom_object_group_id) {
        var defer = $q.defer();
        var url = '/rest/tasks/mom/group/' + mom_object_group_id;

        $http.get(url).success(function(result) {
            //convert datetime strings to Date objects
            for(var i in result.tasks) {
                var task = result.tasks[i];
                task.starttime = self.convertDatestringToLocalUTCDate(task.starttime);
                task.endtime = self.convertDatestringToLocalUTCDate(task.endtime);
                task.ingest_status = self.convertNullToUndefined(task.ingest_status);
                task.disk_usage = self.convertNullToUndefined(task.disk_usage);
                task.disk_usage_readable = self.convertNullToUndefined(task.disk_usage_readable);
            }

            var newTaskDict = self.toIdBasedDict(result.tasks);
            var newTaskIds = Object.keys(newTaskDict);

            for(var i = newTaskIds.length-1; i >= 0; i--) {
                var task_id = newTaskIds[i];
                if(!self.taskDict.hasOwnProperty(task_id)) {
                    var task = newTaskDict[task_id];
                    self.tasks.push(task);
                    self.taskDict[task_id] = task;
                }
            }

            self.taskChangeCntr++;
            self.computeMinMaxTaskTimes();

            defer.resolve(result.tasks);
        }).error(function(result) {
            defer.resolve(undefined);
        });

        return defer.promise;
    };

    self.getTasksByMoMParentGroupId = function(mom_object_parent_group_id) {
        var defer = $q.defer();
        var url = '/rest/tasks/mom/parentgroup/' + mom_object_parent_group_id;

        $http.get(url).success(function(result) {
            //convert datetime strings to Date objects
            for(var i in result.tasks) {
                var task = result.tasks[i];
                task.starttime = self.convertDatestringToLocalUTCDate(task.starttime);
                task.endtime = self.convertDatestringToLocalUTCDate(task.endtime);
                task.ingest_status = self.convertNullToUndefined(task.ingest_status);
                task.disk_usage = self.convertNullToUndefined(task.disk_usage);
                task.disk_usage_readable = self.convertNullToUndefined(task.disk_usage_readable);
            }

            var newTaskDict = self.toIdBasedDict(result.tasks);
            var newTaskIds = Object.keys(newTaskDict);

            for(var i = newTaskIds.length-1; i >= 0; i--) {
                var task_id = newTaskIds[i];
                if(!self.taskDict.hasOwnProperty(task_id)) {
                    var task = newTaskDict[task_id];
                    self.tasks.push(task);
                    self.taskDict[task_id] = task;
                }
            }

            self.taskChangeCntr++;
            self.computeMinMaxTaskTimes();

            defer.resolve(result.tasks);
        }).error(function(result) {
            defer.resolve(undefined);
        });

        return defer.promise;
    };

    self.copyTask = function(task) {
        $http.put('/rest/tasks/' + task.id + '/copy').error(function(result) {
            console.log("Error. Could not copy task. " + result);
            alert("Error: Could not copy task with mom id " + task.mom_id);
        })
    };

    self.getTaskDiskUsageByOTDBId = function(otdb_id, force) {
        var defer = $q.defer();
        force = force || false;
        $http.get('/rest/tasks/otdb/' + otdb_id + '/diskusage', { params: { force:force } }).success(function(result) {
            defer.resolve(result);
        }).error(function(result) {
            defer.resolve({found:false});
        });

        return defer.promise;
    };

    self.getTaskDiskUsage = function(task, force) {
        var defer = $q.defer();
        force = force || false;
        $http.get('/rest/tasks/otdb/' + task.otdb_id + '/diskusage', { params: { force:force } }).success(function(result) {
            result.task = task;
            defer.resolve(result);
        }).error(function(result) {
            defer.resolve({found:false});
        });

        return defer.promise;
    };

    self.computeMinMaxTaskTimes = function() {
        var starttimes = self.filteredTasks.map(function(t) { return t.starttime;});
        var endtimes = self.filteredTasks.map(function(t) { return t.endtime;});

        var minStarttime = new Date(Math.min.apply(null, starttimes));
        var maxEndtime = new Date(Math.max.apply(null, endtimes));

        self.taskTimes = {
            min: minStarttime,
            max: maxEndtime
        };
    };

    self.getResources = function() {
        var defer = $q.defer();
        $http.get('/rest/resources').success(function(result) {
            //at this moment, we have way too many resources to show in a gantt-tree.
            //this make the webscheduler way too slow.
            //so, only show the relevant resources, 116 and 117 which are CEP4 bandwith and storage.
            self.resources = result.resources.filter(function(r) { return r.id==116 ||  r.id==117;});
            self.resourceDict = self.toIdBasedDict(self.resources);

            defer.resolve();
        });

        return defer.promise;
    };

    self.getResource = function(resource_id) {
        var defer = $q.defer();
        if(resource_id) {
            $http.get('/rest/resources/' + resource_id).success(function(resource) {
                if(resource && 'id' in resource && resource_id===resource.id) {

                    if(resource.id in self.resourceDict) {
                        var knownResource = self.resourceDict[resource.id];
                        self.applyChanges(knownResource, resource);
                    } else {
                        self.resources.push(resource);
                        self.resourceDict[resource.id] = resource;
                    }
                }

                defer.resolve();
            });
        }

        return defer.promise;
    };

    self.getUsagesForSelectedResource = function() {
        var defer = $q.defer();
        if(self.selected_resource_id) {
            var url = '/rest/resources/' + self.selected_resource_id + '/usages';
            if(self.viewTimeSpan.from && self.viewTimeSpan.to) {
                url += '/' + self.convertLocalUTCDateToISOString(self.viewTimeSpan.from) + '/' + self.convertLocalUTCDateToISOString(self.viewTimeSpan.to);
            }

            $http.get(url).success(function(result) {
                if(self.selected_resource_id in result.resourceusages) {
                    for(var status in result.resourceusages[self.selected_resource_id]) {
                        var usages = result.resourceusages[self.selected_resource_id][status];
                        for(var usage of usages) {
                            //convert datetime strings to Date objects
                            usage.as_of_timestamp = self.convertDatestringToLocalUTCDate(usage.as_of_timestamp);
                        }
                    }

                    self.resourceUsagesForSelectedResource = result.resourceusages[self.selected_resource_id];
                } else {
                    self.resourceUsagesForSelectedResource = {};
                }

                defer.resolve();
            });
        }

        return defer.promise;
    };

    self.getResourceClaims = function(from, until) {
        var defer = $q.defer();
        if(self.projectMode) {
            defer.resolve([]);
            return defer;
        }
        var url = '/rest/resourceclaims';
        if(from) {
            url += '/' + self.convertLocalUTCDateToISOString(from);

            if(until) {
                url += '/' + self.convertLocalUTCDateToISOString(until);
            }
        }

        $http.get(url).success(function(result) {
            //convert datetime strings to Date objects
            for(var i in result.resourceclaims) {
                var resourceclaim = result.resourceclaims[i];
                resourceclaim.starttime = self.convertDatestringToLocalUTCDate(resourceclaim.starttime);
                resourceclaim.endtime = self.convertDatestringToLocalUTCDate(resourceclaim.endtime);
            }

            var newClaimDict = self.toIdBasedDict(result.resourceclaims);
            var newClaimIds = Object.keys(newClaimDict);

            for(var i = newClaimIds.length-1; i >= 0; i--) {
                var claim_id = newClaimIds[i];
                var claim = newClaimDict[claim_id];

                if(!self.resourceClaimDict.hasOwnProperty(claim_id)) {
                    self.resourceClaims.push(claim);
                    self.resourceClaimDict[claim_id] = claim;
                }
            }

            self.computeMinMaxResourceClaimTimes();

            defer.resolve();
        });

        return defer.promise;
    };

    self.computeMinMaxResourceClaimTimes = function() {
        var starttimes = self.resourceClaims.map(function(rc) { return rc.starttime;});
        var endtimes = self.resourceClaims.map(function(rc) { return rc.endtime;});

        var minStarttime = new Date(Math.min.apply(null, starttimes));
        var maxEndtime = new Date(Math.max.apply(null, endtimes));

        self.resourceClaimTimes = {
            min: minStarttime,
            max: maxEndtime
        };
    };

    self.getResourceGroups = function() {
        var defer = $q.defer();
        $http.get('/rest/resourcegroups').success(function(result) {
            //at this moment, we have way too many resources to show in a gantt-tree.
            //this make the webscheduler way too slow.
            //so, only show the relevant resource groups, 1, which is the CEP4 group.
            self.resourceGroups = result.resourcegroups.filter(function(r) { return r.id==1;});
            self.resourceGroupsDict = self.toIdBasedDict(self.resourceGroups);

            defer.resolve();
        });

        return defer.promise;
    };

    self.getResourceGroupMemberships = function() {
        var defer = $q.defer();
        $http.get('/rest/resourcegroupmemberships').success(function(result) {
            self.resourceGroupMemberships = result.resourcegroupmemberships;

            defer.resolve();
        });

        return defer.promise;
    };

    self.getTaskTypes = function() {
        var defer = $q.defer();
        $http.get('/rest/tasktypes').success(function(result) {
            self.tasktypes = result.tasktypes;
            self.tasktypesDict = self.toIdBasedDict(self.tasktypes);

            defer.resolve();
        });

        return defer.promise;
    };

    self.getTaskStatusTypes = function() {
        var defer = $q.defer();
        $http.get('/rest/taskstatustypes').success(function(result) {
            self.taskstatustypes = result.taskstatustypes;

            self.editableTaskStatusIds = [];
            for(var taskstatustype of self.taskstatustypes) {
                if(taskstatustype.name == 'approved' || taskstatustype.name == 'conflict' || taskstatustype.name == 'prescheduled') {
                    self.editableTaskStatusIds.push(taskstatustype.id);
                }
            }

            defer.resolve();
        });

        return defer.promise;
    };

    self.getMoMProjects = function() {
        var defer = $q.defer();
        $http.get('/rest/projects').success(function(result) {
            //convert datetime strings to Date objects
            var dict = {};
            var list = [];
            for(var i in result.momprojects) {
                var momproject = result.momprojects[i];
                momproject.statustime = new Date(momproject.statustime);
                dict[momproject.mom_id] = momproject;
                list.push(momproject);
            }

            list.sort(function(a, b) { return ((a.name < b.name) ? -1 : ((a.name > b.name) ? 1 : 0)); });

            self.momProjects = list;
            self.momProjectsDict = dict;

            defer.resolve();
        });

        return defer.promise;
    };

    self.getMoMObjectDetailsForTask = function(task) {
        $http.get('/rest/momobjectdetails/'+task.mom_id).success(function(result) {
            if(result.momobjectdetails) {
                task.name = result.momobjectdetails.object_name;
                task.project_name = result.momobjectdetails.project_name;
                task.project_id = result.momobjectdetails.project_mom_id;
            }
        });
    };

    self.getProjectTasksTimeWindow = function(project_mom_id) {
        var defer = $q.defer();

        if(project_mom_id === undefined) {
            defer.resolve(undefined);
        } else {
            $http.get('/rest/projects/' + project_mom_id + '/taskstimewindow').success(function(result) {
                defer.resolve(result);
            }).error(function(result) {
                defer.resolve(undefined);
            });
        }

        return defer.promise;
    };

    self.getProjectDiskUsage = function(project_name, force) {
        var defer = $q.defer();
        force = force || false;
        $http.get('/rest/projects/' + project_name + '/diskusage', { params: { force:force } }).success(function(result) {
            defer.resolve(result);
        }).error(function(result) {
            defer.resolve({found:false});
        });

        return defer.promise;
    };

    self.getProjectsDiskUsage = function(force) {
        var defer = $q.defer();
        force = force || false;
        $http.get('/rest/projects/diskusage', { params: { force:force } }).success(function(result) {
            defer.resolve(result);
        }).error(function(result) {
            defer.resolve({found:false});
        });

        return defer.promise;
    };

    self.getMostRecentLogEvents = function() {
        var defer = $q.defer();
        $http.get('/rest/logEvents').success(function(result) {
            var loaded_events = result.logEvents.map(function(x) { return { message: x.value, timestamp: self.convertDatestringToLocalUTCDate(x.timestamp) }; });
            loaded_events.sort(function(a, b) { return ((a.timestamp < b.timestamp) ? -1 : ((a.timestamp > b.timestamp) ? 1 : 0)); });

            for(var event of loaded_events) {
                self.events.push(event);
            }

            defer.resolve();
        });

        return defer.promise;
    };

    self.getConfig = function() {
        var defer = $q.defer();
        $http.get('/rest/config').success(function(result) {
            self.config = result.config;
            defer.resolve();
        });

        return defer.promise;
    };


    //start with local client time
    //lofarTime will be synced with server,
    //because local machine might have incorrect clock
    //take utcOffset into account, see explanation above.
    self.lofarTime = new Date(Date.now() - self.utcOffset);

    self._syncLofarTimeWithServer = function() {
        $http.get('/rest/lofarTime', {timeout:1000}).success(function(result) {
            self.lofarTime = self.convertDatestringToLocalUTCDate(result.lofarTime);

            //check if local to utc offset has changed
            self.utcOffset = moment().utcOffset()*60000;
        });

        setTimeout(self._syncLofarTimeWithServer, 60000);
    };
    self._syncLofarTimeWithServer();

    self.lastUpdateChangeNumber = undefined;

    self.initialLoad = function() {
        $http.get('/rest/mostRecentChangeNumber').success(function(result) {
            if(result.mostRecentChangeNumber >= 0) {
                self.lastUpdateChangeNumber = result.mostRecentChangeNumber;
            }

            var load_promisses = [self.getConfig(),
                                  self.getMoMProjects(),
                                  self.getTaskTypes(),
                                  self.getTaskStatusTypes(),
                                  self.getResourceGroups(),
                                  self.getResources(),
                                  self.getResourceGroupMemberships(),
                                  self.getMostRecentLogEvents()];

            $q.all(load_promisses).then(function() {
                        self.initialLoadComplete = true;
                        self.getTasksAndClaimsForViewSpan();
                        self.subscribeToUpdates();
                    });
        });
    };

    self.subscribeToUpdates = function() {
        var url = '/rest/updates';
        if(self.lastUpdateChangeNumber) {
            url += '/' + self.lastUpdateChangeNumber;
        }
        $http.get(url, {timeout:300000}).success(function(result) {

            try {
                var changeNumbers = result.changes.map(function(item) { return item.changeNumber; });
                self.lastUpdateChangeNumber = changeNumbers.reduce(function(a, b, idx, arr) { return a > b ? a : b; }, undefined);

                var anyResourceClaims = false;
                for(var i in result.changes) {
                    try {
                        var change = result.changes[i];

                        if(change.objectType == 'task') {
                            var changedTask = change.value;
                            if(change.changeType == 'update') {
                                var task = self.taskDict[changedTask.id];
                                if(task) {
                                    self.applyChanges(task, changedTask);
                                } else if(!self.projectMode || self.selected_project_id == task.project_mom_id) {
                                        changedTask.starttime = self.convertDatestringToLocalUTCDate(changedTask.starttime);
                                        changedTask.endtime = self.convertDatestringToLocalUTCDate(changedTask.endtime);
                                        if((changedTask.starttime >= self.viewTimeSpan.from && changedTask.starttime <= self.viewTimeSpan.to) ||
                                           (changedTask.endtime >= self.viewTimeSpan.from && changedTask.endtime <= self.viewTimeSpan.to)) {
                                            changedTask.ingest_status = self.convertNullToUndefined(changedTask.ingest_status);
                                            changedTask.disk_usage = self.convertNullToUndefined(changedTask.disk_usage);
                                            changedTask.disk_usage_readable = self.convertNullToUndefined(changedTask.disk_usage_readable);
                                            self.tasks.push(changedTask);
                                            self.taskDict[changedTask.id] = changedTask;
                                        }
                                    }
                                }
                            else if(change.changeType == 'insert') {
                                //just to be sure, check and remove any task with given changedTask.id
                                var task = self.taskDict[changedTask.id];
                                if(task) {
                                    delete self.taskDict[changedTask.id]
                                    for(var k = self.tasks.length-1; k >= 0; k--) {
                                        if(self.tasks[k].id == changedTask.id) {
                                            self.tasks.splice(k, 1);
                                            break;
                                        }
                                    }
                                }

                                if(!self.projectMode || self.selected_project_id == task.project_mom_id) {
                                    changedTask.starttime = self.convertDatestringToLocalUTCDate(changedTask.starttime);
                                    changedTask.endtime = self.convertDatestringToLocalUTCDate(changedTask.endtime);
                                    changedTask.ingest_status = self.convertNullToUndefined(changedTask.ingest_status);
                                    changedTask.disk_usage = self.convertNullToUndefined(changedTask.disk_usage);
                                    changedTask.disk_usage_readable = self.convertNullToUndefined(changedTask.disk_usage_readable);
                                    self.tasks.push(changedTask);
                                    self.taskDict[changedTask.id] = changedTask;
                                }
                            } else if(change.changeType == 'delete') {
                                delete self.taskDict[changedTask.id]
                                for(var k = self.tasks.length-1; k >= 0; k--) {
                                    if(self.tasks[k].id == changedTask.id) {
                                        self.tasks.splice(k, 1);
                                        break;
                                    }
                                }
                            }

                            self.taskChangeCntr++;

                            self.computeMinMaxTaskTimes();
                        } else if(change.objectType == 'resourceClaim') {
                            if(self.projectMode)
                                continue; //skip claims in projectMode

                            anyResourceClaims = true;
                            var changedClaim = change.value;
                            if(change.changeType == 'update') {
                                var claim = self.resourceClaimDict[changedClaim.id];
                                if(claim) {
                                    self.applyChanges(claim, changedClaim);
                                }
                            } else if(change.changeType == 'insert') {
                                var claim = self.resourceClaimDict[changedClaim.id];
                                if(!claim) {
                                    changedClaim.starttime = self.convertDatestringToLocalUTCDate(changedClaim.starttime);
                                    changedClaim.endtime = self.convertDatestringToLocalUTCDate(changedClaim.endtime);
                                    self.resourceClaims.push(changedClaim);
                                    self.resourceClaimDict[changedClaim.id] = changedClaim;
                                }
                            } else if(change.changeType == 'delete') {
                                delete self.resourceClaimDict[changedClaim.id]
                                for(var k = self.resourceClaims.length-1; k >= 0; k--) {
                                    if(self.resourceClaims[k].id == changedClaim.id) {
                                        self.resourceClaims.splice(k, 1);
                                        break;
                                    }
                                }
                            }

                            self.claimChangeCntr++;
                            self.computeMinMaxResourceClaimTimes();
                        } else if(change.objectType == 'resourceCapacity') {
                            if(change.changeType == 'update') {
                                var changedCapacity = change.value;
                                var resource = self.resourceDict[changedCapacity.resource_id];
                                if(resource) {
                                    resource.available_capacity = changedCapacity.available;
                                    resource.total_capacity = changedCapacity.total;
                                }
                            }
                        } else if(change.objectType == 'resourceAvailability') {
                            if(change.changeType == 'update') {
                                var changedAvailability = change.value;
                                var resource = self.resourceDict[changedAvailability.resource_id];
                                if(resource) {
                                    resource.active = changedAvailability.total;
                                }
                            }
                        } else if(change.objectType == 'logevent') {
                            var event = { message: change.value, timestamp: self.convertDatestringToLocalUTCDate(change.timestamp) };
                            self.events.push(event);

                            //cleanup items older than 6 hours
                            var index = self.events.findIndex(function(event) { return self.lofarTime.getTime() - event.timestamp.getTime() > 6*3600*1000; });
                            if (index > -1) {
                                self.events.splice(0, index);
                            }

                        }
                    } catch(err) {
                        console.log(err)
                    }
                }
            } catch(err) {
                console.log(err)
            }

            //and update again
            self.subscribeToUpdates();
        }).error(function() {
            setTimeout(self.subscribeToUpdates, 1000);
        });
    };

    return self;
}]);

var dataControllerMod = angular.module('DataControllerMod', ['ngResource']);

dataControllerMod.controller('DataController',
                            ['$scope', '$q', 'dataService',
                            function($scope, $q, dataService) {
    var self = this;
    $scope.dataService = dataService;
    dataService.dataCtrl = this;

    $scope.dateOptions = {
        formatYear: 'yyyy',
        startingDay: 1
    };

    $scope.max = 100;
    $scope.dynamic = 63;

    $scope.viewFromDatePopupOpened = false;
    $scope.viewToDatePopupOpened = false;

    $scope.openViewFromDatePopup = function() { $scope.viewFromDatePopupOpened = true; };
    $scope.openViewToDatePopup = function() { $scope.viewToDatePopupOpened = true; };
    $scope.zoomTimespans = [{value:30, name:'30 Minutes'}, {value:60, name:'1 Hour'}, {value:3*60, name:'3 Hours'}, {value:6*60, name:'6 Hours'}, {value:12*60, name:'12 Hours'}, {value:24*60, name:'1 Day'}, {value:2*24*60, name:'2 Days'}, {value:3*24*60, name:'3 Days'}, {value:5*24*60, name:'5 Days'}, {value:7*24*60, name:'1 Week'}, {value:14*24*60, name:'2 Weeks'}, {value:28*24*60, name:'4 Weeks'}, {value:1, name:'Custom (1 min)'}];
    $scope.zoomTimespan = $scope.zoomTimespans[5];
    $scope.jumpToNow = function() {
        var floorLofarTime = dataService.floorDate(dataService.lofarTime, 1, 5);
        dataService.viewTimeSpan = {
            from: dataService.floorDate(new Date(floorLofarTime.getTime() - 0.25*$scope.zoomTimespan.value*60*1000), 1, 5),
            to: dataService.floorDate(new Date(floorLofarTime.getTime() + 0.75*$scope.zoomTimespan.value*60*1000), 1, 5)
        };
    };

    $scope.jumpToNow();

    $scope.loadTasksSelectAndJumpIntoView = function(task_ids) {
        var list_of_promises = task_ids.map(function(t_id) { return $scope.dataService.getTask(t_id); });
        var defer = $q.defer();
        $q.all(list_of_promises).then(function(in_tasks) {
            var loaded_tasks = in_tasks.filter(function(t) { return t != undefined; });
            var loaded_tasks_ids = loaded_tasks.map(function(t) { return t.id; });
            $scope.dataService.setSelectedTaskIds(loaded_tasks_ids);
            $scope.jumpToSelectedTasks();
            defer.resolve(loaded_tasks);
        });
        return defer.promise;
    };

    $scope.loadTaskByOTDBIdSelectAndJumpIntoView = function(otdb_id) {
        var defer = $q.defer();
        $scope.dataService.getTaskByOTDBId(otdb_id).then(function(task) {
            if(task) {
                $scope.dataService.setSelectedTaskId(task.id);
                $scope.jumpToSelectedTasks();
                defer.resolve(task);
            } else {
                defer.resolve(undefined);
            }
        });
        return defer.promise;
    };

    $scope.loadTaskByMoMIdSelectAndJumpIntoView = function(mom_id) {
        var defer = $q.defer();
        $scope.dataService.getTaskByMoMId(mom_id).then(function(task) {
            if(task) {
                $scope.dataService.setSelectedTaskId(task.id);
                $scope.jumpToSelectedTasks();
                defer.resolve(task);
            } else {
                defer.resolve(undefined);
            }
        });
        return defer.promise;
    };

    $scope.loadTasksByMoMGroupIdSelectAndJumpIntoView = function(mom_group_id) {
        var defer = $q.defer();
        $scope.dataService.getTasksByMoMGroupId(mom_group_id).then(function(tasks) {
            if(tasks) {
                var task_ids = tasks.map(function(t) { return t.id; });

                $scope.dataService.setSelectedTaskIds(task_ids);
                $scope.jumpToSelectedTasks();
                defer.resolve(tasks);
            } else {
                defer.resolve(undefined);
            }
        });
        return defer.promise;
    };

    $scope.loadTasksByMoMParentGroupIdSelectAndJumpIntoView = function(mom_parent_group_id) {
        var defer = $q.defer();
        $scope.dataService.getTasksByMoMParentGroupId(mom_parent_group_id).then(function(tasks) {
            if(tasks) {
                var task_ids = tasks.map(function(t) { return t.id; });

                $scope.dataService.setSelectedTaskIds(task_ids);

                if(tasks.length > 1) {
                    $scope.dataService.selected_project_id = tasks[0].project_mom_id;
                }

                $scope.jumpToSelectedTasks();
                defer.resolve(tasks);
            } else {
                defer.resolve(undefined);
            }
        });
        return defer.promise;
    };

    $scope.selectCurrentTask = function() {
        var currentTasks = dataService.tasks.filter(function(t) { return t.starttime <= dataService.viewTimeSpan.to && t.endime >= dataService.viewTimeSpan.from; });
        if(currentTasks.lenght > 0) {
            dataService.setSelectedTaskId(currentTasks[0].id);
        }
    };

    $scope.jumpToSelectedTasks = function() {
        if(dataService.selected_task_ids == undefined)
            return;

        var tasks = dataService.selected_task_ids.map(function(t_id) { return dataService.taskDict[t_id]; });

        if(tasks.length == 0)
            return;

        var minStarttime = new Date(Math.min.apply(null, tasks.map(function(t) { return t.starttime; })));
        var maxEndtime = new Date(Math.max.apply(null, tasks.map(function(t) { return t.endtime; })));

        if(maxEndtime <= minStarttime) {
            //swap
            var tmp = new Date(maxEndtime.getTime());
            maxEndtime = new Date(minStarttime.getTime());
            minStarttime = new Date(tmp.getTime());
        }

        dataService.viewTimeSpan = {
            from: dataService.floorDate(minStarttime, 1, 5),
            to: dataService.ceilDate(maxEndtime, 1, 5)
        };
        dataService.autoFollowNow = false;
    };

    $scope.scrollBack = function() {
        dataService.autoFollowNow = false;
        var viewTimeSpanInmsec = dataService.viewTimeSpan.to.getTime() - dataService.viewTimeSpan.from.getTime();
        dataService.viewTimeSpan = {
            from: dataService.floorDate(new Date(dataService.viewTimeSpan.from.getTime() - 0.5*viewTimeSpanInmsec), 1, 5),
            to: dataService.floorDate(new Date(dataService.viewTimeSpan.to.getTime() - 0.5*viewTimeSpanInmsec), 1, 5)
        };
    };

    $scope.scrollForward = function() {
        dataService.autoFollowNow = false;
        var viewTimeSpanInmsec = dataService.viewTimeSpan.to.getTime() - dataService.viewTimeSpan.from.getTime();
        dataService.viewTimeSpan = {
            from: dataService.floorDate(new Date(dataService.viewTimeSpan.from.getTime() + 0.5*viewTimeSpanInmsec), 1, 5),
            to: dataService.floorDate(new Date(dataService.viewTimeSpan.to.getTime() + 0.5*viewTimeSpanInmsec), 1, 5)
        };
    };

    $scope.onZoomTimespanChanged = function() {
        var viewTimeSpanInmsec = dataService.viewTimeSpan.to.getTime() - dataService.viewTimeSpan.from.getTime();
        var focusTime = new Date(dataService.viewTimeSpan.from + 0.5*viewTimeSpanInmsec);

        if(dataService.autoFollowNow) {
            focusTime = dataService.floorDate(dataService.lofarTime, 1, 5);
        } else {
            var tasks = dataService.selected_task_ids.map(function(t_id) { return dataService.taskDict[t_id]; });

            if(tasks.lenght > 0) {
                var minStarttime = new Date(Math.min.apply(null, tasks.map(function(t) { return t.starttime; })));
                var maxEndtime = new Date(Math.max.apply(null, tasks.map(function(t) { return t.endtime; })));

                focusTime = dataService.floorDate(new Date(0.5*(minStarttime.getTime() + maxEndtime.getTime())), 1, 5);
            }
        }

        dataService.viewTimeSpan = {
            from: dataService.floorDate(new Date(focusTime.getTime() - 0.25*$scope.zoomTimespan.value*60*1000)),
            to: dataService.floorDate(new Date(focusTime.getTime() + 0.75*$scope.zoomTimespan.value*60*1000))
        };
    };

    $scope.selectZoomTimespan = function() {
        var viewTimeSpanInmsec = dataService.viewTimeSpan.to.getTime() - dataService.viewTimeSpan.from.getTime();
        var viewTimeSpanInMinutes = Math.round(viewTimeSpanInmsec/60000);

        var foundZoomTimespan = $scope.zoomTimespans.find(function(zts) { return zts.value == viewTimeSpanInMinutes; });

        if(foundZoomTimespan) {
            $scope.zoomTimespan = foundZoomTimespan;
        } else {
            var customZoomTimespan = $scope.zoomTimespans.find(function(zts) { return zts.name.startsWith('Custom'); });
            customZoomTimespan.value = viewTimeSpanInMinutes;
            if(viewTimeSpanInMinutes < 1440) {
                customZoomTimespan.name = 'Custom (' + viewTimeSpanInMinutes + ' min)';
            } else {
                var viewTimeSpanInDays = Math.floor(viewTimeSpanInMinutes / 1440);
                var viewTimeSpanReaminingMinutes = viewTimeSpanInMinutes - viewTimeSpanInDays * 1440;
                customZoomTimespan.name = 'Custom (' + viewTimeSpanInDays  + ' days ' + viewTimeSpanReaminingMinutes + ' min)';
            }
            $scope.zoomTimespan = customZoomTimespan;
        }
    };

    $scope.onViewTimeSpanFromChanged = function() {
        if (!isNaN(dataService.viewTimeSpan.from)) {
            dataService.autoFollowNow = false;
            if(dataService.viewTimeSpan.from >= dataService.viewTimeSpan.to) {
                dataService.viewTimeSpan.to = dataService.floorDate(new Date(dataService.viewTimeSpan.from.getTime() + $scope.zoomTimespan.value*60*1000), 1, 5);
            }
        }
    };

    $scope.onViewTimeSpanToChanged = function() {
        if (!isNaN(dataService.viewTimeSpan.to)) {
            dataService.autoFollowNow = false;
            if(dataService.viewTimeSpan.to <= dataService.viewTimeSpan.from) {
                dataService.viewTimeSpan.from = dataService.floorDate(new Date(dataService.viewTimeSpan.to.getTime() - $scope.zoomTimespan.value*60*1000), 1, 5);
            }
        }
    };

    $scope.getFullTimeWindowForSelectedProject = function() {
        dataService.getProjectTasksTimeWindow(dataService.selected_project_id).then(function(window) {
                    if(window && window.min_starttime && window.max_endtime) {
                        dataService.viewTimeSpan.from = dataService.convertDatestringToLocalUTCDate(window.min_starttime);
                        dataService.viewTimeSpan.to = dataService.convertDatestringToLocalUTCDate(window.max_endtime);
                    }
                });
    };

    $scope.$watch('dataService.viewTimeSpan', function() {
        $scope.selectZoomTimespan();

        $scope.$evalAsync(function() {
            dataService.clearTasksAndClaimsOutsideViewSpan();

            $scope.$evalAsync(function() {
                //for progress tracking
                dataService.loadingChunksQueue = dataService.loadingChunksQueue.filter(function(c) { return c.loading; });
                var loadingChunks = dataService.loadingChunksQueue.filter(function(c) { return c.loading; });
                dataService.nrOfLoadableChunks = dataService.loadingChunksQueue.length;
                dataService.nrOfLoadingChunks = loadingChunks.length;
                dataService.nrOfLoadedChunks = dataService.nrOfLoadableChunks - dataService.nrOfLoadingChunks;

                $scope.$evalAsync(dataService.getTasksAndClaimsForViewSpan);
            });
        });
    }, true);

    $scope.$watch('dataService.filteredTaskChangeCntr', function() {
        dataService.computeMinMaxTaskTimes();
        dataService.filteredTasksDict = dataService.toIdBasedDict(dataService.filteredTasks);
    });

    $scope.$watch('dataService.lofarTime', function() {
        if(dataService.autoFollowNow && (Math.round(dataService.lofarTime.getTime()/1000))%5==0) {
            $scope.jumpToNow();
        }
    });

    $scope.$watch('dataService.autoFollowNow', function() {
        if(dataService.autoFollowNow) {
            $scope.jumpToNow();
        }
    });

    $scope.$watch('dataService.selected_project_id', function() {
        if(dataService.projectMode) {
            $scope.$evalAsync(function() {
                dataService.autoFollowNow = false;
                dataService.viewTimeSpan.from = dataService.lofarTime;
                dataService.viewTimeSpan.to = dataService.lofarTime;
                dataService.tasks.splice(0, dataService.tasks.length);
                dataService.tasksDict = dataService.toIdBasedDict(dataService.tasks);
                dataService.taskChangeCntr++;
                dataService.getProjectTasksTimeWindow(dataService.selected_project_id).then(function(window) {
                    if(window && window.min_starttime && window.max_endtime) {
                        dataService.viewTimeSpan.from = dataService.convertDatestringToLocalUTCDate(window.min_starttime);
                        dataService.viewTimeSpan.to = dataService.convertDatestringToLocalUTCDate(window.max_endtime);
                    }
                });
            });
        }
    });

    $scope.$watch('dataService.selected_project', function() {
        $scope.$evalAsync(function() {
            dataService.selected_project_id = dataService.selected_project.value;
        });
    });

    $scope.$watch('dataService.loadResourceClaims', function() {
        if(dataService.loadResourceClaims) {
            dataService.loadedHours = {};
            dataService.getTasksAndClaimsForViewSpan();
        }
    });

    $scope.$watch('dataService.selected_resource_id', function() {
        $scope.$evalAsync(function() {
            $scope.dataService.getUsagesForSelectedResource();
            $scope.dataService.getResource($scope.dataService.selected_resource_id);
        });
    });


    dataService.initialLoad();

    //clock ticking every second
    //updating current lofarTime by the elapsed time since previous tick
    //lofarTime is synced every minute with server utc time.
    self._prevTick = Date.now();
    self._doTimeTick = function() {
        var tick = Date.now();
        var elapsed = tick - self._prevTick;
        self._prevTick = tick;
        //evalAsync, so lofarTime will be seen by watches
        $scope.$evalAsync(function() {
            dataService.lofarTime = new Date(dataService.lofarTime.getTime() + elapsed);
        });

        setTimeout(self._doTimeTick, 1000);
    };
    self._doTimeTick();
}
]);

//extend the default dateFilter so that it always displays dates as 'yyyy-MM-dd HH:mm:ss'
//without any extra timezone string.
//see also comments above why we do tricks with local and utc dates
angular.module('raeApp').config(['$provide', function($provide) {
    $provide.decorator('dateFilter', ['$delegate', function($delegate) {
        var srcFilter = $delegate;

        function zeroPaddedString(num) {
            var numstr = num.toString();
            if(numstr.length < 2) {
                return '0' + numstr;
            }
            return numstr;
        };

        var extendsFilter = function() {
            if(arguments[0] instanceof Date && arguments.length == 1) {
                var date = arguments[0];
                var dateString =  date.getFullYear() + '-' + zeroPaddedString(date.getMonth()+1) + '-' + zeroPaddedString(date.getDate()) + ' ' +
                                  zeroPaddedString(date.getHours()) + ':' + zeroPaddedString(date.getMinutes()) + ':' + zeroPaddedString(date.getSeconds());

                return dateString;
            }
            return srcFilter.apply(this, arguments);
        }

        return extendsFilter;
    }])
}])
