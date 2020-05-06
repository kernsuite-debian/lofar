// $Id$

var app = angular.module('raeApp',
                         ['CleanupControllerMod',
                         'DataControllerMod',
                         'GanttResourceControllerMod',
                         'GanttProjectControllerMod',
                         'ChartResourceUsageControllerMod',
                         'GridControllerMod',
                         'EventGridControllerMod',
                         'ui.layout',
                         'ui.bootstrap',
                         'ui.bootstrap.tabs',
                         'highcharts-ng',
                         'ngMaterial']);

app.config(['$compileProvider', function ($compileProvider) {
    $compileProvider.debugInfoEnabled(false);
}]);

var secondsToHHmmss = function(seconds) {
    var hours = Math.floor(seconds / 3600);
    var remaining_seconds = seconds - (3600 * hours);

    var minutes = Math.floor(remaining_seconds / 60);
    remaining_seconds = remaining_seconds - (60 * minutes);

    var str = '';
    if(hours < 10) {
        str += '0';
    }
    str += hours + ':';
    if(minutes < 10) {
        str += '0';
    }
    str += minutes + ':';
    if(remaining_seconds < 10) {
        str += '0';
    }
    str += remaining_seconds;
    return str;
};

app.filter('secondsToHHmmss', function($filter) {
    return secondsToHHmmss;
})

//filter unique items in array
Array.prototype.unique = function() {
    var unique = {};
    var length = this.length;

    for (var i = 0; i < length; i++) {
        var item = this[i];
        unique[item] = true;
    }
    return Object.keys(unique);
};
