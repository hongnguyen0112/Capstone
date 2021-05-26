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

    "package_tech_info": {
        "attributes": [
            "iid",
            "Package_Tech"
        ],
        "key": "id",
        "representation": ["Package_Tech"]
    },

    "chip_attach_info": {
        "attributes": [
            "iid",
            "Chip_Attach"
        ],
        "key": "id",
        "representation": ["Chip_Attach"]
    },

    "include_testerplatform": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "Tester_Platform.Tester_Platform"]
    },

    "segment_info": {
        "attributes": [
            "iid",
            "Segment"
        ],
        "key": "id",
        "representation": ["Segment"]
    },

    "include_segment": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "Segment.Segment"]
    },

     "division_info": {
        "attributes": [
            "iid",
            "Division"
        ],
        "key": "id",
        "representation": ["Division"]
    },

    "include_division": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "Division.Division"]
    },

    "include_package_tech": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "Package_Tech.Package_Tech"]
    },

    "include_chip_attach": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "Chip_Attach.Chip_Attach"]
    }
}