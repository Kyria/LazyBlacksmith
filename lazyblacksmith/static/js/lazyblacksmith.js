var LazyBlacksmith = {
    // loader is the namespace that will be loaded on page load
    loader: false,

    // utils functions
    utils: {
        durationToString: function(duration) {
            days = Math.floor(duration / (24 * 3600));
            duration = duration % (24 * 3600)
            hours = Math.floor(duration / 3600);
            duration = duration % 3600;
            minutes = Math.floor(duration / 60);
            seconds = Math.floor(duration % 60);
            
            durationString = [];
            if(days > 0)    {durationString.push(days+"d");} 
            if(hours > 0)   {durationString.push(hours+"h");}
            if(minutes > 0) {durationString.push(minutes+"m");}
            if(seconds > 0) {durationString.push(seconds+"s");}
            
            if (durationString.length == 0) {durationString.push('0s')}
            
            return durationString.join(' ');
        },
        
        csrfSafeMethod: function(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        },
   
    },
    
    // define the loader to be called
    setLoader: function(loader) {
        LazyBlacksmith.loader = loader;
    },
    
    // init / set all the things then call the loader
    load: function() {
        LazyBlacksmith.init();
        if(LazyBlacksmith.loader){
            if(LazyBlacksmith.loader.hasOwnProperty('onload')) {
                LazyBlacksmith.loader.onload();
            }
        }
    },
    
    // init all the required things
    init: function() {
        // set ajax to use CSRF token where necessary
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                var csrftoken = $('meta[name=csrf-token]').attr('content');
                if (!LazyBlacksmith.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    },
}