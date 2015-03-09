(function () {
    'use strict';


    var module = angular.module('SparQs.controllers', [
        'SparQs.services'
    ]);

    module.config(function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    });

    var DimensionController = function ($scope, Dimensions, Filtering) {

        //Hierarchy of dimensions
        $scope.dimension_groups = [
            {
                "group_name": "Time",
                "dimensions": [
                    Dimensions.get_by_key('time'),
                    Dimensions.get_by_key('timezone')
                ]
            },
            {
                "group_name": "Contents",
                "dimensions": [
                    Dimensions.get_by_key('topics'),
                    Dimensions.get_by_key('words'),
                    Dimensions.get_by_key('hashtags'),
                    //Dimensions.get_by_key('contains_hashtag'),
                    Dimensions.get_by_key('urls'),
                    //Dimensions.get_by_key('contains_url'),
                    Dimensions.get_by_key('contains_media')
                ]
            },
            {
                "group_name": "Meta",
                "dimensions": [
                    Dimensions.get_by_key('language'),
                    Dimensions.get_by_key('sentiment')
                ]
            },
            {
                "group_name": "Interaction",
                "dimensions": [
                    Dimensions.get_by_key('type'),
                    Dimensions.get_by_key('replies'),
                    Dimensions.get_by_key('shares'),
                    Dimensions.get_by_key('mentions'),
                    //Dimensions.get_by_key('contains_mention')
                ]
            },
            {
                "group_name": "Author",
                "dimensions": [
                    Dimensions.get_by_key('sender_name'),
                    Dimensions.get_by_key('sender_message_count'),
                    Dimensions.get_by_key('sender_reply_count'),
                    Dimensions.get_by_key('sender_mention_count'),
                    Dimensions.get_by_key('sender_share_count'),
                    Dimensions.get_by_key('sender_friend_count'),
                    Dimensions.get_by_key('sender_follower_count')
                ]
            }
        ];

        $scope.openFilter = function(dimension, $event) {
            var offset;
            if ($event) {
                var $el = $($event.target).parents('.dimension');
                if ($el) {
                    offset = $el.offset();

                    var filterHeight = Filtering.filter_height_for(dimension) + 20; //for buffer
                    var windowHeight = $(window).height();

                    //no hanging out the bottom
                    offset.top = Math.min(windowHeight - filterHeight, offset.top);

                    //no sticking out the top either
                    offset.top = Math.max(0, offset.top);
                }
            }

            Filtering.toggle(dimension, offset);
        };

        $scope.dropped = undefined;
        $scope.onDimensionDrop = function() {
            //Unselect the dimension if it is on a zone
            if ($scope.dropped && $scope.dropped.zone &&
                    //And make sure the dropzone it was on has agreed to part with it
                $scope.dropped.zone.dimension != $scope.dropped) {

                //Turn off the zone of this dimension
                $scope.dropped.zone = undefined;
            }
            $scope.dropped = undefined; // remove the dropped dimension
        };
    };

    DimensionController.$inject = [
        '$scope',
        'SparQs.services.Dimensions',
        'SparQs.services.Filtering'];
    module.controller('SparQs.controllers.DimensionController', DimensionController);

    var ExampleMessageController = function ($scope, ExampleMessages, Selection, Dataset) {

        $scope.messages = ExampleMessages;

        $scope.get_example_messages = function () {
            var filters = Selection.filters();
            var exclude = Selection.exclude();
            var focus = Selection.focus();
            ExampleMessages.load(Dataset.id, filters, focus, exclude);
        };

        Selection.changed('filters,focus', $scope, $scope.get_example_messages);

        $scope.get_example_messages();

    };
    ExampleMessageController.$inject = [
        '$scope',
        'SparQs.services.ExampleMessages',
        'SparQs.services.Selection',
        'SparQs.services.Dataset'
    ];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SampleQuestionController = function ($scope, $timeout, Selection, SampleQuestions) {

        $scope.questions = SampleQuestions;
        $scope.selection = Selection;

        $scope.get_sample_questions = function () {
            SampleQuestions.load(Selection.dimensions());

        };

        $scope.$watch('questions.list', function(){
            //When the question list changes, we are going to manually (jQuery)
            //update the token classes so that they end up the right color.
            //.question-tag are the dimension tags inside the research questions.
            //The .tag-primary and .tag-secondary tags indicate which .question-tag
            //should be colored which way.
            //The timeout ensures that this runs *after* the new questions have been rendered.
            $timeout(function() {
                $('.question-tag').removeClass('tag-primary tag-secondary');
                var dims = $scope.selection.dimensions();
                dims.forEach(function(dim) {
                    //we already know these dimensions are in zones
                    $('.question-tag.' + dim.key).addClass('tag-' + dim.zone.name);
                });
            }, 0);

        });

        $scope.get_sample_questions();

        Selection.changed('dimensions', $scope, $scope.get_sample_questions);
    };

    SampleQuestionController.$inject = [
        '$scope',
        '$timeout',
        'SparQs.services.Selection',
        'SparQs.services.SampleQuestions'
    ];
    module.controller('SparQs.controllers.SampleQuestionController', SampleQuestionController);

    var VisualizationController = function ($scope, Selection, DataTables, Dataset) {

        $scope.datatable = DataTables;
        $scope.selection = Selection;

        $scope.get_data_table = function () {
            var dimensions = Selection.dimensions();
            var filters = Selection.filters();
            var exclude = Selection.exclude();
            DataTables.load(Dataset.id, dimensions, filters, exclude);
        };

        $scope.get_data_table();

        Selection.changed('dimensions,filters', $scope, $scope.get_data_table);

        $scope.onVisClicked = function(data) {
            Selection.set_focus(data);
        };

    };

    VisualizationController.$inject = [
        '$scope',
        'SparQs.services.Selection',
        'SparQs.services.DataTables',
        'SparQs.services.Dataset'
    ];
    module.controller('SparQs.controllers.VisualizationController', VisualizationController);

    //Extends VisualizationController scope
    var DropzonesController = function($scope, Dimensions, Dropzones, Selection) {
        $scope.dropzones = Dropzones;

        var dropzoneChanged = function(zone, new_dimension, old_dimension) {
            if (new_dimension && new_dimension.zone != zone) {

                if (zone.name == 'secondary' && new_dimension.key == 'time') {
                    //FAIL, remove it
                    new_dimension.zone = undefined;
                    zone.dimension = undefined;
                    return;
                }

                //If the old dimension still thinks it is here, unset it
                if (old_dimension && old_dimension.zone == zone) {
                    old_dimension.zone = undefined;
                }

                //If the dimension's current zone thinks it still owns this dimension
                //then make sure to remove it
                if (new_dimension.zone && new_dimension.zone.dimension == new_dimension) {
                    new_dimension.zone.dimension = undefined;
                }

                new_dimension.zone = zone;
            }
        };

        $scope.$watch('dropzones.primary.dimension', function(newDim, oldDim) {
            dropzoneChanged(Dropzones.primary, newDim, oldDim);
        });
        $scope.$watch('dropzones.secondary.dimension', function(newDim, oldDim) {
            dropzoneChanged(Dropzones.secondary, newDim, oldDim);
        });

        $scope.onDimensionDrop = function() {
            Selection.changed('dimensions');
        };
    };

    DropzonesController.$inject = [
        '$scope',
        'SparQs.services.Dimensions',
        'SparQs.services.Dropzones',
        'SparQs.services.Selection'
    ];
    module.controller('SparQs.controllers.DropzonesController', DropzonesController);


    //Extends DimensionsController
    var FilterController = function ($scope, Filtering, Selection) {

        $scope.filtering = Filtering;

        $scope.closeFilter = function() {
            Filtering.toggle();
        };

        $scope.saveFilter = function () {
            if (Filtering.dimension.is_dirty()) {
                Selection.changed('filters');
                Filtering.dimension.current_filter().saved();
            }
        };

        $scope.resetFilter = function () {
            if (!Filtering.dimension.is_not_applying_filters()) {
                if (Filtering.dimension.is_categorical()){
                    Filtering.dimension.search_key = "";
                    Filtering.dimension.search_key_tmp = "";
                    Filtering.dimension.switch_mode('exclude');
                }else{
                    Filtering.dimension.current_filter().reset();
                }
                Selection.changed('filters');
                Filtering.dimension.current_filter().saved();
            }
        };

        $scope.onQuantitativeBrushed = function(min, max) {
            $scope.$digest();
        };

        $scope.loadMore = function() {
            Filtering.dimension.load_categorical_distribution();
        };

        $scope.search = function() {
            Filtering.dimension.search_key = Filtering.dimension.search_key_tmp;
            Filtering.dimension.load_categorical_distribution();
        };
        $scope.set_back_cur_search = function() {
            if ( Filtering.dimension.search_key_tmp !== Filtering.dimension.search_key )
                Filtering.dimension.search_key_tmp = Filtering.dimension.search_key;

        };



    };

    FilterController.$inject = [
        '$scope',
        'SparQs.services.Filtering',
        'SparQs.services.Selection'
    ];
    module.controller('SparQs.controllers.FilterController', FilterController);

    module.directive('datetimeFormat', function() {
      return {
        require: 'ngModel',
        link: function(scope, element, attrs, ngModelController) {
          ngModelController.$parsers.push(function(data) {
            //convert data from view format to model format
            data = moment(data, "YYYY-MM-DD HH:mm:ss");
            if (data.isValid()) return data.utc().toDate();
            else return undefined;
          });

          ngModelController.$formatters.push(function(data) {
            //convert data from model format to view format
              if (data !== undefined) return moment(data).utc().format("YYYY-MM-DD HH:mm:ss"); //converted
              return data;
          });
        }
      }
    });

    module.directive('whenScrolled', function() {
        return function(scope, element, attr) {
            var raw = element[0];

            var checkBounds = function(evt) {
                if (raw.scrollTop + $(raw).height() == raw.scrollHeight) {
                    scope.$apply(attr.whenScrolled);
                }

            };
            element.bind('scroll load', checkBounds);
        };
    });

    module.directive('ngEnter', function () {
        return function (scope, element, attrs) {
            element.bind("keydown keypress", function (event) {
                if(event.which === 13) {
                    scope.$apply(function (){
                        scope.$eval(attrs.ngEnter);
                    });

                    event.preventDefault();
                }
            });
        };
    });

})();
