import json

class EditablePlatform:
    """
    플랫폼 데이터 객체: 위치, 크기 및 색상 관리 (순수 데이터)
    """
    def __init__(self, x, y, width, height, color=(0, 200, 0), ptype="default"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.ptype = ptype

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": list(self.color),
            "ptype": self.ptype
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['x'], data['y'],
            data['width'], data['height'],
            tuple(data.get('color', (0,200,0))),
            data.get('ptype', 'default')
        )

class MapData:
    """
    맵 전체 데이터를 관리: 플랫폼 목록, 저장/불러오기 기능
    """
    def __init__(self):
        self.platforms = []

    def add_platform(self, platform: EditablePlatform):
        self.platforms.append(platform)

    def remove_platform(self, platform: EditablePlatform):
        self.platforms.remove(platform)

    def clear(self):
        self.platforms.clear()

    def save(self, filename="map.json"):
        import json
        data = [p.to_dict() for p in self.platforms]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load(self, filename="map.json"):
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        self.clear()
        for item in data:
            self.add_platform(EditablePlatform.from_dict(item))

    def get_platforms(self):
        return list(self.platforms)

def export_platforms(platforms):
    return [p.to_dict() for p in platforms]

def load_platforms(filename="map.json"):
    import json
    with open(filename, 'r') as f:
        data = json.load(f)
    return [EditablePlatform.from_dict(item) for item in data]