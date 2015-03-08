/**
 * Created by mjbrooks on 2/25/2015.
 */
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

            var Filter = function (data) {
                this.data = data || {};
                this.old_data = angular.copy(this.data);

                this.dirty = false; //true if has unsaved filter changes
            };

            function _getter_setter(prop, format, parse) {
                return function (value) {
                    if (arguments.length > 0) {

                        if (value === '') {
                            value = undefined;
                        }

                        if (this.data[prop] !== value) {
                            this.data[prop] = parse ? parse(value) : value;
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
                }
            });

            // A simple model class for dimensions
            var Dimension = function (data) {
                angular.extend(this, data);

                this.zone = undefined;
                this.draggable = this;

                this.filter = new Filter(this.filter);
                this.filtering = false; //true if currently being filtered
                this.description = [this.name, this.name, this.name].join(', ') + '!';
                this.table = undefined;
                this.domain = undefined;
                this.distribution = undefined;
            };

            angular.extend(Dimension.prototype, {
                dimension_class: function() {
                    var cls = "";

                    if (this.zone) {
                        cls += 'dimension-' + this.zone.name;
                    }

                    if (!this.filter.is_empty()) {
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
                serialize_filter: function () {
                    return angular.extend({
                        dimension: this.key
                    }, this.filter.data);
                },
                set_filtering: function (filtering) {
                    if (this.filtering != filtering) {
                        this.filtering = filtering;

                        if (filtering) {
                            this.load_distribution()
                        }
                    }
                },
                load_distribution: function (dataset) {
                    if (!this._loading && !this.table) {
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

                                self.distribution = self.get_distribution_in_order(self.table, self.domain, self.domain_labels);

                                if (self.is_categorical()) {
                                    self.filter.levels(self.get_categorical_levels().slice(0, self.num_default_show));
                                    self.search = {level: ""}
                                }
                            });
                    }
                },
                get_categorical_levels: function () {
                    var dimension = this;
                    if (dimension.is_categorical()) {
                        var list = dimension.domain.slice(0);
                        for (var i = 0; i < list.length; i++) {
                            if (list[i] == null)
                                list[i] = "No " + dimension.key;
                        }
                        return list;
                    }
                    return undefined;
                },
                get_distribution_in_order: function (table, domain, labels) {
                    if (!table || !domain) {
                        return undefined;
                    }
                    var dimension = this;
                    var distribution_map = {};
                    table.forEach(function (d) {
                        var level = d[dimension.key];
                        distribution_map[level] = d.value;
                    });

                    dimension.num_default_show = 5;

                    return domain.map(function(level, i) {
                        var value = distribution_map[level] || 0;

                        if (level === null || level === "")
                            level = "No " + dimension.key;

                        var label;
                        if (labels && labels.length > i) {
                            label = labels[i];
                        }

                        return {
                            level: level,
                            label: label,
                            value: value,
                            show: (i < dimension.num_default_show)
                        };
                    });
                },
                show_search: function () {
                    return this.is_categorical() && this.domain && this.domain.length > 10;
                },
                unfilter_level: function (d) {
                    d.show = true;
                    this.filter.levels().push(d.level);

                    this.filter.dirty = true;

                },
                change_level: function (d) {
                    if (d.show == true) {
                        this.filter.levels().push(d.level);
                    } else {
                        var idx = this.filter.levels().indexOf(d.level);
                        if (idx != -1) {
                            this.filter.levels().splice(idx, 1);
                        }
                    }
                    this.filter.dirty = true;

                },
                is_all_filtered: function () {
                    if (typeof (this.filter.levels()) !== "undefined") {
                        return this.is_categorical() && this.filter.levels().length == 0;
                    }
                    return false;
                },
                is_not_filtered: function () {
                    if (typeof (this.filter.levels()) !== "undefined") {
                        return this.is_categorical() && this.filter.levels().length == this.domain.length;
                    }
                    return false;
                },
                filtered_all: function (flag) {
                    var dimension = this;
                    if (typeof (dimension.filter.levels()) !== "undefined") {
                        if (flag == true) {
                            dimension.filter.levels([]);
                            dimension.distribution.forEach(function (d) {
                                d.show = false;
                            });
                        }
                        else {
                            dimension.filter.levels(dimension.get_categorical_levels());
                            dimension.distribution.forEach(function (d) {
                                d.show = true;
                            });
                        }
                        dimension.filter.dirty = true;
                    }
                    return false;
                },
                reset_search: function () {
                    var dimension = this;
                    if (dimension.is_categorical()) {
                        dimension.search = {level: ""};
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
                    "key": "keywords",
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
                    "name": "Contains a hashtag",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "urls",
                    "name": "Urls",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "contains_url",
                    "name": "Contains a url",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "contains_media",
                    "name": "Contains a photo",
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
                    "name": "Contains a mention",
                    "type": "CategoricalDimension"
                },
                {
                    "key": "sender_name",
                    "name": "Author name",
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
