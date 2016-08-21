var researchBlueprint = (function($, lb, utils, eveUtils, Humanize, JSON) {
    "use strict"

    // researchTime = baseResearchTime * timeModifier * levelModifier / 105
    // researchFee = baseJobCost * systemCostIndex * 0.02 * levelModifier / 105
    // copyTime = baseCopyTime * runs * runsPerCopy * timeModifier
    // copyFee = baseJobCost * systemCostIndex * 0.02 * runs * runsPerCopy
    // timeModifier = implant * factory * skills
    // levelModifier = 250*2^(1,25*<level>-2,5)
    var ACTIVITY_RESEARCHING_TIME_EFFICIENCY = 3;
    var ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY = 4;
    var ACTIVITY_COPYING = 5;

    var options = {
        // base values
        baseCost: 0,
        baseCopyTime: 0,
        baseMeTime: 0,
        baseTeTime: 0,
        // indexes
        indexes: {},
        
        // ME speed (5%)
        metallurgyLevel: 0,
        // TE speed (5%)
        researchLevel: 0,
        // copy speed (5%)
        scienceLevel: 0,
        // adv industry (3%)
        advancedIndustryLevel: 0,
        
        // implants
        meImplant: 0,
        teImplant: 0,
        copyImplant: 0,
        
        // facility
        facility: 0,
        // starting ME
        materialEfficiency: 0,        
        // starting TE
        timeEfficiency: 0,
        // copy data
        copyNumber: 1,
        runPerCopy: 1,
        maxRunPerCopy: 1,
        // system
        system: "Jita",
    };

    $.extend(lb.urls, {
        systemUrls: false,
        indexActivityUrl: false,
    });

    // assembly informations
    var facilityStats = [
        { // station
            "me": 1.0,
            "te": 1.0,
            "copy": 1.0,
            "name": 'Station',
        },
        { // Laboratory
            "me": 0.7,
            "te": 0.7,
            "copy": 0.6,
            "name": 'Laboratory',
        },
        { // Hyasyoda Laboratory
            "me": 0.65,
            "te": 0.65,
            "copy": 0.6,
            "name": 'Hyasyoda Laboratory',
        },
    ];
    
   


    /**
     * Init input fields
     * @private
     */
    var _initInputs = function() {
        // checks and update on copy numbers
        $('#copy-number').on('keyup', _copyNumberOnKeyUp)
                         .on('change', _copyNumberOnChange);
                         
        $('#run-per-copy').on('keyup', _runPerCopyOnKeyUp)
                          .on('change', _runPerCopyOnChange);
                          

        $('#facility').on('change', function() {
            options.facility = parseInt($('#facility').val());
        });              

        $('#meImplant').on('change', function() {
            options.meImplant = parseFloat($('#meImplant').val());
        });              

        $('#teImplant').on('change', function() {
            options.teImplant = parseFloat($('#teImplant').val());
        });
        
        $('#copyImplant').on('change', function() {
            options.copyImplant = parseFloat($('#copyImplant').val());
        });
    };

    var _copyNumberOnKeyUp = function(event) {
        if(!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.copyNumber = 1;
        } else {
            options.copyNumber = parseInt($(this).val());
        }
        $(this).val(options.copyNumber);
    }
    
    var _copyNumberOnChange = function(event) {
        $(this).val(options.copyNumber);
        return false; 
    }
    
    var _runPerCopyOnKeyUp = function(event) {
        if(!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.runPerCopy = 1;
        } else if($(this).val() > options.maxRunPerCopy) {
            options.runPerCopy = options.maxRunPerCopy;
        } else {
            options.runPerCopy = parseInt($(this).val());
        }
        $(this).val(options.runPerCopy);
    }
    
    var _runPerCopyOnChange = function(event) {
        $(this).val(options.runPerCopy);
        return false;
    }
    
    /**
     * Init typeahead objects
     * @private
     */
    var _initTypeahead = function() {
        var systems = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            limit: 10,
            prefetch: {
                url: lb.urls.systemUrls,
                filter: function(listResult) {
                    return $.map(listResult['result'], function(system) { return { name: system }; });
                }
            }
        });
        systems.initialize();

        var typeaheadEventSelector = "change typeahead:selected typeahead:autocompleted";
        $('#system').typeahead(null,{
            name: 'system',
            displayKey: 'name',
            source: systems.ttAdapter(),
        }).on(typeaheadEventSelector, function(event, suggestion) {
            options.system = $(this).typeahead('val');
        });
    };


    /**
     * Init all sliders on the page
     * @private
     */
    var _initSliders = function() {
        $('#ME').slider({
            min: 0,
            max: 10,
            range: "min",
            slide: _materialEfficiencyOnUpdate,
        });
        $('#TE').slider({
            min: 0,
            max: 20,
            step: 2,
            range: "min",
            slide: _timeEfficiencyOnUpdate,
        });
        $('#adv-industry-level, #research-level, #science-level, #metallurgy-level').slider({
            min: 0,
            max: 5,
            range: "min",
            slide: _skillOnUpdate,
        });
    };
    
    /**
     * Function called on event update on the material efficiency slider
     * @private
     */
    var _materialEfficiencyOnUpdate = function(event, ui) {
        $('#ME-Level').html(ui.value+"%");
        options.materialEfficiency = parseInt(ui.value);
    };


    /**
     * Function called on event update on the time efficiency slider
     * @private
     */
    var _timeEfficiencyOnUpdate = function(event, ui) {
        $('#TE-Level').html(ui.value+"%");
        options.timeEfficiency = parseInt(ui.value);
    };

    
    /**
     * Function called on event update on the skill level sliders
     * @private
     */
    var _skillOnUpdate = function(event, ui) {
        var id = $(this).attr('id');
        var value = parseInt(ui.value);

        switch(id) {
            case 'adv-industry-level':
                options.advancedIndustryLvl = value;
                $('#adv-industry-level-display').html(value);
                break;

            case 'research-level':
                options.researchLevel = value;
                $('#research-level-display').html(value);
                break;

            case 'science-level':
                options.scienceLevel = value;
                $('#science-level-display').html(value);
                break;

            case 'metallurgy-level':
                options.metallurgyLevel = value;
                $('#metallurgy-level-display').html(value);
                break;
        };
    };
    
    
    /**
     * Runner function
     */
    var run = function() {
        _initInputs();
        _initSliders();
        
        $('#tab-links a').click(function (e) {
            e.preventDefault()
            $(this).tab('show')
        });
        
        // check all required urls (so we don't have to do it later)
        if(!lb.urls.systemUrls || !lb.urls.indexActivityUrl) {
            alert('Error, some URL are missing, this application cannot work properly without them.');
            return;
        }

        // other init that require ajax call
        _initTypeahead();
        
    };


    // -------------------------------------------------
    // return object
    //
    return {
        // required objects
        options: options,

        // functions
        run: run,
    };
})(jQuery, lb, utils, eveUtils, Humanize, JSON);

lb.registerModule('researchBlueprint', researchBlueprint);
