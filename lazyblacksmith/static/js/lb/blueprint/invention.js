var inventionBlueprint = (function($, lb, utils, eveUtils, Humanize) {
    "use strict"

    var ACTIVITY_COPYING = 5;
    var ACTIVITY_INVENTION = 8;

    var options = {
        blueprintId: 0,
        // base values
        copyBaseCost: 0,
        inventionBaseCost: 0,
        baseCopyTime: 0,
        baseInventionTime: 0,
        baseInventionProbability: 0,
        baseOutputRun: 1,
        baseOutputME: 2,
        baseOutputTE: 4,
        
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
        // decryptor
        decryptor: 0,
        // system
        system: "Jita",
        region: 10000002,
    };

    $.extend(lb.urls, {
        systemUrls: false,
        manufacturingUrl: false,
        buildCostUrl: false,
    });
    
    var matData = {
        idList: [],
        materials: {},
    };
    
    var decryptorList = [];
    var decryptorData = {
        idList: [],
        items: {}
    };
    // base decryptor for "no decryptor selected"
    decryptorData.items[0] = {
        name: 'Decryptor',
        probability: 1.00,
        me: 0,
        te: 0,
        run: 0,
    }
    
    var indexes = {};
    var priceData = {
        prices: {},
        isLoaded: false,
    };
    var outputPrices = false;

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

    // Ajax calls
    // -----------
    
    /**
     * Get market price for items
     * @private
     */
    var _getAllPrices = function() {
        if(priceData.isLoaded) {
            return _updateInventionData();
        }

        if(matData.idList.length == 0) {
            return;
        }

        var itemList = matData.idList.concat(decryptorData.idList)

        eveUtils.getItemPrices(itemList, function(jsonPrice) {
            priceData.prices = jsonPrice['prices'];
            priceData.isLoaded = true;
            _updateInventionData();
        });
    };
    
    
    /**
     * Get the output price (manufacturing cost) of product
     * to be able to compare every inventions together
     * @private
     */
    var _getOutputPrices = function(callback) { 
        if(outputPrices) {
            return;
        }
        
        eveUtils.ajaxGetCallJson(lb.urls.buildCostUrl, function(jsonPrice) {
            outputPrices = jsonPrice['prices'];
            callback();
        });
    }
    
    
    /**
     * Get the indexes of the missing solar systems
     * @private
     */
    var _getSystemCostIndex = function() {
        if(options.system in indexes) {
            _updateInventionData();
            return;
        }

        eveUtils.getSystemCostIndex(options.system, function(jsonIndex) {
            $.extend(indexes, jsonIndex['index']);
            _updateInventionData();
        });
    };
    

    // Visual updates
    // ---------------
    
    /**
     * Get the invention data updated (costs, probabilities, time)
     * @private
     */
    var _updateInventionData = function() {
        if(!priceData.isLoaded) {
            return setTimeout(_updateInventionData, 100);;
        }
        if(!outputPrices) {
            return _getOutputPrices(_updateInventionData);
        }
        
        var newProbability = eveUtils.calculateInventionProbability(
            options.baseInventionProbability, 
            options.encryptionLevel,
            options.datacoreLevel1, 
            options.datacoreLevel2, 
            decryptorData.items[options.decryptor].probability
        );
        var inventionTime = eveUtils.calculateInventionTime(
            options.baseInventionTime, 
            facilityStats[options.facility].invention, 
            options.advancedIndustryLevel
        );
        
        var inventionCost = eveUtils.calculateInventionCost(
            options.inventionBaseCost, 
            indexes[options.system][ACTIVITY_INVENTION], 
            options.runs, 
            1.1
        );
        
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
            indexes[options.system][ACTIVITY_COPYING], 
            options.runs, 
            1,
            1.1
        );
       
       var outputRuns = options.baseOutputRun + decryptorData.items[options.decryptor].run;
       var outputME = options.baseOutputME + decryptorData.items[options.decryptor].me;
       var outputTE = options.baseOutputTE + decryptorData.items[options.decryptor].te;
       
       _updateTables(
            newProbability, 
            inventionTime, 
            inventionCost, 
            copyTime, 
            copyCost,
            outputRuns,
            outputME,
            outputTE
        );
    }
    
    /**
     * Update all the tables with the new data
     * @private
     */
    var _updateTables = function(newProbability, inventionTime, inventionCost, copyTime, copyCost, outputRuns, outputME, outputTE) {
        var materialPrice = 0;
        for(var i in matData.idList) {
            var mat = matData.materials[matData.idList[i]];
            var quantity = mat.quantity * options.runs;
            
            var price = 0;
            if(options.region in priceData.prices && mat.id in priceData.prices[options.region]) {
                price = priceData.prices[options.region][mat.id].buy;
                price = (price == 0) ? priceData.prices[options.region][mat.id].sell : price;
            } 
            materialPrice += quantity * price;

            $('#mat-' + mat.id + ' .quantity').html(Humanize.intcomma(quantity, 0));
            $('#mat-' + mat.id + ' .ppu').html(Humanize.intcomma(price, 2));
            $('#mat-' + mat.id + ' .total').html(Humanize.intcomma(quantity * price, 2));
        }
        
        var quantity = (options.decryptor == 0) ? 0 : options.runs;
        var price = 0;
        if(options.decryptor != 0 && options.region in priceData.prices && options.decryptor in priceData.prices[options.region]) {
            price = priceData.prices[options.region][options.decryptor].buy;
            price = (price == 0) ? priceData.prices[options.region][options.decryptor].sell : price;
        } 
        materialPrice += quantity * price;

        $('#mat-decryptor .quantity').html(Humanize.intcomma(quantity, 0));
        $('#mat-decryptor .ppu').html(Humanize.intcomma(price, 2));
        $('#mat-decryptor .total').html(Humanize.intcomma(quantity * price, 2));
        $('#mat-decryptor .name').html(decryptorData.items[options.decryptor].name);

        var inventionTotalPriceProba = (inventionCost + materialPrice + copyCost) / newProbability;
        $('.invention-material-cost').html(Humanize.intcomma(materialPrice, 2));
        $('.invention-install-cost').html(Humanize.intcomma(inventionCost, 2));
        $('.invention-total-cost').html(Humanize.intcomma(inventionCost + materialPrice + copyCost, 2));
        $('.invention-total-cost-proba').html(Humanize.intcomma(inventionTotalPriceProba, 2));
        $('.invention-time').html(utils.durationToString(inventionTime));
        $('.invention-probability').html(Humanize.intcomma(newProbability * 100, 2) + '%');
        $('.output-qty').html(outputRuns);
        $('.output-me').html(outputME);
        $('.output-te').html(outputTE);
        
        $('.output-cost').html(Humanize.intcomma(outputPrices[outputME], 2));
        $('.output-cost-invention').html(Humanize.intcomma(outputPrices[outputME] + inventionTotalPriceProba / (outputRuns * options.runs), 2));
        
        $('.copy-time').html(utils.durationToString(copyTime));
        $('.copy-cost').html(Humanize.intcomma(copyCost, 2));
    };

    
    // EVENTS
    // ------
   
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
            _updateInventionData();
        });  
        
        $('#region').on('change', function() {
            options.region = parseInt($('#region').val());
            _updateInventionData();
        });       
        
        $('#decryptor').on('change', function() {
            options.decryptor = parseInt($('#decryptor').val());
            _updateInventionData();
        });              
        
        $('#copyImplant').on('change', function() {
            options.copyImplant = parseFloat($('#copyImplant').val());
            _updateInventionData();
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
        _updateInventionData();
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
        eveUtils.initSolarSystemTypeahead('#system', function(event, suggestion) {
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
                options.encryptionLevel = value;
                $('#encryption-level-display').html(value);
                break;
                
            case 'datacore1-level':
                options.datacoreLevel1 = value;
                $('#datacore1-level-display').html(value);
                break;
                
            case 'datacore2-level':
                options.datacoreLevel2 = value;
                $('#datacore2-level-display').html(value);
                break;
        };
        _updateInventionData();
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
        if(!lb.urls.manufacturingUrl || !lb.urls.buildCostUrl) {
            alert('Error, some URL are missing, this application cannot work properly without them.');
            return;
        }

        // other init that require ajax call
        _initTypeahead();
        _getAllPrices();
    };


    // -------------------------------------------------
    // return object
    //
    return {
        // required objects
        options: options,
        matData: matData,
        indexes: indexes,
        decryptorData: decryptorData,

        // functions
        run: run,
    };
})(jQuery, lb, utils, eveUtils, Humanize);

lb.registerModule('inventionBlueprint', inventionBlueprint);
