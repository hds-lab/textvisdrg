(function () {
    'use strict';


    var dataset = 1;

    var module = angular.module('SparQs.controllers', [
        'SparQs.services'
    ]);

    module.config(function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    });

    var DimensionController = function ($scope, Dimensions, Tokens) {

        /* Rendering helpers, these are basically filters */
        $scope.get_filter_class = function (dimension) {
            if (dimension.has_filter()) {
                return "filter-active";
            } else {
                return "";
            }
        };

        //Hierarchy of dimensions
        $scope.dimension_groups = [
            {
                "group_name": "Time",
                "dimensions": [
                    Dimensions.get_by_key('time'),
                    Dimensions.get_by_key('timezone')
                ]
            },
            {
                "group_name": "Contents",
                "dimensions": [
                    Dimensions.get_by_key('topics'),
                    Dimensions.get_by_key('keywords'),
                    Dimensions.get_by_key('hashtags'),
                    Dimensions.get_by_key('contains_hashtag'),
                    Dimensions.get_by_key('urls'),
                    Dimensions.get_by_key('contains_url'),
                    Dimensions.get_by_key('contains_media')
                ]
            },
            {
                "group_name": "Meta",
                "dimensions": [
                    Dimensions.get_by_key('language'),
                    Dimensions.get_by_key('sentiment')
                ]
            },
            {
                "group_name": "Interaction",
                "dimensions": [
                    Dimensions.get_by_key('type'),
                    Dimensions.get_by_key('replies'),
                    Dimensions.get_by_key('shares'),
                    Dimensions.get_by_key('mentions'),
                    Dimensions.get_by_key('contains_mention')
                ]
            },
            {
                "group_name": "Author",
                "dimensions": [
                    Dimensions.get_by_key('sender_name'),
                    Dimensions.get_by_key('sender_message_count'),
                    Dimensions.get_by_key('sender_reply_count'),
                    Dimensions.get_by_key('sender_mention_count'),
                    Dimensions.get_by_key('sender_share_count'),
                    Dimensions.get_by_key('sender_friend_count'),
                    Dimensions.get_by_key('sender_follower_count')
                ]
            }
        ];

        //The token tray is a list of token placeholders, which may contain tokens.
        $scope.tokenTray = Tokens.map(function(token) {
            return {
                token: token
            };
        });


        $scope.onTokenTrayDrop = function() {
            console.log("Dropped on tray");
        };

        $scope.onTokenDimensionDrop = function () {
            console.log("Dropped on dimension");
        };

    };

    DimensionController.$inject = ['$scope', 'SparQs.services.Dimensions', 'SparQs.services.Tokens'];
    module.controller('SparQs.controllers.DimensionController', DimensionController);


    var ExampleMessageController = function ($scope, ExampleMessages) {
        var filters = [
            {
                "dimension": "time",
                "min_time": "2015-02-02T01:19:08Z",
                "max_time": "2015-03-02T01:19:09Z"
            }
        ];

        var focus = [
            {
                "dimension": "time",
                "value": "2015-02-02T01:19:09Z"
            }
        ];

        $scope.get_example_messages = function () {
            ExampleMessages.load(dataset, filters, focus);
        };

        $scope.get_example_messages();

    };
    ExampleMessageController.$inject = ['$scope', 'SparQs.services.ExampleMessages'];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SampleQuestionController = function ($scope, Selection, SampleQuestions) {

        $scope.selection = Selection;
        $scope.questions = SampleQuestions;

        $scope.get_sample_questions = function () {
            SampleQuestions.load(Selection.dimensions());
        };

        $scope.get_sample_questions();
    };

    SampleQuestionController.$inject = ['$scope', 'SparQs.services.Selection', 'SparQs.services.SampleQuestions'];
    module.controller('SparQs.controllers.SampleQuestionController', SampleQuestionController);
})();
