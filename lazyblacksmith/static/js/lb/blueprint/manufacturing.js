var manufacturingBlueprint = (function ($, lb, utils, eveUtils, eveData, Humanize) {
    'use strict'

    // template variables
    var tplSublistBlock = ''
    var tplSublistRow = ''
    var tplModalPrice = ''

    // multibuy field
    var multiBuy = ''

    // page options
    var options = {
        hasManufacturedComponent: false,
        useIcons: false,

        // bp informations
        materialEfficiency: 0,
        timeEfficiency: 0,
        runs: 1,

        // skill infos
        industryLvl: 0,
        advancedIndustryLvl: 0,
        t2ConstructionLvl: 0,
        datacoreLevel1: 0,
        datacoreLevel2: 0,

        // implant
        manufTeImplant: 1.00
    }

    // urls
    $.extend(lb.urls, {
        systemUrls: false,
        materialBOMUrl: false,
        priceUrl: false,
        indexActivityUrl: false,

        // template links
        tplSublistBlockUrl: false,
        tplSublistRowUrl: false,
        tplModalPriceUrl: false
    })

    // item price data and index
    var priceData = {
        isLoaded: false,
        prices: {},
        adjusted: {},

        // item configs
        items: {},
        itemList: [],

        totalCost: 0,
        totalInstallationCost: 0
    }

    var costIndex = {}

    var materialsData = {
        // produced item id
        productItemId: 0,

        // components
        materials: {},
        componentIdList: []
    }

    var materialQuantityList

    // states
    var isMaterialListLoaded = false
    var useComponents = false
    var lastTab = '#tab-summary'
    var modalPriceUpdatePrice = true

    // assembly informations
    var facilityStats = eveData.facilities
    var structureRigs = eveData.structureIndustryRigs
    var structureSecStatusMultiplier = eveData.structureSecStatusMultiplier
    var thukkerRigSecStatusMultiplier = eveData.thukkerRigSecStatusMultiplier

    // -------------------------------------------------
    // Material list generators and ajax getters
    //

    /**
     * generate the material list with quantity for all main materials
     * or only components, depending on the settings we have.
     *
     * @private
     * @return the list of objects for each materials, including id, name, qty
     */
    var _generateMaterialListQuantity = function () {
        var materialList = {}
        var onlySubComponents = (useComponents && options.hasManufacturedComponent)

        for (var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]]

            // we want all material, or at least, those that cannot be manufactured (PI, moongoo...)
            if (!material.isManufactured || !onlySubComponents) {
                materialList[material.id] = materialList[material.id] || {
                    qty: 0,
                    name: material.name,
                    icon: material.icon,
                    volume: material.volume
                }
                materialList[material.id].qty += material.qtyJob
            } else {
                for (var j in material.componentIdList) {
                    var subMaterial = material.materials[material.componentIdList[j]]
                    materialList[subMaterial.id] = materialList[subMaterial.id] || {
                        qty: 0,
                        name: subMaterial.name,
                        icon: subMaterial.icon,
                        volume: subMaterial.volume
                    }
                    materialList[subMaterial.id].qty += subMaterial.qtyJob
                }
            }
        }
        materialQuantityList = materialList
    }

    /**
     * Generate the item price list for configs.
     * The list will have the following order for the ease of configs:
     * - product
     * - components
     * - subcomponents
     */
    var _generateMaterialListPrice = function () {
        priceData.itemList.push(materialsData.productItemId)
        priceData.items[materialsData.productItemId] = {
            'type': materialsData.materials[materialsData.productItemId].priceType,
            'region': materialsData.materials[materialsData.productItemId].priceRegion,
            'id': materialsData.productItemId,
            'name': materialsData.materials[materialsData.productItemId].name,
            'icon': materialsData.materials[materialsData.productItemId].icon
        }

        var subComponentList = []
        var subComponents = {}

        for (var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]]

            if ($.inArray(material.id, priceData.itemList) === -1) {
                priceData.itemList.push(material.id)
                priceData.items[material.id] = {
                    'type': material.priceType,
                    'region': material.priceRegion,
                    'id': material.id,
                    'name': material.name,
                    'icon': material.icon
                }
            }

            if (material.isManufactured) {
                for (var j in material.componentIdList) {
                    var subMaterial = material.materials[material.componentIdList[j]]

                    if ($.inArray(subMaterial.id, subComponentList) === -1 &&
                       $.inArray(subMaterial.id, priceData.itemList) === -1) {
                        subComponentList.push(subMaterial.id)
                        subComponents[subMaterial.id] = {
                            'type': subMaterial.priceType,
                            'region': subMaterial.priceRegion,
                            'id': subMaterial.id,
                            'name': subMaterial.name,
                            'icon': subMaterial.icon
                        }
                    }
                }
            }
        }

        $.merge(priceData.itemList, subComponentList)
        $.extend(true, priceData.items, subComponents)
        _initPriceModalContent()
    }

    /**
     * Get market price for items
     * @private
     */
    var _getAllPrices = function () {
        if (priceData.isLoaded) {
            return _updatePriceTable()
        }

        if (priceData.itemList.length === 0) {
            return
        }

        eveUtils.getItemPrices(priceData.itemList, function (jsonPrice) {
            priceData.prices = jsonPrice['prices']
            priceData.adjusted = jsonPrice['adjusted']
            priceData.isLoaded = true
            _updatePriceTable()
        })
    }

    /**
     * Get the list of materials for the given blueprint
     * @private
     */
    var _getComponentMaterials = function () {
        if (isMaterialListLoaded || !options.hasManufacturedComponent) {
            _generateMaterialListPrice()
            _generateMaterialListQuantity()
            return
        }
        if (tplSublistBlock === '' || tplSublistRow === '') {
            // if any template is not yet set, try again in 1sec
            return setTimeout(_getComponentMaterials, 100)
        }
        utils.ajaxGetCallJson(lb.urls.materialBOMUrl, function (materialListResult) {
            var materialList = materialListResult['result']
            var html = ''

            for (var i in materialList) {
                var rows = ''
                var tmpMaterial = materialList[i]
                var material = materialsData.materials[tmpMaterial['product_id']]
                material.blueprint_id = tmpMaterial['id']
                material.blueprint_name = tmpMaterial['name']
                material.blueprint_icon = tmpMaterial['icon']
                material.runsPerJob = tmpMaterial['max_run_per_bp']
                material.maxRunPerBp = tmpMaterial['max_run_per_bp']
                material.volume = tmpMaterial['volume']

                // quantity and runs
                material.resultQtyPerRun = tmpMaterial['product_qty_per_run']
                material.runs = Math.ceil(material.qtyJob / material.resultQtyPerRun)

                // production time per run (base time)
                material.timePerRun = tmpMaterial['time']

                var timePerRun = eveUtils.calculateJobTime(
                    material.timePerRun, 1, facilityStats[material.facility].bpTe, material.timeEfficiency,
                    (material.isManufactured) ? options.manufTeImplant : 1.00,
                    options.industryLvl, options.advancedIndustryLvl,
                    0, 0, 0,
                    structureRigs[material.structureTeRig].timeBonus, structureSecStatusMultiplier[material.structureSecStatus],
                    facilityStats[material.facility].structure, false
                )
                material.timeTotal = eveUtils.calculateJobTime(
                    material.timePerRun, material.runs, facilityStats[material.facility].bpTe, material.timeEfficiency,
                    (material.isManufactured) ? options.manufTeImplant : 1.00,
                    options.industryLvl, options.advancedIndustryLvl,
                    0, 0, 0,
                    structureRigs[material.structureTeRig].timeBonus, structureSecStatusMultiplier[material.structureSecStatus],
                    facilityStats[material.facility].structure, false
                )

                var timeHuman = utils.durationToString(timePerRun)
                var timeTotalHuman = utils.durationToString(material.timeTotal)

                // sub materials
                for (var j in tmpMaterial['materials']) {
                    var tmpSubMaterial = tmpMaterial['materials'][j]

                    material.componentIdList.push(tmpSubMaterial['id'])
                    var subMaterial = material.materials[tmpSubMaterial['id']] = {
                        'id': tmpSubMaterial['id'],
                        'name': tmpSubMaterial['name'],
                        'icon': tmpSubMaterial['icon'],
                        'qtyRequiredPerRun': tmpSubMaterial['quantity'],
                        'priceType': tmpSubMaterial['price_type'],
                        'priceRegion': tmpSubMaterial['price_region'],
                        'volume': tmpSubMaterial['volume']
                    }

                    subMaterial.qtyAdjusted = eveUtils.calculateAdjustedQuantity(
                        subMaterial.qtyRequiredPerRun,
                        material.materialEfficiency,
                        facilityStats[material.facility].bpMe,
                        structureRigs[material.structureMeRig].materialBonus,
                        structureSecStatusMultiplier[material.structureSecStatus],
                        facilityStats[material.facility].structure
                    )

                    subMaterial.qtyJob = eveUtils.calculateJobQuantityBatch(
                        subMaterial.qtyAdjusted,
                        material.runs,
                        material.runsPerJob
                    )

                    rows += tplSublistRow.replace(/@@ID@@/g, subMaterial.id)
                                        .replace(/@@QTY@@/g, subMaterial.qtyRequiredPerRun)
                                        .replace(/@@QTY-STD@@/g, Humanize.intcomma(subMaterial.qtyRequiredPerRun))
                                        .replace(/@@QTY-ADJ@@/g, subMaterial.qtyAdjusted)
                                        .replace(/@@QTY-JOB@@/g, subMaterial.qtyJob)
                                        .replace(/@@QTY-ADJ-HUMAN@@/g, Humanize.intcomma(subMaterial.qtyAdjusted, 2))
                                        .replace(/@@QTY-JOB-HUMAN@@/g, Humanize.intcomma(subMaterial.qtyJob))
                                        .replace(/@@ICON@@/g, subMaterial.icon)
                                        .replace(/@@NAME@@/g, subMaterial.name)
                }
                html += tplSublistBlock.replace(/@@ICON@@/g, material.blueprint_icon)
                                     .replace(/@@NAME@@/g, material.blueprint_name)
                                     .replace(/@@ID@@/g, material.id)
                                     .replace(/@@PRODUCT_NAME@@/g, material.name)
                                     .replace(/@@PRODUCT_QTY@@/g, material.resultQtyPerRun)
                                     .replace(/@@QTY@@/g, material.qtyJob)
                                     .replace(/@@RUN@@/g, material.runs)
                                     .replace(/@@RUNPERJOB@@/g, material.runsPerJob)
                                     .replace(/@@SYSTEM@@/g, material.factorySystem)
                                     .replace(/@@FACILITY_NAME@@/g, facilityStats[material.facility].name)
                                     .replace(/@@ACTIVITY_TIME_HUMAN@@/g, timeHuman)
                                     .replace(/@@ACTIVITY_TIME_TOTAL@@/g, timeTotalHuman)
                                     .replace(/@@BOM@@/g, rows)
            }

            $('#tab-subcomp .content').html(html)

            $('#tab-subcomp .lb-sorted').tablesorter({
                theme: "bootstrap",
                headerTemplate : '{content} {icon}',
                cssIconAsc: 'fa fa-sort-up',
                cssIconDesc: 'fa fa-sort-down',
                cssIconNone: 'fa fa-sort',
            });

            // update material quantity list
            _generateMaterialListQuantity()

            // generate the material list for prices
            _generateMaterialListPrice()

            isMaterialListLoaded = true

            // update tables
            for (var i in materialsData.componentIdList) {
                var componentId = materialsData.componentIdList[i]
                _updateComponentBpInfoDisplay(componentId)
            }

            _updateSummaryTabs()
        })
    }

    /**
     * Get the indexes of the missing solar systems
     * @private
     */
    var _getSystemCostIndex = function () {
        if ((!isMaterialListLoaded && options.hasManufacturedComponent) || !priceData.isLoaded) {
            // if any required data is not yet set, try again in 1sec
            return setTimeout(_getSystemCostIndex, 100)
        }

        var materialList = $.merge([materialsData.productItemId], materialsData.componentIdList)
        var systemList = []

        for (var i in materialList) {
            var system = materialsData.materials[materialList[i]].factorySystem
            if (!(system in costIndex) && $.inArray(system, systemList) === -1) {
                systemList.push(system)
            }
        }

        if (systemList.length === 0) {
            return _updateTaxTable()
        }

        eveUtils.getSystemCostIndex(systemList, function (jsonIndex) {
            $.extend(costIndex, jsonIndex['index'])
            _updateTaxTable()
        }, function (errorObject) {
            var jsonResponse = errorObject.responseJSON
            utils.flashNotify(jsonResponse.message, jsonResponse.status)

            // find where solarsystem are bad, and revert to previous.
            for (var i in materialList) {
                var system = materialsData.materials[materialList[i]].factorySystem

                if (!(system in costIndex)) {
                    var systemPrevious = materialsData.materials[materialList[i]].factorySystemPrevious
                    materialsData.materials[materialList[i]].factorySystem = systemPrevious

                    if (materialList[i] !== materialsData.productItemId) {
                        _updateComponentBpInfoDisplay(materialList[i])
                    } else {
                        $('#system').val(systemPrevious)
                        $('#system').typeahead('val', systemPrevious)
                    }
                }
            }
        })
    }

    // -------------------------------------------------
    // Functions (no events, no event functions)
    //

    /**
     * Update main blueprint components.
     * Use the runsPerJob value to calculate correctly with the adjusted quantities
     * @private
     */
    var _updateMaterial = function () {
        for (var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]]
            var parentMaterial = materialsData.materials[materialsData.productItemId]

            // check if cap parts
            var meSecStatusMult = structureSecStatusMultiplier[parentMaterial.structureSecStatus]
            var meBonus = structureRigs[parentMaterial.structureMeRig].materialBonus

            if (parentMaterial.isCapPart && parentMaterial.structureMeRig === eveData.structureIndustryRigList.thukker) {
                meBonus = structureRigs[parentMaterial.structureMeRig].capPartBonus
                meSecStatusMult = thukkerRigSecStatusMultiplier[parentMaterial.structureSecStatus]
            }

            var quantityAdjusted = eveUtils.calculateAdjustedQuantity(
                material.qtyRequiredPerRun,
                options.materialEfficiency,
                facilityStats[parentMaterial.facility].bpMe,
                meBonus,
                meSecStatusMult,
                facilityStats[parentMaterial.facility].structure
            )

            var quantityJob = eveUtils.calculateJobQuantityBatch(
                quantityAdjusted,
                options.runs,
                parentMaterial.runsPerJob
            )

            var selector = '.main-list tr.material[data-id="' + material.id + '"]'
            $(selector + ' td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2))
            $(selector + ' td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob))

            material.qtyAdjusted = quantityAdjusted
            material.qtyJob = quantityJob
        }

        _updateComponentMaterial()
        _updateComponentTime()
        _generateMaterialListQuantity()
    }

    /**
     * Update compenents bill of materials.
     * @private
     */
    var _updateComponentMaterial = function () {
        if (!isMaterialListLoaded || !options.hasManufacturedComponent) {
            return
        }

        for (var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]]

            // if it's not a manufactured material, we stop here
            if (!material.isManufactured) {
                continue
            }

            var runs = Math.ceil(
                material.qtyJob / material.resultQtyPerRun
            )
            material.runs = runs

            $('.sub-list-' + material.id + ' .run-required').html(runs)
            $('.sub-list-' + material.id + ' .qty-required').html(material.qtyJob)

            // update the sub comps (if there are some :)) for this material
            for (var j in material.componentIdList) {
                var subMaterial = material.materials[material.componentIdList[j]]

                // check if cap parts
                var meSecStatusMult = structureSecStatusMultiplier[material.structureSecStatus]
                var meBonus = structureRigs[material.structureMeRig].materialBonus

                if (material.isCapPart && material.structureMeRig === eveData.structureIndustryRigList.thukker) {
                    meBonus = structureRigs[material.structureMeRig].capPartBonus
                    meSecStatusMult = thukkerRigSecStatusMultiplier[material.structureSecStatus]
                }

                var quantityAdjusted = eveUtils.calculateAdjustedQuantity(
                    subMaterial.qtyRequiredPerRun,
                    material.materialEfficiency,
                    facilityStats[material.facility].bpMe,
                    meBonus,
                    meSecStatusMult,
                    facilityStats[material.facility].structure
                )

                var quantityJob = eveUtils.calculateJobQuantityBatch(
                    quantityAdjusted,
                    material.runs,
                    material.runsPerJob
                )

                subMaterial.qtyAdjusted = quantityAdjusted
                subMaterial.qtyJob = quantityJob

                var selector = '.sub-list-' + material.id + ' tr.material[data-id="' + subMaterial.id + '"]'
                $(selector + ' td[data-name="quantity-adjusted"]').html(Humanize.intcomma(quantityAdjusted, 2))
                $(selector + ' td[data-name="quantity-job"]').html(Humanize.intcomma(quantityJob))
            }
        }
    }

    /**
     * Update main blueprint times. Always called by update material function.
     * @private
     */
    var _updateTime = function () {
        var material = materialsData.materials[materialsData.productItemId]
        var time_per_run = eveUtils.calculateJobTime(
            materialsData.materials[materialsData.productItemId].timePerRun,
            1, facilityStats[material.facility].bpTe, options.timeEfficiency,
            (material.isManufactured) ? options.manufTeImplant : 1.00,
            options.industryLvl, options.advancedIndustryLvl,
            options.t2ConstructionLvl, options.datacoreLevel1, options.datacoreLevel2,
            structureRigs[material.structureTeRig].timeBonus, structureSecStatusMultiplier[material.structureSecStatus],
            facilityStats[material.facility].structure, true
        )
        var time = eveUtils.calculateJobTime(
            materialsData.materials[materialsData.productItemId].timePerRun,
            options.runs, facilityStats[material.facility].bpTe, options.timeEfficiency,
            (material.isManufactured) ? options.manufTeImplant : 1.00,
            options.industryLvl, options.advancedIndustryLvl,
            options.t2ConstructionLvl, options.datacoreLevel1, options.datacoreLevel2,
            structureRigs[material.structureTeRig].timeBonus, structureSecStatusMultiplier[material.structureSecStatus],
            facilityStats[material.facility].structure, true
        )

        materialsData.materials[materialsData.productItemId].timeTotal = time

        var time_text = utils.durationToString(time)
        var time_per_run_text = utils.durationToString(time_per_run)
        $('.main-list .total-time').html(time_text)
        $('.main-list .time-per-run').html(time_per_run_text)
    }

    /**
     * Update component blueprints times. Always called by update components material function.
     * @private
     */
    var _updateComponentTime = function () {
        if (!isMaterialListLoaded || !options.hasManufacturedComponent) {
            return
        }

        for (var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]]

            if (!material.isManufactured) {
                continue
            }

            var time = eveUtils.calculateJobTime(
                material.timePerRun, material.runs, facilityStats[material.facility].bpTe, material.timeEfficiency,
                (material.isManufactured) ? options.manufTeImplant : 1.00,
                options.industryLvl, options.advancedIndustryLvl,
                0, 0, 0,
                structureRigs[material.structureTeRig].timeBonus, structureSecStatusMultiplier[material.structureSecStatus],
                facilityStats[material.facility].structure, false
            )

            var time_per_run = eveUtils.calculateJobTime(
                material.timePerRun, 1, facilityStats[material.facility].bpTe, material.timeEfficiency,
                (material.isManufactured) ? options.manufTeImplant : 1.00,
                options.industryLvl, options.advancedIndustryLvl,
                0, 0, 0,
                structureRigs[material.structureTeRig].timeBonus, structureSecStatusMultiplier[material.structureSecStatus],
                facilityStats[material.facility].structure, false
            )

            material.timeTotal = time

            var time_text = utils.durationToString(time)
            var time_per_run_text = utils.durationToString(time_per_run)
            $('.sub-list-' + material.id + ' .total-time').html(time_text)
            $('.sub-list-' + material.id + ' .time-per-run').html(time_per_run_text)
        }
    }

    /**
     * Update component factory informations (from modal)
     * @private
     */
    var _updateComponentInformations = function (allComponents) {
        // init values
        var selector
        var components
        if (allComponents) {
            components = materialsData.componentIdList
        } else {
            components = [parseInt($('#componentModalBpName').attr('data-bp-id'))]
        }

        // get data
        var system = $('#modal-system').val().toLowerCase()
        var runsPerJob = $('#modalRunsPerJob').val()

        var ME = parseInt(utils.noUiSliderGetValue('#ModalME'))
        var TE = parseInt(utils.noUiSliderGetValue('#ModalTE'))

        var facility = parseInt($('#modal-facility').val())

        var structureMeRig = parseInt($('#modal-structure-me-rig input:checked').val())
        var structureTeRig = parseInt($('#modal-structure-te-rig input:checked').val())
        var structureSecStatus = $('#modal-structure-sec-status input:checked').val()

        for (var i in components) {
            var componentId = components[i]
            materialsData.materials[componentId].factorySystemPrevious = materialsData.materials[componentId].factorySystem
            materialsData.materials[componentId].factorySystem = system
            materialsData.materials[componentId].facility = facility
            materialsData.materials[componentId].materialEfficiency = ME
            materialsData.materials[componentId].timeEfficiency = TE
            materialsData.materials[componentId].structureMeRig = structureMeRig
            materialsData.materials[componentId].structureTeRig = structureTeRig
            materialsData.materials[componentId].structureSecStatus = structureSecStatus

            if (isNaN(runsPerJob) || !runsPerJob || parseInt(runsPerJob) <= 0) {
                materialsData.materials[componentId].runsPerJob = materialsData.materials[componentId].maxRunPerBp
            } else {
                materialsData.materials[componentId].runsPerJob = parseInt(runsPerJob)
            }

            _updateComponentBpInfoDisplay(componentId)
        }

        _updateComponentMaterial()
        _updateComponentTime()
        _generateMaterialListQuantity()
        _getSystemCostIndex()
        $('#componentModalBpName').modal('hide')
    }

    /**
     * update component factory informations in the page
     * @private
     * @param the id of the blueprint we update
     */
    var _updateComponentBpInfoDisplay = function (id) {
        if (facilityStats[materialsData.materials[id].facility].structure) {
            var ss = eveData.securityStatus[materialsData.materials[id].structureSecStatus]
            var rigs = 'ME: ' + structureRigs[materialsData.materials[id].structureMeRig].meta
            rigs += ' - TE: ' + structureRigs[materialsData.materials[id].structureTeRig].meta

            $('.sub-list-' + id + ' .structure-ss').html(ss)
            $('.sub-list-' + id + ' .structure-rigs').html(rigs)
            $('.sub-list-' + id + ' .display-structure-config').show()
        } else {
            $('.sub-list-' + id + ' .display-structure-config').hide()
        }

        $('.sub-list-' + id + ' .system').html(materialsData.materials[id].factorySystem)
        $('.sub-list-' + id + ' .me').html(materialsData.materials[id].materialEfficiency)
        $('.sub-list-' + id + ' .te').html(materialsData.materials[id].timeEfficiency)
        $('.sub-list-' + id + ' .facility').html(facilityStats[materialsData.materials[id].facility].name)
        $('.sub-list-' + id + ' .run-per-job').html(materialsData.materials[id].runsPerJob)
    }

    /**
     * Update all tables from summary and price tables.
     * @private
     */
    var _updateSummaryTabs = function () {
        // wait until materials are fully loaded
        if (!isMaterialListLoaded && options.hasManufacturedComponent) {
            return
        }
        _updateMaterialSummaryTable()
        _updateTimeTable()
        _getAllPrices()
    }

    /**
     * Update the production time in the summary tab.
     * Only called by _updateSummaryTabs
     * @private
     */
    var _updateTimeTable = function () {
        var iconColumn = ''
        if (options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>'
        }
        var rowTime = '<tr>' + iconColumn + '<td>@@NAME@@</td><td>@@TIME@@</td></tr>'
        var output = ''

        var materialList = $.merge([materialsData.productItemId], materialsData.componentIdList)

        for (var i in materialList) {
            var material = materialsData.materials[materialList[i]]
            if (material.isManufactured) {
                output += rowTime.replace(/@@ICON@@/g, material.icon)
                                 .replace(/@@NAME@@/g, material.name)
                                 .replace(/@@TIME@@/g, utils.durationToString(material.timeTotal))
            }
        }
        $('#materials-time tbody').html(output)
        $("#materials-time").trigger("update",[true]);
    }

    /**
     * Update the material list with quantity in the summary tab.
     * Only called by _updateSummaryTabs
     * @private
     */
    var _updateMaterialSummaryTable = function () {
        var iconColumn = ''
        if (options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>'
        }
        var rowMaterial = '<tr>' + iconColumn
        rowMaterial += '<td>@@NAME@@</td><td class="quantity">@@QTY@@</td>'
        rowMaterial += '<td class="quantity">@@VOLUME@@</td><td class="quantity">@@TOTAL_VOLUME@@</td></tr>'
        var output = ''
        multiBuy = ''

        var globalVolume = 0.0
        for (var id in materialQuantityList) {
            var totalVolume = materialQuantityList[id].volume * materialQuantityList[id].qty
            globalVolume += totalVolume
            output += rowMaterial.replace(/@@ICON@@/g, materialQuantityList[id].icon)
                                 .replace(/@@NAME@@/g, materialQuantityList[id].name)
                                 .replace(/@@QTY@@/g, Humanize.intcomma(materialQuantityList[id].qty))
                                 .replace(/@@VOLUME@@/g, Humanize.intcomma(materialQuantityList[id].volume, 2))
                                 .replace(/@@TOTAL_VOLUME@@/g, Humanize.intcomma(totalVolume, 2))
            multiBuy += materialQuantityList[id].name + ' ' + materialQuantityList[id].qty + '\n'
        }
        $('#materials-requirement #mat-total-volume').html(Humanize.intcomma(globalVolume, 2))
        $('#materials-requirement tbody').html(output)
        $("#materials-requirement").trigger("update",[true]);
    }

    /**
     * Update the price list with total etc in the price tab.
     * Only called by _getAllPrices and price modal
     * @private
     */
    var _updatePriceTable = function () {
        var prices = priceData.prices
        var itemPrice = priceData.items
        var iconColumn = ''
        if (options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>'
        }
        var rowPrice = '<tr>' + iconColumn + '<td>@@NAME@@</td>' +
                     '<td class="quantity">@@QTY@@</td>' +
                     '<td class="ppu price">@@PRICE@@</td>' +
                     '<td class="total price">@@PRICE_TOTAL@@</td></tr>'

        var output = ''
        var materialTotalPrice = 0

        // calculate price per material and display it
        for (var id in materialQuantityList) {
            var itemPrice = priceData.items[id]
            var priceRegion = priceData.prices[itemPrice.region]
            var price = (priceRegion != undefined && id in priceRegion) ? priceRegion[id][itemPrice.type] : 0

            var materialPrice = price * materialQuantityList[id].qty
            materialTotalPrice += materialPrice

            output += rowPrice.replace(/@@ICON@@/g, materialQuantityList[id].icon)
                               .replace(/@@NAME@@/g, materialQuantityList[id].name)
                               .replace(/@@QTY@@/g, Humanize.intcomma(materialQuantityList[id].qty))
                               .replace(/@@PRICE@@/g, Humanize.intcomma(price, 2))
                               .replace(/@@PRICE_TOTAL@@/g, Humanize.intcomma(materialPrice, 2))
        }
        $('#materials-prices tbody').html(output)
        $("#materials-prices").trigger("update",[true]);

        priceData.totalCost = materialTotalPrice
        _getSystemCostIndex()
    }

    /**
     * Update the price list with total etc in the price tab.
     * Only called by _getSystemCostIndex
     * @private
     */
    var _updateTaxTable = function () {
        var onlySubComponents = (useComponents && options.hasManufacturedComponent)
        var totalInstallationCost = 0

        var iconColumn = ''
        if (options.useIcons) {
            iconColumn = '<td class="icon"><img src="@@ICON@@" alt="@@NAME@@" /></td>'
        }
        var rowTax = '<tr>' + iconColumn + '<td>@@NAME@@</td>' +
                   '<td class="quantity">@@QTY@@</td>' +
                   '<td class="tax price">@@TAX@@</td></tr>'

        // set the main blueprint
        var taxPrice = _calculateBaseCost(materialsData.productItemId)
        taxPrice *= 1.1 * costIndex[materialsData.materials[materialsData.productItemId].factorySystem][eveData.activity.manufacturing]
        totalInstallationCost += taxPrice

        var output = rowTax.replace(/@@ICON@@/g, materialsData.materials[materialsData.productItemId].icon)
                           .replace(/@@NAME@@/g, materialsData.materials[materialsData.productItemId].name)
                           .replace(/@@TAX@@/g, Humanize.intcomma(taxPrice, 2))
                           .replace(/@@QTY@@/g, Humanize.intcomma(materialsData.materials[materialsData.productItemId].qtyJob))

        // display the tax for components
        for (var i in materialsData.componentIdList) {
            var material = materialsData.materials[materialsData.componentIdList[i]]

            if (material.isManufactured) {
                var taxPrice = _calculateBaseCost(material.id)
                taxPrice *= 1.1 * costIndex[material.factorySystem][eveData.activity.manufacturing]

                output += rowTax.replace(/@@ICON@@/g, material.icon)
                                .replace(/@@NAME@@/g, material.name)
                                .replace(/@@TAX@@/g, Humanize.intcomma(taxPrice, 2))
                                .replace(/@@QTY@@/g, Humanize.intcomma(material.qtyJob))

                if (onlySubComponents) {
                    totalInstallationCost += taxPrice
                }
            }
        }
        $('#materials-taxes tbody').html(output)
        $("#materials-taxes").trigger("update",[true]);

        priceData.totalInstallationCost = totalInstallationCost
        _updateMarginMarkupTable()
    }

    /**
     * Update the margin/markup part of the price table using all required data
     * @private
     */
    var _updateMarginMarkupTable = function () {
        var itemPrice = priceData.items[materialsData.productItemId]
        var priceRegion = priceData.prices[itemPrice.region]
        var productPrice = (priceRegion != undefined &&
                            materialsData.productItemId in priceRegion) ? priceRegion[materialsData.productItemId]['sell'] : 0

        var totalCost = priceData.totalCost + priceData.totalInstallationCost
        var unitCost = totalCost / materialsData.materials[materialsData.productItemId].qtyJob
        var totalProductPrice = productPrice * materialsData.materials[materialsData.productItemId].qtyJob

        var margin = totalProductPrice - totalCost
        var marginPercent = (productPrice > 0) ? (margin / totalProductPrice) * 100 : 0
        var markupPercent = (productPrice > 0) ? (margin / totalCost) * 100 : 0

        $('#materials-prices tfoot td#mat-total-price').html(Humanize.intcomma(priceData.totalCost, 2))
        $('#materials-prices tfoot td#total-cost-per-unit').html(Humanize.intcomma(unitCost, 2))
        $('#materials-prices tfoot td#product-price').html(Humanize.intcomma(productPrice, 2))
        $('#materials-prices tfoot td#installation-cost').html(Humanize.intcomma(priceData.totalInstallationCost, 2))
        $('#materials-prices tfoot td#margin').html(Humanize.intcomma(margin, 2))
        $('#materials-prices tfoot td#margin-percent').html(Humanize.intcomma(marginPercent, 2) + '%')
        $('#materials-prices tfoot td#markup-percent').html(Humanize.intcomma(markupPercent, 2) + '%')
    }

    /**
     * Calculate the base cost for installation fee
     * if a component has no adjusted price, force the value to 1.0
     * @param  material_id the id of the material we want to job cost
     * @private
     */
    var _calculateBaseCost = function (material_id) {
        var material
        var runs
        if (material_id == materialsData.productItemId) {
            material = materialsData
            runs = options.runs
        } else {
            material = materialsData.materials[material_id]
            runs = materialsData.materials[material_id].runs
        }

        var baseCost = 0
        for (var i in material.componentIdList) {
            var component = material.materials[material.componentIdList[i]]
            var adjustedPrice = priceData.adjusted[component.id]
            adjustedPrice = (adjustedPrice === undefined) ? 1.0 : adjustedPrice
            baseCost += component.qtyRequiredPerRun * adjustedPrice
        }
        return baseCost * runs
    }

    // -------------------------------------------------
    // Events declarations
    //

    /**
     * Ajax call to get html template for later use.
     * @private
     */
    var _initTemplates = function () {
        $.get(lb.urls.tplSublistBlockUrl,
            function (tpl) { tplSublistBlock = tpl }
        )
        $.get(lb.urls.tplSublistRowUrl,
            function (tpl) { tplSublistRow = tpl }
        )
        $.get(lb.urls.tplModalPriceUrl,
            function (tpl) { tplModalPrice = tpl }
        )
    }

    /**
     * Init tooltips
     * @private
     */
    var _initTooltip = function () {
        $('[data-toggle="tooltip"]').tooltip()
    }

    /**
     * Init input fields
     * @private
     */
    var _initInputs = function () {
        $('#runs').on('keyup', _runsOnKeyUp)
                  .on('change', _runOnChange)

        $('#facility').on('change', function () {
            var facility = parseInt($('#facility').val())
            materialsData.materials[materialsData.productItemId].facility = facility
            _toggleStructureConfigsDisplay(facilityStats[facility].structure, false)
            _updateTime()
            _updateMaterial()
        })
        $("#structure-sec-status input[type='radio']").on('change', function () {
            materialsData.materials[materialsData.productItemId].structureSecStatus = $(this).val()
            _updateTime()
            _updateMaterial()
        })
        $("#structure-te-rig input[type='radio']").on('change', function () {
            materialsData.materials[materialsData.productItemId].structureTeRig = parseInt($(this).val())
            _updateTime()
        })
        $("#structure-me-rig input[type='radio']").on('change', function () {
            materialsData.materials[materialsData.productItemId].structureMeRig = parseInt($(this).val())
            _updateMaterial()
        })

        $('#modal-facility').on('change', function () {
            var facility = parseInt($('#modal-facility').val())
            _toggleStructureConfigsDisplay(facilityStats[facility].structure, true)
        })

        $("#raw-components input[type='checkbox']").on('change', _componentButtonOnStateChange)

        $("#toggleMaxRunPerBpcModal input[type='checkbox']").on('change', _toggleMaxRunPerBpcModal)
        $('#maxRunBpc').on('click', _setMaxRunBpc)
        $('#runsPerJob').on('keyup', _runsPerJobOnKeyUp)
                        .on('change', _runsPerJobOnChange)

        $('#manufTeImplant').on('change', function () {
            options.manufTeImplant = parseFloat($('#manufTeImplant').val())
            _updateTime()
            _updateComponentTime()
        })
    }

    /**
     * Init tab event actions
     * @private
     */
    var _initTabs = function () {
        $('#bp-tabs a').on('click',
            function (e) {
                e.preventDefault()
                $(this).tab('show')
            }
        ).on('shown.bs.tab', _tabOnShow)
    }

    /**
     * Init typeahead objects
     * @private
     */
    var _initTypeahead = function () {
        eveUtils.initSolarSystemTypeahead('#system', function (event, suggestion) {
            var manufSystem = materialsData.materials[materialsData.productItemId].factorySystem
            if (manufSystem == $(this).typeahead('val').toLowerCase()) {
                return
            }
            materialsData.materials[materialsData.productItemId].factorySystemPrevious = manufSystem
            materialsData.materials[materialsData.productItemId].factorySystem = $(this).typeahead('val').toLowerCase()
            _getSystemCostIndex()
        })
        eveUtils.initSolarSystemTypeahead('#modal-system')
    }

    /**
     * Init all sliders on the page
     * @private
     */
    var _initSliders = function () {
        var skillSliderConf = {
            start: 0,
            connect: [true, false],
            step: 1,
            range: {
                min: 0,
                max: 5
            }
        }
        var meSliderConf = {
            start: 0,
            connect: [true, false],
            step: 1,
            range: {
                min: 0,
                max: 10
            }
        }
        var teSliderConf = {
            start: 0,
            connect: [true, false],
            step: 2,
            range: {
                min: 0,
                max: 20
            }
        }

        utils.noUiSliderCreate('#ME', meSliderConf)
        utils.noUiSliderCreate('#ModalME', meSliderConf)
        utils.noUiSliderCreate('#TE', teSliderConf)
        utils.noUiSliderCreate('#ModalTE', teSliderConf)
        utils.noUiSliderCreate('#industry-level, #adv-industry-level, #t2-level, #t2-science1, #t2-science2', skillSliderConf)

        utils.noUiSliderSetValue('#ME', options.materialEfficiency)
        utils.noUiSliderSetValue('#TE', options.timeEfficiency)
        utils.noUiSliderSetValue('#adv-industry-level', options.advancedIndustryLvl)
        utils.noUiSliderSetValue('#industry-level', options.industryLvl)
        utils.noUiSliderSetValue('#t2-level', options.t2ConstructionLvl)
        utils.noUiSliderSetValue('#t2-science1', options.datacoreLevel1)
        utils.noUiSliderSetValue('#t2-science2', options.datacoreLevel2)

        utils.noUiSliderBind('#ME', 'slide', _materialEfficiencyOnUpdate)
        utils.noUiSliderBind('#TE', 'slide', _timeEfficiencyOnUpdate)
        utils.noUiSliderBind('#ModalME', 'slide', _modalMaterialEfficiencyOnUpdate)
        utils.noUiSliderBind('#ModalTE', 'slide', _modalTimeEfficiencyOnUpdate)
        utils.noUiSliderBind(
            '#industry-level, #adv-industry-level, #t2-level, #t2-science1, #t2-science2',
            'slide', _skillOnUpdate
        )
    }

    /**
     * Init all sliders on the page
     * @private
     */
    var _initModal = function () {
        $('#subComponentBpConfigModal').on('show.bs.modal', function (event) {
            var button = $(event.relatedTarget)
            var id = button.attr('data-id')
            var name = materialsData.materials[id].name

            var system = materialsData.materials[id].factorySystem
            var facility = materialsData.materials[id].facility

            var structureMeRig = materialsData.materials[id].structureMeRig
            var structureTeRig = materialsData.materials[id].structureTeRig
            var structureSecStatus = materialsData.materials[id].structureSecStatus

            var me = materialsData.materials[id].materialEfficiency
            var te = materialsData.materials[id].timeEfficiency

            var runsPerJob = materialsData.materials[id].runsPerJob

            $('#componentModalBpName').html(name)
            $('#componentModalBpName').attr('data-bp-id', id)
            $('#modal-system').val(system)
            $('#modalRunsPerJob').val(runsPerJob)
            $('#modal-facility option[value=' + facility + ']').prop('selected', true)
            $('#modal-structure-me-rig input[value=' + structureMeRig + ']').parent().button('toggle')
            $('#modal-structure-te-rig input[value=' + structureTeRig + ']').parent().button('toggle')
            $('#modal-structure-sec-status input[value=' + structureSecStatus + ']').parent().button('toggle')

            utils.noUiSliderSetValue('#ModalME', me)
            utils.noUiSliderSetValue('#ModalTE', te)
            $('#Modal-ME-Level').html(me)
            $('#Modal-TE-Level').html(te)

            if ($('#modalRunsPerJob').attr('disabled')) {
                $('#toggleMaxRunPerBpcModal label').button('toggle')
                $('#modalRunsPerJob').attr('disabled', false)
            }
        })

        $('#modal-apply').on('click', _onModalBpApplyOne)
        $('#modal-apply-all').on('click', _onModalBpApplyAll)
    }

    /**
     * Init the content of the price modal
     * @private
     */
    var _initPriceModalContent = function () {
        if (tplModalPrice == '' || !priceData.isLoaded) {
            // if any template is not yet set, try again in 1sec
            return setTimeout(_initPriceModalContent, 100)
        }

        var $output = $('')

        for (var i in priceData.itemList) {
            var item = priceData.items[priceData.itemList[i]]

            var tpl = tplModalPrice.replace(/@@ID@@/g, item.id)
                                   .replace(/@@NAME@@/g, item.name)
                                   .replace(/@@ICON@@/g, item.icon)

            tpl = $(tpl)
            // need to use attr for checked and selected as when we display it, we lost the "prop" value...
            tpl.find('.modal-order-type .btn-' + item.type).button('toggle')
            // tpl.find('.modal-order-type .btn-' + item.type + ' input').prop('checked', true);

            // clone the list of region, unselect any, select the correct region..
            tpl.find('.modal-region').append($('#modal-region-all > option').clone())
            // tpl.find('.modal-region option:selected').removeAttr("selected");
            tpl.find('.modal-region').val(item.region)
            // tpl.find('.modal-region option[value="' + item.region + '"]').prop('selected', true);

            // get the current price
            var currentPrice = (priceData.prices[item.region][item.id]) ? priceData.prices[item.region][item.id][item.type] : 0
            tpl.attr('title', Humanize.intcomma(currentPrice, 2) + ' ISK')

            // add to the output
            tpl.appendTo('#priceConfigModal .lb-list tbody')
        }
        _initPriceModalEvent()
    }

    /**
     * [_initPirceModalEvent description]
     * @private
     */
    var _initPriceModalEvent = function () {
        // add check event when we click on the table cell, for easier use
        $('.checkbox-cell').on('click', function (event) {
            var checkbox = $(this).find('input[type="checkbox"]')
            checkbox.prop('checked', !checkbox.prop('checked'))

            if (checkbox.attr('id') == 'modal-price-checkall') {
                _checkboxPriceToggleAllOnChange(event, checkbox)
            }
        })

        // but we need to stop event propagation when we click on the checkbox
        $('.checkbox-cell input[type="checkbox"]').on('click', function (event) {
            event.stopPropagation()
        })

        // check them all
        $('#modal-price-checkall').on('change', _checkboxPriceToggleAllOnChange)

        // price tooltips !
        $('[data-toggle="tooltip"]').tooltip()

        // change price
        $('.modal-region').on('change', _priceChangeOnTypeRegionChange)
        $('.modal-order-type .btn input').on('change', _priceChangeOnTypeRegionChange)

        // apply to all select action, using checked rows
        $('#modal-order-type-apply-all').on('click', function (event) {
            var typeOrder = $('#modal-order-all').val()
            modalPriceUpdatePrice = false

            $('#priceConfigModal .lb-list tbody .checkbox-cell input:checked').each(function () {
                var id = $(this).attr('data-id')
                $('.price-config-row[data-id="' + id + '"] .modal-order-type .btn-' + typeOrder).button('toggle')
                $('.price-config-row[data-id="' + id + '"]').tooltip('hide')
            })

            modalPriceUpdatePrice = true
            _updatePriceTable()
        })

        $('#modal-region-apply-all').on('click', function (event) {
            var region = $('#modal-region-all').val()
            modalPriceUpdatePrice = false

            $('#priceConfigModal .lb-list tbody .checkbox-cell input:checked').each(function (event) {
                var id = $(this).attr('data-id')
                $('.modal-region[data-id="' + id + '"]').val(region).change()
                $('.price-config-row[data-id="' + id + '"]').tooltip('hide')
            })

            modalPriceUpdatePrice = true
            _updatePriceTable()
        })
    }

    // -------------------------------------------------
    // Events functions
    //

    /**
     * Toggle the display of struture configurations depending on the parameter.
     * If isStructure is True, we display ME/TE Rig and Security Status configs.
     * Else we hide these configs.
     * @param  {Boolean} isStructure Wether if the selected facility is a structure or not
     * @param  {Boolean} modal true if we are in the modal. Define the class to update
     * @private
     */
    var _toggleStructureConfigsDisplay = function (isStructure, modal) {
        if (modal) {
            var structConfClass = '.modal-structure-configs'
        } else {
            var structConfClass = '.structure-configs'
        }
        if (isStructure) {
            $(structConfClass).show()
        } else {
            $(structConfClass).hide()
        }
    }

    /**
     * Function called on event keyup for 'run' text field
     * Replace the text input value with an integer (if it's anything else)
     * @private
     */
    var _runsOnKeyUp = function (e) {
        if (!$.isNumeric($(this).val()) || $(this).val() < 1) {
            options.runs = 1
        } else {
            options.runs = parseInt($(this).val())
        }
        var material = materialsData.materials[materialsData.productItemId]
        var qty = material.resultQtyPerRun * options.runs
        material.qtyJob = qty

        $('#qty-required-' + material.id).html(Humanize.intcomma(qty))

        _updateMaterial()
        _updateTime()

        return false
    }

    /**
     * Function called on event change for 'run' text field
     * prevents from bugging where no keyup is done.
     * @private
     */
    var _runOnChange = function (e) {
        $(this).val(options.runs)
        return false
    }

    /**
     * Function called on event change for 'runs per job' text field
     * prevents from bugging where no keyup is done.
     */
    var _runsPerJobOnChange = function () {
        var material = materialsData.materials[materialsData.productItemId]
        $(this).val(material.runsPerJob)
        return false
    }

    /**
     * Function called on event change for 'runs per job' text field
     * Replace the text input value with an integer (if it's anything else)
     * @private
     */
    var _runsPerJobOnKeyUp = function () {
        var material = materialsData.materials[materialsData.productItemId]
        if (!$.isNumeric($(this).val()) || $(this).val() < 1) {
            material.runsPerJob = material.runsPerJob
            $(this).val(material.runsPerJob)
            return false
        } else {
            material.runsPerJob = parseInt($(this).val())
        }

        _updateMaterial()
        _updateTime()

        return false
    }

    /**
     * Function called on event show for tabs
     * @private
     * @TODO only call update on some tabs.
     */
    var _tabOnShow = function (e) {
        var tab = $(this).attr('href')

        // use component button events.
        if (options.hasManufacturedComponent) {
            switch (tab) {
                case '#tab-summary':
                    if (lastTab == '#tab-price') {
                        $('#raw-components').detach().appendTo(tab + ' .raw-component-btn')
                        lastTab = tab
                    }
                    break
                case '#tab-price':
                    if (lastTab == '#tab-summary') {
                        $('#raw-components').detach().appendTo(tab + ' .raw-component-btn')
                        lastTab = tab
                    }
                    break
            }
        }

        // only update when on summary / price tables
        if (tab == '#tab-price' || tab == '#tab-summary') {
            _updateSummaryTabs()
        }
    }

    /**
     * Function called on event update on the material efficiency slider
     * @private
     */
    var _materialEfficiencyOnUpdate = function (value) {
        var value = parseInt(value)
        $('#ME-Level').html(value + '%')
        options.materialEfficiency = parseInt(value)
        _updateMaterial()
    }

    /**
     * Function called on event update on the time efficiency slider
     * @private
     */
    var _timeEfficiencyOnUpdate = function (value) {
        var value = parseInt(value)
        $('#TE-Level').html(value + '%')
        options.timeEfficiency = parseInt(value)
        _updateTime()
    }

    /**
     * Function called on event update on the material efficiency slider
     * in the modal window
     * @private
     */
    var _modalMaterialEfficiencyOnUpdate = function (value) {
        var value = parseInt(value)
        $('#Modal-ME-Level').html(value)
    }

    /**
     * Function called on event update on the time efficiency slider
     * in the modal window
     * @private
     */
    var _modalTimeEfficiencyOnUpdate = function (value) {
        var value = parseInt(value)
        $('#Modal-TE-Level').html(value)
    }

    /**
     * Function called on event update on the skill level sliders
     * @private
     */
    var _skillOnUpdate = function (value) {
        var id = $(this.target).attr('id')
        var value = parseInt(value)

        switch (id) {
            case 'industry-level':
                options.industryLvl = value
                $('#industry-level-display').html(value)
                break

            case 'adv-industry-level':
                options.advancedIndustryLvl = value
                $('#adv-industry-level-display').html(value)
                break

            case 't2-level':
                options.t2ConstructionLvl = value
                $('#t2-level-display').html(value)
                break

            case 't2-science1':
                options.datacoreLevel1 = value
                $('#t2-science1-display').html(value)
                break

            case 't2-science2':
                options.datacoreLevel2 = value
                $('#t2-science2-display').html(value)
                break
        };
        _updateTime()
        _updateComponentTime()
    }

    /**
     * Proxy function for apply click event in modal
     * @call updateComponentInformations
     * @private
     */
    var _onModalBpApplyOne = function () {
        _updateComponentInformations(false)
    }

    /**
     * Proxy function for apply all click event in modal
     * @call updateComponentInformations
     * @private
     */
    var _onModalBpApplyAll = function () {
        _updateComponentInformations(true)
    }

    /**
     *  Toggle button event to set max run bpc for component in modal form
     *  @private
     */
    var _toggleMaxRunPerBpcModal = function () {
        var id = $('#componentModalBpName').attr('data-bp-id')
        if (!this.checked) {
            $('#modalRunsPerJob').val(materialsData.materials[id].runsPerJob)
            $('#modalRunsPerJob').attr('disabled', false)
        } else {
            $('#modalRunsPerJob').val('Max BPC Run')
            $('#modalRunsPerJob').prop('disabled', true)
        }
    }

    /**
     *  Set set max run bpc for run/job for main BPO
     *  @private
     */
    var _setMaxRunBpc = function () {
        var id = materialsData.productItemId
        $('#runsPerJob').val(materialsData.materials[id].maxRunPerBp)
        materialsData.materials[id].runsPerJob = materialsData.materials[id].maxRunPerBp

        _updateMaterial()
        _updateTime()

        return false
    }

    /**
     * Update button "raw components" state and update tables
     * @private
     */
    var _componentButtonOnStateChange = function () {
        // update button styles
        var state = 'YES'
        var style = 'btn-danger'
        var newStyle = 'btn-success'

        if (!this.checked) {
            state = 'NO'
            style = 'btn-success'
            newStyle = 'btn-danger'
        }
        $('#raw-components .state').html(state)
        $('#raw-components .btn').removeClass(style).addClass(newStyle)

        // update material tables infos.
        useComponents = this.checked
        _generateMaterialListQuantity()
        _updateSummaryTabs()
    }

    /**
     * (Un)Check all checkbox in price modal
     * when the "check all" checkbox is used
     * @param checkbox jQuery Object which contains the checkbox to check
     * @private
     */
    var _checkboxPriceToggleAllOnChange = function (event, checkbox) {
        checkbox = typeof checkbox !== 'undefined' ? checkbox : $(this)
        var state = checkbox.prop('checked')
        $('#priceConfigModal .lb-list tbody .checkbox-cell input').prop('checked', state)
    }

    /**
     * Change price for specified item and update all blueprint prices
     * @private
     */
    var _priceChangeOnTypeRegionChange = function (event) {
        // get data
        var item = priceData.items[$(this).attr('data-id')]
        var newRegion = $('.modal-region[data-id="' + item.id + '"]').val()
        var newType = $('.modal-order-type .btn input[data-id="' + item.id + '"]:checked').val()

        // update item infos
        item.region = newRegion
        item.type = newType

        // now get the price and display it
        var currentPrice = priceData.prices[item.region][item.id]
        currentPrice = (currentPrice === undefined) ? 0 : currentPrice[item.type]
        currentPrice = Humanize.intcomma(currentPrice, 2)
        $('.price-config-row[data-id="' + item.id + '"]').attr('data-original-title', currentPrice + ' ISK')
                                                         .removeClass('focus')
                                                         .tooltip('show')
        if (modalPriceUpdatePrice) {
            _updatePriceTable()
        }
    }

    /**
     * Runner function
     */
    var run = function () {
        // init interface stuff before some check, to have no UI issue
        _initSliders()
        _initInputs()
        _initTooltip()

        $('#multibuy').on('click', function () {
            utils.copyToClipboard(multiBuy)
        })

        $('.lb-sorted').tablesorter({
            theme: "bootstrap",
            headerTemplate : '{content} {icon}',
            cssIconAsc: 'fa fa-sort-up',
            cssIconDesc: 'fa fa-sort-down',
            cssIconNone: 'fa fa-sort',
        });

        // check all required urls (so we don't have to do it later)
        if (!lb.urls.systemUrls || !lb.urls.materialBOMUrl || !lb.urls.priceUrl || !lb.urls.indexActivityUrl ||
            !lb.urls.tplSublistBlockUrl || !lb.urls.tplSublistRowUrl || !lb.urls.tplModalPriceUrl) {
            alert('Error, some URL are missing, this application cannot work properly without them.')
            return
        }

        // other init that require ajax call
        _initTemplates()
        _initTypeahead()
        _initTabs()
        _initModal()

        // get materials
        _getComponentMaterials()
        _updateSummaryTabs()
        _updateMaterial()
        _updateTime()

    }

    // -------------------------------------------------
    // return object
    //
    return {
        // required objects
        options: options,
        materialsData: materialsData,

        // functions
        run: run
    }
})(jQuery, lb, utils, eveUtils, eveData, Humanize)

lb.registerModule('manufacturingBlueprint', manufacturingBlueprint)
