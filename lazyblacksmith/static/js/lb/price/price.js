var itemPriceLookup = (function ($, lb, Humanize, utils) {
    "use strict";

    var sorting = [[1,1]];
    var regions = {};
    var items = {};

    // hash data
    var itemNameHash = "";
    var itemIdHash = false;

    var options = {
        useIcons: false,
    }

    $.extend(lb.urls, {
        itemSearchUrl: false,
    });

    var resultRow = '<a href="#" data-id="@@ID@@" data-icon="@@ICON@@" data-name="@@NAME@@" class="list-group-item list-group-item-action search-price">@@NAME@@</a>';
    var itemOldValue = "";
    var itemSearchBodyResult = '#resultList';

    /**
     * Search item function
     * @param string the name we want to search
     * @private
     */
    var _searchItem = function(name) {
        if(name == itemOldValue) {
            return false;
        }
        var url = lb.urls.itemSearchUrl;
        if(!url) {
            alert('Price URL has not been set.');
            return false;
        }

        // remove all problematic chars
        var nameEscaped = name.replace(/\//g, "")
                              .replace(/\\/g, "")
                              .replace(/`/g, "");

        if(nameEscaped.length < 3) {
            $(itemSearchBodyResult).html("");
            return false;
        }

        url = url.replace(/0000/, nameEscaped);

        // ajax call to get the blueprints
        utils.ajaxGetCallJson(url, function(jsonData) {
            var htmlResult = "";
            var data = jsonData.result;

            // for each items in data
            for(var item in data) {
                if(data[item].name.toLowerCase() == itemNameHash) {
                    itemIdHash = data[item].id;
                }
                var view = resultRow.replace(/@@ID@@/, data[item].id)
                                    .replace(/@@ICON@@/, data[item].icon)
                                    .replace(/@@NAME@@/g, data[item].name);
                htmlResult += view;
            }

            // display result
            if(htmlResult == "") {
                $(itemSearchBodyResult).html("");
            } else {
                $(itemSearchBodyResult).html(htmlResult);
            }

            // event on click to load item price
            $('.search-price').on('click', function() {
                // change active state
                $('.search-price').removeClass('active');
                $(this).addClass('active');

                // update headers and image
                $('#item-name').html($(this).attr('data-name'));
                if(options.useIcons) {
                    $('#item-icon').html("<img src='" + $(this).attr('data-icon') + "' alt='icon' />");
                }

                // get price
                _searchPrice($(this).attr('data-id'));

                items[$(this).attr('data-name')] = $(this).attr('data-id');
                window.location.hash = $(this).attr('data-name').replace(/ /g, '_').toLowerCase();
                return false;
            });

            if(itemIdHash) {
                $(".search-price[data-id='"+itemIdHash+"']").click();
            }
        }, function() {
            $(itemSearchBodyResult).html("");
        });
    };

    /**
     * Load the item price accross the regions
     * @param  the item_id to load
     * @private
     */
    var _searchPrice = function(item_id) {
        if(!$.isNumeric(item_id)) {
            return false;
        }

        eveUtils.getItemPrices(item_id, function(jsonPrice) {
            var prices = jsonPrice['prices'];
            var output = "";
            for(var regionId in prices) {
                output += "<tr><td>" + regions[regionId] + "</td>";
                output += "<td class='text-right'>" + Humanize.intcomma(prices[regionId][item_id].sell, 2) + "</td>";
                output += "<td class='text-right'>" + Humanize.intcomma(prices[regionId][item_id].buy, 2) + "</td>";
                output += "<td class='text-right'>" + prices[regionId][item_id].updated_at + "</td></tr>";
            }
            $('.price-list tbody').html(output);
            $(".price-list").trigger("update",[sorting]);
        });

    }


    /**
     * Runner function
     */
    var run = function() {
        var options = {
            callback: function (value) {
                _searchItem(value);
            },
            wait: 250,
            highlight: true,
            captureLength: 3
        }

        $('#itemSearch').typeWatch(options).on('keydown',
            function() {
                itemOldValue = $(this).val();
            }
        );

        $('.price-list').tablesorter({
            theme: "bootstrap",
            headerTemplate : '{content} {icon}',
            cssIconAsc: 'fa fa-sort-up',
            cssIconDesc: 'fa fa-sort-down',
            cssIconNone: 'fa fa-sort',
        });

        // if hash is present, load data and prices
        if(window.location.hash) {
            itemNameHash = window.location.hash.split('#')[1].replace(/_/g, ' ').toLowerCase();
            $('#itemSearch').val(itemNameHash);
            _searchItem(itemNameHash);
        }

    };


    return {
        run: run,
        regions: regions,
        options: options,
    }

}) (jQuery, lb, Humanize, utils);

lb.registerModule('itemPriceLookup', itemPriceLookup);
