(function () {
    'use strict';


    var module = angular.module('SparQs.charts', []);

    module.directive('quantHistogram', function ($parse) {

        function link(scope, $element, attrs) {

            var yProp = attrs.chartY || 'y';
            var xProp = attrs.chartX || 'x';

            var xScale = d3.scale.ordinal();
            var yScale = d3.scale.linear();

            var getX = function(d) {
                return d[xProp];
            };

            var getY = function(d) {
                return d[yProp];
            };

            var $d3_element = d3.select($element[0]);
            var svg = $d3_element.append("svg");

            var margin = {
                top: 3,
                right: 3,
                bottom: 3,
                left: 3
            };

            var chart = svg
                .append('g')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            var elementSize = function () {
                console.log("visible: " + $element.is(':visible'));
                return {
                    width: $element.innerWidth(),
                    height: $element.innerHeight()
                }
            };

            // Watch for size changes
            //scope.$watch(elementSize, function () {
            //    scope.render();
            //}, true);

            // Watch for visibility changes
            scope.$watch('visible', function(newVals, oldVals) {
                if (newVals) return scope.render();
            }, false);

            // Watch for data changes (just reference, not object equals)
            scope.$watch('distribution', function(newVals, oldVals) {
                return scope.render();
            }, false);

            scope.render = function () {
                var size = elementSize();

                console.log('Full size', size);
                var graphWidth = size.width - margin.right - margin.left;
                var graphHeight = size.height - margin.top - margin.bottom;
                console.log('rendering to ' + graphWidth + ' x ' + graphHeight);

                var data = scope.distribution || [];

                var yExtent = d3.extent(data, getY);
                yScale
                    .domain([0, yExtent[1]])
                    .range([0, graphHeight]);

                xScale
                    .domain(data.map(getX))
                    .rangeRoundBands([0, graphWidth], 0.1, 0.1);

                var bind = chart.selectAll('rect.bar')
                    .data(data);

                bind.exit()
                    .remove();

                bind.enter()
                    .append("rect")
                    .attr('class', 'bar')
                    .attr('height', 0)
                    .attr('x', function(d) {
                        return xScale(d[xProp]);
                    })
                    .attr('y', function(d) {
                        return graphHeight - yScale(d[yProp]);
                    })
                    .attr('width', xScale.rangeBand())
                    .attr("height", function(d) {
                        return yScale(d[yProp]);
                    });
            };
        }

        return {
            //Use as a tag only
            restrict: 'E',
            replace: false,

            //Directive's inner scope
            scope: {
                distribution: '=distribution',
                visible: '=visible'
            },
            link: link
        };
    });
})();
