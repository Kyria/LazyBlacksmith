var searchBlueprint = (function ($, lb, utils) {
    "use strict";

    var blueprintBodyResult = '#searchBlueprintResult tbody';
    var noResultMessage = '<tr><td colspan="2">No results.</td></tr>';
    var resultBtn = '<a href="@@LINK@@" class="btn btn-outline-secondary btn-sm" data-toggle="tooltip" data-placement="top" title="@@NAME@@">@@ICON@@</a> ';

    var showCorporationBlueprints = false;

    $.extend(lb.urls, {
        searchUrl: false,
        inventionUrl: '',
        manufacturingUrl: '',
        researchUrl: ''
    });

    var blueprintOldValue = "";

    /**
     * Toggle corporation blueprints
     */
    var _toggleCorporationBlueprintsOnChange = function() {
        var checked = this.checked;
        if(this.checked) {
            $('.blueprint-corporation').show();
            $('.blueprint-character').hide();
            $("#toggleCorporationBlueprints label").removeClass('btn-secondary').addClass('btn-info');
        } else {
            $('.blueprint-corporation').hide();
            $('.blueprint-character').show();
            $("#toggleCorporationBlueprints label").removeClass('btn-info').addClass('btn-secondary');
        }
        showCorporationBlueprints = this.checked;
        _searchOwnedBlueprint($('#ownedBlueprintSearch').val().toLowerCase());
    };

    /**
     * Search blueprint function
     * @param string the name we want to search
     * @private
     */
    var _searchBlueprint = function(name) {
        if(name == blueprintOldValue) {
            return false;
        }
        var url = lb.urls.searchUrl;
        if(!url) {
            alert('Search Blueprint URL has not been set.');
            return false;
        }

        // remove all problematic chars
        var nameEscaped = name.replace(/\//g, "")
                              .replace(/\\/g, "")
                              .replace(/`/g, "");

        if(nameEscaped.length < 3) {
            $(blueprintBodyResult).html(noResultMessage);
            return false;
        }

        url = url.replace(/0000/, nameEscaped);

        // ajax call to get the blueprints
        utils.ajaxGetCallJson(url, function(jsonData) {
            var htmlResult = "";
            var data = jsonData.result;

            // for each items in data
            for(var item in data) {
                var inventionLink = lb.urls.inventionUrl.replace(/999999999/, data[item].id);
                var manufacturingLink = lb.urls.manufacturingUrl.replace(/999999999/, data[item].id);
                var researchLink = lb.urls.researchUrl.replace(/999999999/, data[item].id);
                var reactionLink = lb.urls.reactionUrl.replace(/999999999/, data[item].id);

                var invention = (!data[item].invention) ? '' : resultBtn.replace(/@@LINK@@/, inventionLink)
                                                                        .replace(/@@NAME@@/, 'Invention')
                                                                        .replace(/@@ICON@@/, '<i class="fa fa-flask" aria-hidden="true"></i>');

                var reaction = (!data[item].reaction) ? '' : resultBtn.replace(/@@LINK@@/, reactionLink)
                                                                        .replace(/@@NAME@@/, 'Reaction')
                                                                        .replace(/@@ICON@@/, '<i class="fa fa-share-alt" aria-hidden="true"></i>');

                var research = resultBtn.replace(/@@LINK@@/, researchLink)
                                        .replace(/@@NAME@@/, 'Research')
                                        .replace(/@@ICON@@/, '<i class="fa fa-hourglass-o" aria-hidden="true"></i> / <i class="fa fa-diamond" aria-hidden="true"></i>');
                var manufacturing = resultBtn.replace(/@@LINK@@/, manufacturingLink)
                                             .replace(/@@NAME@@/, 'Manufacture')
                                             .replace(/@@ICON@@/, '<i class="fa fa-industry" aria-hidden="true"></i>');

                htmlResult += '<tr><td>' + data[item].name + '</td>';
                if(!data[item].reaction) {
                    htmlResult += '<td class="text-right"><div class="btn-group" role="group">' + invention  + research + manufacturing + '</div></td></tr>';
                } else {
                    htmlResult += '<td class="text-right"><div class="btn-group" role="group">' + reaction + '</div></td></tr>';
                }
            }

            // display result
            if(htmlResult == "") {
                $(blueprintBodyResult).html(noResultMessage);
            } else {
                $(blueprintBodyResult).html(htmlResult);
            }
            $('[data-toggle="tooltip"]').tooltip();
        }, function() {
            $(blueprintBodyResult).html('<tr><td colspan="2">Error while trying to get results.</td></tr>');
        });
    };

    /**
     * Seaerch through the owned blueprint list.
     */
    var _searchOwnedBlueprint = function(name) {
        var classToFilter = (showCorporationBlueprints) ? '.blueprint-corporation' : '.blueprint-character';
        $(classToFilter).show();
        $(classToFilter).filter(function() {
            var bpName = $(this).find('td.name').html().toLowerCase();
            return bpName.indexOf(name) == -1;
        }).hide();
    };

    /**
     * Runner function
     */
    var run = function() {
        $('#blueprint').typeWatch({
            callback: function (value) {
                _searchBlueprint(value);
            },
            wait: 250,
            highlight: true,
            captureLength: 3
        }).on('keydown',
            function() {
                blueprintOldValue = $(this).val();
            }
        );

        $('#ownedBlueprintSearch').typeWatch({
            callback: function (value) {
                _searchOwnedBlueprint(value.toLowerCase());
            },
            wait: 250,
            highlight: true,
            captureLength: 0
        }).on('keydown',
            function() {
                blueprintOldValue = $(this).val();
            }
        );
        $("#toggleCorporationBlueprints input[type='checkbox']").on('change', _toggleCorporationBlueprintsOnChange);
        $('[data-toggle="tooltip"]').tooltip();
    };


    return {
        run: run,
    }

}) (jQuery, lb, utils);

lb.registerModule('searchBlueprint', searchBlueprint);
