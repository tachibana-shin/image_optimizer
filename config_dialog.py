from qt.core import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox
from calibre.utils.config import JSONConfig

# プリファレンスの初期化（設定を共有するためにmain.pyと同じ）
prefs = JSONConfig('plugins/image_optimizer')

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Optimization Config")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        
        # prefs から保存された値を読み取る
        self.size_input = QLineEdit(self)
        self.size_input.setText(prefs['size'])
        self.size_input.setPlaceholderText("Example: 1080")
        
        self.quality_input = QLineEdit(self)
        self.quality_input.setText(prefs['quality'])
        self.quality_input.setPlaceholderText("Example: 85")
        
        self.format_input = QComboBox(self)
        self.format_input.addItems([
            "Original",  # 元のフォーマットを維持
            "JPEG",      # 写真に最適
            "PNG",       # グラフィック、ロゴに最適
            "WebP",      # 優れた圧縮 (Epub 3)
            "AVIF",      # 現在最高の圧縮 (pillow-avif-pluginが必要)
            "BMP",       # 非圧縮
            "TIFF",      # 高品質
            "GIF",       # アニメーション/8ビット
            "QOI",       # 新しい超高速フォーマット
            "TGA",       # ゲームグラフィック
            "ICO"        # アイコン
        ])

        self.keep_time_import_input = QCheckBox(self)
        self.keep_time_import_input.setChecked(prefs['keep_time_import'])
        
        # 選択されたフォーマットを復元
        index = self.format_input.findText(prefs['format'])
        if index >= 0:
            self.format_input.setCurrentIndex(index)

        layout.addWidget(QLabel("Max Size (px):"))
        layout.addWidget(self.size_input)
        layout.addWidget(QLabel("Compression Quality (1-100):"))
        layout.addWidget(self.quality_input)
        layout.addWidget(QLabel("Format Conversion:"))
        layout.addWidget(self.format_input)
        layout.addWidget(QLabel("Keep Import Time:"))
        layout.addWidget(self.keep_time_import_input)
        
        btn = QPushButton("Start", self)
        btn.clicked.connect(self.save_and_accept)
        layout.addWidget(btn)

    def save_and_accept(self):
        # ダイアログを閉じる前に値を prefs に保存
        prefs['size'] = self.size_input.text().strip()
        prefs['quality'] = self.quality_input.text().strip()
        prefs['format'] = self.format_input.currentText()
        prefs['keep_time_import'] = self.keep_time_import_input.isChecked()
        self.accept()

    def get_values(self):
        # Job ロジックに合わせて結果を返す
        return {
            'size': prefs['size'],
            'quality': prefs['quality'],
            'format': prefs['format'],
            'keep_time_import': prefs['keep_time_import']
        }
