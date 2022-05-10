var lb = (function($, utils) {
    "use strict";
    // all modules
    var modules = {};

    // urls
    var urls = {};

    // init all the required things
    var _init = function() {
        // set ajax to use CSRF token where necessary
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                var csrftoken = $('meta[name=csrf-token]').attr('content');
                if (!utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    };

    /**
     * Register a module for further use
     */
    var registerModule = function(moduleName, module) {
        modules[moduleName] = module;
    };


    /**
     * Call the run function on the specific module
     */
    var run = function(module) {
        _init();
        if(module in modules) {
            if(modules[module]){
                if(modules[module].hasOwnProperty('run')) {
                    modules[module].run();
                }
            }
        }
    };

    return {
        registerModule: registerModule,
        run: run,
        urls: urls,
    };

})(jQuery, utils);
