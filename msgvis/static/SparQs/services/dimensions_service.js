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
                this.description = [this.name, this.name, this.name].join(', ') + '!';
                this.table = undefined;
                this.domain = undefined;
                this.distribution = undefined;
                this.search_key = "";
                this.search_results = {"": this};

            };

            angular.extend(Dimension.prototype, {
                dimension_class: function() {
                    var cls = "";

                    if (this.zone) {
                        cls += 'dimension-' + this.zone.name;
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
                is_not_applying_filters: function(){
                    return this.filter_type['filter'].is_empty() &&
                           this.filter_type['exclude'].is_empty();
                },
                is_dirty: function(){
                    console.log("is_dirty is called");
                    console.log(this.filter_type['filter'].dirty || this.filter_type['exclude'].dirty);
                    return this.filter_type['filter'].dirty ||
                           this.filter_type['exclude'].dirty;
                },
                load_distribution: function (dataset) {
                    if (this.is_categorical() && !this.table){
                        //$('.level-select-button.all').prop('disabled', true);
                        //$('.level-select-button.none').prop('disabled', false);
                        return this.load_categorical_distribution(dataset);
                    }
                    else if (!this._loading && !this.table) {
                        this._loading = true;

                        var request = {
                            dataset: Dataset.id,
                            dimensions: [this.key]
                        };

                        var apiUrl = djangoUrl.reverse('data-table');

                        var self = this;
                        return $http.post(apiUrl, request)
                            .success(function (data) {
                                var result = data.result;
                                self._loading = false;

                                self.table = result.table;
                                self.domain = result.domains[self.key];
                                self.domain_labels = result.domain_labels[self.key] || {};
                            });
                    }
                },
                get_current_distribution: function(){
                    return this.search_results[this.search_key].distribution;
                },
                load_categorical_distribution: function (dataset) {
                    var self = this;
                    if (!self._loading) {
                        self._loading = true;
                        var target = self;
                        if ( typeof(self.search_key) !== "undefined" && self.search_key !== "" &&
                             typeof(self.search_results[self.search_key]) === "undefined" ){
                            target = {}
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


                        return $http.post(apiUrl, request)
                            .success(function (data) {
                                var result = data.result;
                                self._loading = false;

                                if ( result !== null && typeof(result) !== "undefined" ){
                                    result.table = result.table;
                                    result.domain = result.domains[self.key];
                                    result.domain_labels = result.domain_labels[self.key] || {};
                                    result.distribution = self.get_distribution_in_order(result.table, result.domain, result.domain_labels);

                                    self.add_categorical_distribution(target, result);

                                }
                            });
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
                            level = "No " + self.key;

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
                        return true
                    }
                    return false;
                },
                is_all_unselected: function () {
                    var self = this;
                    if (self.mode == "filter" && (!self.current_filter().levels() || self.current_filter().levels().length == 0)) {
                        return true
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
                }
            });

            return new Dimensions([
                {
                    "key": "time",
                    "name": "Time",
                    "type": "TimeDimension"
                },
                {
                    "key": "timezone",
                    "name": "Timezone",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "topics",
                    "name": "Topics",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "words",
                    "name": "Keywords",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "hashtags",
                    "name": "Hashtags",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "contains_hashtag",
                    "name": "Contains a Hashtag",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "urls",
                    "name": "Urls",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "contains_url",
                    "name": "Contains a Url",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "contains_media",
                    "name": "Contains a Photo",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "language",
                    "name": "Language",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "sentiment",
                    "name": "Sentiment",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "type",
                    "name": "Message Type",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "replies",
                    "name": "Num. Replies",
                    "type": "QuantitativeDimension"
                },
                {
                    "key": "shares",
                    "name": "Num. Shares",
                    "type": "QuantitativeDimension"
                },
                {
                    "key": "mentions",
                    "name": "Mentions",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "contains_mention",
                    "name": "Contains a Mention",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "sender_name",
                    "name": "Author Name",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "sender_message_count",
                    "name": "Num. Messages",
                    "type": "QuantitativeDimension"
                },
                {
                    "key": "sender_reply_count",
                    "name": "Num. Replies",
                    "type": "QuantitativeDimension"
                },
                {
                    "key": "sender_mention_count",
                    "name": "Num. Mentions",
                    "type": "QuantitativeDimension"
                },
                {
                    "key": "sender_share_count",
                    "name": "Num. Shares",
                    "type": "QuantitativeDimension"
                },
                {
                    "key": "sender_friend_count",
                    "name": "Num. Friends",
                    "type": "QuantitativeDimension"
                },
                {
                    "key": "sender_follower_count",
                    "name": "Num. Followers",
                    "type": "QuantitativeDimension"
                }
            ]);
        }
    ]);

})();
