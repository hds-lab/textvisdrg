(function () {
    'use strict';

    var module = angular.module('SparQs.services');

    //The collection of dimensions.
    //Dimension objects have some extra functionality added.
    module.factory('SparQs.services.Dimensions', [
        '$http', 'djangoUrl', 'SparQs.services.Dataset',
        function ($http, djangoUrl, Dataset) {

            var filterProps = [
                'min',
                'max',
                'min_time',
                'max_time',
                'levels'
            ];

            var djangoDateFormat = d3.time.format('%Y-%m-%dT%H:%M:%SZ');
            var userDateFormat = d3.time.format('%Y/%m/%d %H:%M:%S');

            var formatDate = function(val) {
                if (val) return userDateFormat(val);
                else return val;
            };
            var parseDate = function(str) {
                if (str instanceof Date) return str;

                if (str && str !== '') return userDateFormat.parse(str);

                else return undefined;
            };

            var Filter = function (data) {
                this.data = data || { };
                this.old_data = angular.copy(this.data);

                this.dirty = false; //true if has unsaved filter changes
            };

            function _getter_setter(prop, format, parse) {
                return function (value) {
                    if (arguments.length > 0) {

                        if (value === '') {
                            value = undefined;
                        }

                        value = parse ? parse(value) : value;

                        if (this.data[prop] !== value) {
                            this.data[prop] = value;
                            this.dirty = true;
                        }
                    }

                    var val = this.data[prop];
                    return format ? format(val) : val;
                }
            }

            angular.extend(Filter.prototype, {
                min: _getter_setter('min', Math.round),
                max: _getter_setter('max', Math.round),
                min_time: _getter_setter('min_time'),
                max_time: _getter_setter('max_time'),
                levels: _getter_setter('levels'),
                is_empty: function () {
                    if (angular.equals(this.data, {})) {
                        return true;
                    }
                    var data = this.data;
                    return !filterProps.some(function (prop) {
                        return data.hasOwnProperty(prop) &&
                            (data[prop] || data[prop] === 0 || data[prop] === '0' || data[prop] === false);
                    });
                },
                reset: function () {
                    if (!this.is_empty()) {
                        this.data = {};
                        this.dirty = true;
                    }
                },
                undo: function () {
                    if (this.dirty) {
                        this.data = angular.clone(this.old_data);
                        this.dirty = false;
                    }
                },
                saved: function () {
                    this.old_data = angular.copy(this.data);
                    this.dirty = false;
                },
                add_to_levels: function(level){
                    if (!this.levels())
                        this.levels([]);
                    this.levels().push(level);
                    this.dirty = true;
                },
                remove_from_levels: function(level){
                    if (this.levels()){
                        var idx = this.levels().indexOf(level);
                        if (idx != -1) {
                            this.levels().splice(idx, 1);
                        }
                        this.dirty = true;
                    }
                }
            });

            // A simple model class for dimensions
            var Dimension = function (data) {
                angular.extend(this, data);

                this.zone = undefined;
                this.draggable = this;

                this.filter_type = {};
                this.filter_type['filter'] = new Filter(this.filter_type['filter']);
                this.filter_type['exclude'] = new Filter(this.filter_type['exclude']);
                this.mode = this.is_categorical() ? "exclude" : "filter";
                this.group_action = false;

                this.filtering = false; //true if currently being filtered
                this.table = undefined;
                this.domain = undefined;
                this.distribution = undefined;
                this.search_key = "";
                this.search_results = {"": this};

            };

            angular.extend(Dimension.prototype, {
                dimension_class: function() {
                    var cls = "primary-enabled";

                    if (this.key != 'time') {
                        //Time cannot be a secondary axis
                        cls += ' secondary-enabled'
                    }

                    if (this.zone) {
                        cls += ' dimension-' + this.zone.name;
                    }

                    if (this.group_name) {
                        cls += ' group-' + this.group_name;
                    }

                    if (!this.is_not_applying_filters()) {
                        cls += ' filter-applied';
                    }

                    if (this.filtering) {
                        cls += ' filtering-open';
                    }

                    return cls;
                },
                is_quantitative: function () {
                    return this.type == 'QuantitativeDimension';
                },
                is_time: function () {
                    return this.type == 'TimeDimension';
                },
                is_quantitative_or_time: function () {
                    return this.type == 'QuantitativeDimension' || this.type == 'TimeDimension';
                },
                is_categorical: function () {
                    return this.type == 'CategoricalDimension';
                },
                current_filter: function(){
                    return this.filter_type[this.mode];
                },
                serialize_filter: function (mode) {
                    return angular.extend({
                        dimension: this.key
                    }, this.filter_type[mode].data);
                },
                set_filtering: function (filtering) {
                    if (this.filtering != filtering) {
                        this.filtering = filtering;

                        if (filtering) {
                            this.load_distribution()
                        }
                    }
                },
                clear_filtering: function () {
                    if (this.filtering) {
                        this.filtering = false;
                        this.filter_type['filter'].reset();
                        this.filter_type['exclude'].reset();
                    }
                },
                is_not_applying_filters: function(){
                    return ((this.is_categorical() && this.is_all_selected()) ||
                            (!this.is_categorical() && this.current_filter().is_empty()));
                },
                is_dirty: function(){
                    //console.log("is_dirty is called");
                    //console.log(this.filter_type['filter'].dirty || this.filter_type['exclude'].dirty);
                    return this.filter_type['filter'].dirty ||
                           this.filter_type['exclude'].dirty;
                },
                load_distribution: function (dataset) {
                    if (this.is_categorical() && !this.table){
                        //$('.level-select-button.all').prop('disabled', true);
                        //$('.level-select-button.none').prop('disabled', false);
                        return this.load_categorical_distribution(dataset);
                    }
                    else if (!this.loading && !this.table) {
                        this.loading = true;

                        var request = {
                            dataset: Dataset.id,
                            dimensions: [this.key]
                        };

                        var apiUrl = djangoUrl.reverse('data-table');

                        var self = this;
                        this.request = $http.post(apiUrl, request)
                            .success(function (data) {
                                var result = data.result;
                                self.loading = false;
                                self.request = false;
                                self.table = result.table;
                                self.domain = result.domains[self.key];
                                self.domain_labels = result.domain_labels[self.key] || {};
                            });
                        
                        return this.request;
                    }
                },
                get_current_distribution: function(){
                    return this.search_results[this.search_key].distribution;
                },
                load_categorical_distribution: function (dataset) {
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


                        this.request = $http.post(apiUrl, request)
                            .success(function (data) {
                                var result = data.result;
                                self.loading = false;
                                self.request = undefined;
                                if ( result !== null && typeof(result) !== "undefined" ){
                                    result.table = result.table;
                                    result.domain = result.domains[self.key];
                                    result.domain_labels = result.domain_labels[self.key] || {};
                                    result.distribution = self.get_distribution_in_order(result.table, result.domain, result.domain_labels);

                                    self.add_categorical_distribution(target, result);

                                }
                            });
                        
                        return this.request;
                    }
                },
                add_categorical_distribution: function(target, result){
                    $.merge(target.table, result.table);
                    $.merge(target.domain, result.domain);
                    $.extend(target.domain_labels, result.domain_labels);
                    $.merge(target.distribution, result.distribution);
                    target.page += 1;
                },
                get_categorical_levels: function () {
                    var dimension = this;
                    if (dimension.is_categorical()) {
                        var list = dimension.domain.slice(0);
                        for (var i = 0; i < list.length; i++) {
                            if (list[i] == null)
                                list[i] = "No " + dimension.name;
                        }
                        return list;
                    }
                    return undefined;
                },
                inverse_level: function(level){
                     var dimension = this;
                    if ( level == "No " + dimension.name )
                        return "";
                    return level;
                },
                get_distribution_in_order: function (table, domain, labels) {
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
                            value: value,
                            show: self.current_show_state(level)
                        };
                    });
                },
                show_search: function () {
                    return this.is_categorical() && this.domain && this.domain.length > 10;
                },
                current_show_state: function(level){
                    var self = this;
                    var levels = self.current_filter().levels();
                    if ( levels && levels.indexOf(level) != -1 ){
                        return self.mode != "exclude"
                    }
                    return self.mode == "exclude";
                },
                check_original_list_when_change: function(data_point){
                    var self = this;
                    self.distribution.forEach(function(d){
                        if (d.level === data_point.level){
                            d.show = data_point.show;
                        }
                    });
                },
                change_level: function (d) {
                    var criteria = {
                        filter: { include: true, exclude: false },
                        exclude: { include: false, exclude: true }
                    };
                    if ( d.show == criteria[this.mode].include ) {
                        this.filter_type[this.mode].add_to_levels(this.inverse_level(d.level));
                    } else {
                        this.filter_type[this.mode].remove_from_levels(this.inverse_level(d.level));
                    }
                    if ( this.search_key != "")
                        this.check_original_list_when_change(d);
                },
                switch_mode: function(mode){
                    if ( mode !== 'exclude' && mode !== "filter" ) return;
                    this.mode = mode;
                    for (var m in this.filter_type){
                        this.filter_type[m].reset();
                    }
                    this.group_action = true;
                },
                is_all_selected: function () {
                    var self = this;
                    if (self.mode == "exclude" && (!self.current_filter().levels() || self.current_filter().levels().length == 0)) {
                        return true;
                    }
                    else if (self.mode == "filter" && self.current_filter().levels() && self.current_filter().levels().length == self.domain.length){
                        return true;
                    }
                    return false;
                },
                is_all_unselected: function () {
                    var self = this;
                    if (self.mode == "filter" && (!self.current_filter().levels() || self.current_filter().levels().length == 0)) {
                        return true;
                    }
                    else if (self.mode == "exclude" && self.current_filter().levels() && self.current_filter().levels().length == self.domain.length){
                        return true;
                    }
                    return false;
                },
                reset_search: function () {
                    var self = this;
                    if (self.is_categorical()) {
                        self.search_key = "";
                        self.search_key_tmp = "";
                    }
                }
            });

            //The actual dimension service class
            var Dimensions = function (list) {
                this.by_key = {};
                var self = this;

                //Instantiate Dimensions
                this.list = list.map(function (dimdata) {
                    var dim = new Dimension(dimdata);
                    self.by_key[dim.key] = dim;
                    return dim;
                });
            };

            angular.extend(Dimensions.prototype, {
                get_by_key: function (key) {
                    return this.by_key[key];
                },
                get_groups: function() {
                    //Hierarchy of dimensions
                    var groups = [
                        {
                            "group_name": "Time",
                            "dimensions": [
                                this.get_by_key('time'),
                                this.get_by_key('timezone')
                            ]
                        },
                        {
                            "group_name": "Contents",
                            "dimensions": [
                                //this.get_by_key('topics'),
                                //this.get_by_key('words'),
                                this.get_by_key('hashtags'),
                                //this.get_by_key('contains_hashtag'),
                                this.get_by_key('urls'),
                                //this.get_by_key('contains_url'),
                                this.get_by_key('contains_media')
                            ]
                        },
                        {
                            "group_name": "Meta",
                            "dimensions": [
                                //this.get_by_key('language'),
                                this.get_by_key('sentiment')
                            ]
                        },


                        {
                            "group_name": "Author",
                            "dimensions": [
                                this.get_by_key('sender'),
                         /*       this.get_by_key('sender_message_count'),
                                this.get_by_key('sender_reply_count'),
                                this.get_by_key('sender_mention_count'),
                                this.get_by_key('sender_share_count'),
                                this.get_by_key('sender_friend_count'),
                                this.get_by_key('sender_follower_count')*/
                            ]
                        },

                        {
                            "group_name": "Interaction",
                            "dimensions": [
                                this.get_by_key('type'),
                                //this.get_by_key('replies'),
                                //this.get_by_key('shares'),
                                this.get_by_key('mentions')
                                //this.get_by_key('contains_mention')
                            ]
                        }
                    ];

                    groups.forEach(function(group) {
                        group.dimensions.forEach(function(dimension) {
                            dimension.group_name = group.group_name;
                        });
                    });

                    return groups;
                }
            });

            return new Dimensions([
                {
                    "key": "time",
                    "name": "Time",
                    "type": "TimeDimension",
                    "description": "The time a message was sent (UTC)."
                },
                {
                    "key": "timezone",
                    "name": "Timezone",
                    "type": "CategoricalDimension",
                    "description": "The timezone (proxy for location) of a message."
                },
                {
                    "key": "topics",
                    "name": "Topics",
                    "type": "CategoricalDimension",
                    "description": "Topics in the dataset based on a topic model."
                },
                {
                    "key": "words",
                    "name": "Keywords",
                    "type": "CategoricalDimension",
                    "description": "Words extracted from messages."
                },
                {
                    "key": "hashtags",
                    "name": "Hashtags",
                    "type": "CategoricalDimension",
                    "description": "Hashtags used in messages."
                },
                {
                    "key": "contains_hashtag",
                    "name": "Contains a Hashtag",
                    "type": "CategoricalDimension",
                    "description": "Whether a message includes a hashtag."
                },
                {
                    "key": "urls",
                    "name": "Urls",
                    "type": "CategoricalDimension",
                    "description": "Urls included in messages."
                },
                {
                    "key": "contains_url",
                    "name": "Contains a Url",
                    "type": "CategoricalDimension",
                    "description": "Whether a message includes a url."
                },
                {
                    "key": "contains_media",
                    "name": "Contains a Photo",
                    "type": "CategoricalDimension",
                    "description": "Whether a message includes a photo."
                },
                {
                    "key": "language",
                    "name": "Language",
                    "type": "CategoricalDimension",
                    "description": "The language of a message."
                },
                {
                    "key": "sentiment",
                    "name": "Sentiment",
                    "type": "CategoricalDimension",
                    "description": "Sentiment (positive, negative, neutral) from sentiment analysis."
                },
                {
                    "key": "type",
                    "name": "Tweet Type",
                    "type": "CategoricalDimension",
                    "description": "Whether a message is an original tweet, a retweet, or a reply."
                },
                {
                    "key": "replies",
                    "name": "Num. Replies",
                    "type": "QuantitativeDimension",
                    "description": "Number of known replies a message received."
                },
                {
                    "key": "shares",
                    "name": "Num. Shares",
                    "type": "QuantitativeDimension",
                    "description": "Times a message was shared or retweeted."
                },
                {
                    "key": "mentions",
                    "name": "Mentions",
                    "type": "CategoricalDimension",
                    "description": "Usernames mentioned in messages."
                },
                {
                    "key": "contains_mention",
                    "name": "Contains a Mention",
                    "type": "CategoricalDimension",
                    "description": "Whether or not a message @mentions someone."
                },
                {
                    "key": "sender",
                    "name": "Author Name",
                    "type": "CategoricalDimension",
                    "description": "Name of the person who sent a message."
                },
                {
                    "key": "sender_message_count",
                    "name": "Num. Messages",
                    "type": "QuantitativeDimension",
                    "description": "Total messages sent by a message's author."
                },
                {
                    "key": "sender_reply_count",
                    "name": "Num. Replies",
                    "type": "QuantitativeDimension",
                    "description": "Total replies received by a message's author."
                },
                {
                    "key": "sender_mention_count",
                    "name": "Num. Mentions",
                    "type": "QuantitativeDimension",
                    "description": "Total mentions of a message's author."
                },
                {
                    "key": "sender_share_count",
                    "name": "Num. Shares",
                    "type": "QuantitativeDimension",
                    "description": "Total shares or retweets received by a message's author."
                },
                {
                    "key": "sender_friend_count",
                    "name": "Num. Friends",
                    "type": "QuantitativeDimension",
                    "description": "Number of people a message's author is following."
                },
                {
                    "key": "sender_follower_count",
                    "name": "Num. Followers",
                    "type": "QuantitativeDimension",
                    "description": "Number of people following a message's author."
                },
                {
                    "key": "groups",
                    "name": "Groups",
                    "type": "CategoricalDimension",
                    "description": "Groups of messages."
                }
            ]);
        }
    ]);

})();
