schema = {
    "Product_info": {
        "attributes": [
            "iid",
            "Product",
        ],
        "key": "Product",
        "representation": ["Product"]
    },

    "Segment_info": {
        "attributes": [
            "iid",
            "Segment"
        ],
        "key": "Segment",
        "representation": ["Segment"]
    },

    "TCSS_info": {
        "attributes": [
            "iid",
            "TCSS"
        ],
        "key": "TCSS",
        "representation": ["TCSS"]
    },

    "AT_Site_info": {
        "attributes": [
            "iid",
            "AT_Site"
        ],
        "key": "AT_Site",
        "representation": ["AT_Site"]
    },

    "Cycle_info": {
        "attributes": [
            "iid",
            "Cycle"
        ],
        "key": "Cycle",
        "representation": ["Cycle"]
    },

    "Phase_info": {
        "attributes": [
            "iid",
            "Phase"
        ],
        "key": "Phase",
        "representation": ["Phase"]
    },
    
    "Comment_info": {
        "attributes": [
            "iid",
            "Comment"
        ],
        "key": "Comment",
        "representation": ["Comment"]
    },

    "product_details": {
        "relates": [
            "Product",
            "Segment",
            "TCSS",
            "Package_Tech",
            "Chip_Attach",
            "Tester_Platform",
            "AT_Site",
            "Division"
        ],
        "attributes": [
            "iid"
        ],
        "key": "Product",
        "representation": ["Product.Product"]
    },

    "product_cycle": {
        "relates": [
            "Product",
            "Cycle"
        ],
        "attributes": [
            "iid"
        ],
        "key": "Product",
        "representation": ["Product.Product"]
    },

    "production_log": {
        "relates": [
            "Product",
            "Cycle",
            "Phase",
            "Comment"
        ],
        "attributes": [
            "idd",
            "WW"
        ],
        "key": "Product",
        "representation": ["Product.Product"]
    }
}
