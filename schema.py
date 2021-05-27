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

    "tcss_info": {
        "attributes": [
            "iid",
            "TCSS"
        ],
        "key": "id",
        "representation": ["TCSS"]
    },

    "at_site_info": {
        "attributes": [
            "iid",
            "AT_Site"
        ],
        "key": "id",
        "representation": ["AT_Site"]
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

    "include_tcss": {
        "attributes": [
            "iid"
        ],
        "key": "id",
        "representation": ["product.Product_RMIT"]
    },

    "include_at_site": {
        "attributes": [
            "iid"
        ],
        "key": "id",
        "representation": ["product.Product_RMIT"]
    },

    "include_cycle": {
        "attributes": [
            "iid"
        ],
        "key": "id",
        "representation": ["product.Product_RMIT"]
    },

    "include_comment": {
        "attributes": [
            "idd"
        ],
        "key": "id",
        "representation": ["product.Product_RMIT", "cycle.cycle", "phase.Phase", "comment.WW", "comment.comment"]
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
        "representation": ["product.Product_RMIT"]
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
        "representation": ["product.Product_RMIT"]
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
        "representation": ["product.Product_RMIT"]
    },

    "include_package_tech": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT"]
    },

    "include_chip_attach": {
        "attributes": [
           "iid" 
        ],
        "key": "id",
        "representation": ["product.Product_RMIT"]
    }
}