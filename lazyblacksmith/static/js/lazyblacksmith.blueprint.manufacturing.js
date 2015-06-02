LazyBlacksmith.blueprint.manufacturing = {
    ME: 0,
    TE: 0,
    runs: 1,

    hasManufacturedComponent: false,
    
    // urls
    systemUrls: false,
    materialBOM: false,
    tplSublistBlockUrl: false,
    tplSublistRowUrl: false,
    
    // boolean : did we already load submaterials ?
    materialBOMLoaded: false,

    // tpl values
    tplSublistBlock: '',
    tplSublistRow: '',

    arrayStats: [
                    { // station
                        "me": 1.0,
                        "te": 1.0,
                    },
                    { // Assembly Array
                        "me": 0.98,
                        "te": 0.75,
                    },
                    { // Thukker Component Array
                        "me": 0.9,
                        "te": 0.75,
                    },
                    { // Rapid Assembly Array
                        "me": 1.05,
                        "te": 0.65,
                    },
                ],

    onload: function() {
        LazyBlacksmith.blueprint.manufacturing.initTemplates();
        LazyBlacksmith.blueprint.manufacturing.initSliders();
        LazyBlacksmith.blueprint.manufacturing.initInputs();
        LazyBlacksmith.blueprint.manufacturing.initTabs(); 
        LazyBlacksmith.blueprint.manufacturing.initTypeahead(); 
        LazyBlacksmith.blueprint.manufacturing.initModal(); 
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
            if(!LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded) {
                LazyBlacksmith.blueprint.manufacturing.getMaterialsBOM();
                LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded = true;
            } else {
                LazyBlacksmith.blueprint.manufacturing.updateSummary();
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
            range: "min",
            step: 2,
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
            range: "min",
            step: 2,
            slide: LazyBlacksmith.blueprint.manufacturing.updateModalTE,
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

            $('#componentModalBpName').html(name);
            $('#componentModalBpName').attr('data-bp-id', id);
            $('#modal-tax').val(tax);
            $('#modal-system').val(system);
            $('#modal-facility option[value='+facility+']').prop('selected',true);
            $('#ModalME').slider("option", "value", me);
            $('#ModalTE').slider("option", "value", te);
            $('#Modal-ME-Level').html(me+"%");
            $('#Modal-TE-Level').html(te+"%");
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

        $(selector).attr('data-system', system);
        $(selector).attr('data-facility', facility);
        $(selector).attr('data-tax', tax);

        $(selector+' .me').html(ME);
        $(selector+' .te').html(TE);

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
        $('#Modal-ME-Level').html(ui.value+"%");
    },

    updateModalTE: function(event, ui) {
        $('#Modal-TE-Level').html(ui.value+"%");
    },

    updateTimes: function() {
        var TEBonus = (1.00-LazyBlacksmith.blueprint.manufacturing.TE/100.00);
        var time_pu = parseInt($('.main-list .time-per-run').attr('data-time'));
        var facilityBonus = LazyBlacksmith.blueprint.manufacturing.getFacilityTe(parseInt($('#facility').val()));
        var time_pu_adjusted = time_pu * TEBonus * facilityBonus;
        //durationToString
        var time_text = LazyBlacksmith.utils.durationToString(time_pu_adjusted*LazyBlacksmith.blueprint.manufacturing.runs);
        $('.main-list .total-time').html(time_text);

        $('.main-list .materials-list tr.material').each(
            function() {
                if(!LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded || 
                    $(this).attr('data-is-manufactured') == 'False') {
                    return;
                }
                var id = parseInt($(this).attr('data-id'));               
                var runs = parseInt($('#run-required-'+id).text());

                var facility = parseInt($('.sub-list-'+id).attr('data-facility'));
                var facilityTE = LazyBlacksmith.blueprint.manufacturing.getFacilityTe(facility);
                var TE = (1.00-parseInt($('.sub-list-'+id+' .te').text()) / 100);

                var time_pu = parseInt($('.sub-list-'+id+' .time-per-run').attr('data-time'));
                var time_pu_adjusted = time_pu * TE * runs * facilityTE;      
                var time_text = LazyBlacksmith.utils.durationToString(time_pu_adjusted);

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
                
                var MEBonus = (1.00-LazyBlacksmith.blueprint.manufacturing.ME/100.00);
                var facilityBonus = LazyBlacksmith.blueprint.manufacturing.getFacilityMe(parseInt($('#facility').val()));
                var quantityAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(quantity, MEBonus, facilityBonus);
                var quantityJob = LazyBlacksmith.blueprint.manufacturing.calculateJob(quantityAdjusted, LazyBlacksmith.blueprint.manufacturing.runs);

                $(this).find('td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2));
                $(this).find('td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob));
        
                $(this).attr('data-qty-adj',quantityAdjusted);
                $(this).attr('data-qty-job',quantityJob);                   
                
                if(!LazyBlacksmith.blueprint.manufacturing.materialBOMLoaded || $(this).attr('data-is-manufactured') == 'False') {
                    return;
                }

                $('#qty-required-'+id).html(quantityJob);

                // calculate the number of run required for each subcomps
                var qty_required = parseInt($('#qty-required-'+id).text());
                var batch_per_run = parseInt($('.sub-list-'+id).attr('data-output-per-run'));

                var runs = Math.ceil(qty_required/batch_per_run)
                $('#run-required-'+id).html(runs);

                var facility = parseInt($('.sub-list-'+id).attr('data-facility'));
                var facilityME = LazyBlacksmith.blueprint.manufacturing.getFacilityMe(facility);

                var ME = (1.00-parseInt($('.sub-list-'+id+' .me').text()) / 100);

                // update the sub comps (if there are some :)) for this material
                $('.sub-list-'+id+' .materials-list tr.material').each(
                    function() {
                        var quantity = parseInt($(this).attr('data-qty'));

                        var quantityAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(quantity, ME, facilityME);
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
    updateSummary: function() {
        html = "";
        materials = [];
        names = [];
        $('.material').each(
            function() { 
                qty = parseInt($(this).attr('data-qty-job'));
                id = $(this).attr('data-id');
                name = $(this).attr('data-name');
                if(!(id in materials)) {
                    materials[id] = 0;
                }
                materials[id] += qty;
                names[id] = name;
            }
        );

        for(var id in materials) {
            html += names[id] + " - " + materials[id] + "<br>";
        }

        html += "<br><br>";
        $('.total-time').each(
            function() {
                id = $(this).attr('data-id');
                time = $(this).text();
                html += names[id] + ": " + time + "<br>";
            }
        );
        $('#tab-summary').html(html);
    },

    /**
     * Calculate the adjusted quantity
     */
    calculateAdjusted: function(quantity, MEBonus, FacilityBonus) {
        return Math.max(1, quantity * MEBonus * FacilityBonus);
    },
    
    /**
     * Calculate the job quantity
     */
    calculateJob: function(quantityAdjusted, runs) {
        return Math.max(runs, Math.ceil(quantityAdjusted * runs));
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
    
    /**
     * Ajax functions
     */
    getMaterialsBOM:function() {
        if(!LazyBlacksmith.blueprint.manufacturing.materialBOM){
            alert('Error, no URL is found to get BOM for materials.');
            return;
        }
        $.getJSON(LazyBlacksmith.blueprint.manufacturing.materialBOM, function(materialListResult) {
            var materialList = materialListResult['result'];
            var templateTable = LazyBlacksmith.blueprint.manufacturing.tplSublistBlock;
            var templateRows = LazyBlacksmith.blueprint.manufacturing.tplSublistRow;
            
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

                var facilityTE = LazyBlacksmith.blueprint.manufacturing.getFacilityTe(facility);
                var facilityME = LazyBlacksmith.blueprint.manufacturing.getFacilityMe(facility);

                // production time
                var time = material['time'];
                var time_human = LazyBlacksmith.utils.durationToString(time);
                var time_total_human = LazyBlacksmith.utils.durationToString(time * 0.8 * runs * facilityTE);

                // sub materials
                for(var bomIndex in material['materials']) {
                    var bom = material['materials'][bomIndex];
                    var qtyAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(bom['quantity'], 0.9, facilityME);
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
                                     .replace(/@@FACILITY@@/g, facility)
                                     .replace(/@@ACTIVITY_TIME@@/g, time)
                                     .replace(/@@ACTIVITY_TIME_HUMAN@@/g, time_human)
                                     .replace(/@@ACTIVITY_TIME_TOTAL@@/g, time_total_human)
                                     .replace(/@@BOM@@/g, rows);
            }
            
            $('#tab-subcomp').html(html);
            LazyBlacksmith.blueprint.manufacturing.updateSummary();
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