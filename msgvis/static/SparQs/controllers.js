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

    var DimensionController = function ($scope, Dimensions, token_images) {

        /* Rendering helpers, these are basically filters */
        $scope.get_dimension_class = function (dimension) {
            if (dimension.has_token()) {
                return "selected-" + dimension.token.name;
            } else {
                return "";
            }

        };
        $scope.get_filter_class = function (dimension) {
            if (dimension.has_filter()) {
                return "filter-active";
            } else {
                return "";
            }
        };

        $scope.get_token_class = function (token) {
            return "token-" + token.name;
        };


        /* Models */
        $scope.dimensions = Dimensions;

        $scope.tokenTray = [
            {
                name: 'primary',
                image: token_images['primary']
            },
            {
                name: 'secondary',
                image: token_images['secondary']
            }
        ];


        $scope.onTokenTrayDrop = function() {
            console.log("Dropped on tray");
        };

        $scope.onTokenDimensionDrop = function () {
            console.log("Dropped on dimension");
        };

    };

    DimensionController.$inject = ['$scope', 'SparQs.services.Dimensions', 'token_images'];
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

    var SampleQuestionController = function ($scope, $http) {

        dimension_one = "time";
        dimension_two = "hashtags";

        $scope.get_dimension_class = function (dimension_key) {
            console.log(dimension_key);
            if ($scope.dimension_one == dimension_key) return "first-dimension";
            else if ($scope.dimension_two == dimension_key) return "second-dimension";
            else return "";

        };

        $scope.get_sample_questions = function (request) {
            $http.post('/api/questions/', request)
                .success(function (data) {
                    $scope.sample_questions = data;
                });
        };

        $scope.get_sample_questions({
            "dimensions": ["hashtags", "time"]
        });

    };
    SampleQuestionController.$inject = ['$scope', '$http'];
    module.controller('SparQs.controllers.SampleQuestionController', SampleQuestionController);
})();
