(function () {
    'use strict';


    var module = angular.module('SparQs.controllers', [
        'SparQs.services'
    ]);

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

        $scope.openFilter = function(dimension, $event) {
            var offset;
            if ($event) {
                var $el = $($event.target).parents('.dimension');
                if ($el) {
                    offset = $el.offset();
                }
            }

            Filtering.toggle(dimension, offset);
        }
    };

    DimensionController.$inject = [
        '$scope',
        'SparQs.services.Dimensions',
        'SparQs.services.Filtering',
        'SparQs.services.Tokens',
        'SparQs.services.Selection'];
    module.controller('SparQs.controllers.DimensionController', DimensionController);


    var ExampleMessageController = function ($scope, ExampleMessages, Selection, Dataset) {

        $scope.messages = ExampleMessages;

        $scope.get_example_messages = function () {
            var filters = Selection.filters();
            var focus = Selection.focus();
            ExampleMessages.load(Dataset.id, filters, focus);
        };

        Selection.changed('filters,focus', $scope, $scope.get_example_messages);

    };
    ExampleMessageController.$inject = [
        '$scope',
        'SparQs.services.ExampleMessages',
        'SparQs.services.Selection',
        'SparQs.services.Dataset'
    ];
    module.controller('SparQs.controllers.ExampleMessageController', ExampleMessageController);

    var SampleQuestionController = function ($scope, $timeout, Selection, SampleQuestions) {

        $scope.questions = SampleQuestions;
        $scope.selection = Selection;

        $scope.get_sample_questions = function () {
            SampleQuestions.load(Selection.dimensions());

        };

        $scope.$watch('questions.list', function(){
            //When the question list changes, we are going to manually (jQuery)
            //update the token classes so that they end up the right color.
            //.question-dim are the dimension tags inside the research questions.
            //The .token-primary and .toke-secondary tags indicate which .question-dim
            //should be colored which way.
            //The timeout ensures that this runs *after* the new questions have been rendered.
            $timeout(function() {
                $('.question-dim.token-primary').removeClass('token-primary');
                $('.question-dim.token-secondary').removeClass('token-secondary');
                var dims = $scope.selection.dimensions();
                dims.forEach(function(dim) {
                    $('.question-dim.' + dim.key).addClass(dim.token_class());
                });
            }, 0);

        });

        $scope.get_sample_questions();

        Selection.changed('dimensions', $scope, $scope.get_sample_questions);

        //$scope.$watch('selection.dimensions()', function() {
        //    $scope.get_sample_questions();
        //}, true);
    };

    SampleQuestionController.$inject = [
        '$scope',
        '$timeout',
        'SparQs.services.Selection',
        'SparQs.services.SampleQuestions'
    ];
    module.controller('SparQs.controllers.SampleQuestionController', SampleQuestionController);

    var VisualizationController = function ($scope, Selection, DataTables, Dataset) {

        $scope.datatable = DataTables;
        $scope.selection = Selection;

        $scope.get_data_table = function () {
            var dimensions = Selection.dimensions();
            var filters = Selection.filters();
            DataTables.load(Dataset.id, dimensions, filters);
        };

        $scope.get_data_table();

        Selection.changed('dimensions,filters', $scope, $scope.get_data_table);

        $scope.onVisClicked = function() {
            console.log(arguments);
        };

    };

    VisualizationController.$inject = [
        '$scope',
        'SparQs.services.Selection',
        'SparQs.services.DataTables',
        'SparQs.services.Dataset'
    ];
    module.controller('SparQs.controllers.VisualizationController', VisualizationController);

    //Extends DimensionsController
    var FilterController = function ($scope, Filtering, Selection) {
        $scope.filtering = Filtering;

        $scope.closeFilter = function() {
            Filtering.toggle();
        };

        $scope.saveFilter = function () {
            if (Filtering.dimension.filter.dirty) {
                Selection.changed('filters');
                Filtering.dimension.filter.saved();
            }
        };

        $scope.resetFilter = function () {
            if (!Filtering.dimension.filter.is_empty()) {
                if (Filtering.dimension.is_categorical()){
                    Filtering.dimension.filtered_all(false);
                    if ( typeof(Filtering.dimension.search) != "undefined")
                        Filtering.dimension.search.level = "";
                }else{
                    Filtering.dimension.filter.reset();
                }
                Selection.changed('filters');
                Filtering.dimension.filter.saved();
            }
        };

        $scope.onQuantitativeBrushed = function(min, max) {
            $scope.$digest();
        }


    };

    FilterController.$inject = [
        '$scope',
        'SparQs.services.Filtering',
        'SparQs.services.Selection'
    ];
    module.controller('SparQs.controllers.FilterController', FilterController);

    module.directive('datetimeFormat', function() {
      return {
        require: 'ngModel',
        link: function(scope, element, attrs, ngModelController) {
          ngModelController.$parsers.push(function(data) {
            //convert data from view format to model format
            return data; //converted
          });

          ngModelController.$formatters.push(function(data) {
            //convert data from model format to view format
              if ( typeof(data) !== "undefined" )
                return moment(data).utc().format("YYYY-MM-DD HH:mm:ss"); //converted
              return data;
          });
        }
      }
    });
})();
