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

    //A service for loading dimension distributions.
    module.factory('SparQs.services.DimensionDistributions', [
        '$http', 'djangoUrl', 'SparQs.services.Dataset',
        function dimensionDistributionsFactory($http, djangoUrl, Dataset) {

            var Distribution = function(data) {
                angular.extend(this, data);
            };

            angular.extend(Distribution.prototype, {

            });


            var apiUrl = djangoUrl.reverse('data-tables');

            var DimensionDistributions = function () {
            };

            angular.extend(DimensionDistributions.prototype, {
                load: function (dimension) {
                    var request = {
                        dataset: Dataset.id,
                        dimensions: [dimension.key]
                    };

                    var self = this;
                    return $http.post(apiUrl, request)
                        .success(function (data) {
                            dimension.set_distribution(data.result);
                        });
                }
            });

            return new DimensionDistributions();
        }
    ]);

    //The collection of tokens.
    module.factory('SparQs.services.Tokens', [
        'token_images',
        function tokensFactory(token_images) {

            var Token = function (data) {
                angular.extend(this, data);
            };

            angular.extend(Token.prototype, {
                token_class: function () {
                    return "token-" + this.name;
                }
            });

            return [
                new Token({
                    order: 0,
                    name: 'primary',
                    image: token_images['primary']
                }),
                new Token({
                    order: 1,
                    name: 'secondary',
                    image: token_images['secondary']
                })
            ];
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
                }
            });

            return new Filtering();
        }
    ]);

    //A service for summarizing the state of the current selection,
    //including selected dimensions, filters, and focus.
    module.factory('SparQs.services.Selection', [
        '$rootScope',
        'SparQs.services.Dimensions',
        function selectionFactory($rootScope, Dimensions) {

            var test_focus = [
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
                    var with_token = Dimensions.get_with_token();

                    //Sort by the token order
                    with_token.sort(function (d1, d2) {
                        return d1.token().order - d2.token().order;
                    });
                    return with_token;
                },
                filters: function () {
                    var with_filter = Dimensions.get_with_filters();

                    //Prepare filter data
                    return with_filter.map(function (dim) {
                        return dim.serialize_filter();
                    })
                },
                focus: function () {
                    return test_focus;
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
                }

            });

            return new Selection();
        }
    ]);

    //A service for loading sample questions.
    module.factory('SparQs.services.SampleQuestions', [
        '$http', '$sce', 'djangoUrl', 'SparQs.services.Dimensions',
        function sampleQuestionsFactory($http, $sce, djangoUrl, Dimensions) {

            var apiUrl = djangoUrl.reverse('research-questions');

            var replace_dim_labels = function(text, dims){
                var chunks = [];
                var chunk_str = "";
                var chunk_mode = 0;
                var dim_list = [];
                for ( var i = 0 ; i < text.length ; i++ ){
                    if (text[i] != '\\' && text[i] != '\/'){
                        chunk_str += text[i];
                    }
                    else{
                        if ( chunk_mode == 0 ){
                            for ( var j = chunk_str.length - 1 ; j >= 0 ; j-- ){
                                if ( !isNaN(+chunk_str[j]) && 1 <= +chunk_str[j] && +chunk_str[j] <= dims.length  ){
                                    dim_list.push(dims[+chunk_str[j] - 1]);
                                }
                                else{
                                    chunk_str = chunk_str.substr(0, j + 1);
                                    chunks.push(chunk_str);
                                    chunk_str = "";
                                    break;
                                }
                            }
                            chunk_mode = 1;
                        }
                        else{
                            var str_with_dims = "<span class='question-dim ";
                            for ( var j = 0 ; j < dim_list.length ; j++ ){
                                if ( j > 0 ) str_with_dims += " ";
                                try {
                                    str_with_dims += dim_list[j].key;
                                }
                                catch(err) {
                                    debugger;
                                }

                            }
                            str_with_dims += "'>"
                            str_with_dims += chunk_str;
                            str_with_dims += "<\/span>";
                            chunks.push(str_with_dims);
                            chunk_str = "";
                            dim_list = [];
                            chunk_mode = 0;
                        }

                    }
                }
                if (chunk_str.length > 0)
                    chunks.push(chunk_str);
                return chunks.join('');
            };

            //A model class for sample questions
            var Question = function (data) {
                angular.extend(this, data);

                //Hook up the dimensions to the question
                this.dimensions = this.dimensions.map(function (dimkey) {
                    return Dimensions.get_by_key(dimkey);
                });

                this.text = $sce.trustAsHtml(replace_dim_labels(this.text, this.dimensions));
            };

            var SampleQuestions = function () {
                this.list = [];
            };

            angular.extend(SampleQuestions.prototype, {
                load: function (dimensions) {
                    var dimension_keys = dimensions.map(function (d) {
                        return d.key
                    });

                    var request = {
                        dimensions: dimension_keys
                    };

                    var self = this;
                    $http.post(apiUrl, request)
                        .success(function (data) {
                            self.list = data.questions.map(function (qdata) {
                                return new Question(qdata);
                            });
                        });

                }
            });

            return new SampleQuestions();
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
                load: function (dataset, filters, focus) {

                    var request = {
                        dataset: dataset,
                        filters: filters,
                        focus: focus
                    };

                    var self = this;
                    $http.post(apiUrl, request)
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
                this.rows = [];
            };

            angular.extend(DataTables.prototype, {
                load: function (dataset, dimensions, filters) {
                    if (!dimensions.length) {
                        return;
                    }

                    var dimension_keys = dimensions.map(function (d) {
                        return d.key
                    });

                    var request = {
                        dataset: dataset,
                        filters: filters,
                        dimensions: dimension_keys
                    };

                    var self = this;
                    $http.post(apiUrl, request)
                        .success(function (data) {
                            self.rows = data.result;
                        });
                }
            });

            return new DataTables();
        }
    ]);

})();
