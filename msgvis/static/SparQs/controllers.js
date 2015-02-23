(function () {
    'use strict';

    var module = angular.module('SparQs.controllers', [
        'SparQs.services'
    ]);

    module.config(function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    });


    var dimension_one = "time";
    var dimension_two = "hashtags";

    var DimensionController = function ($scope, Dimensions, Tokens) {

        /* Rendering helpers, these are basically filters */
        $scope.get_filter_class = function (dimension) {
            if (dimension.has_filter()) {
                return "filter-active";
            } else {
                return "";
            }
        };

        /* Models */
        $scope.dimensions = Dimensions;

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


    var ExampleMessageController = function ($scope, $http) {

        $scope.get_example_messages = function (request) {
            $http.post('/api/message/', request)
                .success(function (data) {
                    $scope.example_messages = data;
                });
        };

        $scope.get_example_messages({
            "dataset": 1,
            "dimensions": ["time", "hashtags"],
            "filters": [
                {
                    "dimension": "time",
                    "min_time": "2015-02-02T01:19:08Z",
                    "max_time": "2015-03-02T01:19:09Z"
                }
            ],
            //"focus": [
            //    {
            //        "dimension": "time",
            //        "value": "2015-02-02T01:19:09Z"
            //    }
            //]
        });

    };
    ExampleMessageController.$inject = ['$scope', '$http'];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SampleQuestionController = function ($scope, Selection, SampleQuestions) {

        $scope.get_sample_questions = function (request) {
            $scope.questions.load(Selection.dimensions);
        };

        $scope.selection = Selection;
        $scope.questions = SampleQuestions;
        $scope.questions.load(Selection.dimensions);

    };
    SampleQuestionController.$inject = ['$scope', 'SparQs.services.Selection', 'SparQs.services.SampleQuestions'];
    module.controller('SparQs.controllers.SampleQuestionController', SampleQuestionController);
})();
