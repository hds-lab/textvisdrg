(function () {
    'use strict';

    var module = angular.module('dimensions.controllers', [

    ]);

    var requires = ['$scope'
      ];
    var DimensionController = function ($scope) {

        $scope.$watch(function(){
            console.log("digest called");
        });

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


    DimensionController.$inject = requires;
    module.controller('dimensions.controllers.dimensionController', DimensionController);


})();
