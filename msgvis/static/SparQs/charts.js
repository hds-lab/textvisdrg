(function () {
    'use strict';


    var module = angular.module('SparQs.charts', []);

    module.directive('quantHistogram', function () {

        var QuantHistogram = function ($element, attrs, onBrushed) {

            var $d3_element = d3.select($element[0]);
            var yProp = 'value';

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
                .on("brush", function () {
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


            var updateScaleDomains = function (table, domain, isTime) {

                var yExtent = d3.extent(table, function (d) {
                    return d[yProp];
                });

                yScale.domain([0, yExtent[1]]);
                var buffer = 1;
                //var xDomain;
                if (isTime) {
                    //xDomain = d3.range(
                    //   new Date(distribution.min_bin),
                    //   new Date((new Date(distribution.max_bin)) + 1000 * distribution.bin_size), // it is exclusive on max
                    //   +distribution.bin_size * 1000
                    //);
                    xCurrentScale = xTimeScale;
                    xAxis.tickFormat(d3.time.format("%Y-%m-%d %H:%M:%S"));
                    xAxis.ticks(1);
                    buffer = 1000;

                    domain = domain.map(function (timeStr) {
                        return new Date(timeStr);
                    });
                } else {
                    xCurrentScale = xLinearScale;
                    xAxis.tickFormat(d3.format("d"));
                    xAxis.ticks(5);
                }

                xAxis.scale(xCurrentScale);
                brush.x(xCurrentScale);

                xScale.domain(domain);
                if (domain.length > 0) {
                    xCurrentScale.domain([domain[0] - buffer, +domain[domain.length - 1] + buffer]);
                } else {
                    xCurrentScale.domain([0, 1]);
                }
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

            var updateSize = function (isTime) {
                //The top y-axis label might stick out
                var format = yAxis.tickFormat() || yScale.tickFormat(yAxis.ticks());
                var maxYVal = format(yScale.domain()[1]);
                size.margin.left = 10 + 7 * maxYVal.length;

                //The right-most x-axis label tends to stick out
                format = xAxis.tickFormat() || xCurrentScale.tickFormat(xAxis.ticks());
                if (isTime) {
                    size.margin.right = 5;
                }
                else {
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
                if (!dimension || (!dimension.is_quantitative_or_time())) {
                    return;
                }

                var table = dimension.table || [];
                var domain = dimension.domain || [];
                var xProp = dimension.key;

                updateScaleDomains(table, domain, dimension.is_time());
                updateSize(dimension.is_time());

                //Shift the chart
                chart.attr('transform', 'translate(' + size.margin.left + ',' + size.margin.top + ')');


                //Update the scale ranges
                yScale.range([size.height, 0]);
                xScale.rangeBands([0, size.width], 0, 0);
                xCurrentScale.range([0, size.width]);


                //Update the axes
                xAxisGroup
                    .attr("transform", "translate(0," + size.height + ")")
                    .call(xAxis);

                yAxisGroup.call(yAxis);

                //Draw some bars
                var bars = barsGroup.selectAll('rect.bar')
                    .data(table);

                //Remove and add bars
                bars.exit()
                    .remove();

                bars.enter()
                    .append("rect")
                    .attr('class', 'bar')
                    .attr('height', 0);

                //Update the bars
                bars.attr('y', function (d) {
                    return yScale(d[yProp]);
                })
                    .attr('width', xScale.rangeBand())
                    .attr("height", function (d) {
                        return size.height - yScale(d[yProp]);
                    });

                if (dimension.is_time()) {
                    bars.attr('x', function (d) {
                        return xScale(new Date(d[xProp]));
                    })
                } else {
                    bars.attr('x', function (d) {
                        return xScale(d[xProp]);
                    });
                }

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
            this.setBrushExtent = function (min, max) {
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

                var onBrushed = function (min, max) {
                    if (scope.dimension && scope.dimension.filter) {

                        if (scope.dimension.is_time()) {
                            //var format = d3.time.format("%Y-%m-%d %H:%M:%S");
                            //min = new Date(min);
                            //max = new Date(max);
                            scope.dimension.filter.min_time(min);
                            scope.dimension.filter.max_time(max);
                        } else {
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
                scope.$watch('dimension.table', function (newVals, oldVals) {
                    return hist.render(scope.dimension);
                }, false);

                // Watch for filter changes
                scope.$watch('dimension.filter.data', function (newVal, oldVal) {
                    if (newVal) {
                        if (scope.dimension.is_time()) {
                            if (newVal.min_time && newVal.max_time) {
                                var min_time = new Date(newVal.min_time);
                                var max_time = new Date(newVal.max_time);
                                hist.setBrushExtent(min_time, max_time);
                            }
                        } else {
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

    module.directive('categoricalHistogram', function () {


        var dimensionScale = {};
        var setup_dimension_scale = function(dimension, width){
            var values = dimension.table.map(function(d){ return d.value; });
            var scale = d3.scale.linear();
            scale.domain([0, d3.max(values)]);
            scale.range([0, width]);
            dimensionScale[dimension.key] = scale;
        };
        var create_bar = function($element, dimension, level_value) {
            var elementSize = {
                width: $element.parent().width(),
                height: $element.parent().height()
            };
            var $d3_element = d3.select($element[0]);
            var svg = $d3_element.append("svg");
            svg.attr("width", elementSize.width);
            svg.attr("height", elementSize.height);

            var rect = svg.append("rect");
            rect.attr("width", dimensionScale[dimension.key](level_value));
            rect.attr("height", elementSize.height);
        };

        var render_bar = function(scope, $element, attrs){
            if ( typeof(scope.dimension) !== "undefined" ){
                var elementSize = {
                    width: $element.parent().width(),
                    height: $element.parent().height()
                };
                if ( typeof(dimensionScale[scope.dimension.key]) === "undefined" ){
                    setup_dimension_scale(scope.dimension, elementSize.width);
                }
                create_bar($element, scope.dimension, scope.levelValue);
            }
        };

        function link(scope, $element, attrs){
            scope.$watch('dimension.filtering', function (newVals, oldVals) {
                    if (newVals) return render_bar(scope, $element, attrs);
            }, false);

        }

        return {
            restrict: 'E',
            replace: false,

            scope: {
                dimension: '=dimension',
                levelValue: '=levelValue'
            },
            link: link

        }
    });

    module.directive('sparqsVis', function () {

        var SparQsVis = function ($element, attrs, onClicked) {

            var DEFAULT_VALUE_KEY = 'value';

            function dataClicked() {
                onClicked();
            }

            function aggregationLabel(dimension) {
                return 'Avg. ' + dimension.name;
            }

            function weightedAverage(arr, valueKey, columnDataKey) {
                if (arr.length == 0) return 0;

                var denom = 0,
                    sum = 0;

                arr.forEach(function(row) {
                    denom += row[valueKey];
                    sum += row[valueKey] * row[columnDataKey];
                });

                if (denom > 0) {
                    return sum / denom;
                } else {
                    return 0;
                }
            }

            function buildFullTable(primary, secondary, table, domains) {
                var rows;

                if (primary.is_quantitative_or_time() && secondary && secondary.is_quantitative_or_time()) {
                    //We're doing a scatter plot which is totally different
                    // and much simpler.

                    rows = table.map(function(row) {
                        return [row[primary.key], row[secondary.key]];
                    });

                    rows.unshift([primary.key, secondary.key]);
                    return rows;
                }

                //Otherwise let the fun begin...

                //Use the primary dim values down the left always
                var rowHeaders = domains[primary.key];
                var columnHeaders = [DEFAULT_VALUE_KEY];

                //Names inside the datatable rows
                var rowDataKey = primary.key;
                var columnDataKey = DEFAULT_VALUE_KEY;

                //A function for aggregating cell values (used for quant secondary dimensions)
                var columnAggregation = false;
                if (secondary){
                    if (!secondary.is_quantitative_or_time()) {
                        //Use the secondary dim values across the top
                        columnHeaders = domains[secondary.key];
                    } else {
                        //Leave the header alone but note we need to aggregate
                        columnAggregation = true;
                    }

                    columnDataKey = secondary.key;
                }

                // Create a matrix of zeros
                rows = new Array(rowHeaders.length + 1);

                // Maps from domain values to row/col indices
                var rowIndex = {};
                var columnIndex = {};

                // r is the row-index into the matrix.
                // r-1 can be used to index into the row headers
                // c is the column-index into the matrix.
                // c-1 can be used to index into the column headers
                var r, c;
                var dimValue = function(val) {
                    return val === null ? 'NULL' : val.toString();
                };
                for (r = 0; r <= rowHeaders.length; r++) {
                    rows[r] = new Array(columnHeaders.length + 1);

                    if (r == 0) {
                        //Create the header row
                        rows[r][0] = primary.key;
                        for (c = 1; c <= columnHeaders.length; c++) {
                            rows[r][c] = dimValue(columnHeaders[c - 1]);

                            //Build the column index
                            columnIndex[columnHeaders[c - 1]] = c;
                        }
                    } else {
                        // Build the row index
                        rowIndex[rowHeaders[r - 1]] = r;

                        // Put the primary dimension value in place
                        rows[r][0] = dimValue(rowHeaders[r - 1]);

                        for (c = 1; c <= columnHeaders.length; c++) {
                            // Fill the cells with zeros
                            rows[r][c] = 0;

                            // But if we're aggregating fill with an array
                            if (columnAggregation) {
                                rows[r][c] = [];
                            }
                        }
                    }
                }

                // Now fill in the non-zeros from the table
                table.forEach(function(row) {
                    var value = row[DEFAULT_VALUE_KEY];
                    var r = rowIndex[row[rowDataKey]];
                    var c = 1;
                    if (columnAggregation) {
                        //We are aggregating
                        rows[r][c].push(row);
                    } else {

                        if (secondary) {
                            //we have secondary dimension values in the headers which means
                            //the column index comes from the data
                            c = columnIndex[row[columnDataKey]];
                        }

                        rows[r][c] = value;
                    }
                });

                if (columnAggregation) {
                    // Finish the aggregation
                    for (r = 1; r <= rowHeaders.length; r++) {
                        for (c = 1; c <= columnHeaders.length; c++) {
                            rows[r][c] = weightedAverage(rows[r][c], DEFAULT_VALUE_KEY, columnDataKey);
                        }
                    }
                }

                ////Convert back to objects
                //var tableOut = [];
                //var dimValue;
                //for (p = 0; p < primaryDomain.length; p++) {
                //    var row = {};
                //    dimValue = primaryDomain[p];
                //    row[primary.key] = dimValue === null ? dimValue : dimValue.toString();
                //    if (secondaryDomain) {
                //        for (s = 0; s < secondaryDomain.length; s++) {
                //            dimValue = secondaryDomain[s];
                //            row[secondary.key] = dimValue === null ? dimValue : dimValue.toString();
                //            row[DEFAULT_VALUE_KEY] = rows[p][s];
                //        }
                //    } else {
                //        row[DEFAULT_VALUE_KEY] = rows[p];
                //    }
                //    tableOut.push(row);
                //}

                return rows;
            }

            function getC3Config(primary, secondary, domains) {
                //Default setup: one-axis bar chart vs. counts

                var config = {
                    data:{
                        type: 'bar',
                        x: primary.key,
                        names: {
                            value: 'Num. Messages'
                        },
                        onclick: dataClicked
                    },
                    axis:  {
                        x: {
                            type: 'category',
                            label: {
                                text: primary.name,
                                position: 'outer-center'
                            }
                        },
                        y: {
                            label: {
                                text: 'Num. Messages',
                                position: 'outer-middle'
                            }
                        }
                    },
                    legend: {
                        show: false
                    }
                };

                //If x is quantitative, use a line chart
                if (primary.is_quantitative_or_time()) {
                    config.axis.x.type = 'indexed';

                    if (secondary) {
                        config.data.type = 'spline';
                    } else {
                        config.data.type = 'area-spline';
                    }

                    //Special time-specific overrides
                    if (primary.is_time()) {
                        config.axis.x.type = 'timeseries';

                        //parsing django time values
                        config.data.xFormat = '%Y-%m-%dT%H:%M:%SZ';
                    }
                }

                if (secondary) {
                    // There are two dimensions

                    if (secondary.is_quantitative_or_time()) {
                        //We'll be swapping the y axis

                        if (primary.is_quantitative_or_time()) {
                            //Nope, draw a scatter plot

                            config.data.type = 'scatter';

                            //Use the secondary dimension as the y label
                            config.axis.y.label.text = secondary.name;

                            config.axis.x.tick = {
                                fit: false
                            };
                        } else {
                            // We are using aggregated y-values
                            config.axis.y.label.text = aggregationLabel(secondary);
                        }
                    } else {
                        // The secondary dimension is categorical, so it
                        // requires a legend to reveal the groups.

                        config.legend.show = true;
                        config.legend.position = 'inset';
                        config.legend.inset = {
                            anchor: 'top-right',
                            x: 20,
                            y: 10,
                            step: 2
                        };
                    }
                }

                return config;
            }

            this.render = function (dataTable) {
                if (!dataTable) {
                    return;
                }

                //Get the dimensions in the data table
                var dimensions = dataTable.dimensions;
                var primary = dimensions[0];
                var secondary = undefined;
                if (dimensions.length == 2) {
                    secondary = dimensions[1];
                }
                if (primary) {
                    var table = buildFullTable(primary, secondary, dataTable.table, dataTable.domains);
                    var config = getC3Config(primary, secondary, dataTable.domains);
                    config.data.rows = table;
                    config.bindto = $element.find('.sparqs-vis-render-target')[0];
                    var chart = c3.generate(config);
                }
            };
        };

        function link(scope, $element, attrs) {
            if (!scope._sparqsVis) {

                var onClicked = function () {
                    if (scope.onClicked) {
                        scope.onClicked();
                    }
                };

                var vis = scope._sparqsVis = new SparQsVis($element, attrs, onClicked);

                // Watch for changes to the datatable
                scope.$watch('dataTable.table', function (newVals, oldVals) {
                    return vis.render(scope.dataTable);
                }, false);

            } else {
                throw("What is this madness");
            }
        }

        return {
            restrict: 'E',
            replace: false,

            scope: {
                dataTable: '=visDataTable',
                onClicked: '=onClicked'
            },
            link: link,
            template: '<div class="sparqs-vis-render-target"></div>'
        }
    });
})();
