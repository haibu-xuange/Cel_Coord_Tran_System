# frame.py

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import math
from celestial_coords import *

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

class CoordinateConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1f3d, stop:1 #1a3b5a);
                border-radius: 10px;
            }
            QGroupBox {
                background: rgba(16, 32, 64, 200);
                border: 2px solid #3a6da3;
                border-radius: 8px;
                color: #a0d0ff;
                font-size: 14px;
                padding: 15px;
                margin: 10px;
            }
            QSpinBox, QDoubleSpinBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid #3a6da3;
                border-radius: 4px;
                color: #a0f0ff;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a6da3, stop:1 #2a4d7a);
                border: 1px solid #4d8fcc;
                border-radius: 5px;
                color: #d0f0ff;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4d8fcc, stop:1 #3a6da3);
            }
                           
                /* 统一字体颜色设置 */
            QGroupBox, QLabel, QSpinBox, QDoubleSpinBox, QComboBox {
                color: #a0d0ff;  /* 与标题相同的冰蓝色 */
                font-family: 'Segoe UI';
            }

            /* 输入控件增强对比度 */
            QSpinBox, QDoubleSpinBox {
                background: rgba(16, 32, 64, 0.6);
                border: 1px solid #3a6da3;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
                selection-color: #ffffff;
                selection-background-color: #3a6da3;
            }

            /* 下拉菜单样式 */
            QComboBox {
                background: rgba(16, 32, 64, 0.6);
                border: 1px solid #3a6da3;
                padding: 3px;
                min-width: 80px;
            }

            /* 数字输入框文本特别处理 */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background: transparent;
            }

            /* 增加文字阴影提升可读性 */
            QGroupBox::title {
                color: #b0e0ff;
                font-size: 15px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
            }

            /* 输入标签强调效果 */
            QLabel {
                font-weight: semi-bold;
                color: #b0f0ff;  /* 比标题稍亮的青色 */
            }
        """)
        # 启用窗口透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 创建模糊背景
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(5, 5)
        self.centralWidget().setGraphicsEffect(self.shadow)        

        
    def init_ui(self):
        self.setWindowTitle('天球坐标系转换工具')
        self.setGeometry(100, 100, 1000, 600)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        self.setPalette(palette)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        # 左侧输入区（可伸缩）
        input_panel = QWidget()
        input_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        input_layout = QVBoxLayout(input_panel)

        # 输入面板
        input_panel = QWidget()
        input_layout = QVBoxLayout(input_panel)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(15)
        
        # 球面坐标系输入
        spherical_group = self.create_spherical_group()
        cartesian_group = self.create_cartesian_group()
        
        input_layout.addWidget(spherical_group)
        input_layout.addWidget(cartesian_group)
        input_layout.addStretch()
        
        # 3D可视化面板
        self.sphere_widget = CelestialSphereWidget()
        self.sphere_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_layout.addWidget(input_panel, 35)  # 35%宽度
        main_layout.addWidget(self.sphere_widget, 65)  # 65%宽度
        
        # 设置中心部件
        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        
    def create_spherical_group(self):
        group = QGroupBox("天球球面坐标系")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QFormLayout()
        layout.setContentsMargins(5, 15, 5, 10)
        layout.setVerticalSpacing(12)        
        
        # 赤经输入
        self.ra_h = self.create_spinbox(0, 23)
        self.ra_m = self.create_spinbox(0, 59)
        self.ra_s = self.create_double_spinbox(0, 59.999)
        ra_widget = self.create_horizontal_widget(
            [self.ra_h, "时", self.ra_m, "分", self.ra_s, "秒"])
        layout.addRow("赤经 (RA):", ra_widget)
        
        # 赤纬输入
        self.dec_sign = QComboBox()
        self.dec_sign.addItems(['+ (北纬)', '- (南纬)'])
        self.dec_deg = self.create_spinbox(0, 90)
        self.dec_min = self.create_spinbox(0, 59)
        self.dec_sec = self.create_double_spinbox(0, 59.999)
        dec_widget = self.create_horizontal_widget(
            [self.dec_sign, self.dec_deg, "度", self.dec_min, "分", self.dec_sec, "秒"])
        layout.addRow("赤纬 (Dec):", dec_widget)
        
        # 距离输入
        self.distance = self.create_double_spinbox(0, 1e9)
        layout.addRow("向径 (pc):", self.distance)
        
        # 转换按钮
        self.to_cartesian_btn = QPushButton('转换为天球空间直角坐标系 →')
        self.to_cartesian_btn.clicked.connect(self.to_cartesian)
        self.to_cartesian_btn.setStyleSheet(self.button_style("#4CAF50"))
        layout.addRow(self.to_cartesian_btn)
        
        group.setLayout(layout)
        return group
        
    def create_cartesian_group(self):
        group = QGroupBox("天球空间直角坐标系")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QFormLayout()
        
        self.x_input = self.create_double_spinbox(-1e9, 1e9)
        self.y_input = self.create_double_spinbox(-1e9, 1e9)
        self.z_input = self.create_double_spinbox(-1e9, 1e9)
        
        layout.addRow("X:", self.x_input)
        layout.addRow("Y:", self.y_input)
        layout.addRow("Z:", self.z_input)
        
        self.to_spherical_btn = QPushButton('← 转换为天球球面坐标系')
        self.to_spherical_btn.clicked.connect(self.to_spherical)
        self.to_spherical_btn.setStyleSheet(self.button_style("#2196F3"))
        layout.addRow(self.to_spherical_btn)
        
        group.setLayout(layout)
        return group
        
    def create_horizontal_widget(self, items):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        for item in items:
            if isinstance(item, str):
                layout.addWidget(QLabel(item))
            else:
                layout.addWidget(item)
        return widget
        
    def create_spinbox(self, min_val, max_val):
        sb = QSpinBox()
        sb.setRange(min_val, max_val)
        sb.setStyleSheet("QSpinBox { padding: 5px; background: white; }")
        sb.setMinimumWidth(70)
        return sb
        
    def create_double_spinbox(self, min_val, max_val):
        sb = QDoubleSpinBox()
        sb.setRange(min_val, max_val)
        sb.setDecimals(3)
        sb.setStyleSheet("QDoubleSpinBox { padding: 5px; background: white; }")
        sb.setMinimumWidth(90)
        return sb
        
    def button_style(self, color):
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {color}; opacity: 0.9; }}
        """
        
    def to_cartesian(self):
        try:
            ra_h = self.ra_h.value()
            ra_m = self.ra_m.value()
            ra_s = self.ra_s.value()
            sign = 1 if self.dec_sign.currentText() == '+ (北纬)' else -1
            dec_d = self.dec_deg.value()
            dec_m = self.dec_min.value()
            dec_s = self.dec_sec.value()
            distance = self.distance.value()

            ra_hours = hms_to_hours(ra_h, ra_m, ra_s)
            dec_deg = dms_to_deg(dec_d, dec_m, dec_s, sign)
            x, y, z = spherical_to_cartesian(ra_hours, dec_deg, distance)
            
            self.x_input.setValue(x)
            self.y_input.setValue(y)
            self.z_input.setValue(z)
            self.update_visualization(ra_hours, dec_deg, distance)
        except Exception as e:
            QMessageBox.warning(self, "转换错误", str(e))
        
    def to_spherical(self):
        try:
            x = self.x_input.value()
            y = self.y_input.value()
            z = self.z_input.value()

            ra_hours, dec_deg, r = cartesian_to_spherical(x, y, z)
            ra_h, ra_m, ra_s = hours_to_hms(ra_hours)
            dec_d, dec_m, dec_s, sign = deg_to_dms(dec_deg)

            self.ra_h.setValue(ra_h)
            self.ra_m.setValue(ra_m)
            self.ra_s.setValue(ra_s)
            self.dec_sign.setCurrentIndex(0 if sign == 1 else 1)
            self.dec_deg.setValue(dec_d)
            self.dec_min.setValue(dec_m)
            self.dec_sec.setValue(dec_s)
            self.distance.setValue(r)
            self.update_visualization(ra_hours, dec_deg, r)
        except Exception as e:
            QMessageBox.warning(self, "转换错误", str(e))
        
    def update_visualization(self, ra_hours, dec_deg, distance):
        ra_deg = ra_hours * 15
        self.sphere_widget.set_points(ra_deg, dec_deg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoordinateConverter()
    ex.show()
    sys.exit(app.exec_())