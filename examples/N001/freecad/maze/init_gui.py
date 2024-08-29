# -*- coding: utf-8 -*-
from freecad import app, gui
import os

ROOTPATH = os.path.join(os.path.dirname(__file__))
ICONPATH = os.path.join(ROOTPATH, "resources/icons")
APPICON = os.path.join(ICONPATH, "maze.svg")


class MazeWorkbench(gui.Workbench):
    '''
    迷宫插件，主要用于生成迷宫的三维模型
    '''
    # 插件名称
    MenuText = "迷宫"
    # 插件提示，在参数设置的工作台列表中显示
    ToolTip = "这是一个迷宫工作台"
    # 插件图标
    Icon = APPICON

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        '''
        初始化时执行，可以在这里初始化菜单、工具栏
        '''
        app.Console.PrintMessage("迷宫工作台已加载。\n")
        # 向FreeCAD添加指令
        gui.addCommand("CreateMaze", CreateMaze())
        # 向当前工作台添加一个命令按钮
        self.appendToolbar("Maze", ["CreateMaze"])

    def Activated(self):
        '''
        切换到（变为活动）当前工作台时执行
        '''
        pass

    def Deactivated(self):
        '''
        当前工作台从活动变为不活动时执行
        '''
        pass


class CreateMaze():
    def GetResources(self):
        return {"Pixmap": APPICON,
                "MenuText": "创建迷宫",
                "ToolTip": "创建一个3D迷宫"}

    def Activated(self):
        app.Console.PrintMessage("迷宫已创建完成\n")
        return

    def IsActive(self):
        '''
        判断当前命令是否可用
        '''
        return True


gui.addWorkbench(MazeWorkbench())
