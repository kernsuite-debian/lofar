'use strict';
angular.module('ui.layout', []).controller('uiLayoutCtrl', [
  '$scope',
  '$attrs',
  '$element',
  function uiLayoutCtrl($scope, $attrs, $element) {
    return {
      opts: angular.extend({}, $scope.$eval($attrs.uiLayout), $scope.$eval($attrs.options)),
      element: $element
    };
  }
]).directive('uiLayout', [
  '$parse',
  function ($parse) {
    var splitBarElem_htmlTemplate = '<div class="stretch ui-splitbar"></div>';
    return {
      restrict: 'AE',
      compile: function compile(tElement, tAttrs) {
        var _i, _childens = tElement.children(), _child_len = _childens.length;
        var opts = angular.extend({}, $parse(tAttrs.uiLayout)(), $parse(tAttrs.options)());
        var isUsingColumnFlow = opts.flow === 'column';
        tElement.addClass('stretch').addClass('ui-layout-' + (opts.flow || 'row'));
        var child_lenghts = [];
        var total_length = isUsingColumnFlow ? tElement[0].clientWidth : tElement[0].clientHeight;
        for (_i = 0; _i < _child_len; ++_i) {
          angular.element(_childens[_i]).addClass('stretch');
          var init_length_attr = isUsingColumnFlow ? _childens[_i].attributes.getNamedItem('ui-layout-init-width') || _childens[_i].attributes.getNamedItem('ui-layout-init-min-width') : _childens[_i].attributes.getNamedItem('ui-layout-init-height') || _childens[_i].attributes.getNamedItem('ui-layout-init-min-height');
          if(init_length_attr) {
            if(init_length_attr.nodeValue.includes('%')) {
                var child_length_perc = parseFloat(init_length_attr.nodeValue);
                child_lenghts.push(child_length_perc);
            }
            else {
                var child_length_perc = 100.0*parseFloat(init_length_attr.nodeValue) / total_length;
                child_lenghts.push(child_length_perc);
            }

            //if there is more room than needed for the initial min length, distribute evenly
            var is_minimal_length = isUsingColumnFlow ? _childens[_i].attributes.getNamedItem('ui-layout-init-width') === null : _childens[_i].attributes.getNamedItem('ui-layout-init-height') === null;
            if(is_minimal_length) {
                child_lenghts[child_lenghts.length-1] = Math.max(child_lenghts[child_lenghts.length-1], 100.0 / _child_len);
            }
        }
          else
            child_lenghts.push(undefined);
        }

        if (_child_len > 1) {
          var totalDefinedChildLength = child_lenghts.filter(function(cl) { return cl != undefined;}).reduce(function(a, b){return a+b;});
          var remainingLengthForUndefinedChilds = 100 - totalDefinedChildLength;
          var numUndefinedChilds = child_lenghts.filter(function(cl) { return cl == undefined;}).length;
          var undefinedChildLength = remainingLengthForUndefinedChilds / numUndefinedChilds;

          var flowProperty = isUsingColumnFlow ? 'left' : 'top';
          var oppositeFlowProperty = isUsingColumnFlow ? 'right' : 'bottom';
          var prevPerc = 0;
          for (_i = 0; _i < _child_len; ++_i) {
            var child_length = child_lenghts[_i];
            if(child_length == undefined) {
                child_length = undefinedChildLength;
            }
            var area = angular.element(_childens[_i]).css(flowProperty, prevPerc + '%').css(oppositeFlowProperty, 100 - (prevPerc + child_length) + '%');
            if (_i < _child_len - 1) {
              var bar = angular.element(splitBarElem_htmlTemplate).css(flowProperty, prevPerc + child_length + '%');
              area.after(bar);
            }
            prevPerc += child_length;
          }
        }
      },
      controller: 'uiLayoutCtrl'
    };
  }
]).directive('uiSplitbar', function () {
  var htmlElement = angular.element(document.body.parentElement);
  return {
    require: '^uiLayout',
    restrict: 'EAC',
    link: function (scope, iElement, iAttrs, parentLayout) {
      var animationFrameRequested, lastX;
      var _cache = {};
      var isUsingColumnFlow = parentLayout.opts.flow === 'column';
      var mouseProperty = isUsingColumnFlow ? 'clientX' : 'clientY';
      var flowProperty = isUsingColumnFlow ? 'left' : 'top';
      var oppositeFlowProperty = isUsingColumnFlow ? 'right' : 'bottom';
      var sizeProperty = isUsingColumnFlow ? 'width' : 'height';
      var barElm = iElement[0];
      function _cached_layout_values() {
        var layout_bb = parentLayout.element[0].getBoundingClientRect();
        var bar_bb = barElm.getBoundingClientRect();
        _cache.time = +new Date();
        _cache.barSize = bar_bb[sizeProperty];
        _cache.layoutSize = layout_bb[sizeProperty];
        _cache.layoutOrigine = layout_bb[flowProperty];
      }
      function _draw() {
        var the_pos = (lastX - _cache.layoutOrigine) / _cache.layoutSize * 100;
        the_pos = Math.min(the_pos, 100 - _cache.barSize / _cache.layoutSize * 100);
        the_pos = Math.max(the_pos, parseInt(barElm.previousElementSibling.style[flowProperty], 10));
        if (barElm.nextElementSibling.nextElementSibling) {
          the_pos = Math.min(the_pos, parseInt(barElm.nextElementSibling.nextElementSibling.style[flowProperty], 10));
        }
        barElm.style[flowProperty] = barElm.nextElementSibling.style[flowProperty] = the_pos + '%';
        barElm.previousElementSibling.style[oppositeFlowProperty] = 100 - the_pos + '%';
        animationFrameRequested = null;
      }
      function _resize(mouseEvent) {
        lastX = mouseEvent[mouseProperty] || mouseEvent.originalEvent[mouseProperty];
        if (animationFrameRequested) {
          window.cancelAnimationFrame(animationFrameRequested);
        }
        if (!_cache.time || +new Date() > _cache.time + 1000) {
          _cached_layout_values();
        }
        animationFrameRequested = window.requestAnimationFrame(_draw);
      }
      iElement.on('mousedown touchstart', function (e) {
        e.preventDefault();
        e.stopPropagation();
        htmlElement.on('mousemove touchmove', _resize);
        return false;
      });
      htmlElement.on('mouseup touchend', function () {
        htmlElement.off('mousemove touchmove');
      });
    }
  };
});
var lastTime = 0;
var vendors = [
    'ms',
    'moz',
    'webkit',
    'o'
  ];
for (var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
  window.requestAnimationFrame = window[vendors[x] + 'RequestAnimationFrame'];
  window.cancelAnimationFrame = window[vendors[x] + 'CancelAnimationFrame'] || window[vendors[x] + 'CancelRequestAnimationFrame'];
}
if (!window.requestAnimationFrame) {
  window.requestAnimationFrame = function (callback) {
    var currTime = new Date().getTime();
    var timeToCall = Math.max(0, 16 - (currTime - lastTime));
    var id = window.setTimeout(function () {
        callback(currTime + timeToCall);
      }, timeToCall);
    lastTime = currTime + timeToCall;
    return id;
  };
}
if (!window.cancelAnimationFrame) {
  window.cancelAnimationFrame = function (id) {
    clearTimeout(id);
  };
}
