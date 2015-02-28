/**
 * Created by mjbrooks on 2/25/2015.
 */
(function () {
    'use strict';

    var module = angular.module('SparQs.services');

    //The collection of dimensions.
    //Dimension objects have some extra functionality added.
    module.factory('SparQs.services.Dimensions', [
        'SparQs.services.DimensionDistributions',
        function (DimensionDistributions) {

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
                return function(value) {
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

                this.token_holder = {};
                this.filter = new Filter(this.filter);
                this.filtering = false; //true if currently being filtered
                this.description = [this.name, this.name, this.name].join(', ') + '!';
                this.distribution = undefined;
            };

            angular.extend(Dimension.prototype, {
                token: function () {
                    // Get the token on this dimension, or null.
                    return this.token_holder.token;
                },
                token_class: function () {
                    var token = this.token();
                    return token ? token.token_class() : "";
                },
                filter_class: function () {
                    var cls = this.filter.is_empty() ? '' : 'filter-applied';
                    if (this.filtering) {
                        cls += ' filtering-open';
                    }
                    return cls;
                },
                is_quantitative: function () {
                    return this.type == 'QuantitativeDimension';
                },
                serialize_filter: function () {
                    return angular.extend({
                        dimension: this.key
                    }, this.filter.data);
                },
                set_filtering: function(filtering) {
                    if (this.filtering != filtering) {
                        this.filtering = filtering;

                        if (filtering) {
                            this.load_distribution()
                        }
                    }
                },
                load_distribution: function (dataset) {
                    if (!this._loading && !this.distribution) {
                        this._loading = true;
                        DimensionDistributions.load(this);
                    }
                },
                set_distribution: function(distribution) {
                    this._loading = false;
                    this.distribution = distribution;
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
                get_with_token: function () {
                    return this.list.filter(function (dim) {
                        return dim.token();
                    });
                },
                get_with_filters: function () {
                    return this.list.filter(function (dim) {
                        return !dim.filter.is_empty();
                    });
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
