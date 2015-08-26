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
            var groups = Selection.groups();
            var request = ExampleMessages.load(Dataset.id, filters, focus, exclude, groups);
            if (request) {
                usSpinnerService.spin('examples-spinner');

                request.then(function() {

                    usSpinnerService.stop('examples-spinner');
                });
            }
        };
        $scope.refresh = function () {
            var request = ExampleMessages.refresh();
            if (request) {
                usSpinnerService.spin('examples-spinner');

                request.then(function() {

                    usSpinnerService.stop('examples-spinner');
                });
            }
        };
        $scope.convert_request_to_readable_str = function() {
            var request = ExampleMessages.prev_request;
            var str = "";
            if (request){
                request.focus.forEach(function(d){
                    if (d.dimension != "groups"){
                        str += d.dimension;
                        if (d.hasOwnProperty('value'))
                            str += '=' + d.value;
                        else if (d.hasOwnProperty('min_time') )
                            str += '=' + d.min_time;
                        else if (d.hasOwnProperty('min') )
                            str += '=' + d.min;
                        str += " ";
                    }
                });
                if ( request.hasOwnProperty('groups') && request.groups ){
                    str += "in Group";
                    request.groups.forEach(function(d){
                        str += " " + d;
                    });
                }
            }
            if (str != ""){
                str = "Current Source: " + str;
            }
            return str;
        };

        Selection.changed('filters,focus,groups', $scope, $scope.get_example_messages);

        //$scope.get_example_messages();


    };
    ExampleMessageController.$inject = [
        '$scope',
        'SparQs.services.ExampleMessages',
        'SparQs.services.Selection',
        'SparQs.services.Dataset',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SearchAndGroupController = function ($scope, KeywordMessages, Group, Dataset, Selection, usSpinnerService) {

        $scope.Group = Group;
        Group.load(Dataset.id);

        $scope.group_name = "";
        $scope.messages = KeywordMessages;
        $scope.inclusive_keywords = "";
        $scope.exclusive_keywords = "";

        $scope.edit_mode = false;
        $scope.new_param = {};
        $scope.new_param.group_name = "";
        $scope.new_param.inclusive_keywords = "";
        $scope.new_param.exclusive_keywords = "";


        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };

        $scope.search = function ($event) {
            if ($event){
                $event.stopPropagation();
            }
            var inclusive_keywords = ($scope.edit_mode) ? $scope.new_param.inclusive_keywords : $scope.inclusive_keywords;
            var exclusive_keywords = ($scope.edit_mode) ? $scope.new_param.exclusive_keywords : $scope.exclusive_keywords;
            var request = KeywordMessages.load(Dataset.id, 1, inclusive_keywords, exclusive_keywords);
            if (request) {
                usSpinnerService.spin('search-spinner');

                request.then(function() {
                    usSpinnerService.stop('search-spinner');
                });
            }
        };


        $scope.update_page = function (page) {

            var request = KeywordMessages.load(Dataset.id, page);
            if (request) {
                usSpinnerService.spin('search-spinner');

                request.then(function() {
                    usSpinnerService.stop('search-spinner');
                });
            }
        };

        $scope.reset_search = function(){
            $scope.messages = KeywordMessages;
            $scope.group_name = "";
            $scope.inclusive_keywords = "";
            $scope.exclusive_keywords = "";
            $scope.messages.count = -1;
        };

        $scope.save = function ($event) {
            if ($event){
                $event.stopPropagation();
            }
            var name = ($scope.edit_mode) ? $scope.new_param.group_name : $scope.group_name;
            var inclusive_keywords = ($scope.edit_mode) ? $scope.new_param.inclusive_keywords : $scope.inclusive_keywords;
            var exclusive_keywords = ($scope.edit_mode) ? $scope.new_param.exclusive_keywords : $scope.exclusive_keywords;

            if (name == "" || name == undefined){
                name = "";
                name += (inclusive_keywords != "") ? inclusive_keywords + " " : "";
                name += (exclusive_keywords != "") ? "excluding " + exclusive_keywords + " " : "";
            }

            inclusive_keywords = ((inclusive_keywords != "")) ? inclusive_keywords.split(" ") : [];
            exclusive_keywords = ((exclusive_keywords != "")) ? exclusive_keywords.split(" ") : [];


            var request = Group.save(Dataset.id, name, inclusive_keywords, exclusive_keywords);
            if (request) {
                if ($scope.edit_mode){

                    usSpinnerService.spin('update-spinner');

                    request.then(function() {
                        usSpinnerService.stop('update-spinner');
                        $scope.finish_edit();
                        if ( !$scope.is_empty() ) $scope.search();
                    });
                }
                else{
                    usSpinnerService.spin('save-spinner');

                    request.then(function() {
                        usSpinnerService.stop('save-spinner');
                        $scope.reset_search();
                    });
                }
            }
            else{
                $scope.edit_mode = false;
            }
        };



        $scope.is_empty = function(){
            return (!$scope.edit_mode && $scope.messages.count == -1 )
        };
        $scope.is_being_editing = function(group){
            return $scope.edit_mode && Group.current_group_id == group.id;
        };
        $scope.show_mask = function(group){
            return $scope.edit_mode && !$scope.is_being_editing(group);
        };
        $scope.editing_class = function(group){
            return ($scope.is_being_editing(group)) ? "edit-class" : "";
        };

        $scope.edit_group = function($event, group){
            $event.stopPropagation();
            $scope.new_param.group_name = group.name;
            $scope.new_param.inclusive_keywords = group.inclusive_keywords.join(' ');
            $scope.new_param.exclusive_keywords = group.exclusive_keywords.join(' ');
            Group.current_group_id = group.id;
            $scope.edit_mode = true;
            $scope.search();

        };
        $scope.finish_edit = function($event){
            if ($event){
                $event.stopPropagation();
            }
            Group.current_group_id = -1;
            $scope.edit_mode = false;
            $scope.messages.count = -1;
        };


        $scope.delete_group = function($event, group){
            $event.stopPropagation();
            var msg = "Are you sure you want to delete group #" + group.id + "?";
            if ( window.confirm(msg) ){
                Group.delete_group(group);
            }
        };


        $scope.toggle_group = function($event, group){
            $event.stopPropagation();
            group.selected = !group.selected;
            Group.select_group(group);
            Selection.changed('groups');

        };

        $scope.group_class = function(group){
            return ($scope.is_being_editing(group)) ? "edit-class" : ((group.selected) ? "active" : "");
        };

    };
    SearchAndGroupController.$inject = [
        '$scope',
        'SparQs.services.KeywordMessages',
        'SparQs.services.Group',
        'SparQs.services.Dataset',
        'SparQs.services.Selection',
        'usSpinnerService'
    ];
    module.controller('SparQs.controllers.SearchAndGroupController', SearchAndGroupController);


    var VisualizationController = function ($scope, Selection, DataTables, Dataset, usSpinnerService) {

        $scope.datatable = DataTables;
        $scope.selection = Selection;

        $scope.get_data_table = function () {
            var dimensions = Selection.dimensions();
            var filters = Selection.filters();
            var exclude = Selection.exclude();
            var groups = Selection.groups();

            var request = DataTables.load(Dataset.id, dimensions, filters, exclude, groups);

            if (request) {
                usSpinnerService.spin('vis-spinner');

                request.then(function () {
                    usSpinnerService.stop('vis-spinner');
                });
            }
        };

        $scope.get_data_table();

        Selection.changed('dimensions,filters,groups', $scope, $scope.get_data_table);

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
