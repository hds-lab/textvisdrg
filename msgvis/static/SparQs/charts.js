(function () {
    'use strict';


    var module = angular.module('SparQs.charts', []);

    module.directive('quantHistogram', function () {

        var QuantHistogram = function ($element, attrs, onBrushed) {

            var $d3_element = d3.select($element[0]);
            var yProp = 'value';

            var xScale = d3.scale.ordinal();
            var xLinearScale = d3.scale.linear();
            var xTimeScale = d3.time.scale.utc();
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
                    if (scope.dimension && scope.dimension.current_filter()) {
                        var filter = scope.dimension.current_filter();
                        if (scope.dimension.is_time()) {
                            filter.min_time(min);
                            filter.max_time(max);
                        } else {
                            filter.min(min);
                            filter.max(max);
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
                scope.$watch('dimension.current_filter().data', function (newVal, oldVal) {
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

        var get_scale = function(dimension, width){
            var values = dimension.table.map(function(d){ return d.value; });
            var scale = d3.scale.linear();
            scale.domain([0, d3.max(values)]);
            scale.range([0, width]);
            return scale;
        };

        var render_bar = function(scope, $element, attrs, distribution){
            if ( typeof(scope.dimension) !== "undefined" ){
                var elementSize = {
                    width: $element.parent().width(),
                    height: $element.parent().height()
                };
                var scale = get_scale(scope.dimension, elementSize.width * 0.1);
                var $d3_element = d3.select($element[0]);
                var d3_select = $d3_element.selectAll('.level-div')
                    .data(distribution)
                    .classed('active', true);

                d3_select.enter()
                    .append('div')
                    .classed('level-div', true)
                    .each(function(d){
                        var self = d3.select(this);
                        self.classed('active', true);

                        var label = self.append('div')
                            .classed('level-name', true)
                            .append('label');
                        label.append('input')
                            .attr('type', 'checkbox')
                            .classed('level-show', true);
                        label.append('span').classed('level-name-text', true);

                        self.append('div').classed('level-value', true);
                        self.append('div').classed('level-bar', true);
                    });

                d3_select.exit()
                    .each(function(d){
                        var self = d3.select(this);
                        self.classed('active', false);
                        self.style('display', 'none');
                    });

                $d3_element.selectAll('.level-div.active')
                    .each(function(d){
                        var self = d3.select(this);
                        var $self = $(this);
                        self.style('display', 'block');

                        $self.find('.level-show').prop('checked', (d.show));
                        self.select('.level-show').on('change', function(d){
                            d.show = $(this).prop("checked");
                            scope.dimension.change_level(d);
                            scope.$parent.$parent.$digest();
                        });
                        self.select('.level-name-text').text(d.label || d.level);
                        self.select('.level-value').text(d.value);
                        self.select('.level-bar')
                            .style("width", (scale(d.value)) + "px")
                            .style("height", "0.7em");
                    });


            }
        };

        var reset_levels = function(scope, $element, attrs){
            if ( typeof(scope.dimension) !== "undefined" ){
                var reset_value = {'filter': false, 'exclude': true};
                var $d3_element = d3.select($element[0]);
                scope.dimension.distribution.forEach(function(d){
                    d.show = reset_value[scope.dimension.mode];
                });

                $d3_element.selectAll('.level-div')
                    .each(function(d){
                        var self = d3.select(this);
                        var $self = $(this);

                        // turn off the event handler first
                        self.select('.level-show').on('change', null);
                        $self.find('.level-show').prop('checked', reset_value[scope.dimension.mode]);
                        self.select('.level-show').on('change', function(d){
                            d.show = $(this).prop("checked");
                            scope.dimension.change_level(d);
                            scope.$parent.$parent.$digest();
                        });
                    });

                scope.dimension.group_action = false;
            }
        };

        function link(scope, $element, attrs){
            scope.$watch('dimension.group_action', function (newVals, oldVals) {
                    if (newVals) return reset_levels(scope, $element, attrs);
            }, false);
            scope.$watch('dimension.get_current_distribution().length', function (newVals, oldVals) {
                    if (newVals) {
                        // Note:
                        // For unknown reasons, the show will be reset to the original state (in filter mode is false, exclude mode is true.)
                        // So it need to be set to its real state based on filter/exclude.
                        var distribution = scope.dimension.get_current_distribution();
                        distribution.forEach(function(d){
                            d.show = scope.dimension.current_show_state(d.level);
                        });

                        return render_bar(scope, $element, attrs, distribution);
                    }
            }, false);
            scope.$watch('dimension', function (newVals, oldVals) {
                    if (newVals && newVals.is_categorical()) {
                        // Note:
                        // For unknown reasons, the show will be reset to the original state (in filter mode is false, exclude mode is true.)
                        // So it need to be set to its real state based on filter/exclude.
                        var distribution = scope.dimension.get_current_distribution();
                        distribution.forEach(function(d){
                            d.show = scope.dimension.current_show_state(d.level);
                        });

                        return render_bar(scope, $element, attrs, distribution);
                    }
            }, false);
            scope.$watch('dimension.is_not_applying_filters()', function(newVals, oldVals){
                if (newVals == true && oldVals == false){
                    console.log("reset checkboxes");
                    return reset_levels(scope, $element, attrs);
                }
            }, false);
        }

        return {
            restrict: 'E',
            replace: false,

            scope: {
                dimension: '=dimension'
            },
            link: link

        }
    });
    
    module.directive('keywordsHistogram', function () {

        var get_scale = function(dimension, width){
            var values = dimension.table.map(function(d){ return d.value; });
            var scale = d3.scale.linear();
            scale.domain([0, d3.max(values)]);
            scale.range([0, width]);
            return scale;
        };

        var render_bar = function(scope, $element, attrs, distribution){
            if ( typeof(scope.keywords) !== "undefined" ){
                var elementSize = {
                    width: $element.parent().width(),
                    height: $element.parent().height()
                };
                var scale = get_scale(scope.keywords, elementSize.width * 0.1);
                var $d3_element = d3.select($element[0]);
                var d3_select = $d3_element.selectAll('.level-div')
                    .data(distribution)
                    .classed('active', true);

                d3_select.enter()
                    .append('div')
                    .classed('level-div', true)
                    .each(function(d){
                        var self = d3.select(this);
                        self.classed('active', true);

                        var label = self.append('div')
                            .classed('level-name', true);

                        label.append('span').classed('level-name-text', true);

                        self.append('div').classed('level-value', true);
                        self.append('div').classed('level-bar', true);
                    });

                d3_select.exit()
                    .each(function(d){
                        var self = d3.select(this);
                        self.classed('active', false);
                        self.style('display', 'none');
                    });

                $d3_element.selectAll('.level-div.active')
                    .each(function(d){
                        var self = d3.select(this);
                        var $self = $(this);
                        self.style('display', 'block');

                        self.select('.level-name-text').text(d.label || d.level);
                        self.select('.level-value').text(d.value);
                        self.select('.level-bar')
                            .style("width", (scale(d.value)) + "px")
                            .style("height", "0.7em");
                    });


            }
        };

        function link(scope, $element, attrs){
            
            scope.$watch('keywords.get_current_keywords_distribution().length', function (newVals, oldVals) {
                    if (newVals) {
                        // Note:
                        // For unknown reasons, the show will be reset to the original state (in filter mode is false, exclude mode is true.)
                        // So it need to be set to its real state based on filter/exclude.
                        var distribution = scope.keywords.get_current_keywords_distribution();

                        return render_bar(scope, $element, attrs, distribution);
                    }
            }, false);
            
        }

        return {
            restrict: 'E',
            replace: false,

            scope: {
                keywords: '=keywords'
            },
            link: link

        }
    });
    

    module.directive('sparqsVis', function () {

        var SparQsVis = function (scope, $element, attrs, onClicked, groupColor) {

            var DEFAULT_VALUE_KEY = 'value';

            var self = this;
            self.group_color = groupColor;
            function dataClicked(data, element) {

                // save the info of each dimension of the clicked point value in a list
                var values = [];

                // get the primary dimension value
                var primaryValue = self.primaryValueLabel.inverse(data.x);

                // if it is a quantitative dimension, get its bucket info
                if ( self.primary.is_quantitative() ){
                    var range = {'min': primaryValue};
                    var next_value = self.primaryValueLabel.get_next_value(primaryValue);
                    if ( typeof(next_value) !== "undefined" ){
                        range.max = next_value;
                    }
                    primaryValue = range;
                }
                // so as time dimension, but use different format as time filter is using min_time and max_time
                else if ( self.primary.is_time() ){
                    var range = {'min_time': primaryValue};
                    var next_value = self.primaryValueLabel.get_next_value(primaryValue);
                    if ( typeof(next_value) !== "undefined" ){
                        range.max_time = next_value;
                    }
                    primaryValue = range;
                }
                // if not quan or time, just us exact filter
                else{
                    primaryValue = {'value': primaryValue };
                }
                values.push(primaryValue);

                // the flow below is the same as above, but it is for the secondary dimension
                var secondaryValue = undefined;
                if (self.secondaryValueLabel){
                    secondaryValue = self.secondaryValueLabel.inverse(data.id);
                    if ( self.secondary.is_quantitative() ){
                        var range = {'min': secondaryValue};
                        var next_value = self.secondaryValueLabel.get_next_value(secondaryValue);
                        if ( typeof(next_value) !== "undefined" ){
                            range.max = next_value;
                        }
                        secondaryValue = range;
                    }
                    else if ( self.secondary.is_time() ){
                        var range = {'min_time': secondaryValue};
                        var next_value = self.secondaryValueLabel.get_next_value(secondaryValue);
                        if ( typeof(next_value) !== "undefined" ){
                            range.max_time = next_value;
                        }
                        secondaryValue = range;
                    }
                    else{
                        secondaryValue = {'value': secondaryValue };
                    }
                    values.push(secondaryValue);
                }
                onClicked(values);
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

            function valueLabelMap(dimension, domain, domain_labels, is_primary) {
                var valueLabels = {};
                var valueLabelsInverse = {};
                var nextValue = {};
                for (var idx = 0 ; idx < domain.length ; idx++ ){
                    var value = domain[idx];
                    //Use the domain label or the value itself as the label
                    var label = value;

                    if (domain_labels) {
                        label = domain_labels[idx];
                    }

                    if (label === null || label === '') {
                        label = "No " + dimension.name;
                    }

                    valueLabels[value] = label.toString();
                    if (is_primary && dimension.is_categorical()){
                        valueLabelsInverse[idx] = value;
                        if (valueLabelsInverse[idx] === null)
                            valueLabelsInverse[idx] = "";

                    }else{
                        valueLabelsInverse[label.toString()] = value;
                        if (valueLabelsInverse[label.toString()] === null)
                            valueLabelsInverse[label.toString()] = "";
                    }

                    // if the dimension is quan or time, save the next bucket of the current one in a dict
                    if ( dimension.is_quantitative_or_time() ){
                        if ( idx < domain.length - 1 ){
                            nextValue[value] = domain[idx + 1];
                        }else{
                            nextValue[value] = undefined;
                        }
                    }
                }

                var mapFn = function(value) {
                    return valueLabels[value] || value.toString();
                };

                mapFn.inverse = function(label) {
                    // find the label in valueLabels.values
                    // or if it isn't there return null;
                    if ( dimension.is_time() ){
                        label = moment(label).utc().format("YYYY-MM-DDTHH:mm:ss") + "Z";
                    }
                    return "" + valueLabelsInverse[label] || "";
                };

                // if the dimension is quan or time, create the mapping function for the bucket info
                if ( dimension.is_quantitative_or_time() ){
                    mapFn.get_next_value = function(value){
                            return nextValue[value];

                    };
                }

                return mapFn;
            }

            function buildFullTable(primary, secondary, table, domains, domain_labels) {
                var rows;

                //Get functions that map from values to labels
                self.primaryValueLabel = valueLabelMap(primary, domains[primary.key], domain_labels[primary.key], true);
                self.secondaryValueLabel = undefined;
                if (secondary) {
                    self.secondaryValueLabel = valueLabelMap(secondary, domains[secondary.key], domain_labels[secondary.key], false);
                }

                if (primary.is_quantitative_or_time() && secondary && secondary.is_quantitative_or_time()) {
                    //We're doing a scatter plot which is totally different
                    // and much simpler.
                    rows = table.map(function(row) {
                        return [
                            self.primaryValueLabel(row[primary.key]),
                            self.secondaryValueLabel(row[secondary.key])
                        ];
                    });

                    rows.unshift([primary.key, secondary.key]);
                    return rows;
                }

                //Otherwise let the fun begin...

                //Use the primary dim values down the left always
                var rowHeaders = domains[primary.key].map(self.primaryValueLabel);
                var columnHeaders = [DEFAULT_VALUE_KEY];

                //Names inside the datatable rows
                var rowDataKey = primary.key;
                var columnDataKey = DEFAULT_VALUE_KEY;

                //A function for aggregating cell values (used for quant secondary dimensions)
                var columnAggregation = false;
                if (secondary){
                    if (!secondary.is_quantitative_or_time()) {
                        //Use the secondary dim values across the top
                        columnHeaders = domains[secondary.key].map(self.secondaryValueLabel);
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
                for (r = 0; r <= rowHeaders.length; r++) {
                    rows[r] = new Array(columnHeaders.length + 1);

                    if (r == 0) {
                        //Create the header row
                        rows[r][0] = primary.key;
                        for (c = 1; c <= columnHeaders.length; c++) {
                            rows[r][c] = columnHeaders[c - 1];

                            //Build the column index
                            columnIndex[columnHeaders[c - 1]] = c;
                        }
                    } else {
                        // Build the row index
                        rowIndex[rowHeaders[r - 1]] = r;

                        // Put the primary dimension value in place
                        rows[r][0] = rowHeaders[r - 1];

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
                    var r = rowIndex[self.primaryValueLabel(row[primary.key])];
                    var i;
                    if ( typeof(r) === "undefined" && primary.is_quantitative_or_time() ){
                        var rowList = Object.keys(rowIndex);
                        if ( primary.is_quantitative()) rowList.map(function(d){return +d;}).sort(function(a, b){return (a) - (b);});
                        else if ( primary.is_time()) rowList.sort();

                        for (i = 0 ; i < rowList.length ; i++ ){
                            if ( rowList[i] < row[primary.key] ){
                                r = rowIndex["" + rowList[i]];
                                break;
                            }
                        }
                    }
                    var c = 1;
                    if (columnAggregation) {
                        //We are aggregating
                        rows[r][c].push(row);
                    } else {

                        if (secondary) {
                            //we have secondary dimension values in the headers which means
                            //the column index comes from the data
                            c = columnIndex[self.secondaryValueLabel(row[secondary.key])];
                            if ( typeof(c) === "undefined" && secondary.is_quantitative_or_time() ){
                                var columnList = Object.keys(columnIndex);
                                if ( secondary.is_quantitative()) columnList.map(function(d){return +d;}).sort(function(a, b){return (a) - (b);});
                                else if ( primary.is_time()) rowList.sort();

                                for (i = 0 ; i < columnList.length ; i++ ){
                                    if ( columnList[i] < row[secondary.key] ){
                                        c = columnIndex["" + columnList[i]];
                                        break;
                                    }
                                }
                            }
                        }

                        rows[r][c] = value;

                    }
                });

                if (columnAggregation) {
                    // Finish the aggregation
                    for (r = 1; r <= rowHeaders.length; r++) {
                        for (c = 1; c <= columnHeaders.length; c++) {
                            rows[r][c] = weightedAverage(rows[r][c], DEFAULT_VALUE_KEY, secondary.key);
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

            function getC3Config(primary, secondary, domains, domain_labels) {
                //Default setup: one-axis bar chart vs. counts

                var defaultDotRadius = 3;

                var config = {
                    size: {
                        height: 400
                    },
                    point: {
                        r: defaultDotRadius
                    },
                    data:{
                        type: 'bar',
                        x: primary.key,
                        names: {
                            value: 'Num. Messages'
                        },
                        onclick: dataClicked,
                        onmouseover: function(d){
                            scope.$parent.$broadcast('add-history', 'vis:point:mouseover', {d: d});
                        },
                        xLocaltime: false
                    },
                    axis:  {
                        x: {
                            type: 'category',
                            localtime: false,
                            label: {
                                text: primary.name,
                                position: 'outer-center'
                            },
                            height: 60
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
                    },
                    tooltip: {
                        grouped: false, // Default true
                        position: function (data, width, height, element) {
                            var position = $(element).position();
                            position.top += 20;
                            position.left += 20;
                            return position;
                        }
                    },
                    subchart: {
                        show: function(primary){
                            return primary.is_quantitative_or_time();
                        }(primary),
                        size: {
                            height: 30
                        },
                        onbrush: function (domain) {
                            scope.$parent.$broadcast('add-history', 'vis:subchart:onbrush', {domain: domain});
                        }
                    },
                    color: {
                        pattern: function(){
                            if (domains.hasOwnProperty("groups")){
                                return domains.groups.map(function(d){ return self.group_color(d) });
                            }
                            else {
                                return ["#999"]
                            }
                        }()
                    },
                    grid: {
                        x: {
                            show: true
                        },
                        y: {
                            show: true
                        }
                    },


                };

                //If x is quantitative, use a line chart
                if (primary.is_quantitative_or_time()) {
                    config.axis.x.type = 'indexed';
                    config.data.type = 'area';

                    if (secondary) {
                        config.data.type = 'line';
                    }

                    //Special time-specific overrides
                    if (primary.is_time()) {
                        config.axis.x.type = 'timeseries';

                        //parsing django time values
                        config.data.xFormat = '%Y-%m-%dT%H:%M:%SZ';
                        
                        config.axis.x.tick = {
                            fit: false
                        };

                        var tooltipDateFormat = d3.time.format.utc('%c');
                        config.tooltip.format = {
                            title: function(d) {
                                return tooltipDateFormat(d);
                            }
                        };
                        
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
                              x: 10
                        };
                        config.legend.item = {
                            onmouseover: function(id){
                                self.chart.focus();
                                self.chart.defocus(id);
                                scope.$parent.$broadcast('add-history', 'vis:legend:mouseover', {id: id});
                            },
                            onclick: function(id){
                                self.chart.toggle(id);
                                scope.$parent.$broadcast('add-history', 'vis:legend:click', {id: id});
                            }
                        };

                        var num_of_levels = domains[secondary.key].length;
                        var legend_step = Math.ceil(num_of_levels / 4);
                        config.legend.inset.step = legend_step;
                        config.padding = {top: 30 * legend_step}
                        config.legend.inset.y = -config.padding.top;


                    }
                }

                return config;
            }

            self.render = function (dataTable) {
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
                    self.primary_domain = dataTable.domains;
                    var table = buildFullTable(primary, secondary, dataTable.table, dataTable.domains, dataTable.domain_labels);
                    var config = getC3Config(primary, secondary, dataTable.domains, dataTable.domain_labels);
                    config.data.rows = table;
                    config.bindto = $element.find('.sparqs-vis-render-target')[0];

                    self.chart = c3.generate(config);
                    self.primary = primary;
                    self.secondary = secondary;
                }
            };
        };

        function link(scope, $element, attrs) {
            if (!scope._sparqsVis) {

                var onClicked = function (data) {

                    if (scope.onClicked) {
                        scope.onClicked(data);
                    }
                };

                var vis = scope._sparqsVis = new SparQsVis(scope, $element, attrs, onClicked, scope.groupColors);

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
                onClicked: '=onClicked',
                groupColors: '=groupColors'
            },
            link: link,
            transclude: true,
            template: '<div class="sparqs-vis-render-target"></div>' +
            '<div ng-transclude></div>'
        }
    });
})();
