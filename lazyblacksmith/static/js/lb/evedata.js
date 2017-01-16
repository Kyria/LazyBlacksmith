var eveData = (function() {
    "use strict";
    /**
     * Structure data
     */
    var structureRigs = [
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
            "name": 'Raitaru',
            "structure": true,
        },
        { // [2]
            "bpMe": 0.99,
            "bpTe": 0.80,
            "jobMe": 0.80,
            "jobTe": 0.80,
            "copy": 0.80,
            "invention": 0.80,
            "name": 'Azbel',
            "structure": true,
        },
        { // [3]
            "bpMe": 0.99,
            "bpTe": 0.70,
            "jobMe": 0.70,
            "jobTe": 0.70,
            "copy": 0.70,
            "invention": 0.70,
            "name": 'Sotiyo',
            "structure": true,
        },
        { // [4]
            "bpMe": 1.0,
            "bpTe": 1.0,
            "jobMe": 1.0,
            "jobTe": 1.0,
            "copy": 1.0,
            "invention": 1.0,
            "name": 'Other Structures',
            "structure": true,
        },
        { // [5] - manufacturing
            "bpMe": 0.98,
            "bpTe": 0.75,
            "name": 'Assembly Array',
            "structure": false,
        },
        { // [6] - manufacturing
            "bpMe": 0.9,
            "bpTe": 0.75,
            "name": 'Thukker Component Array',
            "structure": false,
        },
        { // [7] - Manufacturing
            "bpMe": 1.05,
            "bpTe": 0.65,
            "name": 'Rapid Assembly Array',
            "structure": false,
        },
        { // [8] - Research - Invention
            "jobMe": 0.7,
            "jobTe": 0.7,
            "copy": 0.6,
            "invention": 0.5,
            "name": 'Laboratory',
            "structure": false,
        },
        { // [9] - Research
            "jobMe": 0.65,
            "jobTe": 0.65,
            "copy": 0.6,
            "name": 'Hyasyoda Laboratory',
            "structure": false,
        },
        { // [10] - Invention
            "copy": 1.0,
            "invention": 1.0,
            "name": 'Experimental Laboratory',
            "structure": false,
        },
    ];

    
    return {
        structureRigs: structureRigs,
        structureSecStatusMultiplier: structureSecStatusMultiplier,
        facilities: facilities,
    };

})();
