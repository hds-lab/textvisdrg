(function () {
    'use strict';


    var module = angular.module('SparQs.controllers', [
        'SparQs.services',
        'angularSpinner',
        'angucomplete-alt'
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

    var DatasetController = function ($scope, Dataset) {
        $scope.Dataset = Dataset;

    };
    DatasetController.$inject = [
        '$scope',
        'SparQs.services.Dataset'
    ];
    module.controller('SparQs.controllers.DatasetController', DatasetController);

    var DimensionController = function ($scope, Dimensions, Filtering, Selection, History) {

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

                // Dimension change event 
                Selection.changed('dimensions');
            }
            $scope.dropped = undefined; // remove the dropped dimension
        };
        $scope.changeDimension = function(dimension){
            History.add_record("dimension:changed", {dimension: dimension.key});
            console.log($scope.Messages);
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
        };

        $scope.$on('add-history', function($event, type, contents){
            History.add_record(type, contents);
        });
    };

    DimensionController.$inject = [
        '$scope',
        'SparQs.services.Dimensions',
        'SparQs.services.Filtering',
        'SparQs.services.Selection',
        'SparQs.services.ActionHistory'
    ];
    module.controller('SparQs.controllers.DimensionController', DimensionController);

    var ExampleMessageController = function ($scope, ExampleMessages, Selection, Group, Dataset, usSpinnerService, History) {

        $scope.Messages = ExampleMessages;

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
            for ( var i = 0 ; i < focus.length ; i++ ){
                if ( focus[i].dimension == "groups" ){
                    groups = [+focus[i].value];
                    focus.splice(i,  1);
                    break;
                }
            }

            var request = ExampleMessages.load(Dataset.id, 1, filters, focus, exclude, groups);
            if (request) {
                usSpinnerService.spin('examples-spinner');
                $('#messages .message-list').scrollTop(0);
                History.add_record("example-messages:load:request-start", {filters: filters, exclude: exclude, focus: focus, groups: groups});

                request.then(function() {

                    usSpinnerService.stop('examples-spinner');
                    History.add_record("example-messages:load:request-end", {filters: filters, exclude: exclude, focus: focus, groups: groups});
                });
            }
        };

        $scope.convert_request_to_readable_str = function() {
            var request = ExampleMessages.prev_request;
            var str = "";
            if (request){
                request.focus.forEach(function(d){
                    console.log(d)
                    if (d.dimension != "groups"){
                        str += d.dimension;
                        if(d.dimension == "time"){                        
                                str += '=' + moment(d.min_time).utcOffset(0).format('MMM DD, YYYY H:mm');
                        } else {
                            if (d.hasOwnProperty('value') )
                                str +=  '=' + ((d.value != "") ? d.value : "No contains");
                            else if (d.hasOwnProperty('min') )
                                str += '=' + d.min;                            
                       }
                        str += " ";
                    }
                });
                if (request.hasOwnProperty('groups') && request.groups ){
                    str += "in Group [";
                    request.groups.forEach(function(d, i){
                        str += (i > 0) ? " | " : "";
                        str += Group.group_dict[d].name;
                    });
                    str += "]"
                }
            }
            return str;
        };

        $scope.is_empty = function(){
            return (ExampleMessages.prev_request == 0);
        };
        $scope.not_empty_url = function(url){
            return !(url.trim() == "")
        };
        $scope.update_page = function (page) {

            var request = ExampleMessages.load(Dataset.id, page);
            if (request) {
                usSpinnerService.spin('examples-spinner');
                History.add_record("example-message:switch-page:request-start", {page: page});

                request.then(function() {
                    History.add_record("example-message:switch-page:request-end", {page: page});
                    usSpinnerService.stop('examples-spinner');
                });
            }
        };
        $scope.highlight_current_page = function (page){
            return (page == ExampleMessages.current_page) ? "current-page" : "";
        };


        // Callback functions for focus & dimension/groups change events
        Selection.changed('focus', $scope, $scope.get_example_messages);
        Selection.changed('dimensions,groups', $scope, ExampleMessages.clear.bind(ExampleMessages));

        $scope.$on('add-history', function($event, type, contents){
            History.add_record(type, contents);
        });


    };
    ExampleMessageController.$inject = [
        '$scope',
        'SparQs.services.ExampleMessages',
        'SparQs.services.Selection',
        'SparQs.services.Group',
        'SparQs.services.Dataset',
        'usSpinnerService',
        'SparQs.services.ActionHistory'
    ];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SearchAndGroupController = function ($scope, Keywords, KeywordMessages, Group, Dataset, Selection, usSpinnerService, History) {

        $scope.Group = Group;
        Group.load(Dataset.id);
        $scope.keyword_list_url = Keywords.list_url;
        $scope.Messages = KeywordMessages;
        $scope.Keywords = Keywords;

        $scope.search_params = {
            group_name: "",
            keywords: "",
            types_list: [],
            selected_keyword_items: [],
            tweet_types: {tweet: true, retweet: true, reply: true}
        };
        $scope.edit_params = {
            group_name: "",
            keywords: "",
            types_list: [],
            selected_keyword_items: [],
            tweet_types: {tweet: true, retweet: true, reply: true}
        };
        $scope.tmp_params = {
            group_name: "",
            keywords: "",
            types_list: [],
            selected_keyword_items: [],
            tweet_types: {tweet: true, retweet: true, reply: true}
        };

        var params = {};
        params["edit_mode_" + false] = $scope.search_params;
        params["edit_mode_" + true] = $scope.edit_params;
        params["edit_mode_tmp"] = $scope.tmp_params;

        $scope.edit_mode = false;


        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };

        $scope.search = function ($event, is_search) {
            if ($event){
                $event.stopPropagation();
            }
            var current_params = params["edit_mode_" + $scope.edit_mode];
            var keywords = current_params.selected_keyword_items.map(function(d){ return d.text }).join(",");
            var types_list = [];
            for ( var type in current_params.tweet_types ){
                if ( current_params.tweet_types.hasOwnProperty(type) && current_params.tweet_types[type] === true ){
                    types_list.push(type);
                }
            }

            var request = KeywordMessages.load(Dataset.id, 1, keywords, types_list);
            if (request) {
                usSpinnerService.spin('search-spinner');
                if (is_search){
                    usSpinnerService.spin('vis-spinner');
                }
                $scope.change_mode("group_messages");
                $('#search .message-list').scrollTop(0);

                History.add_record("search:request-start", {edit_mode: $scope.edit_mode, current_params: current_params});

                request.then(function() {
                    usSpinnerService.stop('search-spinner');

                    History.add_record("search:request-end", {edit_mode: $scope.edit_mode, current_params: current_params});
                    if (is_search)
                        $scope.save($event, is_search);

                });
            }

        };


        $scope.update_page = function (page) {
            var request = KeywordMessages.load(Dataset.id, page);
            if (request) {
                usSpinnerService.spin('search-spinner');
                $scope.change_mode("group_messages");
                History.add_record("search:switch-page:request-start", {page: page});

                request.then(function() {
                    usSpinnerService.stop('search-spinner');
                    History.add_record("search:switch-page:request-stop", {page: page});
                });
            }
        };

        $scope.highlight_current_page = function (page){
            return (page == KeywordMessages.current_page) ? "current-page" : "";
        };

        $scope.reset_search = function(){
            var current_params = params["edit_mode_" + $scope.edit_mode];
            History.add_record("search:reset-search", {edit_mode: $scope.edit_mode, current_params: current_params});

            current_params.group_name = "";
            current_params.selected_keyword_items = [];
            current_params.tweet_types = {tweet: true, retweet: true, reply: true};
            $scope.$broadcast('angucomplete-alt:clearInput');

            KeywordMessages.reset();
            $scope.change_mode("keyword_list");

            if (Group.reset_search_group()){
                Selection.changed('groups');
            }
        };
        $scope.reset_selection = function(){

            History.add_record("search:reset-selected-groups", {edit_mode: $scope.edit_mode, current_selection: Group.selected_groups});

            if (Group.reset_selection()){
                Selection.changed('groups');
            }

        };

        $scope.save = function ($event, is_search, group) {
            var current_params = params["edit_mode_" + $scope.edit_mode];

            var name = current_params.group_name;
            var keywords = current_params.selected_keyword_items.map(function(d){ return d.text }).join(",");
            var types_list = [];
            for ( var type in current_params.tweet_types ){
                if ( current_params.tweet_types.hasOwnProperty(type) && current_params.tweet_types[type] === true ){
                    types_list.push(type);
                }
            }

            if (is_search && !$scope.edit_mode){
                name = "Current Search Results";
            }
            else if (name == "" || name == undefined){
                name = keywords;
                if (name.length > 40){
                    name = name.substr(0, 40) + "...";
                }
            }


            var request = Group.save(Dataset.id, name, keywords, types_list, is_search);
            if (request) {

                if (!is_search && $scope.edit_mode){
                    History.add_record("group:save-edit:request-start", {group: group});
                    usSpinnerService.spin('update-spinner');

                    request.then(function() {
                        usSpinnerService.stop('update-spinner');
                        History.add_record("group:save-edit:request-stop", {group: group});
                        $scope.finish_edit();
                        if (group.selected) {
                            Selection.changed('groups');
                        }
                    });
                }
                else{
                    if (!$scope.edit_mode && !is_search)
                        usSpinnerService.spin('save-spinner');
                    History.add_record("group:save-search:request-start", {edit_mode: $scope.edit_mode});

                    request.then(function() {
                        if (!$scope.edit_mode && !is_search)
                            usSpinnerService.stop('save-spinner');
                        History.add_record("group:save-search:request-end", {edit_mode: $scope.edit_mode});
                        if (is_search){
                            Selection.changed('groups');
                        }
                    });
                }
            }
            else{
                History.add_record("group:save-edit:no-change", {group: group});
                $scope.change_mode("keyword_list");
                $scope.finish_edit($event, group);
            }
        };

        $scope.not_empty_url = function(url){
            return !(url.trim() == "")
        };

        $scope.is_empty = function(){
            return (KeywordMessages.count == -1 )
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
        $scope.show_messages = function($event, group, is_search){
            $event.stopPropagation();
            History.add_record("group:show-messages", {group: group, is_search: is_search});

            var current_params = params["edit_mode_" + $scope.edit_mode];
            current_params.group_name = group.name;
            current_params.selected_keyword_items = group.keywords.split(',').map(function(d){ return {text: d.trim()} });
            current_params.tweet_types = {tweet: false, retweet: false, reply: false};
            group.include_types.forEach(function(d){
                current_params.tweet_types[d] = true;
            });


            $scope.search($event, is_search);
        };
        $scope.reset_edits = function(){
            var tmp_params = params["edit_mode_tmp"];

            if ( $scope.edit_mode ){
                $scope.edit_mode = "tmp";
                $scope.save(undefined, false, tmp_params.group);
                if (!tmp_params.originally_selected){
                    $scope.toggle_group(undefined, tmp_params.group);
                }
                var original_group = tmp_params.group;
                original_group.name = tmp_params.group_name;
                original_group.keywords = tmp_params.selected_keyword_items.map(function(d){ return d.text }).join(',');
                original_group.include_types = [];
                for ( var type in tmp_params.tweet_types ){
                    if (tmp_params.tweet_types.hasOwnProperty(type) && tmp_params.tweet_types[type]){
                        original_group.include_types.push(type);
                    }
                }

            }
        };

        $scope.edit_group = function($event, group){

            $scope.reset_edits();

            $scope.edit_mode = true;
            var tmp_params = params["edit_mode_tmp"];
            tmp_params.group_name = group.name;
            tmp_params.selected_keyword_items = group.keywords.split(',').map(function(d){ return { text: d.trim() }; });
            tmp_params.tweet_types = {tweet: false, retweet: false, reply: false};
            group.include_types.forEach(function(d){
                tmp_params.tweet_types[d] = true;
            });
            tmp_params.originally_selected = group.selected;
            tmp_params.group = group;

            History.add_record("group:start_edit", {group: group});
            $scope.show_messages($event, group, false);
            if (!group.selected){
                $scope.toggle_group($event, group);
            }
            Group.current_group_id = group.id;

        };
        $scope.group_color = function(group){
            if (!group){
                group = Group.group_dict[Group.current_search_group_id];
            }
            if (group && group.selected) return {'background-color': group.color};
            return {'border': "1px solid #ccc" };


        };

        $scope.finish_edit = function($event, group, reset_changes){
            if ( $event ){
                $event.stopPropagation();
            }
            if (reset_changes){
                $scope.reset_edits();
            }
            else if ( $scope.edit_mode ){
                var tmp_params = params["edit_mode_tmp"];
                if (!tmp_params.originally_selected){
                    $scope.toggle_group(undefined, tmp_params.group);
                }
            }

            History.add_record("group:finish-edit", {group: group});
            Group.current_group_id = -1;
            KeywordMessages.reset();

            $scope.edit_mode = false;
            $scope.change_mode("keyword_list");
        };


        $scope.delete_group = function($event, group){
            if ( $event ){
                $event.stopPropagation();
            }
            var msg = "Are you sure you want to delete group \"#" + group.order + " " + group.name + "\"?";
            History.add_record("group:delete-attempt", {group: group});
            if ( window.confirm(msg) ){
                if (group.selected){
                    $scope.toggle_group($event, group)
                }

                var request = Group.delete_group(group);
                if (request) {
                    usSpinnerService.spin('update-spinner');
                    request.then(function() {
                        usSpinnerService.stop('update-spinner');
                    });
                }

            }
        };


        $scope.toggle_group = function($event, group){
            if ($event){
                $event.stopPropagation();
            }
            if (group){
                History.add_record("group:toggle", {group: group, is_selected_now: !group.selected});
                Group.toggle_group(group);
                Selection.changed('groups');
            } else {
                if (Group.toggle_current_search_group()){
                    History.add_record("group:toggle:current-search-group", "");
                    Selection.changed('groups');
                }

            }
        };

        $scope.group_class = function(group){
            return ($scope.is_being_editing(group)) ? "edit-class" : ((group.selected) ? "active" : "");
        };


        // Load keywords distribution
        Keywords.load_keywords_distributions();

        $scope.$watch('Keywords.request', function(newVal, oldVal) {
            if (Keywords && Keywords.request) {
                usSpinnerService.spin('keywords-spinner');
                History.add_record("keyword-list:request-start", "");

                Keywords.request.then(function() {
                    usSpinnerService.stop('keywords-spinner');
                    History.add_record("keyword-list:request-stop", "");
                })
            }
        });

        $scope.loadMoreKeywords = function() {
            History.add_record("keyword-list:load-more", "");
            Keywords.load_keywords_distributions();
        };


        var current_mode = "keyword_list";
        $scope.is_mode = function(mode){
            return (current_mode == mode);
        };
        $scope.tab_class = function(mode){
            return ($scope.is_mode(mode)) ? 'active' : "";
        };
        $scope.change_mode = function(mode, $event){
            if (mode != current_mode){
                History.add_record("search-result:switch-mode", {target_mode: mode, by_user: ($event !== undefined)});
                current_mode = mode;
            }
        };
        $scope.input_changed = function(selected_item){
            History.add_record("keyword:input-changed", {currentStr: selected_item});
        };

        $scope.select_keywords = function(selected_item){
            var self = this;
            var current_params = params["edit_mode_" + $scope.edit_mode];
            if ( selected_item && current_params.selected_keyword_items.filter(function(d){ return d.text == selected_item.title; }).length == 0) {
                current_params.selected_keyword_items.push({text: selected_item.title});
                History.add_record("keyword:select", {item: selected_item.title});
            }
        };
        $scope.remove_selected = function(item){
            var current_params = params["edit_mode_" + $scope.edit_mode];
            var idx = current_params.selected_keyword_items.indexOf(item);
            if ( idx != -1 ){
                current_params.selected_keyword_items.splice(idx, 1);
                History.add_record("keyword:remove", {item: item});
            }
        };
        $scope.press_enter_key = function(searchStr){
            if ( searchStr && searchStr.trim() != "" ){
                $scope.select_keywords({title: searchStr.trim()});
                $scope.$broadcast('angucomplete-alt:clearInput');
                History.add_record("keyword:press-enter:add-keyword", {item: searchStr.trim()});
            }
            else {
                History.add_record("keyword:press-enter:search", "");
                $scope.search(undefined, true);
            }
        };

        $scope.delete_previous_item = function(){
            var current_params = params["edit_mode_" + $scope.edit_mode];
            if ( current_params.selected_keyword_items.length > 0 ){
                var item = current_params.selected_keyword_items.pop();
                History.add_record("keyword:delete-previous-item", {item: item});
                return item.text;
            }
            return "";
        };

        $scope.calc_input_width = function(text){
            return { width: (text) ? ((text.length + 1) * 5.4 + 20) : 150 };
        };

        $scope.record_changes_of_old_keywords = function(item){
            History.add_record("keyword:edit-previous-item", {item: item});
        };

        $scope.record_change = function(type, is_selected){
            History.add_record("search:change-type", {type: type, is_selected: is_selected});
        };

        $scope.$on('add-history', function($event, type, contents){
            History.add_record(type, contents);
        });


    };
    SearchAndGroupController.$inject = [
        '$scope',
        'SparQs.services.Keywords',
        'SparQs.services.KeywordMessages',
        'SparQs.services.Group',
        'SparQs.services.Dataset',
        'SparQs.services.Selection',
        'usSpinnerService',
        'SparQs.services.ActionHistory'
    ];
    module.controller('SparQs.controllers.SearchAndGroupController', SearchAndGroupController);


    var VisualizationController = function ($scope, Group, Selection, Filtering, DataTables, Dataset, usSpinnerService, History) {

        $scope.datatable = DataTables;
        $scope.selection = Selection;
        $scope.groupColors = Group.get_color.bind(Group);

        $scope.title = function(){
            return (Group.selected_groups.length == 0 ) ? "of the Whole Dataset" : "of the Tweets in Selected Groups"
        };


        $scope.get_data_table = function () {
            var dimensions = Selection.dimensions();
            var filters = Selection.filters();
            var exclude = Selection.exclude();
            var groups = Selection.groups();
            Selection.reset_focus();
            var request = DataTables.load(Dataset.id, dimensions, filters, exclude, groups);

            if (request) {
                usSpinnerService.spin('vis-spinner');
                History.add_record("data-table:request-start", {dimensions: dimensions.map(function(d){ return d.key; }), filters: filters, exclude: exclude, groups: groups});

                request.then(function () {
                    usSpinnerService.stop('vis-spinner');
                    History.add_record("data-table:request-stop", {dimensions: dimensions.map(function(d){ return d.key; }), filters: filters, exclude: exclude, groups: groups});

                });
            }
        };

        $scope.get_data_table();

        Selection.changed('filters,groups', $scope, $scope.get_data_table);

        $scope.onVisClicked = function(data) {
            History.add_record("vis:point:click", {data: data});
            Selection.set_focus(data);
        };
        $scope.show_filter = function(){
            var dimension = Selection.dimensions();
            if (dimension.length == 0) return false;
            else dimension = dimension[0];
            return dimension.is_categorical();
        };


        $scope.openFilter = function($event) {
            var offset = {top: 0};
            var dimension = Selection.dimensions();
            if (dimension.length == 0) return;
            else dimension = dimension[0];
            if ($event) {
                var $el = $($event.target);
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
            History.add_record("vis:open-filter", {dimension: dimension.key});
            Filtering.toggle(dimension, offset);
        };

        $scope.reload = function(){
            if (Filtering.dimension && Filtering.dimension.filtering ){
                History.add_record("vis:clear-filtering", {dimension: Filtering.dimension.key});
                Filtering.dimension.clear_filtering();
                //Filtering.toggle();
            }
            $scope.get_data_table();
        };
        Selection.changed('dimensions', $scope, $scope.reload);

        $scope.spinnerOptions = {
            radius: 20,
            width:6,
            length: 10,
            color: "#000000"
        };

        $scope.$on('add-history', function($event, type, contents){
            History.add_record(type, contents);
        });
    };

    VisualizationController.$inject = [
        '$scope',
        'SparQs.services.Group',
        'SparQs.services.Selection',
        'SparQs.services.Filtering',
        'SparQs.services.DataTables',
        'SparQs.services.Dataset',
        'usSpinnerService',
        'SparQs.services.ActionHistory'
    ];
    module.controller('SparQs.controllers.VisualizationController', VisualizationController);


    //Extends DimensionsController
    var FilterController = function ($scope, Filtering, Selection, usSpinnerService, History) {

        $scope.filtering = Filtering;

        $scope.spinnerOptions = {
            radius: 15,
            width: 4,
            length: 8,
            color: "#000000"
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
            History.add_record("filter:close", {dimension: Filtering.dimension.key});
            Filtering.toggle();
        };

        $scope.saveFilter = function () {
            if (Filtering.dimension.is_dirty()) {
                History.add_record("filter:changed", {dimension: Filtering.dimension.key});
                Selection.changed('filters');
                Filtering.dimension.current_filter().saved();
            }
        };

        $scope.resetFilter = function () {
            if (!Filtering.dimension.is_not_applying_filters()) {
                History.add_record("filter:reset", {dimension: Filtering.dimension.key});
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
            History.add_record("filter:load-more", {dimension: Filtering.dimension.key});
            Filtering.dimension.load_categorical_distribution();
        };

        $scope.search = function() {
            History.add_record("filter:search", {dimension: Filtering.dimension.key, search_key: Filtering.dimension.search_key_tmp});
            Filtering.dimension.search_key = Filtering.dimension.search_key_tmp;
            Filtering.dimension.load_categorical_distribution();
        };
        $scope.set_back_cur_search = function() {
            if ( Filtering.dimension.search_key_tmp !== Filtering.dimension.search_key ){
                History.add_record("filter:set-back-cur-search", {dimension: Filtering.dimension.key, search_key: Filtering.dimension.search_key_tmp});
                Filtering.dimension.search_key_tmp = Filtering.dimension.search_key;
            }

        };

        $scope.$on('add-history', function($event, type, contents){
            History.add_record(type, contents);
        });

    };

    FilterController.$inject = [
        '$scope',
        'SparQs.services.Filtering',
        'SparQs.services.Selection',
        'usSpinnerService',
        'SparQs.services.ActionHistory'
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
