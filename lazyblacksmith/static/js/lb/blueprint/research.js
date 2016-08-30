var researchBlueprint = (function($, lb, utils, eveUtils, Humanize) {
    "use strict"

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
        meImplant: 1.00,
        teImplant: 1.00,
        copyImplant: 1.00,
        
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
     * Get the indexes of the missing solar systems
     * @private
     */
    var _getSystemCostIndex = function() {
        if(options.system in options.indexes) {
            _updateResearchTimeAndCost();
            _updateCopyTimeAndCost();
            return;
        }
        
        var url = lb.urls.indexActivityUrl.replace(/111111/, options.system);

        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function(jsonIndex) {
                $.extend(options.indexes, jsonIndex['index']);
                _updateResearchTimeAndCost();
                _updateCopyTimeAndCost();
            },
        });

    };

    
    /**
     * Get new copy time and price and update table
     * Called by events
     * @private
     */
    var _updateCopyTimeAndCost = function() {
        var copyTime = eveUtils.calculateCopyTime(
            options.baseCopyTime, 
            options.copyNumber, 
            options.runPerCopy, 
            facilityStats[options.facility].copy,
            options.copyImplant,
            options.scienceLevel,
            options.advancedIndustryLevel
        );
        
        var copyCost = eveUtils.calculateCopyInstallationCost(
            options.baseCost, 
            options.indexes[options.system][ACTIVITY_COPYING], 
            options.copyNumber, 
            options.runPerCopy,
            1.1
        );
        
        $('.copy-time').html(utils.durationToString(copyTime));
        $('.copy-cost').html(Humanize.intcomma(copyCost, 2));
    };
   
    
    /**
     * Get research time and cost and update table for each ME/TE level
     * Called by events
     * @private
     */
    var _updateResearchTimeAndCost = function() {
        var MEDelta = 0;
        var TEDelta = 0;
        for(var level = 1; level <= 10; level++) {
            var METime = eveUtils.calculateResearchTime(
                options.baseMeTime,
                level,
                facilityStats[options.facility].me,
                options.meImplant,
                options.metallurgyLevel,
                options.advancedIndustryLevel
            );
            var MECost = eveUtils.calculateResearchInstallationCost(
                options.baseCost, 
                options.indexes[options.system][ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY], 
                level,
                1.1
            );
            var TETime = eveUtils.calculateResearchTime(
                options.baseTeTime,
                level,
                facilityStats[options.facility].te,
                options.teImplant,
                options.researchLevel,
                options.advancedIndustryLevel
            );
            var TECost = eveUtils.calculateResearchInstallationCost(
                options.baseCost, 
                options.indexes[options.system][ACTIVITY_RESEARCHING_TIME_EFFICIENCY], 
                level,
                1.1
            );
            if(options.materialEfficiency >= level) {
                MEDelta = METime;
            }
            if((options.timeEfficiency / 2) >= level) {
                TEDelta = TETime;
            }
            _updateResearchTables(METime, MECost, MEDelta, TETime, TECost, TEDelta, level);
        }
    };
    
    
    /**
     * Update ME/TE tables
     * Called by _updateResearchTimeAndCost
     * @private
     */
    var _updateResearchTables = function(METime, MECost, MEDelta, TETime, TECost, TEDelta, level) {
        $('#ME-' + level + ' .total').html(utils.durationToString(METime));
        $('#ME-' + level + ' .delta').html(utils.durationToString(METime - MEDelta));
        $('#ME-' + level + ' .price').html(Humanize.intcomma(MECost, 2));
        $('#TE-' + level + ' .total').html(utils.durationToString(TETime));
        $('#TE-' + level + ' .delta').html(utils.durationToString(TETime - TEDelta));
        $('#TE-' + level + ' .price').html(Humanize.intcomma(TECost, 2));
    };

    
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
            _updateResearchTimeAndCost();
            _updateCopyTimeAndCost();
        });              

        $('#meImplant').on('change', function() {
            options.meImplant = parseFloat($('#meImplant').val());
            _updateResearchTimeAndCost();
        });              

        $('#teImplant').on('change', function() {
            options.teImplant = parseFloat($('#teImplant').val());
            _updateResearchTimeAndCost();
        });
        
        $('#copyImplant').on('change', function() {
            options.copyImplant = parseFloat($('#copyImplant').val());
            _updateCopyTimeAndCost();
        });
    };

    
    /**
     * Copy Number on keyup event
     * @private
     */
    var _copyNumberOnKeyUp = function(event) {
        if(!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.copyNumber = 1;
            $(this).val(options.copyNumber);
        } else {
            options.copyNumber = parseInt($(this).val());
        }
        _updateCopyTimeAndCost();
    };
       
    /**
     * Copy Number on change event
     * @private
     */ 
    var _copyNumberOnChange = function(event) {
        $(this).val(options.copyNumber);
        return false; 
    };
    
    /**
     * Run per copy on keyup event
     * @private
     */
    var _runPerCopyOnKeyUp = function(event) {
        if(!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.runPerCopy = 1;
            $(this).val(options.runPerCopy);
        } else if($(this).val() > options.maxRunPerCopy) {
            options.runPerCopy = options.maxRunPerCopy;
            $(this).val(options.runPerCopy);
        } else {
            options.runPerCopy = parseInt($(this).val());
        }
        _updateCopyTimeAndCost();
    };
    
    
    /**
     * Run per copy on change event
     * @private
     */
    var _runPerCopyOnChange = function(event) {
        $(this).val(options.runPerCopy);
        return false;
    };
    
    
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
            _getSystemCostIndex();
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
        _updateResearchTimeAndCost();
    };


    /**
     * Function called on event update on the time efficiency slider
     * @private
     */
    var _timeEfficiencyOnUpdate = function(event, ui) {
        $('#TE-Level').html(ui.value+"%");
        options.timeEfficiency = parseInt(ui.value);
        _updateResearchTimeAndCost();
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
                options.advancedIndustryLevel = value;
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
        _updateResearchTimeAndCost();
        _updateCopyTimeAndCost();
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
        $('[data-toggle="tooltip"]').tooltip();
        
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
})(jQuery, lb, utils, eveUtils, Humanize);

lb.registerModule('researchBlueprint', researchBlueprint);
