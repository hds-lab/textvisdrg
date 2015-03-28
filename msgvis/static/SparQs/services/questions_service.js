(function () {
    'use strict';

    var module = angular.module('SparQs.services');

    //A service for loading sample questions.
    module.factory('SparQs.services.SampleQuestions', [
        '$http', '$sce', '$timeout', 'djangoUrl', 'SparQs.services.Dimensions',
        function sampleQuestionsFactory($http, $sce, $timeout, djangoUrl, Dimensions) {

            var apiUrl = djangoUrl.reverse('research-questions');

            var replace_dim_labels = function (text, dims) {
                var chunks = [];
                var chunk_str = "";
                var chunk_mode = 0;
                var dim_list = [];
                for (var i = 0; i < text.length; i++) {
                    if (text[i] != '\\' && text[i] != '\/') {
                        chunk_str += text[i];
                    }
                    else {
                        var j;
                        if (chunk_mode == 0) {

                            for (j = chunk_str.length - 1; j >= 0; j--) {
                                if (!isNaN(+chunk_str[j]) && 1 <= +chunk_str[j] && +chunk_str[j] <= dims.length) {
                                    dim_list.push(dims[+chunk_str[j] - 1]);
                                }
                                else {
                                    break;
                                }
                            }
                            chunk_str = chunk_str.substr(0, j + 1);
                            chunks.push(chunk_str);
                            chunk_str = "";
                            chunk_mode = 1;
                        } else {
                            var str_with_dims = "<span class='question-tag ";
                            for (j = 0; j < dim_list.length; j++) {
                                if (typeof (dim_list[j]) === "undefined") continue;
                                if (j > 0) str_with_dims += " ";
                                str_with_dims += dim_list[j].key;


                            }
                            str_with_dims += "'>";
                            str_with_dims += chunk_str;
                            str_with_dims += "<\/span>";
                            chunks.push(str_with_dims);
                            chunk_str = "";
                            dim_list = [];
                            chunk_mode = 0;
                        }

                    }
                }
                if (chunk_str.length > 0)
                    chunks.push(chunk_str);
                return chunks.join('');
            };

            //A model class for sample questions
            var Question = function (data) {
                angular.extend(this, data);

                //Hook up the dimensions to the question
                this.dimensions = this.dimensions.map(function (dimkey) {
                    return Dimensions.get_by_key(dimkey);
                });

                this.text = $sce.trustAsHtml(replace_dim_labels(this.text, this.dimensions));
            };

            var SampleQuestions = function () {
                this.current = undefined;
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
                    return $http.post(apiUrl, request)
                        .success(function (data) {
                            var question = data.questions.slice(0, 1)
                                .map(function (qdata) {
                                    return new Question(qdata);
                                });

                            self.current = question.length ? question[0] : undefined;

                            $timeout(function() {
                                $('.source-popover').popover({html: true})
                            }, 10);
                        });

                }
            });

            return new SampleQuestions();
        }
    ]);
})();
