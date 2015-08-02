(function () {
    'use strict';

    var module = angular.module('SparQs.services', [
        'ng.django.urls',
        'SparQs.bootstrap',
        'ngSanitize'
    ]);

    module.factory('SparQs.services.Dataset', [
        'SparQs.bootstrap.dataset',
        function(datasetId) {
            return {
                id: datasetId
            };
        }
    ]);

    //The dimension drop zones
    module.factory('SparQs.services.Dropzones', [
        function dropzonesFactory() {

            var Dropzone = function (data) {
                angular.extend(this, data);

                this.dimension = undefined;
            };

            angular.extend(Dropzone.prototype, {
                zone_class: function () {
                    return "dropzone-" + this.name;
                },
                accept_class: function() {
                    return '.' + this.name + "-enabled";
                }
            });

            var primary = new Dropzone({
                order: 0,
                name: 'primary',
                text: "Drop a dimension here"
            });

            var secondary = new Dropzone({
                order: 1,
                name: 'secondary',
                text: "Drop another dimension here"
            });

            return {
                zones: [
                    primary,
                    secondary
                ],
                primary: primary,
                secondary: secondary
            };
        }
    ]);

    //A service for managing the filter popups
    module.factory('SparQs.services.Filtering', [
        '$rootScope',
        'SparQs.services.Dimensions',
        function filteringFactory($rootScope, Dimensions) {
            var Filtering = function () {
                this.dimension = undefined;
            };

            angular.extend(Filtering.prototype, {
                _start: function(dimension, offset) {
                    dimension.set_filtering(true);
                    this.dimension = dimension;
                    this.offset = offset;
                },
                _stop: function() {
                    if (this.dimension) {
                        this.dimension.set_filtering(false);
                    }
                },
                toggle: function (dimension, offset) {
                    if (dimension) {
                        if (dimension.filtering) {
                            this._stop();
                        } else {
                            if (this.dimension && this.dimension.filtering) {
                                this._stop();
                            }

                            this._start(dimension, offset);
                        }
                    } else {
                        this._stop();
                    }
                },
                filter_height_for: function(dimension) {
                    if (dimension.is_quantitative_or_time()) {
                        return 220;
                    } else if (dimension.is_categorical()) {
                        return 381;
                    }
                    return 0;
                },
                get_filtered: function () {
                    return Dimensions.list.filter(function (dim) {
                        return !dim.filter_type['filter'].is_empty();
                    });
                },
                get_exclude: function () {
                    return Dimensions.list.filter(function (dim) {
                        return !dim.filter_type['exclude'].is_empty();
                    });
                }
            });

            return new Filtering();
        }
    ]);

    //A service for summarizing the state of the current selection,
    //including selected dimensions, filters, and focus.
    module.factory('SparQs.services.Selection', [
        '$rootScope',
        'SparQs.services.Filtering',
        'SparQs.services.Dropzones',
        function selectionFactory($rootScope, Filtering, Dropzones) {

            var current_focus = [
                //{
                //    "dimension": "time",
                //    "value": "2015-02-02T01:19:09Z"
                //}
            ];


            var Selection = function () {

            };

            var changedEvent = 'SparQs.services.Selection.changed';

            angular.extend(Selection.prototype, {
                dimensions: function () {
                    return Dropzones.zones.map(function(z) {
                        return z.dimension;
                    }).filter(function(dim) {
                        return dim;
                    });
                },
                filters: function () {
                    var with_filter = Filtering.get_filtered();

                    //Prepare filter data
                    return with_filter.map(function (dim) {
                        return dim.serialize_filter('filter');
                    })
                },
                exclude: function () {
                    var with_exclude = Filtering.get_exclude();

                    //Prepare filter data
                    return with_exclude.map(function (dim) {
                        return dim.serialize_filter('exclude');
                    })
                },
                focus: function () {
                    return current_focus;
                },
                changed: function (eventType, scope, callback) {
                    // Register for one or more events:
                    //   Selection.changed('dimensions,filters', $scope, $scope.callback_fn);
                    // Trigger one or more events:
                    //   Selection.changed('dimensions,focus');

                    eventType.split(',').forEach(function (eventName) {
                        eventName = changedEvent + '[' + eventName + ']';
                        if (!scope) {
                            //Trigger the event
                            $rootScope.$emit(eventName);
                        } else {
                            //Register new listener
                            var unbind = $rootScope.$on(eventName, callback);
                            scope.$on('$destroy', unbind);
                        }
                    });
                },
                set_focus: function(focus_info){
                    var dimensions = this.dimensions();
                    current_focus = dimensions.map(function (d, i) {
                        var dim = focus_info[i];
                        dim.dimension = dimensions[i].key;
                        return dim;
                    });
                    this.changed('focus');
                }

            });

            return new Selection();
        }
    ]);

    //A service for loading example messages.
    module.factory('SparQs.services.ExampleMessages', [
        '$http', 'djangoUrl',
        function sampleQuestionsFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('example-messages');

            //A model class for messages
            var Message = function (data) {
                angular.extend(this, data);
            };

            var ExampleMessages = function () {
                this.list = [];
            };

            angular.extend(ExampleMessages.prototype, {
                load: function (dataset, filters, focus, exclude) {

                    var request = {
                        dataset: dataset,
                        filters: filters,
                        exclude: exclude,
                        focus: focus
                    };

                    var self = this;
                    return $http.post(apiUrl, request)
                        .success(function (data) {
                            self.list = data.messages.map(function (msgdata) {
                                return new Message(msgdata);
                            });
                        });
                }
            });

            return new ExampleMessages();
        }
    ]);

    //A service for loading datatables.
    module.factory('SparQs.services.DataTables', [
        '$http', 'djangoUrl',
        function dataTablesFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('data-table');

            var DataTables = function () {
                this.dimensions = [];
                this.domains = {};
                this.domain_labels = {};
                this.table = [];
            };

            angular.extend(DataTables.prototype, {
                load: function (dataset, dimensions, filters, exclude) {
                    if (!dimensions.length) {
                        return;
                    }

                    var dimension_keys = dimensions.map(function (d) {
                        return d.key
                    });

                    var request = {
                        dataset: dataset,
                        filters: filters,
                        exclude: exclude,
                        dimensions: dimension_keys,
                        mode: "omit_others"
                    };

                    var self = this;
                    return $http.post(apiUrl, request)
                        .success(function (data) {
                            self.dimensions = dimensions;
                            self.table = data.result.table;
                            self.domains = data.result.domains;
                            self.domain_labels = data.result.domain_labels;
                        });
                }
            });

            return new DataTables();
        }
    ]);

})();
