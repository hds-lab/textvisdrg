(function () {
    'use strict';

    var module = angular.module('SparQs.services', ['ng.django.urls']);

    //The collection of tokens.
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
                    order: 0,
                    name: 'primary',
                    image: token_images['primary']
                }),
                new Token({
                    order: 1,
                    name: 'secondary',
                    image: token_images['secondary']
                })
            ];
        }
    ]);

    //The collection of dimennsions.
    //Dimension objects have some extra functionality added.
    module.factory('SparQs.services.Dimensions', [
        function () {

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

    //A service for summarizing the state of the current selection,
    //including selected dimensions, filters, and focus.
    module.factory('SparQs.services.Selection', [
        'SparQs.services.Dimensions',
        function selectionFactory(Dimensions) {

            var test_filters = [
                {
                    "dimension": "time",
                    "min_time": "2015-02-02T01:19:08Z",
                    "max_time": "2015-03-02T01:19:09Z"
                }
            ];

            var test_focus = [
                //{
                //    "dimension": "time",
                //    "value": "2015-02-02T01:19:09Z"
                //}
            ];


            var Selection = function () {

            };

            angular.extend(Selection.prototype, {
                dimensions: function () {
                    var with_token = Dimensions.get_with_token();

                    //Sort by the token order
                    with_token.sort(function (d1, d2) {
                        return d1.token().order - d2.token().order;
                    });
                    return with_token;
                },
                filters: function () {
                    return test_filters;
                },
                focus: function () {
                    return test_focus;
                }
            });

            return new Selection();
        }
    ]);

    //A service for loading sample questions.
    module.factory('SparQs.services.SampleQuestions', [
        '$http', 'djangoUrl', 'SparQs.services.Dimensions',
        function sampleQuestionsFactory($http, djangoUrl, Dimensions) {

            var apiUrl = djangoUrl.reverse('research-questions');

            //A model class for sample questions
            var Question = function (data) {
                angular.extend(this, data);

                //Hook up the dimensions to the question
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
                            self.list = data.questions.map(function(qdata) {
                                return new Question(qdata);
                            });
                        });
                }
            });

            return new SampleQuestions();
        }
    ]);

    //A service for loading example messages.
    module.factory('SparQs.services.ExampleMessages', [
        '$http', 'djangoUrl',
        function sampleQuestionsFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('example-messages');

            //A model class for messages
            var Message = function (data) {
                angular.extend(this, data);
            };

            var ExampleMessages = function () {
                this.list = [];
            };

            angular.extend(ExampleMessages.prototype, {
                load: function (dataset, filters, focus) {

                    var request = {
                        dataset: dataset,
                        filters: filters,
                        focus: focus
                    };

                    var self = this;
                    $http.post(apiUrl, request)
                        .success(function (data) {
                            self.list = data.messages.map(function(msgdata) {
                                return new Message(msgdata);
                            });
                        });
                }
            });

            return new ExampleMessages();
        }
    ]);

})();
