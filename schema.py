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
}