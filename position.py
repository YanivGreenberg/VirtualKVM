import mss


def get_full_screen_roi():
    """Automatically sets the ROI to cover all connected monitors."""
    with mss.mss() as sct:
        monitors = sct.monitors[1:] 
        
        left = min(monitor["left"] for monitor in monitors)
        top = min(monitor["top"] for monitor in monitors)
        right = max(monitor["left"] + monitor["width"] for monitor in monitors)
        bottom = max(monitor["top"] + monitor["height"] for monitor in monitors)
        
        return {
            "top": top,
            "left": left,
            "width": right - left,
            "height": bottom - top
        }
    

def calculate_mouse_switch_position(x,y,region_from,region_to):
    """
    Maps the mouse position from region_from (PC1) to region_to (PC2),
    while mirroring the X-axis to swap left and right.
    """
    # Step 1: Get relative coordinates in region_from
    relative_x = x - region_from["left"]
    relative_y = y - region_from["top"]

    # Step 2: Mirror X (flip horizontally) and scale to region_to
    mapped_x = (1 - (relative_x / region_from["width"])) * region_to["width"]
    mapped_y = (relative_y / region_from["height"]) * region_to["height"]

    return int(mapped_x), int(mapped_y)  # Return integer pixel values