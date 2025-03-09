# styles.py
MAIN_STYLESHEET = """
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
"""