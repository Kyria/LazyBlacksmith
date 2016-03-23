"use strict";

var manufacturingBlueprint = (function($, lb, utils, eveUtils, Humanize, JSON) {

    // template variables
    var tplSublistBlock = '';
    var tplSublistRow = '';

    // page options
    var options = {
        hasManufacturedComponent: false,
        useIcons: false,

        // bp informations
        materialEfficiency: 0,
        timeEfficiency: 0,
        runs: 1,
        facility: 0,

        // skill infos
        industryLvl: 0,
        advancedIndustryLvl: 0,
        t2ConstructionLvl: 0,
        primaryScienceLevel: 0,
        secondaryScienceLevel: 0,
    };

    // urls
    $.extend(lb.urls, {
        systemUrls: false,
        materialBOMUrl: false,
        priceUrl: false,

        // template links
        tplSublistBlockUrl: false,
        tplSublistRowUrl: false,
    });

    // item price data and index
    var priceData = {
        currentRegion: '10000002',
        typeOrder: 'buy',
        prices: {},
        adjusted: {},
        industryIndex: {},
    };

    var materialsData = {
        // produced item id
        productItemId: 0,

        // components
        materials: {},
        componentIdList: [],
    };

    var materialQuantityList;

    // states
    var isMaterialListLoaded = false;
    var useComponents = false;
    var lastTab = "#tab-summary";

    // assembly informations
    var assemblyStats = [
        { // station
            "me": 1.0,
            "te": 1.0,
            "name": 'Station',
        },
        { // Assembly Array
            "me": 0.98,
            "te": 0.75,
            "name": 'Assembly Array',
        },
        { // Thukker Component Array
            "me": 0.9,
            "te": 0.75,
            "name": 'Thukker Component Array',
        },
        { // Rapid Assembly Array
            "me": 1.05,
            "te": 0.65,
            "name": 'Rapid Assembly Array',
        },
    ];


    // -------------------------------------------------
    // Functions (no events, no event functions)
    //

    /**
     * Update main blueprint components.
     * @private
     */
    var _updateMaterial = function() {
        for(var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]];

            var facility = parseInt($('#facility').val());
            var quantityAdjusted = eveUtils.calculateAdjustedQuantity(
                material.qtyRequiredPerRun,
                options.materialEfficiency,
                assemblyStats[options.facility].me
            );
            var quantityJob = eveUtils.calculateJobQuantity(
                quantityAdjusted,
                options.runs
            );

            var selector = '.main-list tr.material[data-id="' + material.id + '"]';
            $(selector + ' td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2));
            $(selector + ' td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob));

            material.qtyAdjusted = quantityAdjusted;
            material.qtyJob = quantityJob;
        }

        _updateComponentMaterial();
        _updateComponentTime();
        _generateMaterialListQuantity();
    };

    /**
     * Update compenents bill of materials.
     * @private
     */
    var _updateComponentMaterial = function() {
        if(!isMaterialListLoaded || !options.hasManufacturedComponent) {
            return;
        }

        for(var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]];

            // if it's not a manufactured material, we stop here
            if(!material.isManufactured) {
                continue;
            }

            var runs = Math.ceil(
                material.qtyJob / material.resultQtyPerRun
            );
            material.runs = runs;

            $('.sub-list-'+ material.id +' .run-required').html(runs);
            $('.sub-list-'+ material.id +' .qty-required').html(material.qtyJob);

            // update the sub comps (if there are some :)) for this material
            for(var j in material.componentIdList) {
                var subMaterial = material.materials[material.componentIdList[j]];

                var quantityAdjusted = eveUtils.calculateAdjustedQuantity(
                    subMaterial.qtyRequiredPerRun,
                    material.materialEfficiency,
                    assemblyStats[material.facility].me
                );
                var quantityJob = eveUtils.calculateJobQuantity(
                    quantityAdjusted,
                    material.runs
                );

                subMaterial.qtyAdjusted = quantityAdjusted;
                subMaterial.qtyJob = quantityJob;

                var selector = '.sub-list-'+ material.id +' tr.material[data-id="'+ subMaterial.id +'"]';
                $(selector + ' td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2));
                $(selector + ' td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob));

            }
        }
    };

    /**
     * Update main blueprint times. Always called by update material function.
     * @private
     */
    var _updateTime = function() {
        var time = eveUtils.calculateJobTime(
            materialsData.materials[materialsData.productItemId].timePerRun,
            options.runs,
            assemblyStats[options.facility].te,
            options.timeEfficiency,
            options.industryLvl, options.advancedIndustryLvl,
            options.t2ConstructionLvl, options.primaryScienceLevel, options.secondaryScienceLevel,
            true
        );

        materialsData.materials[materialsData.productItemId].timeTotal = time;

        var time_text = utils.durationToString(time);
        $('.main-list .total-time').html(time_text);
    };

    /**
     * Update component blueprints times. Always called by update components material function.
     * @private
     */
    var _updateComponentTime = function() {
        if(!isMaterialListLoaded || !options.hasManufacturedComponent) {
            return;
        }

        for(var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]];

            if(!material.isManufactured) {
                continue;
            }

            var time = eveUtils.calculateJobTime(
                material.timePerRun,
                material.runs,
                assemblyStats[material.facility].te,
                material.timeEfficiency,
                options.industryLvl, options.advancedIndustryLvl,
                0, 0, 0,
                false
            );

            material.timeTotal = time;

            var time_text = utils.durationToString(time);
            $('.sub-list-' + material.id + ' .total-time').html(time_text);
        }
    };

    /**
     * Update component factory informations (from modal)
     * @private
     */
    var _updateComponentInformations = function(allComponents) {
        // init values
        var selector;
        var components;
        if(allComponents) {
            components = materialsData.componentIdList;
        } else {
            components = [parseInt($('#componentModalBpName').attr('data-bp-id'))];
        }

        // get data
        var tax = $('#modal-tax').val();
        var system = $('#modal-system').val();
        var ME = parseInt($('#Modal-ME-Level').text());
        var TE = parseInt($('#Modal-TE-Level').text());
        var facility = parseInt($('#modal-facility').find(':selected').val());

        for(var i in components) {
            var componentId = components[i];
            materialsData.materials[componentId].manufacturingSystem = system;
            materialsData.materials[componentId].facility = facility;
            materialsData.materials[componentId].tax = tax;
            materialsData.materials[componentId].materialEfficiency = ME;
            materialsData.materials[componentId].timeEfficiency = TE;
            _updateComponentBpInfoDisplay(componentId);
        }

        _updateComponentMaterial();
        _updateComponentTime();
        _generateMaterialListQuantity();
        $('#componentModalBpName').modal('hide');
    };

    /**
     * update component factory informations in the page
     * @private
     * @param the id of the blueprint we update
     */
    var _updateComponentBpInfoDisplay = function(id) {
        $('.sub-list-'+ id +' .system').html(materialsData.materials[id].manufacturingSystem);
        $('.sub-list-'+ id +' .tax').html(Humanize.intcomma(materialsData.materials[id].tax,2));
        $('.sub-list-'+ id +' .me').html(materialsData.materials[id].materialEfficiency);
        $('.sub-list-'+ id +' .te').html(materialsData.materials[id].timeEfficiency);
        $('.sub-list-'+ id +' .facility').html(assemblyStats[materialsData.materials[id].facility].name);
    };

    /**
     * Get the list of materials for the given blueprint
     * @private
     */
    var _getComponentMaterials = function() {
        if(isMaterialListLoaded || !options.hasManufacturedComponent) {
            return;
        }
        if(tplSublistBlock == '' || tplSublistRow == '') {
            // if any template is not yet set, try again in 1sec
            return setTimeout(_getComponentMaterials, 1000);
        }
        $.getJSON(lb.urls.materialBOMUrl, function(materialListResult) {
            var materialList = materialListResult['result'];
            var html = '';

            for(var i in materialList) {
                var rows = '';
                var tmpMaterial = materialList[i];
                var material = materialsData.materials[tmpMaterial['product_id']]
                material.blueprint_id = tmpMaterial['id'];
                material.blueprint_name = tmpMaterial['name'];
                material.blueprint_icon = tmpMaterial['icon'];

                // quantity and runs
                material.resultQtyPerRun = tmpMaterial['product_qty_per_run'];
                material.runs = Math.ceil(material.qtyJob / material.resultQtyPerRun);

                // production time
                material.timePerRun = tmpMaterial['time'];
                material.timeTotal = eveUtils.calculateJobTime(
                    material.timePerRun,
                    material.runs,
                    assemblyStats[material.facility].te,
                    material.timeEfficiency,
                    options.industryLvl, options.advancedIndustryLvl,
                    0, 0, 0,
                    false
                );

                var timeHuman = utils.durationToString(material.timePerRun);
                var timeTotalHuman = utils.durationToString(material.timeTotal);

                // sub materials
                for(var j in tmpMaterial['materials']) {
                    var tmpSubMaterial = tmpMaterial['materials'][j];

                    material.componentIdList.push(tmpSubMaterial['id']);
                    var subMaterial = material.materials[tmpSubMaterial['id']] = {
                        'id': tmpSubMaterial['id'],
                        'name': tmpSubMaterial['name'],
                        'icon': tmpSubMaterial['icon'],
                        'qtyRequiredPerRun': tmpSubMaterial['quantity']
                    };

                    subMaterial.qtyAdjusted = eveUtils.calculateAdjustedQuantity(
                        subMaterial.qtyRequiredPerRun,
                        material.materialEfficiency,
                        assemblyStats[material.facility].me
                    );
                    subMaterial.qtyJob = eveUtils.calculateJobQuantity(
                        subMaterial.qtyAdjusted,
                        material.runs
                    );

                    rows += tplSublistRow.replace(/@@ID@@/g, subMaterial.id)
                                        .replace(/@@QTY@@/g, subMaterial.qtyRequiredPerRun)
                                        .replace(/@@QTY-STD@@/g, Humanize.intcomma(subMaterial.qtyRequiredPerRun))
                                        .replace(/@@QTY-ADJ@@/g, subMaterial.qtyAdjusted)
                                        .replace(/@@QTY-JOB@@/g, subMaterial.qtyJob)
                                        .replace(/@@QTY-ADJ-HUMAN@@/g, Humanize.intcomma(subMaterial.qtyAdjusted,2))
                                        .replace(/@@QTY-JOB-HUMAN@@/g, Humanize.intcomma(subMaterial.qtyJob))
                                        .replace(/@@ICON@@/g, subMaterial.icon)
                                        .replace(/@@NAME@@/g, subMaterial.name);
                }
                html += tplSublistBlock.replace(/@@ICON@@/g, material.blueprint_icon)
                                     .replace(/@@NAME@@/g, material.blueprint_name)
                                     .replace(/@@ID@@/g, material.id)
                                     .replace(/@@PRODUCT_NAME@@/g, material.name)
                                     .replace(/@@PRODUCT_QTY@@/g, material.resultQtyPerRun)
                                     .replace(/@@QTY@@/g, material.qtyJob)
                                     .replace(/@@RUN@@/g, material.runs)
                                     .replace(/@@SYSTEM@@/g, material.manufacturingSystem)
                                     .replace(/@@TAX@@/g, Humanize.intcomma(material.tax,2))
                                     .replace(/@@FACILITY_NAME@@/g, assemblyStats[material.facility].name)
                                     .replace(/@@ACTIVITY_TIME_HUMAN@@/g, timeHuman)
                                     .replace(/@@ACTIVITY_TIME_TOTAL@@/g, timeTotalHuman)
                                     .replace(/@@BOM@@/g, rows);
            }

            isMaterialListLoaded = true;
            $('#tab-subcomp').html(html);

            // update material quantity list
            _generateMaterialListQuantity();

            // update tables
            _updateSummaryTabs();
        });
    };

    /**
     * Get market price for items
     * @private
     */
    var _getAllPrices = function() {
        if(priceData.currentRegion in priceData.prices) {
            _updatePriceTable();
            return;
        }

        var data = {
            'buysell': priceData.typeOrder,
            'region': priceData.currentRegion,
            'item_list': [materialsData.productItemId],
        }

        // create the list of component ids
        for(var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]];
            data.item_list.push(material.id);

            for(var j in material.componentIdList) {
                var subBomId = material.componentIdList[j];
                if($.inArray(subBomId, data.item_list) == -1) {
                    data.item_list.push(subBomId);
                }
            }
        }

        // get the prices
        $.ajax({
            url: lb.urls.priceUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            dataType: 'json',
            success: function(jsonPrice) {
                priceData.prices[priceData.currentRegion] = jsonPrice['price'];
                _updatePriceTable();
            },
        });
    };

    /**
     * generate the material list with quantity for all main materials
     * or only components, depending on the settings we have.
     *
     * @private
     * @return the list of objects for each materials, including id, name, qty
     */
    var _generateMaterialListQuantity = function() {
        var materialList = {};
        var onlySubComponents = (useComponents && options.hasManufacturedComponent);

        for(var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]];

            // we want all material, or at least, those that cannot be manufactured (PI, moongoo...)
            if(!material.isManufactured || !onlySubComponents) {
                materialList[material.id] = materialList[material.id] || {
                    qty: 0,
                    name: material.name,
                    icon: material.icon
                };
                materialList[material.id].qty += material.qtyJob;

            } else {
                for(var j in material.componentIdList) {
                    var subMaterial = material.materials[material.componentIdList[j]];
                    materialList[subMaterial.id] = materialList[subMaterial.id] || {
                        qty: 0,
                        name: subMaterial.name,
                        icon: subMaterial.icon
                    };
                    materialList[subMaterial.id].qty += subMaterial.qtyJob;
                }
            }
        }
        materialQuantityList = materialList;
    };

    /**
     * Update all tables from summary and price tables.
     * @private
     * @todo uncomment adjusted price
     */
    var _updateSummaryTabs = function() {
        _updateMaterialSummaryTable();
        _updateTimeTable();
        _getAllPrices();
        //_getAdjustedPrices();
    };


    /**
     * Update the production time in the summary tab.
     * Only called by _updateSummaryTabs
     * @private
     */
    var _updateTimeTable = function() {
        var iconColumn = '';
        if(options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>';
        }
        var rowTime = '<tr>' + iconColumn + '<td>@@NAME@@</td><td>@@TIME@@</td></tr>';
        var output = "";

        var materialList = $.merge([materialsData.productItemId], materialsData.componentIdList);

        for(var i in materialList) {
            var material = materialsData.materials[materialList[i]];
            if(material.isManufactured) {
                output += rowTime.replace(/@@ICON@@/g, material.icon)
                                 .replace(/@@NAME@@/g, material.name)
                                 .replace(/@@TIME@@/g, utils.durationToString(material.timeTotal));
            }
        }
        $('.materials-time tbody').html(output);
    }


    /**
     * Update the material list with quantity in the summary tab.
     * Only called by _updateSummaryTabs
     * @private
     */
    var _updateMaterialSummaryTable = function() {
        var iconColumn = '';
        if(options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>';
        }
        var rowMaterial = '<tr>' + iconColumn + '<td>@@NAME@@</td><td class="quantity">@@QTY@@</td></tr>';
        var output = "";

        for(var id in materialQuantityList) {
            output += rowMaterial.replace(/@@ICON@@/g, materialQuantityList[id].icon)
                                 .replace(/@@NAME@@/g, materialQuantityList[id].name)
                                 .replace(/@@QTY@@/g, Humanize.intcomma(materialQuantityList[id].qty));
        }

        $('.materials-requirement tbody').html(output);
    }


    /**
     * Update the price list with total etc in the price tab.
     * Only called by _getAllPrices
     * @private
     */
    var _updatePriceTable = function() {
        var prices = priceData.prices[priceData.currentRegion];
        var iconColumn = '';
        if(options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>';
        }
        var rowPrice = '<tr>' + iconColumn + '<td>@@NAME@@</td>'
                     + '<td class="quantity">@@QTY@@</td>'
                     + '<td class="ppu price">@@PRICE@@</td>'
                     + '<td class="total price">@@PRICE_TOTAL@@</td></tr>';

        var output = "";
        var materialTotalPrice = 0;

        // calculate price per material and display it
        for(var id in materialQuantityList) {
            var price = (id in prices) ? prices[id][priceLoad.typeOrder] : 0;
            var materialPrice = price * materialQuantityList[id].qty;
            materialTotalPrice += materialPrice;

            output += rowPrice.replace(/@@ICON@@/g, materialQuantityList[id].icon)
                               .replace(/@@NAME@@/g, materialQuantityList[id].name)
                               .replace(/@@QTY@@/g, Humanize.intcomma(materialQuantityList[id].qty))
                               .replace(/@@PRICE@@/g, Humanize.intcomma(price, 2))
                               .replace(/@@PRICE_TOTAL@@/g, Humanize.intcomma(materialPrice, 2));
        }
        $('.materials-prices tbody').html(output);

        // fill footer rows (total, margin, markup...)
        var productPrice = (materialsData.productItemId in prices) ? prices[materialsData.productItemId]['sell'] : 0.0;
        productPrice *= materialsData.materials[materialsData.productItemId].resultTotalQty;

        var margin = productPrice - materialTotalPrice;
        var marginPercent = (productPrice > 0) ? (margin / productPrice) * 100 : 0;
        var markupPercent = (productPrice > 0) ? (margin / materialTotalPrice) * 100 : 0;

        $('.materials-prices tfoot td#mat-total-price').html(Humanize.intcomma(materialTotalPrice, 2));
        $('.materials-prices tfoot td#product-price').html(Humanize.intcomma(productPrice, 2));
        $('.materials-prices tfoot td#margin').html(Humanize.intcomma(margin, 2));
        $('.materials-prices tfoot td#margin-percent').html(Humanize.intcomma(marginPercent, 2) + "%");
        $('.materials-prices tfoot td#markup-percent').html(Humanize.intcomma(markupPercent, 2) + "%");
    };


    /**
     * Update the price list with total etc in the price tab.
     * Only called by _getAdjustedPrices and _getSystemCostIndex
     * @TODO calculate tax
     * @private
     */
    var _updateTaxTable = function() {
        var iconColumn = '';
        if(options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>';
        }
        var rowTax = '<tr>' + iconColumn + '<td>@@NAME@@</td>'
                   + '<td class="quantity">@@QTY@@</td>'
                   + '<td class="tax price">@@TAX@@</td></tr>';

        var output = "";
        var materialList = $.merge([materialsData.productItemId], materialsData.componentIdList);

        for(var i in materialList) {
            material = materialsData.materials[materialList[i]];
            if(material.isManufactured) {
                var tax_price = 0;
                output += rowTax.replace(/@@ICON@@/g, material.icon)
                                .replace(/@@NAME@@/g, material.name)
                                .replace(/@@TAX@@/g, tax_price)
                                .replace(/@@QTY@@/g, Humanize.intcomma(material.qtyJob));
            }
        }
        $('.materials-taxes tbody').html(output);
    };


    // -------------------------------------------------
    // Events declarations
    //

    /**
     * Ajax call to get html template for later use.
     * @private
     */
    var _initTemplates = function () {
        $.get(lb.urls.tplSublistBlockUrl,
            function(tpl) { tplSublistBlock = tpl; }
        );
        $.get(lb.urls.tplSublistRowUrl,
            function(tpl) { tplSublistRow = tpl; }
        );
    };

    /**
     * Init tooltips
     * @private
     */
    var _initTooltip = function() {
        $('[data-toggle="tooltip"]').tooltip();
    };

    /**
     * Init input fields
     * @private
     */
    var _initInputs = function() {
        $('#runs').on('keyup', _runsOnKeyUp)
                  .on('change', _runOnChange);

        $('#facility').on('change', function() {
            options.facility = parseInt($('#facility').val());
            _updateTime();
            _updateMaterial();
        });

        $("#raw-components input[type='checkbox']").on('change', _componentButtonOnStateChange);
    };

    /**
     * Init tab event actions
     * @private
     */
    var _initTabs = function() {
        $('#bp-tabs a').on('click',
            function (e) {
                e.preventDefault();
                $(this).tab('show');
            }
        ).on('shown.bs.tab', _tabOnShow);
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

        $('#system').typeahead(null,{
            name: 'system',
            displayKey: 'name',
            source: systems.ttAdapter(),
        });
        $('#modal-system').typeahead(null,{
            name: 'system',
            displayKey: 'name',
            source: systems.ttAdapter(),
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
        $('#ModalME').slider({
            min: 0,
            max: 10,
            range: "min",
            slide: _modalMaterialEfficiencyOnUpdate,
        });
        $('#ModalTE').slider({
            min: 0,
            max: 20,
            step: 2,
            range: "min",
            slide: _modalTimeEfficiencyOnUpdate,
        });
        $('#industry-level, #adv-industry-level, #t2-level, #t2-science1, #t2-science2').slider({
            min: 0,
            max: 5,
            range: "min",
            slide: _skillOnUpdate,
        });
    };

    /**
     * Init all sliders on the page
     * @private
     */
    var _initModal = function() {
        $('#subComponentBpConfigModal').on('show.bs.modal', function(event) {
            var button = $(event.relatedTarget);
            var id = button.attr('data-id');
            var name = materialsData.materials[id].name;

            var system = materialsData.materials[id].manufacturingSystem;
            var facility = materialsData.materials[id].facility;
            var tax = materialsData.materials[id].tax;

            var me = materialsData.materials[id].materialEfficiency;
            var te = materialsData.materials[id].timeEfficiency;

            $('#componentModalBpName').html(name);
            $('#componentModalBpName').attr('data-bp-id', id);
            $('#modal-tax').val(tax);
            $('#modal-system').val(system);
            $('#modal-facility option[value='+facility+']').prop('selected',true);
            $('#ModalME').slider("option", "value", me);
            $('#ModalTE').slider("option", "value", te);
            $('#Modal-ME-Level').html(me);
            $('#Modal-TE-Level').html(te);
        });

        $('#modal-apply').on('click', _onModalBpApplyOne);
        $('#modal-apply-all').on('click', _onModalBpApplyAll);

        $('#modal-price-apply').on('click',
            function() {
               _getAllPrices();
            }
        );
    };


    // -------------------------------------------------
    // Events functions
    //

    /**
     * Function called on event keyup for 'run' text field
     * @private
     */
    var _runsOnKeyUp = function(e) {
        if(!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.runs = 1;
        } else {
            options.runs = parseInt($(this).val());
        }
        var material = materialsData.materials[materialsData.productItemId];
        var qty = material.resultQtyPerRun * options.runs;
        material.qtyJob = qty;

        $('#qty-required-'+ material.id).html(Humanize.intcomma(qty));

        _updateMaterial();
        _updateTime();

        return false;
    };

    /**
     * Function called on event change for 'run' text field
     * Replace the text input value with an integer (if it's anything else)
     * @private
     */
    var _runOnChange = function(e) {
        $(this).val(options.runs);
        return false;
    };

    /**
     * Function called on event show for tabs
     * @private
     * @TODO only call update on some tabs.
     */
    var _tabOnShow = function(e) {
        var tab = $(this).attr('href');

        // use component button events.
        if(options.hasManufacturedComponent) {
            switch(tab) {
                case '#tab-summary':
                    if(lastTab == "#tab-price") {
                        $('#raw-components').detach().appendTo(tab + ' .raw-component-btn');
                        lastTab = tab;
                    }
                    break;
                case '#tab-price':
                    if(lastTab == "#tab-summary") {
                        $('#raw-components').detach().appendTo(tab + ' .raw-component-btn');
                        lastTab = tab;
                    }
                    break;
            }
        }

        // only update when on summary / price tables
        if(tab == "#tab-price" || tab == "#tab-summary") {
            _updateSummaryTabs();
        }
    };

    /**
     * Function called on event update on the material efficiency slider
     * @private
     */
    var _materialEfficiencyOnUpdate = function(event, ui) {
        $('#ME-Level').html(ui.value+"%");
        options.materialEfficiency = parseInt(ui.value);
        _updateMaterial();
    };

    /**
     * Function called on event update on the time efficiency slider
     * @private
     */
    var _timeEfficiencyOnUpdate = function(event, ui) {
        $('#TE-Level').html(ui.value+"%");
        options.timeEfficiency = parseInt(ui.value);
        _updateTime();
    };

    /**
     * Function called on event update on the material efficiency slider
     * in the modal window
     * @private
     */
    var _modalMaterialEfficiencyOnUpdate = function(event, ui) {
        $('#Modal-ME-Level').html(ui.value);
    };

    /**
     * Function called on event update on the time efficiency slider
     * in the modal window
     * @private
     */
    var _modalTimeEfficiencyOnUpdate = function(event, ui) {
        $('#Modal-TE-Level').html(ui.value);
    };

    /**
     * Function called on event update on the skill level sliders
     * @private
     */
    var _skillOnUpdate = function(event, ui) {
        var id = $(this).attr('id');
        var value = parseInt(ui.value);

        switch(id) {
            case 'industry-level':
                options.industryLvl = value;
                $('#industry-level-display').html(value);
                break;

            case 'adv-industry-level':
                options.advancedIndustryLvl = value;
                $('#adv-industry-level-display').html(value);
                break;

            case 't2-level':
                options.t2ConstructionLvl = value;
                $('#t2-level-display').html(value);
                break;

            case 't2-science1':
                options.primaryScienceLevel = value;
                $('#t2-science1-display').html(value);
                break;

            case 't2-science2':
                options.secondaryScienceLevel = value;
                $('#t2-science2-display').html(value);
                break;
        };
        _updateTime();
        _updateComponentTime();
    };


    /**
     * Proxy function for apply click event in modal
     * @call updateComponentInformations
     * @private
     */
    var _onModalBpApplyOne = function() {
        _updateComponentInformations(false);
    };

    /**
     * Proxy function for apply all click event in modal
     * @call updateComponentInformations
     * @private
     */
    var _onModalBpApplyAll = function() {
        _updateComponentInformations(true);
    };

    /**
     * Update button "raw components" state and update tables
     * @private
     */
    var _componentButtonOnStateChange = function() {
        // update button styles
        var state = "YES";
        var style = 'btn-danger';
        var newStyle = 'btn-success';

        if(!this.checked) {
            state = "NO";
            style = 'btn-success';
            newStyle = 'btn-danger';
        }
        $('#raw-components .state').html(state);
        $('#raw-components .btn').removeClass(style).addClass(newStyle);

        // update material tables infos.
        useComponents = this.checked;
        _generateMaterialListQuantity();
        _updateSummaryTabs();
    };


    /**
     * Runner function
     */
    var run = function() {
        // init interface stuff before some check, to have no UI issue
        _initTooltip();
        _initInputs();
        _initSliders();

        // check all required urls (so we don't have to do it later)
        if(!lb.urls.systemUrls || !lb.urls.materialBOMUrl || !lb.urls.priceUrl || !lb.urls.tplSublistBlockUrl || !lb.urls.tplSublistRowUrl) {
            alert('Error, some URL are missing, this application cannot work properly without them.');
            return;
        }

        // other init that require ajax call
        _initTemplates();
        _initTypeahead();
        _initTabs();
        _initModal();

        // get materials
        _getComponentMaterials();
    };


    // -------------------------------------------------
    // return object
    //
    return {
        // required objects
        options: options,
        materialsData: materialsData,

        // functions
        run: run,
    };
})(jQuery, lb, utils, eveUtils, Humanize, JSON);

lb.registerModule('manufacturingBlueprint', manufacturingBlueprint);


// tax: station cost multiplier : 0.98
