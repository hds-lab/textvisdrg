(function () {
    'use strict';


    var module = angular.module('SparQs.controllers', [
        'SparQs.services'
    ]);

    //Hard coded dataset id for now
    module.constant('SparQs.bootstrap', {
        dataset: 1
    });

    module.config(function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    });

    var DimensionController = function ($scope, Dimensions, Filtering, Tokens, Selection) {

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
        $scope.tokenTray = Tokens.map(function (token) {
            return {
                token: token
            };
        });

        $scope.onTokenTrayDrop = function () {
            console.log("Dropped on tray");
            Selection.changed('dimensions');
        };

        $scope.onTokenDimensionDrop = function () {
            console.log("Dropped on dimension");
            Selection.changed('dimensions');
        };

        $scope.filtering = Filtering
    };

    DimensionController.$inject = [
        '$scope',
        'SparQs.services.Dimensions',
        'SparQs.services.Filtering',
        'SparQs.services.Tokens',
        'SparQs.services.Selection'];
    module.controller('SparQs.controllers.DimensionController', DimensionController);


    var ExampleMessageController = function ($scope, ExampleMessages, Selection, bootstrap) {

        var dataset = bootstrap.dataset;

        $scope.messages = ExampleMessages;

        $scope.get_example_messages = function () {
            var filters = Selection.filters();
            var focus = Selection.focus();
            ExampleMessages.load(dataset, filters, focus);
        };

        Selection.changed('filters,focus', $scope, $scope.get_example_messages);
        /*
         $scope.$watch('selection.filters()', function() {
         $scope.get_example_messages();
         }, true);

         $scope.$watch('selection.focus()', function() {
         $scope.get_example_messages();
         }, true);
         */
    };
    ExampleMessageController.$inject = [
        '$scope',
        'SparQs.services.ExampleMessages',
        'SparQs.services.Selection',
        'SparQs.bootstrap'
    ];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SampleQuestionController = function ($scope, Selection, SampleQuestions) {

        $scope.questions = SampleQuestions;
        $scope.selection = Selection;

        $scope.get_sample_questions = function () {
            SampleQuestions.load(Selection.dimensions());
        };

        $scope.get_sample_questions();

        Selection.changed('dimensions', $scope, $scope.get_sample_questions);

        //$scope.$watch('selection.dimensions()', function() {
        //    $scope.get_sample_questions();
        //}, true);
    };

    SampleQuestionController.$inject = [
        '$scope',
        'SparQs.services.Selection',
        'SparQs.services.SampleQuestions'
    ];
    module.controller('SparQs.controllers.SampleQuestionController', SampleQuestionController);

    var VisualizationController = function ($scope, Selection, DataTables, bootstrap) {

        var dataset = bootstrap.dataset;

        $scope.datatable = DataTables;
        $scope.selection = Selection;

        $scope.get_data_table = function () {
            var dimensions = Selection.dimensions();
            var filters = Selection.filters();
            DataTables.load(dataset, dimensions, filters);
        };

        $scope.get_data_table();

        Selection.changed('dimensions,filters', $scope, $scope.get_data_table);

        //$scope.$watch('selection.dimensions()', function() {
        //    $scope.get_data_table();
        //}, true);
        //
        //$scope.$watch('selection.filters()', function() {
        //    $scope.get_data_table();
        //}, true);
    };

    VisualizationController.$inject = [
        '$scope',
        'SparQs.services.Selection',
        'SparQs.services.DataTables',
        'SparQs.bootstrap'
    ];
    module.controller('SparQs.controllers.VisualizationController', VisualizationController);

    //Extends DimensionsController
    var FilterController = function ($scope, Filtering, Selection) {
        $scope.filtering = Filtering;

        $scope.saveFilter = function() {
            if ($scope.filtering.dimension.filter.dirty) {
                Selection.changed('filters');
                $scope.filtering.dimension.filter.saved();
            }
        };

        $scope.resetFilter = function() {
            if (!$scope.filtering.dimension.filter.is_empty()) {
                $scope.filtering.dimension.filter.reset()
                Selection.changed('filters');
                $scope.filtering.dimension.filter.saved();
            }
        };
    };

    FilterController.$inject = [
        '$scope',
        'SparQs.services.Filtering',
        'SparQs.services.Selection'
    ];
    module.controller('SparQs.controllers.FilterController', FilterController);
})();
