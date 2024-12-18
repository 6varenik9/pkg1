import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import colorsys


class ColorConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.window()
        layout = QVBoxLayout()

        self.rgb_input = self.fields("RGB", 3, layout, self.updateFromRGBInput)
        self.cmyk_input = self.fields("CMYK", 4, layout, self.updateFromCMYKInput)
        self.hls_input = self.fields("HLS", 3, layout, self.updateFromHLSInput)

        self.rgb_sliders = self.sliders("RGB Sliders", ["red", "green", "blue"], layout, 'RGB')
        self.cmyk_sliders = self.sliders("CMYK Sliders", ["cyan", "magenta", "yellow", "black"], layout, 'CMYK')
        self.hls_sliders = self.sliders("HLS Sliders", ["hue", "lightness", "saturation"], layout, 'HLS')

        self.color_display = self.colorDisp()
        layout.addWidget(self.color_display)

        self.setLayout(layout)

    def window(self):
        self.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF;")
        self.setWindowTitle('Цветовой конвертер (RGB ↔️ CMYK ↔️ HLS)')
        self.setGeometry(100, 100, 1000, 700)

    def fields(self, label_text, count, layout, update_function):
        hbox = QHBoxLayout()
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 18px;")
        hbox.addWidget(label)
        input_fields = []
        for _ in range(count):
            input_field = QLineEdit(self)
            input_field.setMinimumSize(80, 30)
            input_field.setStyleSheet("font-size: 16px; color: #FFFFFF;")
            input_field.editingFinished.connect(update_function)
            hbox.addWidget(input_field)
            input_fields.append(input_field)
        layout.addLayout(hbox)
        return input_fields

    def sliders(self, label_text, color_labels, layout, slider_type):
        vbox = QVBoxLayout()
        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        vbox.addWidget(label)

        sliders = []
        for i, color_label in enumerate(color_labels):
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 255 if slider_type == 'RGB' else 100)
            slider.valueChanged.connect(self.update(slider_type))
            self.sliderStyle(slider, color_label)
            sliders.append(slider)

            hslider_box = QHBoxLayout()
            slider_label = QLabel(color_label.capitalize(), self)
            slider_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
            hslider_box.addWidget(slider_label)
            hslider_box.addWidget(slider)
            vbox.addLayout(hslider_box)
        
        layout.addLayout(vbox)
        return sliders

    def sliderStyle(self, slider, color):
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #999999;
                height: 8px;
                border-radius: 25px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 white, stop: 1 {color});
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                border: 1px solid #5c5c5c;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}
        """)

    def colorDisp(self):
        color_display = QFrame(self)
        color_display.setFrameShape(QFrame.StyledPanel)
        color_display.setMinimumHeight(100)
        color_display.setStyleSheet("background-color: #FFFFFF; border-radius: 20px;")
        return color_display

    def update(self, slider_type):
        if slider_type == 'RGB':
            return self.updateRGB
        elif slider_type == 'CMYK':
            return self.updateCMYK
        elif slider_type == 'HLS':
            return self.updateHLS

    def updateRGB(self):
        r, g, b = [slider.value() for slider in self.rgb_sliders]
        self.updateColor(r, g, b)
        self.updateCMYKFields(r, g, b)

    def updateCMYK(self):
        c, m, y, k = [slider.value() / 100.0 for slider in self.cmyk_sliders]
        r, g, b = [int(255 * (1 - val) * (1 - k)) for val in (c, m, y)]
        self.updateColor(r, g, b)
        self.updateCMYKFields(r, g, b)

    def updateHLS(self):
        h = self.hls_sliders[0].value() / 360.0
        l = self.hls_sliders[1].value() / 100.0
        s = self.hls_sliders[2].value() / 100.0
        r, g, b = [int(c * 255) for c in colorsys.hls_to_rgb(h, l, s)]
        self.updateColor(r, g, b)
        self.updateCMYKFields(r, g, b)

    def updateColor(self, r, g, b):
        color = QColor(r, g, b)
        self.color_display.setStyleSheet(f"background-color: {color.name()}; border-radius: 20px;")
        for i, val in enumerate((r, g, b)):
            self.rgb_input[i].setText(str(val))
            self.rgb_sliders[i].blockSignals(True)
            self.rgb_sliders[i].setValue(val)
            self.rgb_sliders[i].blockSignals(False)

    def updateCMYKFields(self, r, g, b):
        cmyk = self.RGBToCMYK(r, g, b)
        for i, val in enumerate(cmyk):
            self.cmyk_input[i].setText(f"{val:.2f}")
            self.cmyk_sliders[i].blockSignals(True)
            self.cmyk_sliders[i].setValue(int(val * 100))
            self.cmyk_sliders[i].blockSignals(False)

        hls = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        for i, val in enumerate((hls[0] * 360, hls[1] * 100, hls[2] * 100)):
            self.hls_input[i].setText(f"{val:.2f}")
            self.hls_sliders[i].blockSignals(True)
            self.hls_sliders[i].setValue(int(val))
            self.hls_sliders[i].blockSignals(False)

    def RGBToCMYK(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        k = 1 - max(r, g, b)
        if k == 1:
            return 0, 0, 0, 1
        return [(1 - x - k) / (1 - k) for x in (r, g, b)] + [k]

    def updateFromRGBInput(self):
        try:
            r, g, b = [int(input_field.text()) for input_field in self.rgb_input]
            self.updateColor(r, g, b)
            self.updateCMYKFields(r, g, b)
        except ValueError:
            pass

    def updateFromCMYKInput(self):
        try:
            c, m, y, k = [float(input_field.text()) for input_field in self.cmyk_input]
            r, g, b = [int(255 * (1 - val) * (1 - k)) for val in (c, m, y)]
            self.updateColor(r, g, b)
            self.updateCMYKFields(r, g, b)
        except ValueError:
            pass

    def updateFromHLSInput(self):
        try:
            h = float(self.hls_input[0].text()) / 360.0
            l = float(self.hls_input[1].text()) / 100.0
            s = float(self.hls_input[2].text()) / 100.0
            r, g, b = [int(c * 255) for c in colorsys.hls_to_rgb(h, l, s)]
            self.updateColor(r, g, b)
            self.updateCMYKFields(r, g, b)
        except ValueError:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColorConverter()
    ex.show()
    sys.exit(app.exec_())
