(function () {
    'use strict';


    var module = angular.module('SparQs.controllers', [
        'SparQs.services',
        'angularSpinner'
    ]);

    module.config(['$interpolateProvider', function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    }]);


    module.config(['usSpinnerConfigProvider', function (usSpinnerConfigProvider) {
        usSpinnerConfigProvider.setDefaults({
            color: '#eee'
        });
    }]);

    var DimensionController = function ($scope, Dimensions, Filtering, Selection) {

        $scope.draggableOptions = {
            revert: 'invalid',
            helper: 'clone',
            appendTo: '#content',
            containment: '#content',
            scroll: false,
            cursorAt: {left: 20, top: 10}
        };

        $scope.dimension_groups = Dimensions.get_groups();

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

                Selection.changed('dimensions');
            }
            $scope.dropped = undefined; // remove the dropped dimension
        };
    };

    DimensionController.$inject = [
        '$scope',
        'SparQs.services.Dimensions',
        'SparQs.services.Filtering',
        'SparQs.services.Selection'];
    module.controller('SparQs.controllers.DimensionController', DimensionController);

    var ExampleMessageController = function ($scope, ExampleMessages, Selection, Dataset, usSpinnerService) {

        $scope.messages = ExampleMessages;

        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10
        };

        $scope.get_example_messages = function () {
            var filters = Selection.filters();
            var exclude = Selection.exclude();
            var focus = Selection.focus();
            var request = ExampleMessages.load(Dataset.id, filters, focus, exclude);
            if (request) {
                usSpinnerService.spin('examples-spinner');

                request.then(function() {
                    usSpinnerService.stop('examples-spinner');
                });
            }
        };

        Selection.changed('filters,focus', $scope, $scope.get_example_messages);

        $scope.get_example_messages();

    };
    ExampleMessageController.$inject = [
        '$scope',
        'SparQs.services.ExampleMessages',
        'SparQs.services.Selection',
        'SparQs.services.Dataset',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SampleQuestionController = function ($scope, $timeout, Selection, SampleQuestions, usSpinnerService) {

        $scope.questions = SampleQuestions;
        $scope.selection = Selection;

        $scope.spinnerOptions = {
            radius: 15,
            width: 4,
            length: 8
        };

        $scope.get_sample_questions = function () {
            var request = SampleQuestions.load(Selection.dimensions());

            if (request) {
                usSpinnerService.spin('questions-spinner');
                request.then(function() {
                    usSpinnerService.stop('questions-spinner');
                })

            }
        };

        $scope.get_authors = function(authors){
            if (!authors) return "";

            var author_list = authors.split("\n");
            var last_names = [];
            author_list.forEach(function(d){
                var l = d.split(" ");
                last_names.push(l.pop());
            });
            if (last_names.length >= 3)
                return last_names[0] + " et al.";
            return last_names.join(" & ");
        };

        $scope.get_full_source_info = function(source){
            if (!source) return "";

            var template = "<div class='source title'><strong>" + source.title + "</strong> (" + source.year + ")</div>";
            template += "<span class='source authors'>" + (source.authors.split('\n').join(", ")) + ".</span> ";
            if ( source.venue )
                template += "<span class='source venue'>Published in <em>" + source.venue + "</em></span>";
            return template;
        };

        $scope.$watch('questions.current', function(){
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
        'SparQs.services.SampleQuestions',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.SampleQuestionController', SampleQuestionController);

    var VisualizationController = function ($scope, Selection, DataTables, Dataset, usSpinnerService) {

        $scope.datatable = DataTables;
        $scope.selection = Selection;

        $scope.get_data_table = function () {
            var dimensions = Selection.dimensions();
            var filters = Selection.filters();
            var exclude = Selection.exclude();

            var request = DataTables.load(Dataset.id, dimensions, filters, exclude);

            if (request) {
                usSpinnerService.spin('vis-spinner');

                request.then(function () {
                    usSpinnerService.stop('vis-spinner');
                });
            }
        };

        $scope.get_data_table();

        Selection.changed('dimensions,filters', $scope, $scope.get_data_table);

        $scope.onVisClicked = function(data) {
            Selection.set_focus(data);
        };

        $scope.spinnerOptions = {
            radius: 20,
            width:6,
            length: 10
        };


    };

    VisualizationController.$inject = [
        '$scope',
        'SparQs.services.Selection',
        'SparQs.services.DataTables',
        'SparQs.services.Dataset',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.VisualizationController', VisualizationController);

    //Extends VisualizationController scope
    var DropzonesController = function($scope, Dimensions, Dropzones, Selection) {
        $scope.dropzones = Dropzones;

        $scope.draggableOptions = {
            containment: '#content',
            scroll: false, 
            revert: 'invalid',
            cursorAt: {left: 20, top: 10}
        };
        
        $scope.droppableOptions = function (zone) {
            return {
                tolerance: 'touch', 
                hoverClass: 'ui-droppable-hover',
                accept: zone.accept_class()
            };
        };
        
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
    var FilterController = function ($scope, Filtering, Selection, usSpinnerService) {

        $scope.filtering = Filtering;

        $scope.spinnerOptions = {
            radius: 15,
            width: 4,
            length: 8
        };

        $scope.$watch('filtering.dimension.request', function(newVal, oldVal) {
            if (Filtering.dimension && Filtering.dimension.request) {
                usSpinnerService.spin('filter-spinner');

                Filtering.dimension.request.then(function() {
                    usSpinnerService.stop('filter-spinner');
                })
            }
        });

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
        'SparQs.services.Selection',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.FilterController', FilterController);

    module.directive('datetimeFormat', function() {
      return {
        require: 'ngModel',
        link: function(scope, element, attrs, ngModelController) {
          ngModelController.$parsers.push(function(data) {
            //convert data from view format to model format
            data = moment.utc(data, "YYYY-MM-DD HH:mm:ss");
            if (data.isValid()) return data.toDate();
            else return undefined;
          });

          ngModelController.$formatters.push(function(data) {
            //convert data from model format to view format
              if (data !== undefined) return moment.utc(data).format("YYYY-MM-DD HH:mm:ss"); //converted
              return data;
          });
        }
      }
    });

    module.directive('whenScrolled', function() {
        return function(scope, element, attr) {
            var raw = element[0];

            var checkBounds = function(evt) {
                if (Math.abs(raw.scrollTop + $(raw).height() - raw.scrollHeight) < 10) {
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
