import cv2 as cv
import numpy as np
import os

# ================== Folders ==================
input_folder = "C:\\Users\\pc\\Desktop\\uas_project\\images"
output1_folder = "C:\\Users\\pc\\Desktop\\uas_project\\output\\output1"  # Casualties + total score
output2_folder = "C:\\Users\\pc\\Desktop\\uas_project\\output\\output2"  # Final output with lines

# ================== Priority & Capacity ==================
casualty_priority = {"star":3, "triangle":2, "square":1}
emergency_priority = {"red":3, "yellow":2, "green":1}
rescuepad_capacity = {"blue":4, "pink":3, "gray":2}

# ================== HSV Ranges ==================
hsv_ranges = {
    "red": (np.array([0, 60, 240]), np.array([5, 102, 255])),
    "yellow": (np.array([21, 163, 252]), np.array([25, 180, 255])),
    "green": (np.array([40, 132, 239]), np.array([45, 138, 255])),
    "blue": (np.array([100, 70, 252]), np.array([120, 125, 255])),
    "pink": (np.array([140, 60, 252]), np.array([151, 100, 255])),
    "gray": (np.array([0, 0, 219]), np.array([1, 5, 225]))
}

# ================== Land & Ocean Masks ==================
lower_land = np.array([55, 178, 127])
upper_land = np.array([65, 230, 153])
lower_ocean = np.array([100, 153, 89])
upper_ocean = np.array([115, 204, 115])

# ================== Colors for Drawing ==================
outline_color = (0,0,0)        # Black outline
land_display = (19, 69, 139)   # Brown
ocean_display = (139,0,0)      # Deep Blue
score_color = (255,0,255)      # Magenta for total score

# ================== Collect Rescue Ratios ==================
rescue_ratios = []

# ================== Process Each Image ==================
images = sorted(os.listdir(input_folder))
for img_name in images:
    if not img_name.lower().endswith((".png", ".jpg", ".jpeg")):
        continue
    
    img_path = os.path.join(input_folder, img_name)
    img = cv.imread(img_path)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # Create land & ocean display masks
    land_mask = cv.inRange(hsv, lower_land, upper_land)
    ocean_mask = cv.inRange(hsv, lower_ocean, upper_ocean)
    display_img = img.copy()
    display_img[land_mask>0] = land_display
    display_img[ocean_mask>0] = ocean_display

    # Gray & threshold for contours
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

    # ================== Detect Casualties & Pads ==================
    casualties = []
    pads = []

    for contour in contours:
        area = cv.contourArea(contour)
        if area < 150:
            continue

        approx = cv.approxPolyDP(contour, 0.03*cv.arcLength(contour, True), True)
        corners = len(approx)
        peri = cv.arcLength(contour, True)
        circularity = 4*np.pi*area/(peri*peri)
        if corners == 3: shape="triangle"
        elif corners == 4: shape="square"
        elif 6<=corners<=8: shape="circle"
        else: shape="star"

        M = cv.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"]/M["m00"])
            cy = int(M["m01"]/M["m00"])
            hsv_value = hsv[cy,cx]
        else:
            cx, cy = 0,0
            hsv_value = np.array([0,0,0])

        # Color detection
        color = "unknown"
        for col, (low, high) in hsv_ranges.items():
            if (low <= hsv_value).all() and (hsv_value <= high).all():
                color = col
                break

        if shape=="circle":  # Rescue pad
            pads.append({"cx":cx, "cy":cy, "color":color, "capacity":rescuepad_capacity.get(color,0), "assigned":0})
        else:  # Casualty
            priority = casualty_priority.get(shape,0)
            total_score = priority * emergency_priority.get(color,0)
            casualties.append({"cx":cx,"cy":cy,"color":color,"priority":priority,"total_score":total_score})
            # Draw total score with outline
            cv.putText(display_img, str(total_score), (cx,cy), cv.FONT_HERSHEY_COMPLEX, 0.5, outline_color, 3)
            cv.putText(display_img, str(total_score), (cx,cy), cv.FONT_HERSHEY_COMPLEX, 0.5, score_color, 2)

    # ================== Assign casualties to pads ==================
    sum_best_scores = 0
    for c in casualties:
        best_score = -1
        best_pad_idx = -1
        for i,p in enumerate(pads):
            if p["assigned"] >= p["capacity"]:
                continue
            dx = c["cx"] - p["cx"]
            dy = c["cy"] - p["cy"]
            distance = np.sqrt(dx*dx + dy*dy)
            score = c["priority"] / (distance + 1)
            if score > best_score:
                best_score = score
                best_pad_idx = i
        if best_pad_idx != -1:
            c["pad"] = best_pad_idx
            pads[best_pad_idx]["assigned"] += 1
            sum_best_scores += best_score
        else:
            c["pad"] = None

    # ================== Draw lines from casualties to pads ==================
    final_img = display_img.copy()
    for c in casualties:
        if c["pad"] is not None:
            p = pads[c["pad"]]
            cv.line(final_img, (c["cx"],c["cy"]), (p["cx"],p["cy"]), (0,0,255),2)

    # ================== Save Output Images ==================
    cv.imwrite(os.path.join(output1_folder, img_name), display_img)
    cv.imwrite(os.path.join(output2_folder, img_name), final_img)

    # ================== Compute Rescue Ratio ==================
    if len(casualties) > 0:
        rescue_ratio = sum_best_scores / len(casualties)
    else:
        rescue_ratio = 0
    rescue_ratios.append((img_name, rescue_ratio))

# ================== Display All Final Outputs ==================
# Display casualties with scores first


sorted_rescue = sorted(rescue_ratios, key=lambda x: x[1], reverse=True)
print("Images sorted by rescue ratio (desc):")
for name, ratio in sorted_rescue:
    print(f"{name}: {ratio:.3f}")

for img_name in sorted(os.listdir(output1_folder)):
    img_path = os.path.join(output1_folder, img_name)
    img = cv.imread(img_path)
    cv.imshow("Casualties with Scores", img)
    key = cv.waitKey(0)  
    cv.destroyAllWindows()  


for img_name in sorted(os.listdir(output2_folder)):
    img_path = os.path.join(output2_folder, img_name)
    img = cv.imread(img_path)
    cv.imshow("Final Results", img)
    key = cv.waitKey(0)
    cv.destroyAllWindows()


cv.destroyAllWindows()

# ================== Delete temporary output images ==================
for f in os.listdir(output1_folder):
    os.remove(os.path.join(output1_folder, f))
for f in os.listdir(output2_folder):
    os.remove(os.path.join(output2_folder, f))
