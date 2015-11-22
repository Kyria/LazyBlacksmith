LazyBlacksmith.blueprint.manufacturing = {
    //variables 
    ME: 0,
    TE: 0,
    runs: 1,
    industryLvl: 0,
    advIndustryLvl: 0,
    t2IndustryLvl: 0,
    t2ScienceLvl1: 0,
    t2ScienceLvl2: 0,
    t2IndustryLvl: 0,

    hasManufacturedComponent: false,
    useIcons: false,

    // urls
    systemUrls: false,
    materialBOM: false,
    tplSublistBlockUrl: false,
    tplSublistRowUrl: false,
    
    // boolean : did we already load submaterials ?
    materialBOMLoaded: false,
    // boolean : do we calculate summary with sub components
    summarySubComponent: false,

    // tpl values
    tplSublistBlock: '',
    tplSublistRow: '',

    arrayStats: [
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
    ],


    onload: function() {
        LazyBlacksmith.blueprint.manufacturing.initTemplates();
        LazyBlacksmith.blueprint.manufacturing.initSliders();
        LazyBlacksmith.blueprint.manufacturing.initInputs();
        LazyBlacksmith.blueprint.manufacturing.initTabs(); 
        LazyBlacksmith.blueprint.manufacturing.initTypeahead(); 
        LazyBlacksmith.blueprint.manufacturing.initModal(); 
        LazyBlacksmith.blueprint.manufacturing.initTooltip(); 
    },
    
    /**
     * Init functions
     */
    initTemplates: function() {
        if(!LazyBlacksmith.blueprint.manufacturing.tplSublistBlockUrl){
            alert('Error, no URL is found to get sublist block template.');
            return;
        }
        if(!LazyBlacksmith.blueprint.manufacturing.tplSublistRowUrl){
            alert('Error, no URL is found to get sublist row template.');
            return;
        }
        $.get(LazyBlacksmith.blueprint.manufacturing.tplSublistBlockUrl, 
            function(tpl) {
                LazyBlacksmith.blueprint.manufacturing.tplSublistBlock = tpl;
            }
        );
        $.get(LazyBlacksmith.blueprint.manufacturing.tplSublistRowUrl, 
            function(tpl) {
                LazyBlacksmith.blueprint.manufacturing.tplSublistRow = tpl;
            }
        );
    },

    initTooltip: function() {
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        })
    },

    initTypeahead: function() {
        var systems = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            limit: 10,
            prefetch: {
                url: LazyBlacksmith.blueprint.manufacturing.systemUrls,
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
    },
    
    initInputs: function() {
        $('#runs').on('keyup',
            function(event) {
                event.preventDefault();
                if(!$.isNumeric($(this).val()) || $(this).val() <= 0) {
                    LazyBlacksmith.blueprint.manufacturing.runs = 1;
                } else {
                    LazyBlacksmith.blueprint.manufacturing.runs = parseInt($(this).val());
                }
                LazyBlacksmith.blueprint.manufacturing.updateMaterials();
                LazyBlacksmith.blueprint.manufacturing.updateTimes();
            }
        );

        $('#facility').on('change', 
            function(event) {
                LazyBlacksmith.blueprint.manufacturing.updateMaterials();
                LazyBlacksmith.blueprint.manufacturing.updateTimes();
        });

        $('#display-sub-components-summary').bootstrapSwitch({
            'size': 'mini',
            'onColor': 'success',
            'labelText': 'Show components requirements',
            'state': false,
            'onSwitchChange': function(event, state) {
                LazyBlacksmith.blueprint.manufacturing.summarySubComponent = state;
                $('#display-sub-components-price').bootstrapSwitch('state', state, true);
                LazyBlacksmith.blueprint.manufacturing.updateSummaryPriceTables();
            }
        });
        $('#display-sub-components-price').bootstrapSwitch({
            'size': 'mini',
            'onColor': 'success',
            'labelText': 'Show components requirements',
            'state': false,
            'onSwitchChange': function(event, state) {
                LazyBlacksmith.blueprint.manufacturing.summarySubComponent = state;
                $('#display-sub-components-summary').bootstrapSwitch('state', state, true);
                LazyBlacksmith.blueprint.manufacturing.updateSummaryPriceTables();
            }
        });
    },
    
    initTabs: function() {
        // tabs
        $('#bp-tabs a').on('click', 
            function (e) {
                e.preventDefault();
                $(this).tab('show');
            }
        );
        $('#bp-tabs a').on('shown.bs.tab', function(e) {
            if(!LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded
                && LazyBlacksmith.blueprint.manufacturing.hasManufacturedComponent) {
                LazyBlacksmith.blueprint.manufacturing.getMaterialsBOM();
                LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded = true;
            } else {
                LazyBlacksmith.blueprint.manufacturing.updateSummaryPriceTables();
            }
        });
    },
    
    initSliders: function() {
        $('#ME').slider({
            min: 0,
            max: 10,
            range: "min",
            slide: LazyBlacksmith.blueprint.manufacturing.updateME,
        });
        $('#TE').slider({
            min: 0,
            max: 20,
            step: 2,
            range: "min",
            slide: LazyBlacksmith.blueprint.manufacturing.updateTE,
        });
        $('#ModalME').slider({
            min: 0,
            max: 10,
            range: "min",
            slide: LazyBlacksmith.blueprint.manufacturing.updateModalME,
        });
        $('#ModalTE').slider({
            min: 0,
            max: 20,
            step: 2,
            range: "min",
            slide: LazyBlacksmith.blueprint.manufacturing.updateModalTE,
        });
        $('#industry-level, #adv-industry-level, #t2-level, #t2-science1, #t2-science2').slider({
            min: 0,
            max: 5,
            range: "min",
            slide: LazyBlacksmith.blueprint.manufacturing.updateSkill,
        });
    },
    
    initModal: function() {
        $('#subComponentBpConfigModal').on('show.bs.modal', function (event) {
            var button = $(event.relatedTarget);
            var id = button.attr('data-id');
            var name = button.attr('data-name');

            var system = $('.sub-list-'+id).attr('data-system');
            var facility = $('.sub-list-'+id).attr('data-facility');
            var tax = $('.sub-list-'+id).attr('data-tax');

            var me = parseInt($('.sub-list-'+id+' .me').text());
            var te = parseInt($('.sub-list-'+id+' .te').text());
            var facility = $('.sub-list-'+id+' .facility').attr('data-facility');

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

        $('#modal-apply').on('click',
            function() {
                LazyBlacksmith.blueprint.manufacturing.updateSubBpInformations(true);
            }
        );

        $('#modal-apply-all').on('click',
            function() {
                LazyBlacksmith.blueprint.manufacturing.updateSubBpInformations(false);
            }
        );
    },

    /**
     * Modal update action.
     */
    updateSubBpInformations: function(one) {
        var selector;
        if(one) {
            var bpId = parseInt($('#componentModalBpName').attr('data-bp-id'));
            selector = '.sub-list-'+bpId;
        } else {
            selector = '[class*=sub-list]';
        }
        var tax = $('#modal-tax').val();
        var system = $('#modal-system').val();
        var facility = parseInt($('#modal-facility').find(':selected').val());
        var ME = parseInt($('#Modal-ME-Level').text());
        var TE = parseInt($('#Modal-TE-Level').text());

        var facilityName = LazyBlacksmith.blueprint.manufacturing.getFacilityName(facility);

        $(selector).attr('data-system', system);
        $(selector).attr('data-tax', tax);

        $(selector+' .me').html(ME);
        $(selector+' .te').html(TE);
        $(selector+' .facility').attr('data-facility', facility);
        $(selector+' .facility').text(facilityName);

        LazyBlacksmith.blueprint.manufacturing.updateMaterials();
        $('#componentModalBpName').modal('hide');
    },

    /**
     * Update functions
     */
    updateME: function(event, ui) {
        $('#ME-Level').html(ui.value+"%");
        LazyBlacksmith.blueprint.manufacturing.ME = parseInt(ui.value);
        LazyBlacksmith.blueprint.manufacturing.updateMaterials();
    },

    updateTE: function(event, ui) {
        $('#TE-Level').html(ui.value+"%");
        LazyBlacksmith.blueprint.manufacturing.TE = parseInt(ui.value);
        LazyBlacksmith.blueprint.manufacturing.updateTimes();
    },

    updateModalME: function(event, ui) {
        $('#Modal-ME-Level').html(ui.value);
    },

    updateModalTE: function(event, ui) {
        $('#Modal-TE-Level').html(ui.value);
    },

    updateSkill: function(event, ui) {
        var id = $(this).attr('id');
        var value = parseInt(ui.value);

        switch(id) {
            case 'industry-level':
                LazyBlacksmith.blueprint.manufacturing.industryLvl = value;
                $('#industry-level-display').html(value);
                break;

            case 'adv-industry-level':
                LazyBlacksmith.blueprint.manufacturing.advIndustryLvl = value;
                $('#adv-industry-level-display').html(value);
                break;

            case 't2-level':
                LazyBlacksmith.blueprint.manufacturing.t2IndustryLvl = value;
                $('#t2-level-display').html(value);
                break;

            case 't2-science1':
                LazyBlacksmith.blueprint.manufacturing.t2ScienceLvl1 = value;
                $('#t2-science1-display').html(value);
                break;

            case 't2-science2':
                LazyBlacksmith.blueprint.manufacturing.t2ScienceLvl2 = value;
                $('#t2-science2-display').html(value);
                break;
        };
        LazyBlacksmith.blueprint.manufacturing.updateTimes();
    },

    updateTimes: function() {
        var timePerUnit = parseInt($('.main-list .time-per-run').attr('data-time'));
        var facility = parseInt($('#facility').val());
        //durationToString
        var time = LazyBlacksmith.blueprint.manufacturing.calculateTime(
            timePerUnit, 
            facility, 
            LazyBlacksmith.blueprint.manufacturing.TE,
            LazyBlacksmith.blueprint.manufacturing.runs,
            true
        );

        var time_text = LazyBlacksmith.utils.durationToString(time);
        $('.main-list .total-time').html(time_text);

        $('.main-list .materials-list tr.material').each(
            function() {
                if(!LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded 
                    || $(this).attr('data-is-manufactured') == undefined) {
                    return;
                }
                var id = parseInt($(this).attr('data-id'));        

                var runs = parseInt($('#run-required-'+id).text());
                var facility = parseInt($('.sub-list-'+id+' .facility').attr('data-facility'));
                var TE = parseInt($('.sub-list-'+id+' .te').text());
                var timePerUnit = parseInt($('.sub-list-'+id+' .time-per-run').attr('data-time'));

                var time = LazyBlacksmith.blueprint.manufacturing.calculateTime(
                    timePerUnit, 
                    facility, 
                    TE,
                    runs,
                    false
                );
                var time_text = LazyBlacksmith.utils.durationToString(time);

                $('.sub-list-'+id+' .total-time').html(time_text);
            }
        );
    },
    
    updateMaterials: function() {
        // main BPO update
        $('.main-list .materials-list tr.material').each(
            function() {
                var id = parseInt($(this).attr('data-id'));
                var quantity = parseInt($(this).attr('data-qty'));
                
                var facility = parseInt($('#facility').val());
                var quantityAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(quantity, LazyBlacksmith.blueprint.manufacturing.ME, facility);
                var quantityJob = LazyBlacksmith.blueprint.manufacturing.calculateJob(quantityAdjusted, LazyBlacksmith.blueprint.manufacturing.runs);

                $(this).find('td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2));
                $(this).find('td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob));
        
                $(this).attr('data-qty-adj',quantityAdjusted);
                $(this).attr('data-qty-job',quantityJob);                   
                
                if(!LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded 
                    || $(this).attr('data-is-manufactured') == undefined) {
                    return;
                }

                $('#qty-required-'+id).html(quantityJob);

                // calculate the number of run required for each subcomps
                var qty_required = parseInt($('#qty-required-'+id).text());
                var batch_per_run = parseInt($('.sub-list-'+id).attr('data-output-per-run'));

                var runs = Math.ceil(qty_required/batch_per_run)
                $('#run-required-'+id).html(runs);

                var facility = parseInt($('.sub-list-'+id+' .facility').attr('data-facility'));

                var ME = parseInt($('.sub-list-'+id+' .me').text());

                // update the sub comps (if there are some :)) for this material
                $('.sub-list-'+id+' .materials-list tr.material').each(
                    function() {
                        var quantity = parseInt($(this).attr('data-qty'));

                        var quantityAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(quantity, ME, facility);
                        var quantityJob = LazyBlacksmith.blueprint.manufacturing.calculateJob(quantityAdjusted, runs);
                        
                        $(this).find('td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2));
                        $(this).find('td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob));
                        
                        $(this).attr('data-qty-adj',quantityAdjusted);
                        $(this).attr('data-qty-job',quantityJob);   
                    }
                );
            } 
        );
        
        // update all times at the end.
        LazyBlacksmith.blueprint.manufacturing.updateTimes();
    },

    /**
     * Update the summary tab.
     */
    getMaterialListAndIcon: function() {
        var materials = [];
        // get the correct material selector
        var materialSelector = '.main-list .material';
        if(LazyBlacksmith.blueprint.manufacturing.summarySubComponent
            && LazyBlacksmith.blueprint.manufacturing.hasManufacturedComponent) {
            materialSelector = '.material:not([data-is-manufactured])';
        }

        // find icons for all items
        var icons = [];
        if(LazyBlacksmith.blueprint.manufacturing.useIcons) {
            var mainItemId = parseInt($('#main-product').attr('data-id'));
            var mainItemIcon = $('#main-product').attr('data-icon');
            var mainItemName = $('#main-product').text();
            icons[mainItemId] = '<img src="'+mainItemIcon+'" alt="'+mainItemName+'">';
            $('.material').each(
                function() {
                    var id = $(this).attr('data-id');
                    var icon = $(this).find('td.icon').html();
                    icons[id]=icon;
                }
            );
        }

        // calculate materials summary
        $(materialSelector).each(
            function() { 
                var qty = parseInt($(this).attr('data-qty-job'));
                var id = $(this).attr('data-id');
                var name = $(this).attr('data-name');
                if(!(id in materials)) {
                    materials[id] = {};
                    materials[id].qty = 0
                }
                materials[id].qty += qty;
                materials[id].itemName = name;
            }
        );
        return {'materials': materials, 'icons': icons}  
    },

    updateSummaryPriceTables: function() {
        var rowMaterial = '<tr>';
        var rowTime = '<tr>';
        var rowPrice = '<tr>';
        var rowTax = '<tr>';
        var iconColumn = '';
        if(LazyBlacksmith.blueprint.manufacturing.useIcons) {
            iconColumn = '<td class="icon">@@ICON@@</td>';
        }
        rowMaterial += iconColumn + '<td>@@NAME@@</td><td class="quantity">@@QTY@@</td></tr>';
        rowTime += iconColumn + '<td>@@NAME@@</td><td>@@TIME@@</td></tr>';
        rowPrice += iconColumn + '<td>@@NAME@@</td><td class="quantity" data-qty="@@QTY@@">@@HMN_QTY@@</td>' 
                               + '<td class="ppu price"></td><td class="total price"></td></tr>';
        rowTax += iconColumn + '<td>@@NAME@@</td><td class="quantity" data-qty="@@QTY@@">@@HMN_QTY@@</td>'
                             + '<td class="tax price"></td></tr>';

        var html_summary = "";
        var html_price = "";

        matAndIcons = LazyBlacksmith.blueprint.manufacturing.getMaterialListAndIcon();

        // fill summary qty table
        for(var id in matAndIcons['materials']) {
            html_summary += rowMaterial.replace(/@@ICON@@/g, matAndIcons['icons'][id])
                               .replace(/@@NAME@@/g, matAndIcons['materials'][id].itemName)
                               .replace(/@@QTY@@/g, Humanize.intcomma(matAndIcons['materials'][id].qty));
            html_price += rowPrice.replace(/@@ICON@@/g, matAndIcons['icons'][id])
                               .replace(/@@NAME@@/g, matAndIcons['materials'][id].itemName)
                               .replace(/@@QTY@@/g, matAndIcons['materials'][id].qty)
                               .replace(/@@HMN_QTY@@/g, Humanize.intcomma(matAndIcons['materials'][id].qty));

        }

        $('.materials-requirement tbody').html(html_summary);
        $('.materials-prices tbody').html(html_price);

        // now do time summary table
        var html_summary = "";
        var html_price = "";

        $('.total-time').each(
            function() {
                var id = $(this).attr('data-id');
                var name = $(this).attr('data-name');
                var time = $(this).text();
                var qty = parseInt($('#qty-required-'+id).attr('data-qty'));

                // main bp case
                if(qty == undefined) {
                    qty = 1;
                }

                html_summary += rowTime.replace(/@@ICON@@/g, matAndIcons['icons'][id])
                               .replace(/@@NAME@@/g, name)
                               .replace(/@@TIME@@/g, time);
                html_price += rowTax.replace(/@@ICON@@/g, matAndIcons['icons'][id])
                               .replace(/@@NAME@@/g, name)
                               .replace(/@@QTY@@/g, qty)
                               .replace(/@@HMN_QTY@@/g, Humanize.intcomma(qty));
            }
        );
        $('.materials-time tbody').html(html_summary);
        $('.materials-taxes tbody').html(html_price);

        LazyBlacksmith.blueprint.manufacturing.updatePrice();
    },

    updatePrice: function() {
        // get ALL items & qty
        // ajax to get prices + adjusted + industry index
        //      UNLESS we already got them !
        // fill price table
        // fill tax table
        //      need to find each bp
        //          for each bp, get BoM, calculate tax and display...
    },

    /**
     * Calculate the adjusted quantity
     */
    calculateAdjusted: function(quantity, ME, facility) {
        var MEBonus = (1.00-ME/100.00);
        var facilityBonus = LazyBlacksmith.blueprint.manufacturing.getFacilityMe(facility);
        return Math.max(1, quantity * MEBonus * facilityBonus);
    },
    
    /**
     * Calculate the job quantity
     */
    calculateJob: function(quantityAdjusted, runs) {
        return Math.max(runs, Math.ceil(quantityAdjusted * runs));
    },

    /**
     * Calculate the manufacturing time with the given informations.
     * 
     * Note: T2Time must never be used for subcomponents (as it's only required for tech2 items)
     */
    calculateTime: function(timePerUnit, facility, TE, runs, useT2Time) {
        var TEBonus = (1.00-TE/100.00);
        var facilityTe = LazyBlacksmith.blueprint.manufacturing.getFacilityTe(facility);
        var time = timePerUnit * TEBonus * facilityTe * runs;
        time *= (1 - LazyBlacksmith.blueprint.manufacturing.industryLvl * 0.04);
        time *= (1 - LazyBlacksmith.blueprint.manufacturing.advIndustryLvl * 0.03);
        if(useT2Time) {
            time *= (1 - LazyBlacksmith.blueprint.manufacturing.t2IndustryLvl * 0.01);
            time *= (1 - LazyBlacksmith.blueprint.manufacturing.t2ScienceLvl1 * 0.01);
            time *= (1 - LazyBlacksmith.blueprint.manufacturing.t2ScienceLvl2 * 0.01);
        }
        return time;
    },

    /**
     * Get facillity bonus values
     */
    getFacilityMe: function(facility) {
        return LazyBlacksmith.blueprint.manufacturing.arrayStats[facility].me;
    },
    getFacilityTe: function(facility) {
        return LazyBlacksmith.blueprint.manufacturing.arrayStats[facility].te;
    },
    getFacilityName: function(facility) {
        return LazyBlacksmith.blueprint.manufacturing.arrayStats[facility].name;
    },
    
    /**
     * Ajax functions
     */
    getMaterialsBOM: function() {
        if(!LazyBlacksmith.blueprint.manufacturing.materialBOM){
            alert('Error, no URL is found to get BOM for materials.');
            return;
        }
        $.getJSON(LazyBlacksmith.blueprint.manufacturing.materialBOM, function(materialListResult) {
            var materialList = materialListResult['result'];
            var templateTable = LazyBlacksmith.blueprint.manufacturing.tplSublistBlock;
            var templateRows = LazyBlacksmith.blueprint.manufacturing.tplSublistRow;
            var ME = 10;
            var TE = 20;
            
            var html = '';
            for(var matIndex in materialList) {
                var material = materialList[matIndex];
                var rows = '';

                // quantity and runs
                var qty = parseInt($('.materials-list tr.material[data-id="'+material['id']+'"]').attr('data-qty-job'));
                var runs = Math.ceil(qty / material['product_qty']);

                // by default, use the same facility, facility tax and system as the main bp 
                var system = $('#system').val();
                var facility = $('#facility').val();
                var tax = $('#tax').val();

                var facilityName = LazyBlacksmith.blueprint.manufacturing.getFacilityName(facility);

                // production time
                var time = material['time'];
                var timeHuman = LazyBlacksmith.utils.durationToString(time);
                var timeTotal = LazyBlacksmith.blueprint.manufacturing.calculateTime(
                    time, 
                    facility, 
                    TE,
                    runs,
                    false
                );
                var timeTotalHuman = LazyBlacksmith.utils.durationToString(timeTotal);

                // sub materials
                for(var bomIndex in material['materials']) {
                    var bom = material['materials'][bomIndex];
                    var qtyAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(bom['quantity'], ME, facility);
                    var qtyJob = LazyBlacksmith.blueprint.manufacturing.calculateJob(qtyAdjusted, runs);
                    
                    rows += templateRows.replace(/@@ID@@/g, bom['id'])
                                        .replace(/@@QTY@@/g, bom['quantity'])
                                        .replace(/@@QTY-STD@@/g, Humanize.intcomma(bom['quantity']))
                                        .replace(/@@QTY-ADJ@@/g, qtyAdjusted)
                                        .replace(/@@QTY-JOB@@/g, qtyJob)
                                        .replace(/@@QTY-ADJ-HUMAN@@/g, Humanize.intcomma(qtyAdjusted,2))
                                        .replace(/@@QTY-JOB-HUMAN@@/g, Humanize.intcomma(qtyJob))
                                        .replace(/@@ICON@@/g, bom['icon'])
                                        .replace(/@@NAME@@/g, bom['name']);                                        
                }                
                html += templateTable.replace(/@@ICON@@/g, material['icon'])
                                     .replace(/@@NAME@@/g, material['name'])
                                     .replace(/@@ID@@/g, material['id'])
                                     .replace(/@@PRODUCT_NAME@@/g, material['product_name'])
                                     .replace(/@@PRODUCT_QTY@@/g, material['product_qty'])
                                     .replace(/@@QTY@@/g, qty)
                                     .replace(/@@RUN@@/g, runs)
                                     .replace(/@@SYSTEM@@/g, system)
                                     .replace(/@@TAX@@/g, tax)
                                     .replace(/@@FACILITY_NAME@@/g, facilityName)
                                     .replace(/@@FACILITY@@/g, facility)
                                     .replace(/@@ACTIVITY_TIME@@/g, time)
                                     .replace(/@@ACTIVITY_TIME_HUMAN@@/g, timeHuman)
                                     .replace(/@@ACTIVITY_TIME_TOTAL@@/g, timeTotalHuman)
                                     .replace(/@@BOM@@/g, rows);
            }
            
            $('#tab-subcomp').html(html);
            LazyBlacksmith.blueprint.manufacturing.updateSummaryPriceTables();
        });
    },
}

/**
Labs 
    research 
        30% reduction in research ME required time
        30% reduction in research TE required time
    hyasyoda:
        35% reduction in research ME required time
        35% reduction in research TE required time
    design : 
        40% reduction in copy activity required time
        50% reduction in invention required time

    thukker array
        25% reduction in manufacturing required time
        10% reduction in manufacturing required materials
    rapid array
        35% reduction in manufacturing required time
        5% penalty in manufacturing required materials
    array
        25% reduction in manufacturing required time
        2% reduction in manufacturing required materials
        
        
        
station costs multiplier
Operations	                                                          Manufacturing output multiplier	Research output multiplier
Amarr Factory Outpost	                                                                           0.5	0.6
Manufacturing (Nullsec conquerable)	                                                               0.6	0.8
Caldari Research Outpost	                                                                       0.6	0.5
Gallente Administrative, Minmatar Service Outposts	                                               0.6	0.6
Cloning (Nullsec conquerable)	                                                                   0.7	0.7
Factory, Shipyard, Assembly Plant, Foundry, Construction Plant, Biotech Production	              0.95	0.98
Warehouse, Chemical Storage, Academy, School	                                                  0.97	0.98
Testing Facilities, Reprocessing Facility, Chemical Refinery	                                  0.97	0.97
Biotech Research Center, Research Center, Biohazard Containment Facility	                      0.98	0.95
[All others]	                                                                                  0.98	0.98

*/