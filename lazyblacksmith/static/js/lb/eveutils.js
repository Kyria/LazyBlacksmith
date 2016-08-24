var eveUtils = (function() {
    "use strict";
    /**
     * Calculate the adjusted quantity
     * @param quantity the base quantity of material
     * @param materialEfficiency the ME level of the blueprint
     * @param facilityBonus the material bonus for the facility
     * @return the adjusted quantity (float)
     */
    var calculateAdjustedQuantity = function(quantity, materialEfficiency, facilityBonus) {
        var materialBonus = (1.00-materialEfficiency/100.00);
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
     * @param useT2Time should we use t2 times
     * @return the manufacturing time
     *
     */
    var calculateJobTime = function(timePerUnit, runs, facilityTimeBonus, timeEfficiency,
                            industrySkillLevel, advancedIndustrySkillLevel,
                            t2ConstructionSkillLevel, primaryScienceSkillLevel, secondaryScienceSkilllevel,
                            useT2Time) {
        var timeBonus = (1.00-timeEfficiency/100.00);
        var time = timePerUnit * timeBonus * facilityTimeBonus * runs;
        time *= (1 - industrySkillLevel * 0.04);
        time *= (1 - advancedIndustrySkillLevel * 0.03);
        if(useT2Time) {
            time *= (1 - t2ConstructionSkillLevel * 0.01);
            time *= (1 - primaryScienceSkillLevel * 0.01);
            time *= (1 - secondaryScienceSkilllevel * 0.01);
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
     * @return the research time in seconds 
     */
    var calculateResearchTime = function(baseResearchTime, level, factoryModifier, 
                                    implantModifier, researchSkilllevel, advancedIndustryLevel) {
        var timeModifier = factoryModifier * implantModifier;
        timeModifier *= (1.00 - researchSkilllevel * 0.05);
        timeModifier *= (1.00 - advancedIndustryLevel * 0.03);
        
        var levelModifier = (250 * Math.pow(2, (1.25 * level - 2.5))) / 105;
        
        return timeModifier * baseResearchTime * levelModifier;
    }
    
    /**
     * Calculate the research installation cost (ME/TE) with the given data
     *
     * @param baseCost the base research cost
     * @param level the level we want to reach
     * @param systemCostIndex the system cost index modifier (float)
     * @return the research cost 
     */
    var calculateResearchInstallationCost = function(baseCost, systemCostIndex, level) {
        var levelModifier = (250 * Math.pow(2, (1.25 * level - 2.5))) / 105;
        return baseCost * systemCostIndex * 0.02 * levelModifier;
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
     * @return the research time in seconds 
     */
    var calculateCopyTime = function(baseCopyTime, runs, runPerCopy, 
                                factoryModifier, implantModifier, 
                                scienceSkillLevel, advancedIndustryLevel) {
        var timeModifier = factoryModifier * implantModifier;
        timeModifier *= (1.00 - scienceSkillLevel * 0.05);
        timeModifier *= (1.00 - advancedIndustryLevel * 0.03);
        
        return timeModifier * baseCopyTime * runPerCopy * runs;
    }
    
    /**
     * Calculate the copy installation cost with the given data
     *
     * @param baseCost the base copy cost
     * @param run the number of copy
     * @param runPerCopy the number of run per copy
     * @param systemCostIndex the system cost index modifier (float)
     * @return the copy cost 
     */
    var calculateCopyInstallationCost = function(baseCost, systemCostIndex, runs, runPerCopy) {
        return baseCost * systemCostIndex * 0.02 * runs * runPerCopy;
    }

    return {
        calculateAdjustedQuantity: calculateAdjustedQuantity,
        calculateJobQuantity: calculateJobQuantity,
        calculateJobTime: calculateJobTime,
        calculateResearchTime: calculateResearchTime,
        calculateResearchInstallationCost: calculateResearchInstallationCost,
        calculateCopyTime: calculateCopyTime,
        calculateCopyInstallationCost: calculateCopyInstallationCost,
    }

})();
