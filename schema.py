schema = {
    "product": {
        "attributes": [
            "iid",
            "Product_RMIT", 
            "Segment", 
            "TCSS", 
            "AT_Site",
            "Division",
            "Package_Tech",
            "Chip_Attach",
            "Tester_Platform",
            "cycle",
            "Phase",
            "WW",
            "comment"
        ],
        "key": "id",
        "representation": ["Product_RMIT"]
    },

    "cycle_info": {
        "attributes": [
            "iid",
            "cycle"
        ],
        "key": "id",
        "representation": ["cycle"]
    },

    "phase_info": {
        "attributes": [
            "iid",
            "Phase"
        ],
        "key": "id",
        "representation": ["Phase"]
    },
    
    "comment_info": {
        "attributes": [
            "iid",
            "WW",
            "comment"
        ],
        "key": "id",
        "representation": ["WW", "comment"]
    },

    "include_cycle": {
        "attributes": [
            "iid"
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "cycle.cycle"]
    },

    "testerplatform_info": {
        "attributes": [
            "iid",
            "Tester_Platform"
        ],
        "key": "id",
        "representation": ["Tester_Platform"]
    },

    "include_testerplatform": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "Tester_Platform.Tester_Platform"]
    }
}