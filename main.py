import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QListWidget,
                             QTextEdit, QPushButton, QHBoxLayout, QLabel, QMessageBox, QDialog)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QTextCursor, QTextCharFormat, QColor

class TextSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("文本查找和替换工具")
        self.setGeometry(100, 100, 800, 600)

        # 搜索关键字输入框
        self.search_label = QLabel("请输入要查找的关键字:")
        self.search_input = QLineEdit()

        # 替换关键字输入框
        self.replace_label = QLabel("请输入替换内容:")
        self.replace_input = QLineEdit()

        # 显示拖放区域
        self.drop_label = QLabel("将文件夹拖放到此处")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet("border: 2px dashed gray; padding: 20px;")
        self.drop_label.setAcceptDrops(True)

        # 结果列表框
        self.result_list = QListWidget()

        # 文件预览框
        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)

        # 搜索按钮
        self.search_button = QPushButton("开始查找")
        self.search_button.clicked.connect(self.search_files)

        # "下一个匹配项" 按钮
        self.next_match_button = QPushButton("下一个匹配项")
        self.next_match_button.clicked.connect(self.go_to_next_match)

        # "替换当前文件所有匹配项" 按钮
        self.replace_current_button = QPushButton("替换当前文件所有匹配项")
        self.replace_current_button.clicked.connect(self.replace_current_file)

        # "替换所有文件匹配项" 按钮
        self.replace_all_button = QPushButton("替换所有文件匹配项")
        self.replace_all_button.clicked.connect(self.replace_all_files)

        # 布局设置
        layout = QVBoxLayout()
        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.replace_label)
        layout.addWidget(self.replace_input)
        layout.addWidget(self.drop_label)
        layout.addWidget(self.search_button)
        layout.addWidget(self.result_list)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.next_match_button)
        button_layout.addWidget(self.replace_current_button)
        button_layout.addWidget(self.replace_all_button)
        layout.addLayout(button_layout)

        layout.addWidget(self.file_preview)

        # 主窗口设置
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 在右上角显示 "i" 图标
        self.create_info_icon()

        # 设置拖放功能
        self.setAcceptDrops(True)
        self.folder_path = ""
        self.matches = []  # 保存所有匹配项的位置
        self.current_match_index = -1  # 当前的匹配项索引

        # 结果点击事件
        self.result_list.itemClicked.connect(self.preview_file)

    def create_info_icon(self):
        """在右上角显示 i 信息图标"""
        self.info_label = QLabel(self)
        self.info_label.setText("ℹ️")  # 使用 i 图标
        self.info_label.setStyleSheet("font-size: 24px; cursor: pointer;")
        self.info_label.setToolTip("点击查看软件协议信息")
        self.info_label.move(self.width() - 30, 10)  # 右上角对齐
        self.info_label.mousePressEvent = self.show_license_info

    def show_license_info(self, event):
        """显示带有 CC Logo、BY、NC 图标的详情页面"""
        dialog = QDialog(self)
        dialog.setWindowTitle("软件协议")

        # 布局
        dialog_layout = QVBoxLayout()

        # CC 图标的 SVG 数据
        svg_data_cc = '''
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" width="30" height="30">
                    <path d="M14.972 0c4.196 0 7.769 1.465 10.715 4.393A14.426 14.426 0 0128.9 9.228C29.633 11.04 30 12.964 30 15c0 2.054-.363 3.978-1.085 5.772a13.77 13.77 0 01-3.2 4.754 15.417 15.417 0 01-4.983 3.322A14.932 14.932 0 0114.973 30c-1.982 0-3.88-.38-5.692-1.14a15.087 15.087 0 01-4.875-3.293c-1.437-1.437-2.531-3.058-3.281-4.862A14.71 14.71 0 010 15c0-1.982.38-3.888 1.138-5.719a15.062 15.062 0 013.308-4.915C7.303 1.456 10.812 0 14.972 0zm.055 2.706c-3.429 0-6.313 1.196-8.652 3.589a12.896 12.896 0 00-2.72 4.031 11.814 11.814 0 00-.95 4.675c0 1.607.316 3.156.95 4.646a12.428 12.428 0 002.72 3.992 12.362 12.362 0 003.99 2.679c1.483.616 3.037.924 4.662.924 1.607 0 3.164-.312 4.675-.937a12.954 12.954 0 004.084-2.705c2.339-2.286 3.508-5.152 3.508-8.6 0-1.66-.304-3.231-.91-4.713a11.994 11.994 0 00-2.651-3.965c-2.412-2.41-5.314-3.616-8.706-3.616z"/>
                </svg>
                '''

        svg_data_by = '''
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" width="30" height="30">
                    <path d="M14.973 0c4.213 0 7.768 1.446 10.66 4.34C28.544 7.25 30 10.803 30 15c0 4.215-1.43 7.723-4.287 10.526C22.678 28.51 19.098 30 14.973 30c-4.054 0-7.571-1.474-10.553-4.42C1.474 22.633 0 19.107 0 15S1.474 7.34 4.42 4.34C7.313 1.446 10.83 0 14.973 0zm.054 2.706c-3.41 0-6.295 1.196-8.652 3.589-2.447 2.5-3.67 5.402-3.67 8.706 0 3.321 1.214 6.196 3.642 8.624 2.429 2.429 5.322 3.642 8.679 3.642 3.339 0 6.25-1.222 8.732-3.67 2.358-2.267 3.536-5.133 3.536-8.598 0-3.41-1.197-6.311-3.589-8.705-2.392-2.392-5.285-3.588-8.678-3.588zm4.018 8.57v6.134H17.33v7.286h-4.66V17.41h-1.714v-6.134a.93.93 0 01.28-.683.933.933 0 01.684-.281h6.161c.25 0 .474.093.67.28a.912.912 0 01.294.684zM12.91 7.42c0-1.41.696-2.116 2.09-2.116s2.09.705 2.09 2.116c0 1.393-.697 2.09-2.09 2.09-1.393 0-2.09-.697-2.09-2.09z"/>
                </svg>
                '''

        svg_data_nc = '''
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" width="30" height="30">
                    <path d="M14.973 0c4.214 0 7.768 1.446 10.66 4.339C28.544 7.232 30 10.786 30 15c0 4.215-1.429 7.723-4.287 10.527C22.678 28.51 19.097 30 14.973 30c-4.072 0-7.59-1.482-10.553-4.446C1.474 22.607 0 19.09 0 15c0-4.107 1.474-7.66 4.42-10.66C7.313 1.446 10.83 0 14.973 0zM3.375 10.956c-.446 1.232-.67 2.58-.67 4.045 0 3.321 1.214 6.196 3.642 8.624 2.447 2.412 5.34 3.617 8.679 3.617 3.375 0 6.285-1.223 8.733-3.67.875-.839 1.561-1.714 2.061-2.626l-5.651-2.518a3.866 3.866 0 01-1.433 2.317c-.76.598-1.657.943-2.693 1.031v2.304h-1.74v-2.304c-1.661-.017-3.18-.615-4.554-1.794l2.063-2.089c.981.91 2.098 1.366 3.348 1.366.517 0 .96-.116 1.326-.349.366-.231.55-.615.55-1.151 0-.376-.135-.68-.402-.911l-1.447-.617-1.767-.804-2.384-1.044-7.661-3.427zm11.652-8.278c-3.41 0-6.295 1.206-8.652 3.616-.59.59-1.143 1.26-1.66 2.01l5.732 2.571a3.513 3.513 0 011.42-1.888c.695-.473 1.508-.737 2.437-.79V5.893h1.741v2.304c1.376.071 2.625.535 3.75 1.392L17.84 11.6c-.84-.59-1.697-.884-2.572-.884-.464 0-.88.09-1.245.267-.366.179-.55.483-.55.911 0 .125.045.25.134.375l1.902.858 1.313.59 2.41 1.07 7.687 3.429c.25-1.054.375-2.125.375-3.214 0-3.447-1.196-6.349-3.588-8.707-2.375-2.41-5.27-3.616-8.68-3.616z"/>
                </svg>
                '''

        # 显示图标的 QSvgWidget
        icon_layout = QHBoxLayout()

        size = 50  # 图标大小为 50x50

        # CC Logo
        cc_logo_widget = QSvgWidget()
        cc_logo_widget.load(svg_data_cc.encode('utf-8'))
        cc_logo_widget.setFixedSize(size, size)
        icon_layout.addWidget(cc_logo_widget)

        # BY 图标
        by_widget = QSvgWidget()
        by_widget.load(svg_data_by.encode('utf-8'))
        by_widget.setFixedSize(size, size)
        icon_layout.addWidget(by_widget)

        # NC 图标
        nc_widget = QSvgWidget()
        nc_widget.load(svg_data_nc.encode('utf-8'))
        nc_widget.setFixedSize(size, size)
        icon_layout.addWidget(nc_widget)

        # 添加图标布局到对话框
        icon_container = QWidget()
        icon_container.setLayout(icon_layout)
        dialog_layout.addWidget(icon_container)

        # 添加协议说明的 QLabel
        license_label = QLabel("本软件遵循 CC BY-NC 2.0 协议，由 OB_BUFF 制作。")
        license_label.setWordWrap(True)  # 如果内容较长，可以换行显示
        dialog_layout.addWidget(license_label)

        # 添加按钮关闭对话框
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        dialog_layout.addWidget(close_button)

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def is_regex(self, text):
        try:
            re.compile(text)
            return True
        except re.error:
            return False

    def search_files(self):
        self.result_list.clear()
        self.file_preview.clear()
        self.matches.clear()
        self.current_match_index = -1

        search_term = self.search_input.text()
        if not search_term or not self.folder_path:
            self.show_error_message("请输入关键字并拖放文件夹！")
            return

        is_regex = self.is_regex(search_term)

        # 遍历文件夹中的所有文件
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        if is_regex:
                            matches = list(re.finditer(search_term, content))
                        else:
                            matches = list(re.finditer(re.escape(search_term), content))

                        if matches:
                            self.result_list.addItem(f"{file_path} - {len(matches)} 处匹配")
                except Exception as e:
                    self.show_error_message(f"无法读取文件: {file_path}\n错误信息: {e}")

    def preview_file(self, item):
        file_info = item.text().split(" - ")[0]
        search_term = self.search_input.text()

        try:
            with open(file_info, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                self.file_preview.setPlainText(content)

                self.matches.clear()
                self.current_match_index = -1

                is_regex = self.is_regex(search_term)

                self.file_preview.moveCursor(QTextCursor.MoveOperation.Start)
                highlight_format = QTextCharFormat()
                highlight_format.setBackground(QColor("yellow"))
                highlight_format.setForeground(QColor("black"))

                pattern = re.compile(search_term) if is_regex else re.compile(re.escape(search_term))

                # 移除之前的高亮
                self.file_preview.setExtraSelections([])

                extraSelections = []

                for match in pattern.finditer(content):
                    start_pos = match.start()
                    end_pos = match.end()
                    selection = QTextEdit.ExtraSelection()
                    selection.cursor = self.file_preview.textCursor()
                    selection.cursor.setPosition(start_pos)
                    selection.cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
                    selection.format = highlight_format
                    extraSelections.append(selection)

                    self.matches.append((start_pos, end_pos))

                self.file_preview.setExtraSelections(extraSelections)

                if self.matches:
                    self.current_match_index = 0
                    self.go_to_match(self.current_match_index)

        except Exception as e:
            self.show_error_message(f"无法预览文件: {file_info}\n错误信息: {e}")

    def go_to_match(self, index):
        if index < 0 or index >= len(self.matches):
            return

        start_pos, end_pos = self.matches[index]
        cursor = self.file_preview.textCursor()
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
        self.file_preview.setTextCursor(cursor)
        self.file_preview.ensureCursorVisible()

    def go_to_next_match(self):
        if self.matches:
            self.current_match_index = (self.current_match_index + 1) % len(self.matches)
            self.go_to_match(self.current_match_index)

    def replace_current_file(self):
        if not self.matches:
            return

        replace_term = self.replace_input.text()
        search_term = self.search_input.text()

        content = self.file_preview.toPlainText()

        is_regex = self.is_regex(search_term)
        if is_regex:
            content = re.sub(search_term, replace_term, content)
        else:
            content = content.replace(search_term, replace_term)

        self.file_preview.setPlainText(content)
        self.save_file(self.result_list.currentItem().text().split(" - ")[0], content)
        self.preview_file(self.result_list.currentItem())

    def replace_all_files(self):
        search_term = self.search_input.text()
        replace_term = self.replace_input.text()

        if not search_term or not self.folder_path:
            self.show_error_message("请输入关键字并拖放文件夹！")
            return

        is_regex = self.is_regex(search_term)

        # 遍历文件夹中的所有文件
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r+', encoding='utf-8', errors='ignore') as file:
                        content = file.read()

                        if is_regex:
                            new_content, num_subs = re.subn(search_term, replace_term, content)
                        else:
                            new_content = content.replace(search_term, replace_term)
                            num_subs = content.count(search_term)

                        if num_subs > 0:
                            file.seek(0)
                            file.write(new_content)
                            file.truncate()
                except Exception as e:
                    self.show_error_message(f"无法读取或替换文件: {file_path}\n错误信息: {e}")

    def save_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as file:
                file.write(content)
        except Exception as e:
            self.show_error_message(f"无法保存文件: {file_path}\n错误信息: {e}")

    def show_error_message(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("错误")
        msg_box.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.folder_path = path
                self.drop_label.setText(f"已选择文件夹: {path}")
            else:
                self.show_error_message("请拖放一个文件夹！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextSearchApp()
    window.show()
    sys.exit(app.exec())
