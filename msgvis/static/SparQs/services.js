(function () {
    'use strict';

    var module = angular.module('SparQs.services', [
        'ng.django.urls',
        'SparQs.bootstrap',
        'ngSanitize'
    ]);

    module.factory('SparQs.services.Dataset', [
        '$http', 'djangoUrl',
        'SparQs.bootstrap.dataset',
        function datasetFactory($http, djangoUrl, datasetId) {
            var apiUrl = djangoUrl.reverse('dataset');

            var Dataset = function () {
                this.id = datasetId
            };

            var request = {
                params: {
                    id: datasetId
                }
            };
            $http.get(apiUrl, request)
                .success(function (data) {
                    angular.extend(Dataset.prototype, data);
                });

            return new Dataset();

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
        'SparQs.services.Dimensions',
        'SparQs.services.Group',
        function selectionFactory($rootScope, Filtering, Dropzones, Dimensions, Group) {

            var current_focus = [
                //{
                //    "dimension": "time",
                //    "value": "2015-02-02T01:19:09Z"
                //}
            ];
            // Default dimension
            var current_dimension = Dimensions.get_by_key("time");


            var Selection = function () {

            };

            var changedEvent = 'SparQs.services.Selection.changed';

            angular.extend(Selection.prototype, {
                dimensions: function () {
                    var list = [];
                    if (typeof(current_dimension) !== "undefined")
                        list.push(current_dimension);
                    if (Group.selected_groups.length > 0)
                        list.push(Dimensions.get_by_key("groups"));
                    return list;
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
                groups: function() {
                    if (Group.selected_groups.length > 0){
                        var groups = Group.selected_groups.map(function(d){ return d.id; });
                        return groups;
                    }
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
                            console.log(eventName);
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
                },
                reset_focus: function(){
                    current_focus = [];
                },
                change_dimension: function(dimension){
                    current_dimension = dimension;
                },
                get_current_dimension: function(){
                    return current_dimension;
                }

            });

            return new Selection();
        }
    ]);

    //A service for loading example messages.
    module.factory('SparQs.services.ExampleMessages', [
        '$http', 'djangoUrl',
        function exampleMessageFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('example-messages');

            //A model class for messages
            var Message = function (data) {
                angular.extend(this, data);
            };

            var ExampleMessages = function () {
                var self = this;
                self.list = [];
                self.prev_request = 0;

                self.current_page = 1;
                self.pages = 0;
                self.count = -1;
            };

            angular.extend(ExampleMessages.prototype, {
                load: function (dataset, page, filters, focus, exclude, groups) {
                    var self = this;

                    var request = self.prev_request;
                    if (request == 0 || arguments.length > 2){
                        request = {
                            dataset: dataset,
                            filters: filters,
                            exclude: exclude,
                            focus: focus,
                            groups: groups
                        };
                    }
                    var messages_per_page = 50;
                    var apiUrl_with_param = apiUrl + "?messages_per_page=" + messages_per_page;
                    if ($.isNumeric(page)){
                        apiUrl_with_param += "&page=" + page;
                        self.current_page = page;
                    }
                    else {
                        self.current_page = 1;
                    }

                    return $http.post(apiUrl_with_param, request)
                        .success(function (data) {
                            self.list = data.messages.results.map(function (msgdata) {
                                return new Message(msgdata);
                            });
                            self.prev_request = request;
                            self.count = data.messages.count;
                            self.page_num = Math.ceil(self.count / messages_per_page);
                            self.pages = [];
                            var i, range = 5;
                            if ( self.current_page < 2 * range ){
                                for (i = 1 ; i <= 2 * range && i <= self.page_num ; i++ ){
                                    self.pages.push(i);
                                }
                            }
                            else if ( self.current_page > self.page_num - range ){
                                for (i = self.page_num - 2 * range + 1 ; i <= self.page_num ; i++ ){
                                    self.pages.push(i);
                                }
                            }
                            else if ( self.page_num > 0 ) {

                                for (i = self.current_page - range ; i <= self.current_page ; i++){

                                    self.pages.push(i);
                                }
                                for (i = self.current_page + 1 ; i <= self.page_num && i < self.current_page + range; i++){
                                    self.pages.push(i);
                                }
                            }
                            self.prev_page = (self.current_page > 1) ? self.current_page - 1 : false;
                            self.next_page = (self.current_page < self.page_num) ? self.current_page + 1 : false;
                        });
                },
                refresh: function(){
                    var self = this;
                    return $http.post(apiUrl, self.prev_request)
                        .success(function (data) {
                            self.list = data.messages.map(function (msgdata) {
                                return new Message(msgdata);
                            });
                        });
                },
                clear: function(){
                    var self = this;
                    self.list = [];
                    self.prev_request = 0;

                    self.current_page = 1;
                    self.pages = 0;
                    self.count = -1;
                }
            });

            return new ExampleMessages();
        }
    ]);

    //A service for loading example messages.
    module.factory('SparQs.services.KeywordMessages', [
        '$rootScope', '$http', 'djangoUrl',
        function keywordMessagesFactory($rootScope, $http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('keyword-messages');

            //A model class for messages
            var Message = function (data) {
                angular.extend(this, data);
            };

            var KeywordMessages = function () {
                var self = this;
                self.keywords = "";
                self.types_list = [];

                self.list = [];
                self.current_page = 1;
                self.pages = 0;
                self.count = -1;

                self.prev_page = false;
                self.next_page = false;

            };

            angular.extend(KeywordMessages.prototype, {
                load: function (dataset, page, keywords, types_list) {
                    var self = this;

                    // using current lists if the lists are not given
                    keywords = keywords || self.keywords;
                    types_list = types_list || self.types_list;

                    var request = {
                        dataset: dataset,
                        keywords: keywords,
                        types_list: types_list
                    };
                    var messages_per_page = 50;
                    var apiUrl_with_param = apiUrl + "?messages_per_page=" + messages_per_page;
                    if ($.isNumeric(page)){
                        apiUrl_with_param += "&page=" + page;
                        self.current_page = page;
                    }
                    else {
                        self.current_page = 1;
                    }


                    return $http.post(apiUrl_with_param, request)
                        .success(function (data) {
                            self.list = data.messages.results.map(function (msgdata) {
                                return new Message(msgdata);
                            });
                            self.count = data.messages.count;
                            self.page_num = Math.ceil(self.count / messages_per_page);
                            self.pages = [];
                            var i, range = 5;
                            if ( self.current_page < 2 * range ){
                                for (i = 1 ; i <= 2 * range && i <= self.page_num ; i++ ){
                                    self.pages.push(i);
                                }
                            }
                            else if ( self.current_page > self.page_num - range ){
                                for (i = self.page_num - 2 * range + 1 ; i <= self.page_num ; i++ ){
                                    self.pages.push(i);
                                }
                            }
                            else if ( self.page_num > 0 ) {

                                for (i = self.current_page - range ; i <= self.current_page ; i++){

                                    self.pages.push(i);
                                }
                                for (i = self.current_page + 1 ; i <= self.page_num && i < self.current_page + range; i++){
                                    self.pages.push(i);
                                }
                            }
                            self.prev_page = (self.current_page > 1) ? self.current_page - 1 : false;
                            self.next_page = (self.current_page < self.page_num) ? self.current_page + 1 : false;
                            self.keywords = keywords;
                            self.types_list = types_list;

                        });
                },
                reset: function(){
                    var self = this;
                    self.prev_page = false;
                    self.next_page = false;
                    self.keywords = "";
                    self.list = [];
                    self.count = -1;
                    self.types_list = [];
                }

            });

            return new KeywordMessages();
        }
    ]);

    //A service for loading example messages.
    module.factory('SparQs.services.Keywords', [
        '$http', 'djangoUrl', 'SparQs.services.Dataset',
        function keywordsFactory($http, djangoUrl, Dataset) {


            var Keywords = function () {
                var self = this;
                self.list_url = djangoUrl.reverse('keyword') + "?dataset=" + Dataset.id + "&q="
                self.key = "words";
                self.search_results = {"": self};
                self.table = undefined;
                self.domain = undefined;
                self.distribution = undefined;
                self.search_key = "";
                self.search_key_tmp = "";
                self.loading = false;
            };


            angular.extend(Keywords.prototype, {
                load_keywords_distributions: function(dataset){
                    var self = this;
                    if (!self.loading) {
                        self.loading = true;
                        var target = self;
                        if ( typeof(self.search_key) !== "undefined" && self.search_key !== "" &&
                             typeof(self.search_results[self.search_key]) === "undefined" ){
                            target = {};
                            target.table = [];
                            target.domain = [];
                            target.domain_labels = {};
                            target.distribution = [];
                            target.page = 0;
                            self.search_results[self.search_key] = target;

                        }
                        else if( !self.table ){
                            self.table = [];
                            self.domain = [];
                            self.domain_labels = {};
                            self.distribution = [];
                            self.page = 0;

                        }

                        var request = {
                            dataset: Dataset.id,
                            dimensions: [self.key],
                            page: target.page + 1,
                            search_key: (self.search_key !== "") ? self.search_key : undefined
                        };

                        var apiUrl = djangoUrl.reverse('data-table');


                        self.request = $http.post(apiUrl, request)
                            .success(function (data) {
                                var result = data.result;
                                self.loading = false;
                                self.request = undefined;
                                if ( result !== null && typeof(result) !== "undefined" ){
                                    result.table = result.table;
                                    result.domain = result.domains[self.key];
                                    result.domain_labels = result.domain_labels[self.key] || {};
                                    result.distribution = self.get_keywords_distribution_in_order(result.table, result.domain, result.domain_labels);

                                    self.add_keywords_distribution(target, result);

                                }
                            });

                        return self.request;
                    }
                },
                get_keywords_distribution_in_order: function (table, domain, labels) {
                    if (!table || !domain) {
                        return undefined;
                    }
                    var self = this;
                    var distribution_map = {};
                    table.forEach(function (d) {
                        var level = d[self.key];
                        distribution_map[level] = d.value;
                    });

                    return domain.map(function(level, i) {
                        var value = distribution_map[level] || 0;

                        if (level === null || level === "")
                            level = "No " + self.name;

                        var label;
                        if (labels && labels.length > i) {
                            label = labels[i];
                        }

                        return {
                            level: level,
                            label: label,
                            value: value
                        };
                    });
                },
                add_keywords_distribution: function(target, result){
                    $.merge(target.table, result.table);
                    $.merge(target.domain, result.domain);
                    $.extend(target.domain_labels, result.domain_labels);
                    $.merge(target.distribution, result.distribution);
                    target.page += 1;
                },
                get_current_keywords_distribution: function(){
                    var self = this;
                    return self.search_results[self.search_key].distribution;
                },
                reset_keywords_search: function () {
                    var self = this;
                    self.search_key = "";
                    self.search_key_tmp = "";
                }
            });

            return new Keywords();
        }
    ]);

    //A service for Groups.
    module.factory('SparQs.services.Group', [
        '$http', 'djangoUrl',
        function GroupFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('group');

            //A model class for messages
            var Message = function (data) {
                angular.extend(this, data);
            };

            var GroupItem = function (data) {
                angular.extend(this, data);
            };

            var Group = function () {
                this.messages = [];
                this.current_group_id = -1;
                this.group_list = [];
                this.group_dict = {};
                this.selected_groups = [];
                this.colors = d3.scale.category10();

                this.search_records = [];
                this.current_search_group_id = -1;
            };


            angular.extend(Group.prototype, {
                load: function (dataset) {

                    var self = this;
                    var request = {
                        params: {
                            dataset: dataset
                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.group_list = [];
                            data.forEach(function (groupdata) {
                                var item = new GroupItem(groupdata);
                                if (item.is_search_record)
                                    self.search_records.push(item);
                                else
                                    self.group_list.push(item);

                                self.group_dict[item.id] = item;

                            });

                        });
                },
                save: function (dataset, name, keywords, types_list, is_search_record) {
                    var self = this;

                    var request = {
                        dataset: dataset,
                        name: name,
                        keywords: keywords,
                        types_list: types_list,
                        is_search_record: is_search_record
                    };

                    self.messages = [];
                    if ( self.current_group_id != -1 ){
                        request.id = self.current_group_id;

                        // Check if anything changes
                        if (keywords == self.group_dict[self.current_group_id].keywords &&
                            types_list.sort().join(" ") == self.group_dict[self.current_group_id].include_types.sort().join(" ") &&
                            name.trim() == self.group_dict[self.current_group_id].name.trim())
                            return false;

                        return $http.put(apiUrl, request)
                        .success(function (data) {
                            self.group_dict[data.id].name = data.name;
                            self.group_dict[data.id].keywords = data.keywords;
                            self.group_dict[data.id].include_types =  data.include_types;
                            self.group_dict[data.id].message_count = data.message_count;
                        });
                    }
                    else{
                        return $http.post(apiUrl, request)
                            .success(function (data) {
                                var new_group = new GroupItem(data);
                                self.group_dict[new_group.id] = new_group;
                                if (!is_search_record){
                                    new_group.selected = false;
                                    self.group_list.push(new_group);
                                } else {
                                    if (self.current_search_group_id != -1){
                                        if (self.search_records[self.search_records.length - 1].selected){
                                            self.search_records[self.search_records.length - 1].selected = false;
                                            self.selected_groups.shift();
                                        }
                                    }
                                    new_group.selected = true;
                                    self.search_records.push(new_group);
                                    self.current_search_group_id = new_group.id;
                                    self.selected_groups.unshift(new_group);
                                    new_group.color = "#ff9896";
                                }

                            });
                    }
                },
                show_messages: function(){
                    var self = this;
                    if (self.current_group_id == -1) return;

                    var request = {
                        params: {
                            group_id: self.current_group_id
                        }
                    };

                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.messages = data.messages.results.map(function (msgdata) {
                                return new Message(msgdata);
                            });
                        });

                },
                create_new_group: function(){
                    var self = this;
                    self.current_group_id = -1;
                    self.messages = [];
                },
                switch_group: function(group){
                    var self = this;
                    self.current_group_id = group.id;
                    var group_ctrl = {
                        name: group.name,
                        keywords: group.keywords,
                        include_types: group.types_list
                    };

                    return group_ctrl;
                },
                toggle_group: function(group){
                    var self = this;
                    group.selected = !group.selected;
                    if (group.selected == true){
                        if (self.selected_groups.indexOf(group) == -1)
                        self.selected_groups.push(group);
                        group.color = self.colors(group.order);
                    }
                    else{
                        var idx = self.selected_groups.indexOf(group);
                        if ( idx != -1 )
                            self.selected_groups.splice(idx, 1);
                    }

                },
                delete_group: function(group){
                    var self = this;

                    var request = {
                        params: {
                            id: group.id
                        }
                    };

                    $http.delete(apiUrl, request)
                        .success(function (data) {
                            var index = self.group_list.indexOf(group);
                            if (index == -1) return;

                            self.group_list.splice(index, 1);
                            delete self.group_dict[group.id];


                            if (group.id == self.current_group_id)
                                self.current_group_id = -1;
                        });
                },
                current_group_name: function(){
                    var self = this;
                    if (self.current_group_id != -1)
                        return self.group_dict[self.current_group_id].name.trim();
                },
                get_color: function(id){
                    var self = this;
                    return self.group_dict[id].color;
                },
                reset_selection: function(){
                    var self = this;
                    if ( self.selected_groups.length > 0 ){
                        self.selected_groups.forEach(function(d){
                            d.selected = false;
                        });
                        self.selected_groups = [];
                        return true;
                    }
                    return false;

                },
                toggle_current_search_group: function(){
                    var self = this;
                    if ( self.current_search_group_id != -1 ){
                        var search_group = self.group_dict[self.current_search_group_id]; 
                        if (search_group.selected){
                            search_group.selected = false;
                            self.selected_groups.shift();
                        }
                        else {
                            search_group.selected = true;
                            self.selected_groups.unshift(search_group);
                        }
                        return true;
                    }
                    return false;
                },
                reset_search_group: function(){
                    var self = this;
                    if ( self.current_search_group_id != -1 ){
                        var search_group = self.group_dict[self.current_search_group_id]; 
                        if (search_group.selected){
                            search_group.selected = false;
                            self.selected_groups.shift();
                        }
                        self.current_search_group_id = -1;
                        return true;
                    }
                    return false;
                }
            });

            return new Group();
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
                load: function (dataset, dimensions, filters, exclude, groups) {
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
                        mode: "omit_others",
                        groups: groups
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

    //A service for add history.
    module.factory('SparQs.services.ActionHistory', [
        '$rootScope', '$http', '$interval', '$window', 'djangoUrl',
        function actionHistoryFactory($rootScope, $http, $interval, $window, djangoUrl) {

            var apiUrl = djangoUrl.reverse('action-history');

            var ActionHistory = function () {
                var self = this;
                var second = 1000;
                var submit_interval = 30;
                self.queue = [];
                var interval_timer = $interval(self.submit_records.bind(self), submit_interval * second);

                if ($window.location.search.indexOf('safe') != -1){
                    window.onbeforeunload = function(){
                        self.submit_records.call(self);
                        return "Are you sure you want to leave the page?";
                    };
                }

                self.init();

            };

            angular.extend(ActionHistory.prototype, {
                init: function(){
                    var self = this;
                    self.add_record('initialization:server-time', '', true);
                    self.add_record('initialization:client-time', '');
                    self.submit_records();
                },
                add_record: function (type, contents, use_server_time) {
                    var self = this;
                    if ( typeof(contents) !== typeof("string") ){
                        contents = JSON.stringify(contents);
                    }

                    var record = {
                        type: type,
                        contents: contents
                    };
                    if (!use_server_time)
                        record.created_at =  moment.utc().format('YYYY-MM-DD HH:mm:ss');
                    console.log(record);
                    self.queue.push(record);


                },
                submit_records: function(){
                    var self = this;
                    console.log(self.queue.length + " record(s) in the action history queue ... " );
                    if (self.queue.length == 0) return;

                    var request = {
                        records: self.queue
                    };
                    self.queue = [];

                    return $http.post(apiUrl, request)
                        .success(function (data) {
                            console.log('save ' + data.records.length + ' record(s)');
                        }).error(function (data) {
                            // push the records back to queue
                            self.queue.concat(request.records);
                        });
                }
            });

            return new ActionHistory();
        }
    ]);

})();
