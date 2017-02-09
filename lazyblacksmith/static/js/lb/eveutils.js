var eveUtils = (function(utils) {
    "use strict";
    /**
     * Calculate the adjusted quantity
     * @param quantity the base quantity of material
     * @param materialEfficiency the ME level of the blueprint
     * @param facilityBonus the material bonus for the facility
     * @param rigBonus the bonus given from the structure rig
     * @param rigMultiplier the multiplier for the rig bonus, depending on security status
     * @param isStructure true if the facility is a structure (EC/Other), trigger the use of rig bonus
     * @return the adjusted quantity (float)
     */
    var calculateAdjustedQuantity = function(quantity, materialEfficiency, facilityBonus, rigBonus, rigMultiplier, isStructure) {
        var materialBonus = (1.00-materialEfficiency/100.00);
        if(isStructure) {
            materialBonus *= 1-(rigBonus * rigMultiplier);
        }
        return Math.max(1.00, quantity * materialBonus * facilityBonus);
    };

    /**
     * Calculate the job quantity
     * @param quantityAdjusted the adjusted quantity
     * @param runs the number of runs
     * @return the final quantity of materials (round to upper integer)
     */
    var calculateJobQuantity = function(quantityAdjusted, runs) {
        return Math.max(runs, Math.ceil(quantityAdjusted * runs));
    };

    /**
     * Calculate the manufacturing time with the given informations.
     * Note: T2Time must never be used for subcomponents (as it's only required for tech2 items)
     *
     * @param timePerUnit the base production time
     * @param runs the number of runs
     * @param facilityTimeBonus the facility bonus
     * @param timeEfficiency the blueprint time efficiency level
     * @param industrySkillLevel the industry skill level
     * @param advancedIndustrySkillLevel the advanced industry skill level
     * @param t2ConstructionSkillLevel the <object> construction skill level (frig, cruiser, capitals...)
     * @param primaryScienceSkillLevel the primary science skill level
     * @param secondaryScienceSkilllevel the secondary science skill level
     * @param rigBonus the bonus given from the structure rig
     * @param rigMultiplier the multiplier for the rig bonus, depending on security status
     * @param isStructure true if the facility is a structure (EC/Other), trigger the use of rig bonus
     * @param useT2Time should we use t2 times
     * @return the manufacturing time
     *
     */
    var calculateJobTime = function(timePerUnit, runs, facilityTimeBonus, timeEfficiency,
                            industrySkillLevel, advancedIndustrySkillLevel,
                            t2ConstructionSkillLevel, primaryScienceSkillLevel, secondaryScienceSkilllevel,
                            rigBonus, rigMultiplier, isStructure, useT2Time) {
        var timeBonus = (1.00-timeEfficiency/100.00);
        var time = timePerUnit * timeBonus * facilityTimeBonus * runs;
        time *= (1 - industrySkillLevel * 0.04);
        time *= (1 - advancedIndustrySkillLevel * 0.03);
        if(useT2Time) {
            time *= (1 - t2ConstructionSkillLevel * 0.01);
            time *= (1 - primaryScienceSkillLevel * 0.01);
            time *= (1 - secondaryScienceSkilllevel * 0.01);
        }
        if(isStructure) {
            time *= 1 - (rigBonus * rigMultiplier);
        }
        return time;
    };

    /**
     * Calculate the research time (ME/TE) with the given data
     *
     * @param baseResearchTime the base research time in seconds
     * @param level the level we want to reach
     * @param factoryModifier the factory modifier (float)
     * @param implantModifier the implant modifier (float)
     * @param researchSkilllevel the research skill level (metallurgy or research)
     * @param advancedIndustryLevel the advanced industry skill level
     * @param rigBonus the bonus given from the structure rig
     * @param rigMultiplier the multiplier for the rig bonus, depending on security status
     * @param isStructure true if the facility is a structure (EC/Other), trigger the use of rig bonus
     * @return the research time in seconds
     */
    var calculateResearchTime = function(baseResearchTime, level, factoryModifier,
                                    implantModifier, researchSkilllevel, advancedIndustryLevel,
                                    rigBonus, rigMultiplier, isStructure) {
        var timeModifier = factoryModifier * implantModifier;
        timeModifier *= (1.00 - researchSkilllevel * 0.05);
        timeModifier *= (1.00 - advancedIndustryLevel * 0.03);

        if(isStructure) {
            timeModifier *= 1 - (rigBonus * rigMultiplier);
        }

        var levelModifier = (250 * Math.pow(2, (1.25 * level - 2.5))) / 105;

        return timeModifier * baseResearchTime * levelModifier;
    }

    /**
     * Calculate the research installation cost (ME/TE) with the given data
     *
     * @param baseCost the base research cost
     * @param level the level we want to reach
     * @param systemCostIndex the system cost index modifier (float)
     * @param tax the facility tax
     * @return the research cost
     */
    var calculateResearchInstallationCost = function(baseCost, systemCostIndex, level, tax) {
        var levelModifier = (250 * Math.pow(2, (1.25 * level - 2.5))) / 105;
        return baseCost * systemCostIndex * 0.02 * levelModifier * tax;
    }

    /**
     * Calculate the copy time with the given data
     *
     * @param baseCopyTime the base copy time in seconds
     * @param run the number of copy
     * @param runPerCopy the number of run per copy
     * @param factoryModifier the factory modifier (float)
     * @param implantModifier the implant modifier (float)
     * @param scienceSkillLevel the science skill level
     * @param advancedIndustryLevel the advanced industry skill level
     * @param rigBonus the bonus given from the structure rig
     * @param rigMultiplier the multiplier for the rig bonus, depending on security status
     * @param isStructure true if the facility is a structure (EC/Other), trigger the use of rig bonus
     * @return the research time in seconds
     */
    var calculateCopyTime = function(baseCopyTime, runs, runPerCopy,
                                factoryModifier, implantModifier,
                                scienceSkillLevel, advancedIndustryLevel,
                                rigBonus, rigMultiplier, isStructure) {
        var timeModifier = factoryModifier * implantModifier;
        timeModifier *= (1.00 - scienceSkillLevel * 0.05);
        timeModifier *= (1.00 - advancedIndustryLevel * 0.03);

        if(isStructure) {
            timeModifier *= 1 - (rigBonus * rigMultiplier);
        }

        return timeModifier * baseCopyTime * runPerCopy * runs;
    }

    /**
     * Calculate the copy installation cost with the given data
     *
     * @param baseCost the base copy cost
     * @param run the number of copy
     * @param runPerCopy the number of run per copy
     * @param systemCostIndex the system cost index modifier (float)
     * @param tax the facility tax
     * @return the copy cost
     */
    var calculateCopyInstallationCost = function(baseCost, systemCostIndex, runs, runPerCopy, tax) {
        return baseCost * systemCostIndex * 0.02 * runs * runPerCopy * tax;
    }

    /**
     * Calculate the invention probability and return the value as decimal
     *
     * @param baseProbability the blueprint base invention probability
     * @param encryptionLevel the level of <faction> encryption
     * @param datacore1Level the level of the first datacore type skill
     * @param datacore2Level the level of the second datacore type skill
     * @param decryptorModifier the decryptor modifier
     * @return the new percentage
     */
    var calculateInventionProbability = function(baseProbability, encryptionLevel,
                                            datacore1Level, datacore2Level, decryptorModifier) {
        var skillModifier = 1 + encryptionLevel / 40 + (datacore1Level + datacore2Level) / 30;
        return baseProbability * skillModifier * decryptorModifier;
    }

    /**
     * Calculate the invention time
     *
     * @param baseInventionTime the base invention time
     * @param facilityModifier the facility bonus for invention
     * @param advancedIndustryLevel the level of advanced Industry
     * @param rigBonus the bonus given from the structure rig
     * @param rigMultiplier the multiplier for the rig bonus, depending on security status
     * @param isStructure true if the facility is a structure (EC/Other), trigger the use of rig bonus
     * @return the new time in second
     */
    var calculateInventionTime = function(baseInventionTime, facilityModifier, advancedIndustryLevel,
                                          rigBonus, rigMultiplier, isStructure) {
        var timeModifier = 1;
        if(isStructure) {
            timeModifier *= 1 - (rigBonus * rigMultiplier);
        }
        return baseInventionTime * facilityModifier * (1 - 0.03 * advancedIndustryLevel) * timeModifier;
    }

    /**
     * Calculate the invention installation cost with the given data
     *
     * @param baseCost the base invention cost
     * @param run the number of invention runs
     * @param tax the facility tax
     * @param systemCostIndex the system cost index modifier (float)
     * @return the invention cost
     */
    var calculateInventionCost = function(baseCost, systemCostIndex, runs, tax) {
        return baseCost * systemCostIndex * runs * 0.02 * tax;
    }

    
    /**
     * Proxy function to get system cost indexes from backend
     * @param systemList the array of system names
     * @param callback function to call when ajax call succeed
     */
    var getSystemCostIndex = function(systemList, callback) {
        var systems = ($.isArray(systemList)) ? systemList.join(',') : systemList;
        var url = lb.urls.indexActivityUrl.replace(/SYSTEM_LIST_TO_REPLACE/, systems);
        utils.ajaxGetCallJson(url, callback);

    };

    /**
     * Proxy function to get item prices from backend
     * @param itemList the array of item ID
     * @param callback function to call when ajax call succeed
     */
    var getItemPrices = function(itemList, callback) {
        var items = ($.isArray(itemList)) ? itemList.join(',') : itemList;
        var url = lb.urls.priceUrl.replace(/ITEM_LIST_TO_REPLACE/, items);
        utils.ajaxGetCallJson(url, callback);
    };

    /**
     * Init the bloodhound for the typeahead
     * @private
     */
    var _getSystemBloodHound = function() {
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
        return systems;
    };

    /**
     * Init solar system typeahead fields
     * @param cssSelector where to apply to the typeahead
     * @param callback function to call when suggestion selected (can be null)
     */
    var initSolarSystemTypeahead = function(cssSelector, callback) {
        var systems = _getSystemBloodHound();

        var typeaheadEventSelector = "change typeahead:selected typeahead:autocompleted";
        var typeahead = $(cssSelector).typeahead(null,{
            name: 'system',
            displayKey: 'name',
            source: systems.ttAdapter(),
        });

        if(callback) {
            typeahead.on(typeaheadEventSelector, callback);
        }
    };

    
    return {
        calculateAdjustedQuantity: calculateAdjustedQuantity,
        calculateJobQuantity: calculateJobQuantity,
        calculateJobTime: calculateJobTime,
        calculateResearchTime: calculateResearchTime,
        calculateResearchInstallationCost: calculateResearchInstallationCost,
        calculateCopyTime: calculateCopyTime,
        calculateCopyInstallationCost: calculateCopyInstallationCost,
        calculateInventionProbability: calculateInventionProbability,
        calculateInventionTime: calculateInventionTime,
        calculateInventionCost: calculateInventionCost,

        // ajax stuff
        getSystemCostIndex: getSystemCostIndex,
        getItemPrices: getItemPrices,
        initSolarSystemTypeahead: initSolarSystemTypeahead,
    };

})(utils);
