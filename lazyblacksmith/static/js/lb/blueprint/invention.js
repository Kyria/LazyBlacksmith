var inventionBlueprint = (function($, lb, utils, eveUtils, Humanize, JSON) {
    "use strict"
    // inventionTime = baseInventionTime ∗ facilityModifier ∗ (1 − 0.03 ∗ AdvancedIndustryLevel)
    // jobFee = baseJobCost ∗ systemCostIndex ∗ 0.02 ∗ runs
    // inventionChance = baseChance ∗ SkillModif ier ∗ DecryptorModif ier
    // SkillModif ier = 1 + EncryptionLevel/40 + (Datacore1Level + Datacore2Level)/30

    var ACTIVITY_COPYING = 5;
    var ACTIVITY_INVENTION = 8;

    var options = {
        // base values
        copyBaseCost: 0,
        inventionBaseCost: 0,
        baseCopyTime: 0,
        baseInventionTime: 0,
        // indexes
        indexes: {},
        
        // copy speed (5%)
        scienceLevel: 0,
        // adv industry (3%)
        advancedIndustryLevel: 0,
        // invention skills
        datacoreLevel1: 0,
        datacoreLevel2: 0,
        encryptionLevel: 0,
        
        // implants
        copyImplant: 1.00,
        
        // facility
        facility: 0,
        // copy data
        runs: 1,
        // system
        system: "Jita",
    };

    $.extend(lb.urls, {
        systemUrls: false,
        indexActivityUrl: false,
        manufacturingUrl: false,
        priceUrl: false,
    });

    // assembly informations
    var facilityStats = [
        { // station
            "copy": 1.0,
            "invention": 1.0,
            "name": 'Station',
        },
        { // Laboratory
            "copy": 0.6,
            "invention": 0.5,
            "name": 'Laboratory',
        },
        { // experimental lab
            "copy": 1.0,
            "invention": 1.0,
            "name": 'Experimental Laboratory',
        },
    ];

    
    /**
     * Get the indexes of the missing solar systems
     * @private
     */
    var _getSystemCostIndex = function() {
        if(options.system in options.indexes) {
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
            options.runs, 
            1, 
            facilityStats[options.facility].copy,
            options.copyImplant,
            options.scienceLevel,
            options.advancedIndustryLevel
        );
        
        var copyCost = eveUtils.calculateCopyInstallationCost(
            options.copyBaseCost, 
            options.indexes[options.system][ACTIVITY_COPYING], 
            options.runs, 
            1,
            1.1
        );
        
        $('.copy-time').html(utils.durationToString(copyTime));
        $('.copy-cost').html(Humanize.intcomma(copyCost, 2));
    };
   
   
    /**
     * Init input fields
     * @private
     */
    var _initInputs = function() {
        // checks and update on copy numbers
        $('#invention-number').on('keyup', _inventionNumberOnKeyUp)
                         .on('change', _inventionNumberOnChange);                        

        $('#facility').on('change', function() {
            options.facility = parseInt($('#facility').val());
            _updateCopyTimeAndCost();
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
    var _inventionNumberOnKeyUp = function(event) {
        if(!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.runs = 1;
        } else {
            options.runs = parseInt($(this).val());
        }
        $(this).val(options.runs);
        _updateCopyTimeAndCost();
    };
       
    /**
     * Copy Number on change event
     * @private
     */ 
    var _inventionNumberOnChange = function(event) {
        $(this).val(options.runs);
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
        $('#adv-industry-level, #science-level, #encryption-level, #datacore1-level, #datacore2-level').slider({
            min: 0,
            max: 5,
            range: "min",
            slide: _skillOnUpdate,
        });
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

            case 'science-level':
                options.scienceLevel = value;
                $('#science-level-display').html(value);
                break;

            case 'encryption-level':
                options.metallurgyLevel = value;
                $('#encryption-level-display').html(value);
                break;
                
            case 'datacore1-level':
                options.metallurgyLevel = value;
                $('#datacore1-level-display').html(value);
                break;
                
            case 'datacore2-level':
                options.metallurgyLevel = value;
                $('#datacore2-level-display').html(value);
                break;
        };
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
        $('[data-toggle="tooltip"]').tooltip({
            container: 'body',
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

lb.registerModule('inventionBlueprint', inventionBlueprint);
