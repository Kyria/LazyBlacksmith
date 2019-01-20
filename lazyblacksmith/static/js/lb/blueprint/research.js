var researchBlueprint = (function ($, lb, utils, eveUtils, eveData, Humanize) {
    'use strict'

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
        system: 'jita',
        systemPrevious: 'jita',
        // runsPerJob
        runs: 1,

        // structure configs
        structureTeRig: 0,
        structureMeRig: 0,
        structureCopyRig: 0,
        structureMaterialRig: 0,
        structureSecStatus: 'h',

        // material configs and informations
        hasCopyMaterial: false,
        hasTeMaterial: false,
        hasMeMaterial: false,
        copyMaterialCost: 0,
        teMaterialCost: 0,
        meMaterialCost: 0
    }

    // list of materials
    var materials = {
        ids: [],
        bom: {}
    }

    $.extend(lb.urls, {
        systemUrls: false,
        indexActivityUrl: false
    })

    // assembly informations
    var facilityStats = eveData.facilities
    var structureRigs = eveData.structureIndustryRigs
    var structureSecStatusMultiplier = eveData.structureSecStatusMultiplier

    /**
     * Update the cost per ME table to compare ME and production cost
     */
    var _updateCostPerMe = function () {
        var price = {}
        var previousME = 0
        for (var ME = 0; ME <= 10; ME++) {
            price[ME] = 0.0
            for (var i in materials.ids) {
                var material = materials.bom[materials.ids[i]]

                var qtyAdjusted = eveUtils.calculateAdjustedQuantity(
                    material.qtyRequiredPerRun,
                    ME,
                    facilityStats[options.facility].bpMe,
                    structureRigs[options.structureMaterialRig].materialBonus,
                    structureSecStatusMultiplier[options.structureSecStatus],
                    facilityStats[options.facility].structure
                )

                var quantityJob = eveUtils.calculateJobQuantity(
                    qtyAdjusted,
                    options.runs
                )

                price[ME] += quantityJob * material.price
            }

            var currentCost = price[ME]
            var deltaMe0 = price[0] - currentCost
            var deltaPrevMe = price[previousME] - currentCost
            var deltaMe0Percent = (1 - currentCost / price[0]) * 100
            var deltaPrevMePercent = (1 - currentCost / price[previousME]) * 100

            $('#ME-profit-' + ME + ' .build-cost').html(Humanize.intcomma(currentCost, 2))
            $('#ME-profit-' + ME + ' .me-0').html(Humanize.intcomma(deltaMe0, 2))
            $('#ME-profit-' + ME + ' .me-0-percent').html(Humanize.intcomma(deltaMe0Percent, 2) + '%')
            $('#ME-profit-' + ME + ' .me-prev').html(Humanize.intcomma(deltaPrevMe, 2))
            $('#ME-profit-' + ME + ' .me-prev-percent').html(Humanize.intcomma(deltaPrevMePercent, 2) + '%')

            previousME = ME
        }
    }

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

        eveUtils.getSystemCostIndex(options.system, function(jsonIndex) {
            $.extend(options.indexes, jsonIndex['index']);
            _updateResearchTimeAndCost();
            _updateCopyTimeAndCost();
        }, function(errorObject) {
            var jsonResponse = errorObject.responseJSON;
            utils.flashNotify(jsonResponse.message, jsonResponse.status);

            options.system = options.systemPrevious;
            $('#system').val(options.system);
            $('#system').typeahead('val',options.system);
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
            options.advancedIndustryLevel,
            structureRigs[options.structureCopyRig].timeBonus,
            structureSecStatusMultiplier[options.structureSecStatus],
            facilityStats[options.facility].structure
        );

        var copyCost = eveUtils.calculateCopyInstallationCost(
            options.baseCost,
            options.indexes[options.system][eveData.activity.copy],
            options.copyNumber,
            options.runPerCopy,
            1.1
        );

        var copyMaterialCostTotal = options.copyMaterialCost * options.copyNumber * options.runPerCopy;

        $('.copy-time').html(utils.durationToString(copyTime));
        $('.copy-cost').html(Humanize.intcomma(copyCost, 2));
        $('.copy-total-cost').html(Humanize.intcomma(copyCost + copyMaterialCostTotal, 2));

        // update materials required for copy
        $('#copy-materials tbody tr').each(
            function() {
                var qty = parseInt($(this).attr('data-qty'));
                qty *= options.copyNumber * options.runPerCopy;
                $(this).find('td.jobqty').html(Humanize.intcomma(qty))
            }
        )
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
                facilityStats[options.facility].jobMe,
                options.meImplant,
                options.metallurgyLevel,
                options.advancedIndustryLevel,
                structureRigs[options.structureMeRig].timeBonus,
                structureSecStatusMultiplier[options.structureSecStatus],
                facilityStats[options.facility].structure
            );
            var MECost = eveUtils.calculateResearchInstallationCost(
                options.baseCost,
                options.indexes[options.system][eveData.activity.me],
                level,
                1.1
            );
            var TETime = eveUtils.calculateResearchTime(
                options.baseTeTime,
                level,
                facilityStats[options.facility].jobTe,
                options.teImplant,
                options.researchLevel,
                options.advancedIndustryLevel,
                structureRigs[options.structureTeRig].timeBonus,
                structureSecStatusMultiplier[options.structureSecStatus],
                facilityStats[options.facility].structure
            );
            var TECost = eveUtils.calculateResearchInstallationCost(
                options.baseCost,
                options.indexes[options.system][eveData.activity.te],
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
        $('#ME-' + level + ' .ptotal').html(Humanize.intcomma(MECost + options.meMaterialCost, 2));
        $('#TE-' + level + ' .total').html(utils.durationToString(TETime));
        $('#TE-' + level + ' .delta').html(utils.durationToString(TETime - TEDelta));
        $('#TE-' + level + ' .price').html(Humanize.intcomma(TECost, 2));
        $('#TE-' + level + ' .ptotal').html(Humanize.intcomma(TECost + options.teMaterialCost, 2));
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

        $('#runs').on('keyup', _runsOnKeyUp)
                  .on('change', _runsOnChange);


        $('#facility').on('change', function() {
            options.facility = parseInt($('#facility').val());
            _toggleStructureConfigsDisplay(facilityStats[options.facility].structure);
            _updateResearchTimeAndCost();
            _updateCopyTimeAndCost();
            _updateCostPerMe();
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
        $("#structure-sec-status input[type='radio']").on('change', function() {
            options.structureSecStatus = $(this).val();
            _updateResearchTimeAndCost();
            _updateCopyTimeAndCost();
            _updateCostPerMe();
        });
        $("#structure-te-rig input[type='radio']").on('change', function() {
            options.structureTeRig = parseInt($(this).val())
            _updateResearchTimeAndCost();
        });
        $("#structure-me-rig input[type='radio']").on('change', function() {
            options.structureMeRig = parseInt($(this).val());
            _updateResearchTimeAndCost();
        });
        $("#structure-copy-rig input[type='radio']").on('change', function() {
            options.structureCopyRig = parseInt($(this).val());
            _updateCopyTimeAndCost();
        });
        $("#structure-mat-rig input[type='radio']").on('change', function() {
            options.structureMaterialRig = parseInt($(this).val());
            _updateCostPerMe();
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
     * Run per copy on keyup event
     * @private
     */
    var _runsOnKeyUp = function(event) {
        if(!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.runs = 1;
            $(this).val(options.runs);
        } else {
            options.runs = parseInt($(this).val());
        }
        $('#nb-run').html(options.runs)
        _updateCostPerMe();
    };


    /**
     * Run per copy on change event
     * @private
     */
    var _runsOnChange = function(event) {
        $(this).val(options.runs);
        return false;
    };



    /**
     * Init typeahead objects
     * @private
     */
    var _initTypeahead = function() {
        eveUtils.initSolarSystemTypeahead('#system', function(event, suggestion) {
            if(options.system == $(this).typeahead('val').toLowerCase()) {
                return;
            }
            options.systemPrevious = options.system;
            options.system = $(this).typeahead('val').toLowerCase();
            _getSystemCostIndex();
        });
    };


    /**
     * Init all sliders on the page
     * @private
     */
    var _initSliders = function() {
        var skillSliderConf = {
            start: 0,
            connect: [true, false],
            step: 1,
            range: {
                min: 0,
                max: 5
            }
        };
        var meSliderConf = {
            start: 0,
            connect: [true, false],
            step: 1,
            range: {
                min: 0,
                max: 10
            }
        };
        var teSliderConf = {
            start: 0,
            connect: [true, false],
            step: 2,
            range: {
                min: 0,
                max: 20
            }
        };

        utils.noUiSliderCreate('#ME', meSliderConf);
        utils.noUiSliderCreate('#TE', teSliderConf);
        utils.noUiSliderCreate('#adv-industry-level, #research-level, #science-level, #metallurgy-level', skillSliderConf);

        utils.noUiSliderSetValue('#ME', options.materialEfficiency);
        utils.noUiSliderSetValue('#TE', options.timeEfficiency);
        utils.noUiSliderSetValue('#adv-industry-level', options.advancedIndustryLevel);
        utils.noUiSliderSetValue('#research-level', options.researchLevel);
        utils.noUiSliderSetValue('#science-level', options.scienceLevel);
        utils.noUiSliderSetValue('#metallurgy-level', options.metallurgyLevel);

        utils.noUiSliderBind('#ME', 'slide', _materialEfficiencyOnUpdate);
        utils.noUiSliderBind('#TE', 'slide', _timeEfficiencyOnUpdate);
        utils.noUiSliderBind(
            '#adv-industry-level, #research-level, #science-level, #metallurgy-level',
            'slide', _skillOnUpdate
        );
    };


    /**
     * Function called on event update on the material efficiency slider
     * @private
     */
    var _materialEfficiencyOnUpdate = function(value) {
        value = parseInt(value);
        $('#ME-Level').html(value+"%");
        options.materialEfficiency = value;
        _updateResearchTimeAndCost();
    };


    /**
     * Function called on event update on the time efficiency slider
     * @private
     */
    var _timeEfficiencyOnUpdate = function(value) {
        var value = parseInt(value);

        $('#TE-Level').html(value+"%");
        options.timeEfficiency = value;
        _updateResearchTimeAndCost();
    };


    /**
     * Toggle the display of struture configurations depending on the parameter.
     * If isStructure is True, we display ME/TE Rig and Security Status configs.
     * Else we hide these configs.
     * @param  {Boolean} isStructure Wether if the selected facility is a structure or not
     * @param  {Boolean} modal true if we are in the modal. Define the class to update
     * @private
     */
    var _toggleStructureConfigsDisplay = function(isStructure) {
        var structConfClass = '.structure-configs';

        if(isStructure) {
            $(structConfClass).show();
        } else {
            $(structConfClass).hide();
        }
    };


    /**
     * Function called on event update on the skill level sliders
     * @private
     */
    var _skillOnUpdate = function(value) {
        var id = $(this.target).attr('id');
        var value = parseInt(value);

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

        // run one recalculation, in case we are not using default data
        _updateResearchTimeAndCost();
        _updateCopyTimeAndCost();
        _updateCostPerMe();
    };


    // -------------------------------------------------
    // return object
    //
    return {
        // required objects
        options: options,
        materials: materials,
        // functions
        run: run,
    };
})(jQuery, lb, utils, eveUtils, eveData, Humanize);

lb.registerModule('researchBlueprint', researchBlueprint);
