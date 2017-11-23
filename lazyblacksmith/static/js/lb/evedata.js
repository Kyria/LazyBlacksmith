var eveData = (function() {
    "use strict";
    /**
     * Structure data
     */
    var structureIndustryRigs = [
        { // No rig bonus
            'timeBonus': 0,
            'materialBonus': 0,
            "meta": "None",
        },
        { // t1 rig bonus
            'timeBonus': 0.20,
            'materialBonus': 0.02,
            "meta": "T1",
        },
        { // t2 rig bonus
            'timeBonus': 0.24,
            'materialBonus': 0.024,
            "meta": "T2",
        }
    ];

    var structureSecStatusMultiplier = {
        'h': 1.0,  // High Sec
        'l': 1.9,  // Low Sec
        'n': 2.1,  // Null Sec / WH
    };

    // as refineries can't be in highsec, multiplier are different..
    var refinerySecStatusMultiplier = {
        'h': 0,
        'l': 1,
        'n': 1.1,
    }

    var securityStatus = {
        'h': 'High Sec',
        'l': 'Low Sec',
        'n': 'Null Sec / WH',
    };

    /**
     * Facillities List
     */
    var facilities = [
        { // [0]
            "bpMe": 1.0, // bonus on blueprint ME
            "bpTe": 1.0, // bonus on blueprint TE
            "jobMe": 1.0, // time bonus on ME Research on BPO
            "jobTe": 1.0, // time bonus on TE Research on BPO
            "copy": 1.0,
            "invention": 1.0,
            "reactionTime": 1.0,
            "name": 'Station',
            "structure": false,
        },
        { // [1]
            "bpMe": 0.99,
            "bpTe": 0.85,
            "jobMe": 0.85,
            "jobTe": 0.85,
            "copy": 0.85,
            "invention": 0.85,
            "reactionTime": 1.0,
            "name": 'Raitaru (M-EC)',
            "structure": true,
        },
        { // [2]
            "bpMe": 0.99,
            "bpTe": 0.80,
            "jobMe": 0.80,
            "jobTe": 0.80,
            "copy": 0.80,
            "invention": 0.80,
            "reactionTime": 1.0,
            "name": 'Azbel (L-EC)',
            "structure": true,
        },
        { // [3]
            "bpMe": 0.99,
            "bpTe": 0.70,
            "jobMe": 0.70,
            "jobTe": 0.70,
            "copy": 0.70,
            "invention": 0.70,
            "reactionTime": 1.0,
            "name": 'Sotiyo (XL-EC)',
            "structure": true,
        },
        { // [4]
            "bpMe": 1.0,
            "bpTe": 1.0,
            "jobMe": 1.0,
            "jobTe": 1.0,
            "copy": 1.0,
            "invention": 1.0,
            "reactionTime": 1.0,
            "name": 'Other Structures',
            "structure": true,
        },
        { // [5]
            "bpMe": 1.0,
            "bpTe": 1.0,
            "jobMe": 1.0,
            "jobTe": 1.0,
            "copy": 1.0,
            "invention": 1.0,
            "reactionTime": 1.0,
            "name": 'Athanor',
            "structure": true,
        },
        { // [6]
            "bpMe": 1.0,
            "bpTe": 1.0,
            "jobMe": 1.0,
            "jobTe": 1.0,
            "copy": 1.0,
            "invention": 1.0,
            "reactionTime": 0.75,
            "name": 'Tatara',
            "structure": true,
        }
    ];

    var implants = {
        'me': {
            '1.00': 'None',
            '0.99': 'MY-701',
            '0.97': 'MY-703',
            '0.95': 'MY-705'
        },
        'te': {
            '1.00': 'None',
            '0.99': 'RR-601',
            '0.97': 'RR-603',
            '0.95': 'RR-605'
        },
        'copy': {
            '1.00': 'None',
            '0.99': 'SC-801',
            '0.97': 'SC-803',
            '0.95': 'SC-805'
        }
    }


    return {
        structureIndustryRigs: structureIndustryRigs,
        refinerySecStatusMultiplier: refinerySecStatusMultiplier,
        structureSecStatusMultiplier: structureSecStatusMultiplier,
        facilities: facilities,
        securityStatus: securityStatus,
        implants: implants,
    };

})();
