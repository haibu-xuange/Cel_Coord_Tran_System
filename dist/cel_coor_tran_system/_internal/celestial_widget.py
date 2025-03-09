# celestial_widget.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QVector3D, QMatrix4x4, QFont
from PyQt5.QtCore import Qt, QPoint
import math

class CelestialSphereWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_point = None
        self.target_point = None
        # 启用窗口透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置窗口大小
        self.setMinimumSize(600, 500)
        # 初始化旋转角度：北极朝上，赤道水平
        self.x_rotation = 0   # 绕X轴的旋转（俯仰角）
        self.y_rotation = 0   # 绕Y轴的旋转（自转角度）
        self.dragging = False
        self.last_pos = QPoint()

    def set_points(self, src_ra, src_dec, tgt_ra=None, tgt_dec=None):
        self.source_point = self.spherical_to_cartesian(src_ra, src_dec)
        self.target_point = self.spherical_to_cartesian(tgt_ra, tgt_dec) if tgt_ra else None
        self.update()

    def spherical_to_cartesian(self, ra, dec, radius=1.0):
        ra_rad = math.radians(ra)
        dec_rad = math.radians(dec)
        x = radius * math.cos(dec_rad) * math.cos(ra_rad)
        y = radius * math.cos(dec_rad) * math.sin(ra_rad)
        z = radius * math.sin(dec_rad)
        return QVector3D(x, y, z)

    def project_point(self, point):
        view = QMatrix4x4()
        view.perspective(30, self.width()/self.height(), 0.1, 100.0)
        view.translate(0, 0, -5)
        
        # 先绕Y轴旋转（自转），再绕X轴旋转（俯仰）
        view.rotate(self.y_rotation, 0, 1, 0)  # Y轴旋转
        view.rotate(self.x_rotation, 1, 0, 0)  # X轴旋转
        
        projected = view.map(point)
        if projected.z() <= 0:
            return None
            
        x = (projected.x() + 1) * self.width() / 2
        y = (1 - projected.y()) * self.height() / 2
        return QPoint(int(x), int(y))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(25, 30, 45))
        
        # 绘制网格系统
        self.draw_grid(painter)
        
        # 绘制坐标点
        if self.source_point:
            self.draw_point(painter, self.source_point, Qt.red)
        if self.target_point:
            self.draw_point(painter, self.target_point, QColor(0, 255, 255))

        # 添加标注
        self.draw_labels(painter)

    def draw_grid(self, painter):
        # 绘制特殊经线（中央子午线）
        self.draw_longitude(painter, 0, QColor(0, 255, 0), 2)  # 绿色
        self.draw_longitude(painter, 180, QColor(0, 255, 0), 2) # 绿色

        # 绘制其他经线
        for ra in range(30, 360, 30):
            self.draw_longitude(painter, ra, QColor(80, 100, 120), 1)

        # 绘制特殊纬线（赤道）
        self.draw_latitude(painter, 0, QColor(0, 255, 255), 3)  # 青色
        
        # 绘制其他纬线
        for dec in list(range(-60, 0, 30)) + list(range(30, 90, 30)):
            self.draw_latitude(painter, dec, QColor(100, 150, 200), 1)

        # 绘制坐标系轴
        self.draw_coordinate_axes(painter)

    def draw_coordinate_axes(self, painter):
        # 定义坐标轴参数
        axis_length = 1.2  # 轴长度
        axis_width = 3      # 线宽
                
        # 绘制X轴（春分点方向，红色）
        x_end = self.spherical_to_cartesian(0, 0, axis_length)
        self.draw_axis(painter, QVector3D(0, 0, 0), x_end, Qt.red, "X轴", axis_width)
        
        # 绘制Y轴（右手系方向，绿色）
        y_end = self.spherical_to_cartesian(90, 0, axis_length)  # 赤经6小时=90度
        self.draw_axis(painter, QVector3D(0, 0, 0), y_end, Qt.green, "Y轴", axis_width)
        
        # 绘制Z轴（天北极方向，蓝色）
        z_end = self.spherical_to_cartesian(0, 90, axis_length)
        self.draw_axis(painter, QVector3D(0, 0, 0), z_end, Qt.blue, "Z轴", axis_width)

    def draw_axis(self, painter, start, end, color, label, width=2):
        # 绘制轴线
        pen = QPen(color)
        pen.setWidth(width)
        painter.setPen(pen)
        
        start_p = self.project_point(start)
        end_p = self.project_point(end)
        if start_p and end_p:
            # 计算二维投影后的实际方向
            dx = end_p.x() - start_p.x()
            dy = end_p.y() - start_p.y()
            angle = math.atan2(dy, dx)
            
            # 绘制箭头
            arrow_size = 12
            p1 = end_p + QPoint(
                int(arrow_size * math.cos(angle + math.pi/6)),
                int(arrow_size * math.sin(angle + math.pi/6))
            )
            p2 = end_p + QPoint(
                int(arrow_size * math.cos(angle - math.pi/6)),
                int(arrow_size * math.sin(angle - math.pi/6))
            )
            
            # 绘制带箭头的线（从地心指向外）
            painter.drawLine(start_p, end_p)
            painter.drawLine(end_p, p1)
            painter.drawLine(end_p, p2)
            
            # 标签位置调整
            label_offset = QPoint(
                int(20 * math.cos(angle)),
                int(20 * math.sin(angle)))
            painter.drawText(end_p + label_offset, label)

    def draw_labels(self, painter):
        # 设置字体样式
        font = QFont('Arial', 10)
        painter.setFont(font)
        
        # 赤道标注（多个位置）
        for ra in [180]:
            pos = self.project_point(self.spherical_to_cartesian(ra, 0))
            if pos:
                painter.setPen(QColor(0, 255, 255))
                painter.drawText(pos.x()+5, pos.y()-5, "赤道")

        # 极地标注
        north_pos = self.project_point(self.spherical_to_cartesian(0, 85))
        if north_pos:
            painter.setPen(Qt.white)
            painter.drawText(north_pos, "北极")
        
        south_pos = self.project_point(self.spherical_to_cartesian(0, -85))
        if south_pos:
            painter.setPen(Qt.white)
            painter.drawText(south_pos.x(), south_pos.y() + 20, "南极")
        
        # 中央子午线标注（多个纬度）
        for dec in [-45]:
            pos = self.project_point(self.spherical_to_cartesian(0, dec))
            if pos:
                painter.setPen(QColor(0, 255, 0))
                painter.drawText(pos.x()+5, pos.y()+5, "中央子午线")

    def draw_longitude(self, painter, ra, color, width=1):
        pen = QPen(color)
        pen.setWidth(width)
        painter.setPen(pen)
        
        points = []
        for dec in range(-90, 91, 2):
            point = self.spherical_to_cartesian(ra, dec)
            screen_point = self.project_point(point)
            if screen_point:
                points.append(screen_point)
        if points:
            painter.drawPolyline(*points)

    def draw_latitude(self, painter, dec, color, width=1):
        pen = QPen(color)
        pen.setWidth(width)
        painter.setPen(pen)
        
        points = []
        for ra in range(0, 361, 3):
            point = self.spherical_to_cartesian(ra, dec)
            screen_point = self.project_point(point)
            if screen_point:
                points.append(screen_point)
        if points:
            painter.drawPolyline(*points)

    def draw_point(self, painter, point, color):
        screen_point = self.project_point(point)
        if screen_point:
            painter.setPen(QPen(color, 2))
            painter.setBrush(color)
            painter.drawEllipse(screen_point, 6, 6)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.last_pos
            
            # 水平拖动：绕Y轴旋转（地轴自转）
            self.y_rotation += delta.x() * 0.5
            
            # 垂直拖动：绕X轴旋转（视角俯仰）
            self.x_rotation -= delta.y() * 0.5
            
            # 限制俯仰角度在[-90, 90]范围内
            self.x_rotation = max(-90, min(90, self.x_rotation))
            
            self.last_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False