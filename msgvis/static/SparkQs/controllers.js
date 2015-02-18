(function () {
    'use strict';

    var module = angular.module('SparkQs.controllers', []);


    var DimensionController = function ($scope) {

        $scope.dimension_groups = [
            {
                "group_name": "Time",
                "dimensions": [
                    {
                        "name": "Time",
                        "type": "TimeDimension"
                    },
                    {
                        "name": "Timezone",
                        "type": "CategoricalDimension"
                    }
                ]
            },
            {
                "group_name": "Contents",
                "dimensions": [
                    {
                        "name": "Topics",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Keywords",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Hashtags",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Contains Hashtags",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "URLs",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Contains URLs",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Contains Media",
                        "type": "CategoricalDimension"
                    },
                ]
            },
            {
                "group_name": "Meta",
                "dimensions": [
                    {
                        "name": "Language",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Sentiment",
                        "type": "CategoricalDimension"
                    }
                ]
            },
            {
                "group_name": "Interaction",
                "dimensions": [
                    {
                        "name": "Message Type",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Replies (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Retweets (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Mentions (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Mentioned User Name",
                        "type": "CategoricalDimension"
                    },
                ]
            },
            {
                "group_name": "Author",
                "dimensions": [
                    {
                        "name": "Name",
                        "type": "CategoricalDimension"
                    },
                    {
                        "name": "Authored Messages (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Replied to (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Mentioned (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Retweeted (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Friends (Count)",
                        "type": "QuantitativeDimension"
                    },
                    {
                        "name": "Followers (Count)",
                        "type": "QuantitativeDimension"
                    },
                ]
            },
        ];

    };
    DimensionController.$inject = ['$scope'];
    module.controller('SparkQs.controllers.dimensionController', DimensionController);


    var ExampleMessageController = function($scope, $http){

        $scope.get_example_messages = function(request){
            $http.post('/api/message/', request)
                .success(function(data) {
                     $scope.example_messages = data;
                });
        }

        $scope.get_example_messages({
              "dimensions": ["time", "hashtags"],
              "filters": [
                {
                  "dimension": "time",
                  "min_time": "2015-02-02T01:19:08Z",
                  "max_time": "2015-02-02T01:19:09Z"
                }
              ],
              "focus": [
                {
                  "dimension": "time",
                  "value": "2015-02-02T01:19:09Z"
                }
              ]
            });

     };
    ExampleMessageController.$inject = ['$scope', '$http'];
    module.controller('SparkQs.controllers.exampleMessageController', ExampleMessageController);

})();
