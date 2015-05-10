LazyBlacksmith.blueprint = {
    blueprintSearchUrl: false,
    blueprintInventionUrl: false,       
    blueprintManufacturingUrl: false,
    blueprintResearchUrl: false,


    blueprintOldValue: "",
    
    onload: function() {
        var options = {
            callback: function (value) {LazyBlacksmith.blueprint.searchBlueprint(value);},
            wait: 300,
            highlight: true,
            captureLength: 3
        }

        $('#blueprint')
            .typeWatch(options)
            .on('keydown', 
                function() {
                    LazyBlacksmith.blueprint.blueprintOldValue = $(this).val();
                }
            );
    },
    
    searchBlueprint: function(name) {
        if(name == LazyBlacksmith.blueprint.blueprintOldValue) {
            return false;
        }
    
        if(!LazyBlacksmith.blueprint.blueprintSearchUrl) {
            alert('Search Blueprint URL has not been set.');
            return false;
        }
        
        // remove all problematic chars        
        var nameEscaped = name.replace(/\//g, "")
                              .replace(/\\/g, "")
                              .replace(/`/g, "");
        
        if(nameEscaped.length < 3) {
            $('#searchBlueprintResult tbody').html('<tr><td colspan="2">No results.</td></tr>');
            return false;
        }
        
        var url = LazyBlacksmith.blueprint.blueprintSearchUrl.replace(/0000/, nameEscaped);
                        
        $.getJSON(url, function(data) {
            htmlResult = "";
            for(var item in data) {
                var inventionLink = LazyBlacksmith.blueprint.blueprintInventionUrl.replace(/0000/, data[item][0]);
                var manufacturingLink = LazyBlacksmith.blueprint.blueprintManufacturingUrl.replace(/0000/, data[item][0]);
                var researchLink = LazyBlacksmith.blueprint.blueprintResearchUrl.replace(/0000/, data[item][0]);
                
                var invention = (data[item][2] == 1) ? '<a href="'+inventionLink+'" class="btn btn-default btn-xs pull-right">Invention</a> ' 
                            : ((data[item][2] == 2) ? '<a href="'+reverseEngineeringLink+'" class="btn btn-default btn-xs pull-right">Reverse Engineering</a> ' : '');
                var research = '<a href="'+researchLink+'" class="btn btn-default btn-xs pull-right">Research ME/TE</a> ';
                var manufacturing = '<a href="'+manufacturingLink+'" class="btn btn-default btn-xs pull-right">Manufacture</a>';
                htmlResult += "<tr><td>"+data[item][1]+'</td><td>'+manufacturing+research+invention+'</td></tr>';
            }
            
            if(htmlResult == "") {
                $('#searchBlueprintResult tbody').html('<tr><td colspan="2">No results.</td></tr>');
            } else {
                $('#searchBlueprintResult tbody').html(htmlResult);
            }
        })
        .error(function() {
            $('#searchBlueprintResult tbody').html('<tr><td colspan="2">Error while trying to get results.</td></tr>');
        });
    },
}
    