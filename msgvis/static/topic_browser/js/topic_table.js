/**
 * Created by mjbrooks on 11/20/2014.
 */
(function () {

    var shadeWords = function(words) {
        var probMax = 0;
        words.each(function() {
            var prob = +$(this).data('probability');
            if (prob > probMax) {
                probMax = prob;
            }
        });

        var probability = d3.scale.linear()
            .range(['white', 'green'])
            .domain([0, probMax]);

        words.each(function() {
            var $this = $(this);
            $this.css({
                'background-color': probability(+$this.data('probability'))
            });
        });
    };

    $(document).ready(function() {
        var topicTable = $('.topics-table');
        if (topicTable.size()) {
            shadeWords(topicTable.find('.word'));
        }

        var wordList = $('.word-list');
        if (wordList.size()) {
            shadeWords(wordList.find('.word'));
        }
    });
})();