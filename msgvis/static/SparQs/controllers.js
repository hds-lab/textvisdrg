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
        $scope.changeDimension = function(dimension){
                console.log(dimension);
                Selection.change_dimension(dimension);
                Selection.changed('dimensions');
        };
        $scope.is_current_dimension = function(dimension){
            return Selection.get_current_dimension() == dimension;
        };
        $scope.get_class = function(dimension){
            if ($scope.is_current_dimension(dimension))
                return "active";
            else
                return "";
        }
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
            length: 10,
            color: "#000000"
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

    var SearchController = function ($scope, KeywordMessages, Group, TabMode, Dataset, usSpinnerService) {

        $scope.Group = Group;

        $scope.messages = KeywordMessages;
        $scope.keyword = "";

        $scope.is_mode = function(check_mode){
            return TabMode.mode == check_mode;
        };
        $scope.change_mode = function(new_mode){
            TabMode.mode = new_mode;
        };
        $scope.tab_class = function(check_mode){
            return ($scope.is_mode(check_mode)) ? "active" : "";
        };


        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };

        $scope.search = function () {
            var keyword = $scope.keyword;
            var request = KeywordMessages.load(Dataset.id, keyword);
            if (request) {
                usSpinnerService.spin('search-spinner');

                request.then(function() {
                    usSpinnerService.stop('search-spinner');
                });
            }
        };

        $scope.reset_search = function(){
            $scope.keyword = "";
        }


    };
    SearchController.$inject = [
        '$scope',
        'SparQs.services.KeywordMessages',
        'SparQs.services.Group',
        'SparQs.services.TabMode',
        'SparQs.services.Dataset',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.SearchController', SearchController);
    
    var GroupController = function ($scope, $timeout, Group, TabMode, Dataset, usSpinnerService) {

        $scope.Group = Group;
        $scope.Group.load(Dataset.id);

        $scope.group = {
            name: "",
            inclusive_keywords: "",
            exclusive_keywords: ""
        };


        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };

        $scope.show_messages = function () {
            var name = $scope.group.name;
            var inclusive_keywords = $scope.group.inclusive_keywords;
            var exclusive_keywords = $scope.group.exclusive_keywords;

            if (name == "" || name == undefined){
                name = "Group ";
                name += (inclusive_keywords != "") ? "including " + inclusive_keywords + " " : "";
                name += (exclusive_keywords != "") ? "excluding " + exclusive_keywords + " " : "";
                $scope.group.name = name;
            }

            inclusive_keywords = ((inclusive_keywords != "")) ? inclusive_keywords.split(" ") : [];
            exclusive_keywords = ((exclusive_keywords != "")) ? exclusive_keywords.split(" ") : [];


            var request = Group.show_messages(Dataset.id, name, inclusive_keywords, exclusive_keywords);
            if (request) {
                usSpinnerService.spin('search-spinner');

                request.then(function() {
                    usSpinnerService.stop('search-spinner');
                    TabMode.mode = "group_messages";


                });
            }
        };

        $scope.create_new_group = function(){
            $scope.group = {
                name: "",
                inclusive_keywords: "",
                exclusive_keywords: ""
            };

            Group.create_new_group();
        };

        $scope.switch_group = function(group){
            $scope.group = Group.switch_group(group);
            $scope.show_messages();

        };

        $scope.group_class = function(group){
            return (group.id == Group.current_group_id) ? "active" : "";
        };




    };
    GroupController.$inject = [
        '$scope',
        '$timeout',
        'SparQs.services.Group',
        'SparQs.services.TabMode',
        'SparQs.services.Dataset',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.GroupController', GroupController);

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
            length: 10,
            color: "#000000"
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

    module.animation('.slide', [function() {
        return {
        // make note that other events (like addClass/removeClass)
        // have different function input parameters
        enter: function(element, doneFn) {
          jQuery(element).fadeIn(1000, doneFn);

          // remember to call doneFn so that angular
          // knows that the animation has concluded
        },

        move: function(element, doneFn) {
          jQuery(element).fadeIn(1000, doneFn);
        },

        leave: function(element, doneFn) {
          jQuery(element).fadeOut(1000, doneFn);
        }
        }
    }]);

})();
