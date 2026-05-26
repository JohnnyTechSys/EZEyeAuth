
import cv2
import iris
import pickle
import os

class Authenticator():
    def __init__(self, storage_dir="."):
        self.pipeline = iris.IRISPipeline()
        self.matcher = iris.HammingDistanceMatcher()
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_path(self, user_id, side):
        return os.path.join(self.storage_dir, f"{user_id}_{side}_template.iris")

    def _preprocess_image(self, img):
        if img is None:
            return None
        h, w = img.shape[:2]
        target_w = 640
        target_h = int(h * (target_w / w))
        return cv2.resize(img, (target_w, target_h))

    def enroll(self, origin_left, origin_right, user_id="default"):
        if not isinstance(origin_left, str) or not isinstance(origin_right, str):
            raise ValueError("Origin must be a string path!")
        if not os.path.exists(origin_left) or not os.path.exists(origin_right):
            raise FileNotFoundError("Origin not found!")

        img_left_pixels = cv2.imread(origin_left, cv2.IMREAD_GRAYSCALE)
        img_right_pixels = cv2.imread(origin_right, cv2.IMREAD_GRAYSCALE)

        img_left_pixels = self._preprocess_image(img_left_pixels)
        img_right_pixels = self._preprocess_image(img_right_pixels)

        if img_left_pixels is None or img_right_pixels is None:
            raise ValueError("Failed to read one or both images. Ensure they are valid image files.")

        left_template = self.pipeline.run(img_data=img_left_pixels, eye_side="left")
        right_template = self.pipeline.run(img_data=img_right_pixels, eye_side="right")

        if left_template.get("error") is not None or right_template.get("error") is not None:
            raise ValueError("Failed to detect iris in one or both images.")

        with open(self._get_path(user_id, "left"), "wb") as f:
            pickle.dump(left_template, f)
        with open(self._get_path(user_id, "right"), "wb") as f:
            pickle.dump(right_template, f)

        return True

    def auth(self, left_unknown, right_unknown, user_id="default"):
        if not self.is_enrolled(user_id):
            raise ValueError(f"User {user_id} is not enrolled.")

        with open(self._get_path(user_id, "left"), "rb") as f:
            left_known = pickle.load(f)
        with open(self._get_path(user_id, "right"), "rb") as f:
            right_known = pickle.load(f)

        img_left_pixels = cv2.imread(left_unknown, cv2.IMREAD_GRAYSCALE)
        img_right_pixels = cv2.imread(right_unknown, cv2.IMREAD_GRAYSCALE)

        img_left_pixels = self._preprocess_image(img_left_pixels)
        img_right_pixels = self._preprocess_image(img_right_pixels)

        if img_left_pixels is None or img_right_pixels is None:
            return False

        left_res = self.pipeline.run(img_data=img_left_pixels, eye_side="left")
        right_res = self.pipeline.run(img_data=img_right_pixels, eye_side="right")

        if left_res.get("error") is not None or right_res.get("error") is not None:
            return False

        def dict_to_template(d):
            return iris.IrisTemplate(iris_codes=[d["iris_codes"]], mask_codes=[d["mask_codes"]])

        right_dist = self.matcher.run(dict_to_template(right_known["iris_template"]), dict_to_template(right_res["iris_template"]))
        left_dist = self.matcher.run(dict_to_template(left_known["iris_template"]), dict_to_template(left_res["iris_template"]))

        if left_dist < 0.32 and right_dist < 0.32:
            return True # Irises match
        else:
            return False # Irises don't match

    def is_enrolled(self, user_id="default"):
        return os.path.exists(self._get_path(user_id, "left")) and os.path.exists(self._get_path(user_id, "right"))

    def clear(self, user_id="default"):
        if os.path.exists(self._get_path(user_id, "left")):
            os.remove(self._get_path(user_id, "left"))
        if os.path.exists(self._get_path(user_id, "right")):
            os.remove(self._get_path(user_id, "right"))


