"use strict";

var utils = (function() {
    var durationToString = function(duration) {
        var days = Math.floor(duration / (24 * 3600));
        var duration = duration % (24 * 3600)
        var hours = Math.floor(duration / 3600);
        var duration = duration % 3600;
        var minutes = Math.floor(duration / 60);
        var seconds = Math.floor(duration % 60);

        var durationString = [];
        if(days > 0)    {durationString.push(days+"d");}
        if(hours > 0)   {durationString.push(hours+"h");}
        if(minutes > 0) {durationString.push(minutes+"m");}
        if(seconds > 0) {durationString.push(seconds+"s");}

        if (durationString.length == 0) {durationString.push('0s')}

        return durationString.join(' ');
    };

    var csrfSafeMethod = function(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method));
    };

    return {
        durationToString: durationToString,
        csrfSafeMethod: csrfSafeMethod,
    }

})();
