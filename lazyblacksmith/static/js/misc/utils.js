var utils = (function($) {
    "use strict";

    var flashMessageType = {
        'info': 'fa fa-info-circle',
        'success': 'fa fa-check-circle',
        'warning': 'fa fa-exclamation-triangle',
        'danger': 'fa fa-exclamation-circle',
    };

    var defaultErrorCallback = function(errorObject) {
        var jsonResponse = errorObject.responseJSON;
        flashNotify(jsonResponse.message, jsonResponse.status);
    };

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

    /**
     * Display a flash message using grawl like notifications.
     */
    var flashNotify = function(message, type) {
        var finalType = type;
        if(!(type in flashMessageType)) {
            finalType = 'info';
        }

        $.notify({
            icon: flashMessageType[finalType],
            message: message,
        }, {
            type: finalType,
            allow_dismiss: true,
            offset: {
                x: 20,
                y: 60,
            },
        });
    };

    /**
     * Copy a given text into clipboard using textarea trick.
     * @param text the text we want to copy
     */
    var copyToClipboard = function(text) {
        $('body').append('<textarea id="clipboard" style="height:1px; width:1px; position: fixed; top:0; left:0; border: none; outline:none; background: transparent"></textarea>');
        $('#clipboard').val(text);
        $('#clipboard')[0].select();
        try {
            var successful = document.execCommand('copy');
            if (successful) {
                flashNotify('Multibuy copied to clipboard.', 'success');
            } else {
                flashNotify('Copy to clipboard failed.', 'danger');
            }
        } catch(err) {
            flashNotify('Copy to clipboard failed.', 'danger');
        }
        $('#clipboard').remove();
    };


    /**
     * Generic ajax get call, without data parameters with json dataType as result
     * @param url the url to call
     * @param callback function to call when ajax call succeed
     */
    var ajaxGetCallJson = function(url, successCallback, errorCallback) {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: successCallback,
            error: errorCallback || defaultErrorCallback,
        });
    };

    /**
     * Generic ajax post call, with json dataType as result
     * also setting content-type to application/json
     * @param url the url to call
     * @param callback function to call when ajax call succeed
     */
    var ajaxPostCallJson = function(url, data, successCallback, errorCallback) {
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: data,
            success: successCallback,
            error: errorCallback || defaultErrorCallback
        });
    };

    /**
     * Generic ajax get call, without data parameters with json dataType as result
     * @param url the url to call
     * @param callback function to call when ajax call succeed
     */
    var ajaxDeleteCallJson = function(url, successCallback, errorCallback) {
        $.ajax({
            url: url,
            type: 'DELETE',
            dataType: 'json',
            success: successCallback,
            error: errorCallback || defaultErrorCallback
        });
    };

    return {
        durationToString: durationToString,
        csrfSafeMethod: csrfSafeMethod,
        flashNotify: flashNotify,
        copyToClipboard: copyToClipboard,

        ajaxDeleteCallJson: ajaxDeleteCallJson,
        ajaxPostCallJson: ajaxPostCallJson,
        ajaxGetCallJson: ajaxGetCallJson,
    }

})(jQuery);
