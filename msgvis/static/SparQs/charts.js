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

        var QuantHistogram = function($element, attrs, onBrushed) {

            var yProp = attrs.chartY || 'y';
            var xProp = attrs.chartX || 'x';
            var $d3_element = d3.select($element[0]);


            var xScale = d3.scale.ordinal();
            var xLinearScale = d3.scale.linear();
            var xTimeScale = d3.time.scale();
            var xCurrentScale = xLinearScale;

            var yScale = d3.scale.linear();
            var xAxis = d3.svg.axis()
                .scale(xCurrentScale)
                .orient('bottom')
                .ticks(5);

            var yAxis = d3.svg.axis()
                .scale(yScale)
                .orient('left')
                .ticks(2);

            var brush = d3.svg.brush()
                .x(xCurrentScale)
                .on("brush", function() {
                    var selection = currentExtent();
                    onBrushed(selection[0], selection[1]);
                });

            var svg = $d3_element.append("svg");

            var chart = svg
                .append('g');

            var xAxisGroup = chart.append('g')
                .attr('class', 'x axis');

            var yAxisGroup = chart.append('g')
                .attr('class', 'y axis');

            var barsGroup = chart.append('g')
                .attr('class', 'bars');

            var brushGroup = chart.append("g")
                .attr("class", "x brush");


            var updateScaleDomains = function(distribution, isTime) {

                var yExtent = d3.extent(distribution.counts, function(d) {
                    return d[yProp];
                });

                yScale.domain([0, yExtent[1]]);
                var xDomain;
                if ( isTime ){

                    xDomain = d3.range(
                       new Date(distribution.min_bin),
                       new Date((new Date(distribution.max_bin)) + 1000 * distribution.bin_size), // it is exclusive on max
                       +distribution.bin_size * 1000
                    );
                    xCurrentScale = xTimeScale;
                    xAxis.tickFormat(d3.time.format("%Y-%m-%d %H:%M:%S"));
                    xAxis.ticks(3);
                }else {

                    xDomain = d3.range(
                        distribution.min_bin,
                        distribution.max_bin + distribution.bin_size, // it is exclusive on max
                        distribution.bin_size
                    );
                    xCurrentScale = xLinearScale;
                    xAxis.tickFormat(d3.format("d"));
                    xAxis.ticks(5);
                }
                xAxis.scale(xCurrentScale);
                brush.x(xCurrentScale);
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
                xCurrentScale.domain([xDomain[0] - 1, xDomain[xDomain.length - 1] + 1]);
            };


            var size = {
                height: undefined,
                width: undefined,
                margin: {
                    top: 5,
                    right: 5,
                    bottom: 20,
                    left: 30
                }
            };

            var updateSize = function(isTime) {
                //The top y-axis label might stick out
                var format = yAxis.tickFormat() || yScale.tickFormat(yAxis.ticks());
                var maxYVal = format(yScale.domain()[1]);
                size.margin.left = 10 + 7 * maxYVal.length;

                //The right-most x-axis label tends to stick out
                format = xAxis.tickFormat() || xCurrentScale.tickFormat(xAxis.ticks());
                if (isTime){
                    size.margin.right = 0;
                }
                else{
                    var maxXVal = format(xCurrentScale.domain()[1]);
                    size.margin.right = 0.5 * 7 * maxXVal.length;
                }


                var elementSize = {
                    width: $element.innerWidth(),
                    height: $element.innerHeight()
                };

                size.width = elementSize.width - size.margin.right - size.margin.left;
                size.height = elementSize.height - size.margin.top - size.margin.bottom;
            };

            this.render = function (dimension) {
                if (!dimension || (!dimension.is_quantitative() && !dimension.is_time())) {
                    return;
                }

                var distribution = dimension.distribution || default_distribution;

                updateScaleDomains(distribution, dimension.is_time());
                updateSize(dimension.is_time());

                //Shift the chart
                chart.attr('transform', 'translate(' + size.margin.left + ',' + size.margin.top + ')');


                //Update the scale ranges
                yScale.range([size.height, 0]);
                xScale.rangeRoundBands([0, size.width], 0, 0.1);
                xCurrentScale.range([0, size.width]);


                //Update the axes
                xAxisGroup
                    .attr("transform", "translate(0," + size.height + ")")
                    .call(xAxis);

                yAxisGroup.call(yAxis);

                //Draw some bars
                var bars = barsGroup.selectAll('rect.bar')
                    .data(distribution.counts);

                bars.exit()
                    .remove();

                bars.enter()
                    .append("rect")
                    .attr('class', 'bar')
                    .attr('height', 0);

                bars.attr('x', function (d) {
                    if (dimension.is_time()) return xScale(+new Date(d[xProp]));
                    else return xScale(d[xProp]);
                })
                    .attr('y', function (d) {
                        return yScale(d[yProp]);
                    })
                    .attr('width', xScale.rangeBand())
                    .attr("height", function (d) {
                        return size.height - yScale(d[yProp]);
                    });

                //Draw the brush
                redrawBrush();
            };

            function currentExtent() {
                return brush.empty() ? xCurrentScale.domain() : brush.extent();
            }

            function redrawBrush() {
                brushGroup
                    .call(brush)
                    .selectAll("rect")
                    .attr("y", 0)
                    .attr("height", size.height);

                var handles = brushGroup.selectAll('.resize')
                    .selectAll('.handle')
                    .data([1]);

                handles.enter()
                    .append('rect')
                    .attr('class', 'handle')
                    .attr('x', -3)
                    .attr('width', 6)
                    .attr('rx', 2)
                    .attr('ry', 2);

                handles
                    .attr('y', size.height / 3)
                    .attr('height', size.height / 3);

                //brushg.selectAll(".resize").append("path")
                //    .attr("transform", "translate(0," +  height / 2 + ")")
                //    .attr("d", arc);
            }

            //The directive calls these when the bindings change
            this.setBrushExtent = function(min, max) {
                if (min === undefined && max === undefined) {
                    brush.clear();
                    redrawBrush();
                    return;
                }

                var extent = currentExtent();
                if (extent[0] !== min || extent[1] !== max) {
                    extent[0] = min;
                    extent[1] = max;
                    brush.extent(extent);
                    redrawBrush();
                }

            };
        };

        function link(scope, $element, attrs) {
            if (!scope._histogram) {

                var onBrushed = function(min, max) {
                    if (scope.dimension && scope.dimension.filter) {

                       if (scope.dimension.is_time()){
                            var format = d3.time.format("%Y-%m-%d %H:%M:%S");
                            min = new Date(min);
                            max = new Date(max);
                            scope.dimension.filter.min_time(min);
                            scope.dimension.filter.max_time(max);
                       }else{
                            scope.dimension.filter.min(min);
                            scope.dimension.filter.max(max);
                       }
                    }

                    if (scope.onBrushed) {
                        scope.onBrushed(min, max);
                    }
                };

                var hist = scope._histogram = new QuantHistogram($element, attrs, onBrushed);

                // Watch for visibility changes
                scope.$watch('dimension.filtering', function (newVals, oldVals) {
                    if (newVals) return hist.render(scope.dimension);
                }, false);

                // Watch for data changes (just reference, not object equals)
                scope.$watch('dimension.distribution', function (newVals, oldVals) {
                    return hist.render(scope.dimension);
                }, false);

                // Watch for filter changes
                scope.$watch('dimension.filter.data', function(newVal, oldVal) {
                    if (newVal) {
                        if (scope.dimension.is_time()){
                            hist.setBrushExtent(newVal.min_time, newVal.max_time);
                        }else{
                            hist.setBrushExtent(newVal.min, newVal.max);
                        }
                    }
                }, true);

            } else {
                throw("What is this madness");
            }
        }

        return {
            //Use as a tag only
            restrict: 'E',
            replace: false,

            //Directive's inner scope
            scope: {
                dimension: '=dimension',
                onBrushed: '=onBrushed'
            },
            link: link
        };
    });

})();
