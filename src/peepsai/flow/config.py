DARK_GRAY = "#333333"
PEEPSAI_ORANGE = "#FF5A50"
GRAY = "#666666"
WHITE = "#FFFFFF"
BLACK = "#000000"

COLORS = {
    "bg": WHITE,
    "start": PEEPSAI_ORANGE,
    "method": DARK_GRAY,
    "router": DARK_GRAY,
    "router_border": PEEPSAI_ORANGE,
    "edge": GRAY,
    "router_edge": PEEPSAI_ORANGE,
    "text": WHITE,
}

NODE_STYLES = {
    "start": {
        "color": PEEPSAI_ORANGE,
        "shape": "box",
        "font": {"color": WHITE},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
    "method": {
        "color": DARK_GRAY,
        "shape": "box",
        "font": {"color": WHITE},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
    "router": {
        "color": {
            "background": DARK_GRAY,
            "border": PEEPSAI_ORANGE,
            "highlight": {
                "border": PEEPSAI_ORANGE,
                "background": DARK_GRAY,
            },
        },
        "shape": "box",
        "font": {"color": WHITE},
        "borderWidth": 3,
        "borderWidthSelected": 4,
        "shapeProperties": {"borderDashes": [5, 5]},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
    "peeps": {
        "color": {
            "background": WHITE,
            "border": PEEPSAI_ORANGE,
        },
        "shape": "box",
        "font": {"color": BLACK},
        "borderWidth": 3,
        "borderWidthSelected": 4,
        "shapeProperties": {"borderDashes": False},
        "margin": {"top": 10, "bottom": 8, "left": 10, "right": 10},
    },
}
