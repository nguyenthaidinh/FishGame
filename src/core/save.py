# src/core/save.py
import json, os
from datetime import datetime

class SaveManager:
    def __init__(self, path=None):
        # root project (nơi có main.py)
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)

        self.path = path or os.path.join(data_dir, "save.json")

        self.data = {
            "coins": 0,
            "unlocked_maps": [1],
            "unlocked_fish": ["fish01"],
            "selected_fish_p1": "fish01",
            "selected_fish_p2": "fish02",
            "highscores": {"1": 0, "2": 0, "3": 0},
            "history": [],
            "settings": {
                "music": 0.6,
                "sfx": 0.7,
                "fullscreen": False
            }
        }

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                if isinstance(obj, dict):
                    self.data.update(obj)
            except Exception as e:
                print("Save load error:", e)

        self.sync_unlocked_fish_by_progress()
        return self.data

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # ================= MAP =================
    def is_unlocked_map(self, map_id: int) -> bool:
        return int(map_id) in self.data.get("unlocked_maps", [1])

    def unlock_map(self, map_id: int):
        map_id = int(map_id)
        self.data.setdefault("unlocked_maps", [1])
        if map_id not in self.data["unlocked_maps"]:
            self.data["unlocked_maps"].append(map_id)

    # ================= SCORE =================
    def update_highscore(self, map_id: int, points: int):
        hs = self.data.setdefault("highscores", {"1": 0, "2": 0, "3": 0})
        k = str(int(map_id))
        hs[k] = max(int(hs.get(k, 0)), int(points))

    # ================= HISTORY =================
    def add_history(self, mode: int, map_id: int, points: int, time_alive: float, result: str):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data.setdefault("history", [])
        self.data["history"].insert(0, {
            "time": t,
            "mode": int(mode),
            "map_id": int(map_id),
            "points": int(points),
            "time_alive": float(time_alive),
            "result": str(result)
        })
        self.data["history"] = self.data["history"][:50]

    # ================= FISH UNLOCK =================
    def progress_max_map(self) -> int:
        return max([int(x) for x in self.data.get("unlocked_maps", [1])] or [1])

    def allowed_fish_count_by_progress(self) -> int:
        m = self.progress_max_map()
        if m <= 1: return 3
        if m == 2: return 8
        return 12

    def sync_unlocked_fish_by_progress(self):
        allowed = self.allowed_fish_count_by_progress()
        target = [f"fish{str(i).zfill(2)}" for i in range(1, allowed + 1)]

        cur = set(self.data.get("unlocked_fish", ["fish01"]))
        cur.update(target)
        self.data["unlocked_fish"] = sorted(cur)

        if self.data["selected_fish_p1"] not in self.data["unlocked_fish"]:
            self.data["selected_fish_p1"] = self.data["unlocked_fish"][0]
        if self.data["selected_fish_p2"] not in self.data["unlocked_fish"]:
            self.data["selected_fish_p2"] = self.data["unlocked_fish"][0]

    def is_unlocked_fish(self, fish_id: str) -> bool:
        return fish_id in self.data.get("unlocked_fish", ["fish01"])
