import Part


class Maze:
    def __init__(self, obj):
        '''对象实始化，可以添加一些属性'''
        obj.addProperty("App::PropertyLength", "Length",
                        "Maze", "长").Length = 10.0
        obj.addProperty("App::PropertyLength", "Width",
                        "Maze", "宽").Width = 10.0
        obj.addProperty("App::PropertyLength", "Height",
                        "Maze", "高").Height = 10.0
        obj.Proxy = self

    def execute(self, fp):
        '''在调用重新计算时会执行该方法'''
        # 创建一个立方体
        box = Part.makeBox(fp.Length, fp.Width, fp.Height)
        fp.Shape = box
