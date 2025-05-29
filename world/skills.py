class SkillHandler:
    def __init__(self, obj):
        self.obj = obj

    def _load(self):
        self.skill_data = self.obj.attributes.get(
            "skill_data", default={}, category="skills")

    def _save(self):
        self.obj.attributes.add(
            "skill_data", self.skill_data, category="skills")
        self._load()
