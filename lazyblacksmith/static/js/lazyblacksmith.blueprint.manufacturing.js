LazyBlacksmith.blueprint.manufacturing = {
    ME: 0,
    TE: 0,
    runs: 1,
    
    systemUrls: false,
    materialBOM: false,
    
    materialBOMLoaded: false,
    
    onload: function() {
        LazyBlacksmith.blueprint.manufacturing.initSliders();
        LazyBlacksmith.blueprint.manufacturing.initInputs();
        LazyBlacksmith.blueprint.manufacturing.initTabs(); 
        LazyBlacksmith.blueprint.manufacturing.initTypeahead(); 
    },
    
    /**
     * Init functions
     */
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
            }
        );
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
    },
    
    updateMaterials: function() {
        // main BPO update
        $('.main-list .materials-list tr.material').each(
            function() {
                var id = parseInt($(this).attr('data-id'));
                var quantity = parseInt($(this).attr('data-qty'));
                
                var MEBonus = (1.00-LazyBlacksmith.blueprint.manufacturing.ME/100.00);
                var FacilityBonus = 100.00/100.00;
                var quantityAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(quantity, MEBonus, FacilityBonus);
                var quantityJob = LazyBlacksmith.blueprint.manufacturing.calculateJob(quantityAdjusted, LazyBlacksmith.blueprint.manufacturing.runs);

                $(this).find('td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2));
                $(this).find('td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob));
        
                $(this).attr('data-qty-adj',quantityAdjusted);
                $(this).attr('data-qty-job',quantityJob);                   
                
                $('#qty-required-'+id).html(quantityJob);
                
                // update the sub comps (if there are some :)) for this material
                $('.sub-list-'+id+' .materials-list tr.material').each(
                    function() {
                        var quantity = parseInt($(this).attr('data-qty'));
                        var runs = parseInt($('#qty-required-'+id).text());
                        
                        var quantityAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(quantity, 0.9, 1);
                        var quantityJob = LazyBlacksmith.blueprint.manufacturing.calculateJob(quantityAdjusted, runs);
                        
                        $(this).find('td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2));
                        $(this).find('td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob));
                        
                        $(this).attr('data-qty-adj',quantityAdjusted);
                        $(this).attr('data-qty-job',quantityJob);   
                    }
                );
            } 
        );
        
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
     * Ajax functions
     */
    getMaterialsBOM:function() {
        if(!LazyBlacksmith.blueprint.manufacturing.materialBOM){
            alert('Error, no URL is found to get BOM for materials.');
            return;
        }
        $.getJSON(LazyBlacksmith.blueprint.manufacturing.materialBOM, function(materialListResult) {
            var materialList = materialListResult['result'];
            var templateTable = $('#table-bom').val();
            var templateRows = $('#table-row-bom').val();
            
            var html = '';
            for(var matIndex in materialList) {
                var material = materialList[matIndex];
                var rows = '';
                var runs = parseInt($('.materials-list tr.material[data-id="'+material['id']+'"]').attr('data-qty-job'));
                          
                for(var bomIndex in material['materials']) {
                    var bom = material['materials'][bomIndex];
                    var qtyAdjusted = LazyBlacksmith.blueprint.manufacturing.calculateAdjusted(bom['quantity'], 0.9, 1);
                    var qtyJob = LazyBlacksmith.blueprint.manufacturing.calculateJob(qtyAdjusted, runs)
                    
                    rows += templateRows.replace(/@@ID@@/g, bom['id'])
                                        .replace(/@@QTY@@/g, bom['quantity'])
                                        .replace(/@@QTY-STD@@/g, Humanize.intcomma(bom['quantity']))
                                        .replace(/@@QTY-ADJ@@/g, Humanize.intcomma(qtyAdjusted,2))
                                        .replace(/@@QTY-JOB@@/g, Humanize.intcomma(qtyJob))
                                        .replace(/@@ICON@@/g, bom['icon'])
                                        .replace(/@@NAME@@/g, bom['name']);                                        
                }                
                html += templateTable.replace(/@@ICON@@/g, material['icon'])
                                     .replace(/@@NAME@@/g, material['name'])
                                     .replace(/@@ID@@/g, material['id'])
                                     .replace(/@@QTY@@/g, runs)
                                     .replace(/@@BOM@@/g, rows);
            }
            
            $('#tab-subcomp').html(html);
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