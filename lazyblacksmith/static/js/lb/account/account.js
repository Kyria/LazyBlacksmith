var accountDashboard = (function($, lb, utils, eveUtils, eveData) {
    "use strict";
    var regions = {};
    var currentScopes = [];

    $.extend(lb.urls, {
        updatePreferenceUrl: false,
        loginUrl: false,
    });

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

    
    /* ---------------------------------------------------------------------- */
    /*                        ACCOUNT PREFERENCES                             */
    /* ---------------------------------------------------------------------- */
    
    var _initScopeInput = function() {
        $("input[name='scope']").on('change', function() {
            if($(this).is(':checked')) {
                currentScopes.push($(this).val());
            } else {
                currentScopes.splice($.inArray($(this).val(), currentScopes),1);
            }
            var url = lb.urls.loginUrl.replace(/XXXXX/, currentScopes.join());
            $('#update-scope').attr('href', url);
        });
    };
    
    
    /* ---------------------------------------------------------------------- */
    /*                       BLUEPRINT PREFERENCES                            */
    /* ---------------------------------------------------------------------- */
    
    var _initInventionModal = function() {
        $('#modalConfigInvention').on('show.bs.modal', function(event) {
            $('#modal-facility-invention').val(inventionSettings.facility);
            $('#modal-system-invention').val(inventionSettings.system);
            $('#structure-invention-rig-invention input[value='+inventionSettings.inventionRig+']').parent().button("toggle");
            $('#structure-copy-rig-invention input[value='+inventionSettings.copyRig+']').parent().button("toggle");
            $('#structure-sec-status-invention input[value='+inventionSettings.security+']').parent().button("toggle");
            $("select[name='modal-region-invention']").val(inventionSettings.priceRegion);
            $('.modal-region-invention-type input[value='+inventionSettings.priceType+']').parent().button("toggle");

            if(eveData.facilities[inventionSettings.facility].structure) {
                $('.structure-configs-invention').show();
            } else {
                $('.structure-configs-invention').hide();
            }
        });
        $('#modal-facility-invention').on('change', function() {
            if(eveData.facilities[parseInt($(this).val())].structure) {
                $('.structure-configs-invention').show();
            } else {
                $('.structure-configs-invention').hide();
            }
        });
    }

    var _initResearchModal = function() {
        $('#modalConfigResearch').on('show.bs.modal', function(event) {
            $('#modal-facility-research').val(researchSettings.facility);
            $('#modal-system-research').val(researchSettings.system);
            $('#structure-me-rig-research input[value='+researchSettings.meRig+']').parent().button("toggle");
            $('#structure-te-rig-research input[value='+researchSettings.teRig+']').parent().button("toggle");
            $('#structure-copy-rig-research input[value='+researchSettings.copyRig+']').parent().button("toggle");
            $('#structure-sec-status-research input[value='+researchSettings.security+']').parent().button("toggle");

            if(eveData.facilities[researchSettings.facility].structure) {
                $('.modal-structure-configs-research').show();
            } else {
                $('.modal-structure-configs-research').hide();
            }
        });
        $('#modal-facility-research').on('change', function() {
            if(eveData.facilities[parseInt($(this).val())].structure) {
                $('.modal-structure-configs-research').show();
            } else {
                $('.modal-structure-configs-research').hide();
            }
        });
    }

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

    var _onModalProdSettingsApply = function(event) {
        var productionSettingsTmp = {
            facility: parseInt($('#modal-facility-main').val()),
            meRig: parseInt($('#modal-structure-me-rig-main input:checked').val()),
            teRig: parseInt($('#modal-structure-te-rig-main input:checked').val()),
            security: $('#modal-structure-security-main input:checked').val(),
            system: $('#modal-system-main').val(),
            componentFacility: parseInt($('#modal-facility-comp').val()),
            componentMeRig: parseInt($('#modal-structure-me-rig-comp input:checked').val()),
            componentTeRig: parseInt($('#modal-structure-te-rig-comp input:checked').val()),
            componentSecurity: $('#modal-structure-security-comp input:checked').val(),
            componentSystem: $('#modal-system-comp').val(),
            priceMineralRegion: parseInt($("select[name='modal-region-minerals']").val()),
            priceMineralType: $('.modal-region-minerals-type input:checked').val(),
            pricePiRegion: parseInt($("select[name='modal-region-pi']").val()),
            pricePiType: $('.modal-region-pi-type input:checked').val(),
            priceMoongooRegion: parseInt($("select[name='modal-region-moongoo']").val()),
            priceMoongooType: $('.modal-region-moongoo-type input:checked').val(),
            priceOtherRegion: parseInt($("select[name='modal-region-others']").val()),
            priceOtherType: $('.modal-region-others-type input:checked').val(),
        };

        eveUtils.ajaxPostCallJson(
            lb.urls.updatePreferenceUrl,
            JSON.stringify({production: productionSettingsTmp}),
            function(data) {
                utils.flashNotify('Production preferences successfuly saved.', 'success');
                productionSettings = productionSettingsTmp;
                _updateProductionConfigTable();
            },
            function(errorData) {
                utils.flashNotify(errorData.responseJSON['message'], 'danger');
            }
        )
    };

    var _onModalResearchSettingsApply = function(event) {
        var researchSettingsTmp = {
            facility: parseInt($('#modal-facility-research').val()),
            meRig: parseInt($('#structure-me-rig-research input:checked').val()),
            teRig: parseInt($('#structure-te-rig-research input:checked').val()),
            copyRig: parseInt($('#structure-copy-rig-research input:checked').val()),
            security: $('#structure-sec-status-research input:checked').val(),
            system: $('#modal-system-research').val(),
        };

        eveUtils.ajaxPostCallJson(
            lb.urls.updatePreferenceUrl,
            JSON.stringify({research: researchSettingsTmp}),
            function(data) {
                utils.flashNotify('Research preferences successfuly saved.', 'success');
                researchSettings = researchSettingsTmp;
                _updateResearchConfigTable();
            },
            function(errorData) {
                utils.flashNotify(errorData.responseJSON['message'], 'danger');
            }
        )
    };

    var _onModalInventionSettingsApply = function(event) {
        var inventionSettingsTmp = {
            facility: parseInt($('#modal-facility-invention').val()),
            inventionRig: parseInt($('#structure-invention-rig-invention input:checked').val()),
            copyRig: parseInt($('#structure-copy-rig-invention input:checked').val()),
            security: $('#structure-sec-status-invention input:checked').val(),
            system: $('#modal-system-invention').val(),
            priceRegion: parseInt($("select[name='modal-region-invention']").val()),
            priceType: $('.modal-region-invention-type input:checked').val(),
        };


        eveUtils.ajaxPostCallJson(
            lb.urls.updatePreferenceUrl,
            JSON.stringify({invention: inventionSettingsTmp}),
            function(data) {
                utils.flashNotify('Invention preferences successfuly saved.', 'success');
                inventionSettings = inventionSettingsTmp;
                _updateInventionConfigTable();
            },
            function(errorData) {
                utils.flashNotify(errorData.responseJSON['message'], 'danger');
            }
        )
    };


    var _updateResearchConfigTable = function() {
        $('#research-config .facility').html(eveData.facilities[researchSettings.facility].name);
        $('#research-config .meRig').html(eveData.structureRigs[researchSettings.meRig].meta);
        $('#research-config .teRig').html(eveData.structureRigs[researchSettings.teRig].meta);
        $('#research-config .copyRig').html(eveData.structureRigs[researchSettings.copyRig].meta);
        $('#research-config .security').html(eveData.securityStatus[researchSettings.security]);
        $('#research-config .system').html(researchSettings.system);
        if(eveData.facilities[researchSettings.facility].structure) {
            $('#research-config .structure').show();
        } else {
            $('#research-config .structure').hide();
        }
    };


    var _updateInventionConfigTable = function() {
        $('#invention-config .facility').html(eveData.facilities[inventionSettings.facility].name);
        $('#invention-config .inventionRig').html(eveData.structureRigs[inventionSettings.inventionRig].meta);
        $('#invention-config .copyRig').html(eveData.structureRigs[inventionSettings.copyRig].meta);
        $('#invention-config .security').html(eveData.securityStatus[inventionSettings.security]);
        $('#invention-config .system').html(inventionSettings.system);
        $('#invention-config .priceRegion').html(regions[inventionSettings.priceRegion]);
        $('#invention-config .priceType').html(inventionSettings.priceType);
        if(eveData.facilities[inventionSettings.facility].structure) {
            $('#invention-config .structure').show();
        } else {
            $('#invention-config .structure').hide();
        }
    };


    var _updateProductionConfigTable = function() {
        $('#production-config .facility').html(eveData.facilities[productionSettings.facility].name);
        $('#production-config .meRig').html(eveData.structureRigs[productionSettings.meRig].meta);
        $('#production-config .teRig').html(eveData.structureRigs[productionSettings.teRig].meta);
        $('#production-config .security').html(eveData.securityStatus[productionSettings.security]);
        $('#production-config .system').html(productionSettings.system);
        $('#production-config .componentFacility').html(eveData.facilities[productionSettings.componentFacility].name);
        $('#production-config .componentMeRig').html(eveData.structureRigs[productionSettings.componentMeRig].meta);
        $('#production-config .componentTeRig').html(eveData.structureRigs[productionSettings.componentTeRig].meta);
        $('#production-config .componentSecurity').html(eveData.securityStatus[productionSettings.componentSecurity]);
        $('#production-config .componentSystem').html(productionSettings.componentSystem);
        $('#production-config .priceMineralRegion').html(regions[productionSettings.priceMineralRegion]);
        $('#production-config .priceMineralType').html(productionSettings.priceMineralType);
        $('#production-config .pricePiRegion').html(regions[productionSettings.pricePiRegion]);
        $('#production-config .pricePiType').html(productionSettings.pricePiType);
        $('#production-config .priceMoongooRegion').html(regions[productionSettings.priceMoongooRegion]);
        $('#production-config .priceMoongooType').html(productionSettings.priceMoongooType);
        $('#production-config .priceOtherRegion').html(regions[productionSettings.priceOtherRegion]);
        $('#production-config .priceOtherType').html(productionSettings.priceOtherType);
        if(eveData.facilities[productionSettings.facility].structure) {
            $('#production-config .structure-main').show();
        } else {
            $('#production-config .structure-main').hide();
        }
        if(eveData.facilities[productionSettings.componentFacility].structure) {
            $('#production-config .structure-comp').show();
        } else {
            $('#production-config .structure-comp').hide();
        }
    };

    /**
     * Init all modals
     * @private
     */
    var _initModal = function() {
        _initProdModal();
        _initResearchModal();
        _initInventionModal();
        $('#open-modal-prod-settings').on('click', function() {
            $('#modalConfigProd').modal('show');
        });
        $('#open-modal-research-settings').on('click', function() {
            $('#modalConfigResearch').modal('show');
        });
        $('#open-modal-invention-settings').on('click', function() {
            $('#modalConfigInvention').modal('show');
        });
        $('#modal-prod-apply').on('click', _onModalProdSettingsApply);
        $('#modal-research-apply').on('click', _onModalResearchSettingsApply);
        $('#modal-invention-apply').on('click', _onModalInventionSettingsApply);
    };

    var _initTypeahead = function() {
        eveUtils.initSolarSystemTypeahead('#modal-system-main');
        eveUtils.initSolarSystemTypeahead('#modal-system-comp');
        eveUtils.initSolarSystemTypeahead('#modal-system-research');
        eveUtils.initSolarSystemTypeahead('#modal-system-invention');
    };

    /**
     * Runner function
     */
    var run = function() {
        _initModal();
        _initTypeahead();
        _initScopeInput();
        $('[data-toggle="tooltip"]').tooltip();
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
        regions:regions,
    };
})(jQuery, lb, utils, eveUtils, eveData);

lb.registerModule('accountDashboard', accountDashboard);
