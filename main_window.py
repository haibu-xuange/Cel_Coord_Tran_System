# main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
                            QPushButton, QLabel, QComboBox, QMessageBox,
                            QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
from celestial_coords import *
from celestial_widget import CelestialSphereWidget
from styles import MAIN_STYLESHEET

class CoordinateConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setStyleSheet(MAIN_STYLESHEET)
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