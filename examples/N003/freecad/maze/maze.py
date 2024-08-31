import Part
from random import randint
from freecad import app
from freecad.maze import APPICON

class Maze:
    inited = False
    cells = 10
    rows = 10
    edgeList = []
    visited = []
    obj = None

    def __init__(self, obj):
        '''对象实始化，可以添加一些属性'''
        obj.addProperty("App::PropertyLength", "WallThickness", "Maze","墙厚度")
        obj.addProperty("App::PropertyLength", "WallHeight","Maze", "墙高度")
        obj.addProperty("App::PropertyLength", "CellSize", "Maze", "迷宫间距")

        obj.addProperty("App::PropertyInteger", "Rows", "Maze", "行数量")
        obj.addProperty("App::PropertyInteger", "Cells", "Maze", "列数量")

        obj.addProperty("App::PropertyBool", "ShowExit", "Maze", "显示入出口")

        # 保存迷宫路径，隐藏属性
        obj.addProperty("App::PropertyString", "edgeList", "Maze",
                        "edgeList", 0, False, True)

        obj.WallThickness = 2.0
        obj.WallHeight = 10.0
        obj.CellSize = 20.0
        obj.Rows = self.rows
        obj.Cells = self.cells
        obj.ShowExit = False
        obj.Proxy = self
        self.obj = obj
        self.type = 'Maze'
        self.inited = True
        self.reload(obj)

        self.make_attachable(obj)

    def make_attachable(self, obj):
        if int(app.Version()[1]) >= 19:
            obj.addExtension("Part::AttachExtensionPython")
        else:
            obj.addExtension("Part::AttachExtensionPython", obj)

        obj.setEditorMode("Placement", 0)

    def execute(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        if not hasattr(fp, "positionBySupport"):
            self.make_attachable(fp)

        fp.positionBySupport()
        maze_shape = self.generate_maze_shape(fp)
        if maze_shape == None:
            return

        if hasattr(fp, "BaseFeature") and fp.BaseFeature != None:
            maze_shape.Placement = (
                fp.Placement
            )
            result_shape = fp.BaseFeature.Shape.fuse(maze_shape)
            result_shape.transformShape(
                fp.Placement.inverse().toMatrix(), True
            )
            fp.Shape = result_shape
        else:
            fp.Shape = maze_shape

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        if str(prop) in ['Rows', 'Cells', 'ShowExit']:
            self.cells = fp.Cells if fp.Cells > 0 else self.cells
            self.rows = fp.Rows if fp.Rows > 0 else self.rows
            self.reload(fp)

        if str(prop) == 'Shape':
            self.type = 'Maze'
            self.inited = True

    def generate_maze_shape(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        walls = self.drawWalls(fp)
        if walls == None:
            return None
        # 将所有墙合并为一个复合形状
        maze_shape = Part.makeCompound(walls)
        return maze_shape

    def reload(self, obj):
        if self.inited == False:
            return
        
        self.edgeList = self.initEdgeList()
        self.visited = self.initVisitedList()
        self.DFS(0, 0, self.edgeList, self.visited)
        if obj.ShowExit:
            self.edgeList.remove((0, 0, 0, 1))
            self.edgeList.remove(
                (self.cells, self.rows-1, self.cells, self.rows))

        obj.edgeList = str(self.edgeList)

    def initVisitedList(self):
        visited = []
        for y in range(self.rows):
            line = []
            for x in range(self.cells):
                line.append(False)
            visited.append(line)
        return visited

    def get_edges(self, x, y):
        result = []
        result.append((x, y, x, y+1))
        result.append((x+1, y, x+1, y+1))
        result.append((x, y, x+1, y))
        result.append((x, y+1, x+1, y+1))

        return result

    def getCommonEdge(self, cell1_x, cell1_y, cell2_x, cell2_y):
        edges1 = self.get_edges(cell1_x, cell1_y)
        edges2 = set(self.get_edges(cell2_x, cell2_y))
        for edge in edges1:
            if edge in edges2:
                return edge
        return None

    def initEdgeList(self):
        edges = set()
        for x in range(self.cells):
            for y in range(self.rows):
                cellEdges = self.get_edges(x, y)
                for edge in cellEdges:
                    edges.add(edge)
        return edges

    def isValidPosition(self, x, y):
        if x < 0 or x >= self.cells:
            return False
        elif y < 0 or y >= self.rows:
            return False
        else:
            return True

    def shuffle(self, dX, dY):
        for t in range(4):
            i = randint(0, 3)
            j = randint(0, 3)
            dX[i], dX[j] = dX[j], dX[i]
            dY[i], dY[j] = dY[j], dY[i]

    def DFS(self, X, Y, edgeList, visited):
        dX = [0,  0, -1, 1]
        dY = [-1, 1, 0,  0]
        self.shuffle(dX, dY)
        for i in range(len(dX)):
            nextX = X + dX[i]
            nextY = Y + dY[i]
            if self.isValidPosition(nextX, nextY):
                if not visited[nextY][nextX]:
                    visited[nextY][nextX] = True
                    commonEdge = self.getCommonEdge(X, Y, nextX, nextY)
                    if commonEdge in edgeList:
                        edgeList.remove(commonEdge)
                    self.DFS(nextX, nextY, edgeList, visited)

    def drawWalls(self, fp):
        walls = []

        cellSize = fp.CellSize
        wallHeight = fp.WallHeight
        wallThickness = fp.WallThickness

        edgeList = self.edgeList if self.edgeList != [] else eval(fp.edgeList)

        if cellSize <= 0 or wallHeight <= 0 or wallThickness <= 0 or edgeList == []:
            return None

        for edge in edgeList:
            # 位置信息
            vector = app.Vector(edge[0]*cellSize, edge[1]*cellSize, 0)
            # 竖线
            if edge[0] == edge[2]:
                # 创建墙的几何形状
                wall = Part.makeBox(wallThickness, cellSize +
                                    wallThickness, wallHeight)
            else:
                wall = Part.makeBox(cellSize+wallThickness,
                                    wallThickness, wallHeight)

            # 将墙移动到指定的位置
            wall.translate(vector)
            walls.append(wall)
        # 添加地面
        ground = Part.makeBox(self.cells*cellSize+wallThickness,
                              self.rows*cellSize+wallThickness, wallThickness)
        walls.append(ground)
        return walls
    
    def loads(self, state):
        pass

    def dumps(self):
        pass


class ViewProviderMaze:
    def __init__(self, obj, icon_fn=None):
        obj.Proxy = self
        self._check_attr()
        self.icon_fn = icon_fn or APPICON

    def _check_attr(self):
        if not hasattr(self, "icon_fn"):
            setattr(
                self,
                "icon_fn",
                APPICON,
            )

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        self._check_attr()
        return self.icon_fn

    def dumps(self):
        self._check_attr()
        return {"icon_fn": self.icon_fn}

    def loads(self, state):
        if state and "icon_fn" in state:
            self.icon_fn = state["icon_fn"]