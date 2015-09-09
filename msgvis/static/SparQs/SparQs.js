/**
 * Top level module for dimension application.
 */
(function () {
    'use strict';

    angular.module('SparQs.bootstrap', []);

    // Declare app level module which depends on other modules
    var app = angular
        .module('SparQs', [
            'SparQs.controllers',
            'SparQs.charts',
            'ngCookies',
            'ngDragDrop',
            'ngAnimate'
        ]);

    //Fix CSRF
    //http://django-angular.readthedocs.org/en/latest/csrf-protection.html
    app.run(['$http', '$cookies', function ($http, $cookies) {
        $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        $http.defaults.headers.put['X-CSRFToken'] = $cookies.csrftoken;
    }]);


})();
