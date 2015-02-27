(function () {
    'use strict';


    var module = angular.module('SparQs.charts', []);

    module.directive('quantHistogram', function ($parse) {

        var default_distribution = {
            counts: [],
            min_bin: 0,
            max_bin: 0,
            bin_size: 1,
            bins: 0
        };

        function link(scope, $element, attrs) {

            var yProp = attrs.chartY || 'y';
            var xProp = attrs.chartX || 'x';

            var xScale = d3.scale.ordinal();
            var xLinearScale = d3.scale.linear();
            var yScale = d3.scale.linear();

            var getX = function (d) {
                return d[xProp];
            };

            var getY = function (d) {
                return d[yProp];
            };

            var xAxis = d3.svg.axis()
                .scale(xLinearScale)
                .orient('bottom')
                .ticks(5);

            var yAxis = d3.svg.axis()
                .scale(yScale)
                .orient('left')
                .ticks(2);

            var $d3_element = d3.select($element[0]);
            var svg = $d3_element.append("svg");

            var chart = svg
                .append('g');

            var xAxisGroup = chart.append('g')
                .attr('class', 'x axis');

            var yAxisGroup = chart.append('g')
                .attr('class', 'y axis');

            var elementSize = function () {
                return {
                    width: $element.innerWidth(),
                    height: $element.innerHeight()
                }
            };

            // Watch for visibility changes
            scope.$watch('dimension.filtering', function (newVals, oldVals) {
                if (newVals) return scope.render();
            }, false);

            // Watch for data changes (just reference, not object equals)
            scope.$watch('dimension.distribution', function (newVals, oldVals) {
                return scope.render();
            }, false);

            scope.updateScaleDomains = function(distribution) {

                var yExtent = d3.extent(distribution.counts, getY);
                yScale.domain([0, yExtent[1]]);

                var xDomain = d3.range(
                    distribution.min_bin,
                    distribution.max_bin + distribution.bin_size, // it is exclusive on max
                    distribution.bin_size
                );
                //Guaranteed to be at least one bin in the xDomain now
                if (xDomain.length == 0) {
                    throw("domain is empty");
                }

                //If there aren't enough bins, then add some on the outside
                while (xDomain.length < distribution.bins) {
                    var first = xDomain[0];
                    var last = xDomain[xDomain.length - 1];

                    if (first >= 0) {
                        xDomain.unshift(first - distribution.bin_size);
                    }

                    xDomain.push(last + distribution.bin_size);
                }

                xScale.domain(xDomain);
                xLinearScale.domain([xDomain[0], xDomain[xDomain.length - 1]]);
            };

            scope.getMargin = function() {
                var margin = {
                    top: 5,
                    right: 5,
                    bottom: 20,
                    left: 30
                };

                //The top y-axis label might stick out
                var format = yAxis.tickFormat() || yScale.tickFormat(yAxis.ticks());
                var maxYVal = format(yScale.domain()[1]);
                margin.left = 10 + 7 * maxYVal.length;

                //The right-most x-axis label tends to stick out
                format = xAxis.tickFormat() || xLinearScale.tickFormat(xAxis.ticks());
                var maxXVal = format(xLinearScale.domain()[1]);
                margin.right = 0.5 * 7 * maxXVal.length;

                return margin;
            };

            scope.render = function () {
                if (!scope.dimension || !scope.dimension.is_quantitative()) {
                    return;
                }

                var distribution = scope.dimension.distribution || default_distribution;

                scope.updateScaleDomains(distribution);
                var margin = scope.getMargin();

                var size = elementSize();
                var graphWidth = size.width - margin.right - margin.left;
                var graphHeight = size.height - margin.top - margin.bottom;

                //Shift the chart
                chart.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

                //Update the scale ranges
                yScale.range([graphHeight, 0]);
                xScale.rangeRoundBands([0, graphWidth], 0, 0.1);
                xLinearScale.range([0, graphWidth]);

                //Update the axes
                xAxisGroup
                    .attr("transform", "translate(0," + graphHeight + ")")
                    .call(xAxis);
                yAxisGroup.call(yAxis);

                //Draw some bars
                var bars = chart.selectAll('rect.bar')
                    .data(distribution.counts);

                bars.exit()
                    .remove();

                bars.enter()
                    .append("rect")
                    .attr('class', 'bar')
                    .attr('height', 0);

                bars.attr('x', function (d) {
                        return xScale(d[xProp]);
                    })
                    .attr('y', function (d) {
                        return yScale(d[yProp]);
                    })
                    .attr('width', xScale.rangeBand())
                    .attr("height", function (d) {
                        return graphHeight - yScale(d[yProp]);
                    });
            };
        }

        return {
            //Use as a tag only
            restrict: 'E',
            replace: false,

            //Directive's inner scope
            scope: {
                dimension: '=dimension'
            },
            link: link
        };
    });
})();
