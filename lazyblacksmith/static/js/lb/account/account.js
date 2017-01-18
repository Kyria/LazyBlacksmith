var accountDashboard = (function($, lb, utils, eveUtils, eveData) {
    "use strict";

    var inventionSettings = {
        facility: false,
        inventionRig: false,
        copyRig: false,
        security: false,
        system: false,
        priceRegion: false,
        priceType: false,
    };
    
    var researchSettings = {
        facility: false,
        meRig: false,
        teRig: false,
        copyRig: false,
        security: false,
        system: false,
    };
    
    var productionSettings = {
        facility: false,
        meRig: false,
        teRig: false,
        security: false,
        system: false,
        componentFacility: false,
        componentMeRig: false,
        componentTeRig: false,
        componentSecurity: false,
        componentSystem: false,
        priceMineralRegion: false,
        priceMineralType: false,
        pricePiRegion: false,
        pricePiType: false,
        priceMoongooRegion: false,
        priceMoongooType: false,
        priceOtherRegion: false,
        priceOtherType: false,
    };

    var _initProdModal = function() {
        $('#modalConfigProd').on('show.bs.modal', function(event) {
            $('#modal-system-main').val(productionSettings.system);
            $('#modal-system-comp').val(productionSettings.componentSystem);
            
            $('#modal-facility-main').val(productionSettings.facility)
            $('#modal-facility-comp').val(productionSettings.componentFacility);
            
            $('#modal-structure-me-rig-main input[value='+productionSettings.meRig+']').parent().button("toggle");
            $('#modal-structure-te-rig-main input[value='+productionSettings.teRig+']').parent().button("toggle");
            $('#modal-structure-me-rig-comp input[value='+productionSettings.componentMeRig+']').parent().button("toggle");
            $('#modal-structure-te-rig-comp input[value='+productionSettings.componentTeRig+']').parent().button("toggle");
            
            $('#modal-structure-security-main input[value='+productionSettings.security+']').parent().button("toggle");
            $('#modal-structure-security-comp input[value='+productionSettings.componentSecurity+']').parent().button("toggle");
            
            
            $('.modal-region-minerals-type input[value='+productionSettings.priceMineralType+']').parent().button("toggle");
            $('.modal-region-pi-type input[value='+productionSettings.pricePiType+']').parent().button("toggle");
            $('.modal-region-moongoo-type input[value='+productionSettings.priceMoongooType+']').parent().button("toggle");
            $('.modal-region-others-type input[value='+productionSettings.priceOtherType+']').parent().button("toggle");
            
            $("select[name='modal-region-minerals']").val(productionSettings.priceMineralRegion);
            $("select[name='modal-region-pi']").val(productionSettings.pricePiRegion);
            $("select[name='modal-region-moongoo']").val(productionSettings.priceMoongooRegion);
            $("select[name='modal-region-others']").val(productionSettings.priceOtherRegion); 
            
            if(eveData.facilities[productionSettings.facility].structure) {
                $('.modal-structure-configs-main').show();
            } else {
                $('.modal-structure-configs-main').hide();
            }
            if(eveData.facilities[productionSettings.componentFacility].structure) {
                $('.modal-structure-configs-comp').show();
            } else {
                $('.modal-structure-configs-comp').hide();
            }
        });
        _initProdModalEvents();
    };
    
    var _initProdModalEvents = function() {
        $('#modal-facility-main').on('change', function() {
            if(eveData.facilities[parseInt($(this).val())].structure) {
                $('.modal-structure-configs-main').show();
            } else {
                $('.modal-structure-configs-main').hide();
            }
        });
        $('#modal-facility-comp').on('change', function() {
            if(eveData.facilities[parseInt($(this).val())].structure) {
                $('.modal-structure-configs-comp').show();
            } else {
                $('.modal-structure-configs-comp').hide();
            }
        });
    };
    
    /**
     * Init all modals
     * @private
     */
    var _initModal = function() {
        _initProdModal();
        $('#open-modal-prod-settings').on('click', function() {
            $('#modalConfigProd').modal('show');
        });
        //$('#modal-apply').on('click', _onModalBpApplyOne);
    };

    var _initTypeahead = function() {
        eveUtils.initSolarSystemTypeahead('#modal-system-main');
        eveUtils.initSolarSystemTypeahead('#modal-system-comp');
    };
    
    /**
     * Runner function
     */
    var run = function() {
        _initModal();
        _initTypeahead();
    };

    // -------------------------------------------------
    // return object
    //
    return {
        // functions
        run: run,
        inventionSettings: inventionSettings,
        researchSettings: researchSettings,
        productionSettings: productionSettings,
    };
})(jQuery, lb, utils, eveUtils, eveData);

lb.registerModule('accountDashboard', accountDashboard);
