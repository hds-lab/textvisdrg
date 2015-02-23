(function () {
    'use strict';

    var module = angular.module('SparQs.services', ['ng.django.urls']);

    module.factory('SparQs.services.Tokens', [
        'token_images',
        function tokensFactory(token_images) {

            var Token = function (data) {
                angular.extend(this, data);
            };

            angular.extend(Token.prototype, {
                token_class: function () {
                    return "token-" + this.name;
                }
            });

            return [
                new Token({
                    name: 'primary',
                    image: token_images['primary']
                }),
                new Token({
                    name: 'secondary',
                    image: token_images['secondary']
                })
            ]
        }
    ]);

    module.factory('SparQs.services.Dimensions', [
        function () {

            var dimension_groups = [
                {
                    "group_name": "Time",
                    "dimensions": [
                        {
                            "key": "time",
                            "name": "Time",
                            "type": "TimeDimension"
                        },
                        {
                            "key": "timezone",
                            "name": "Timezone",
                            "type": "CategoricalDimension"
                        }
                    ]
                },
                {
                    "group_name": "Contents",
                    "dimensions": [
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
                        }
                    ]
                },
                {
                    "group_name": "Meta",
                    "dimensions": [
                        {
                            "key": "language",
                            "name": "Language",
                            "type": "CategoricalDimension"
                        },
                        {
                            "key": "sentiment",
                            "name": "Sentiment",
                            "type": "CategoricalDimension"
                        }
                    ]
                },
                {
                    "group_name": "Interaction",
                    "dimensions": [
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
                        }
                    ]
                },
                {
                    "group_name": "Author",
                    "dimensions": [
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
                    ]
                }
            ];

            // A simple model class for dimensions
            var Dimension = function (data) {
                angular.extend(this, data);

                this.token_holder = {};
                this.filter = undefined;
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
                has_filter: function () {
                    return this.filter;
                }
            });

            //The actual dimension service class
            var Dimensions = function (dimension_groups) {
                this.by_key = {};
                var self = this;

                //Instantiate Dimensions
                dimension_groups.forEach(function (grp) {
                    grp.dimensions = grp.dimensions.map(function (dimdata) {
                        var dim = new Dimension(dimdata);
                        self.by_key[dim.key] = dim;
                        return dim;
                    })
                });

                this.groups = dimension_groups;
            };

            angular.extend(Dimensions.prototype, {
                get_by_key: function (key) {
                    return this.by_key[key];
                }
            });

            return new Dimensions(dimension_groups);
        }
    ]);

    module.factory('SparQs.services.Selection', [
        function selectionFactory() {
            var Selection = function () {
                this.dimensions = [];
                this.filters = [];
                this.focus = [];
            };

            return new Selection();
        }
    ]);

    module.factory('SparQs.services.SampleQuestions', [
        '$http', 'djangoUrl', 'SparQs.services.Dimensions',
        function sampleQuestionsFactory($http, djangoUrl, Dimensions) {

            var apiUrl = djangoUrl.reverse('research-questions');

            //A model class for sample questions
            var SampleQuestion = function (data) {
                angular.extend(this, data);

                //Hook up the dimensions
                this.dimensions = this.dimensions.map(function (dimkey) {
                    return Dimensions.get_by_key(dimkey);
                });
            };

            var SampleQuestions = function () {
                this.list = [];
            };

            angular.extend(SampleQuestions.prototype, {
                load: function (dimensions) {
                    var dimension_keys = dimensions.map(function (d) {
                        return d.key
                    });

                    var request = {
                        dimensions: dimension_keys
                    };

                    var self = this;
                    $http.post(apiUrl, request)
                        .success(function (data) {
                            self.list = data;
                        });
                }
            });

            return new SampleQuestions();
        }
    ]);

})();
