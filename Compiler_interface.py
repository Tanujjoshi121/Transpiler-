import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel,
    QFileDialog, QComboBox, QMessageBox, QFrame
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt
import os
from interpreter import run_compiler
from transpiler_backend import transpile_to_python, transpile_to_cpp, transpile_to_c, transpile_to_java


class TranspilerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Transpiler")
        self.resize(1200, 750)
        self.set_elegant_theme()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        header = QLabel("Code Transpiler")
        header.setStyleSheet("color: #E0E0E0; font-size: 30px; font-weight: 700;")
        subheader = QLabel("Transpile your code seamlessly between multiple languages")
        subheader.setStyleSheet("color: #A0A0A0; font-size: 14px;")
        main_layout.addWidget(header)
        main_layout.addWidget(subheader)

        lang_layout = QHBoxLayout()
        lang_label = QLabel("Select Language:")
        lang_label.setStyleSheet("color: #E0E0E0; font-size: 14px; font-weight: 600;")
        self.language_selector = QComboBox()
        self.language_selector.addItems(["Select Language", "Python", "Java", "C", "C++"])
        self.language_selector.setStyleSheet("""
            QComboBox {
                padding: 8px 14px;
                background-color: #2D2D2D;
                color: #E0E0E0;
                border-radius: 6px;
                font-size: 14px;
            }
            QComboBox:hover {
                background-color: #3A3A3A;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50;
            }
        """)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_selector)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)

        self.tips_box = QLabel("💡 Select a language to get code tips and hints here.")
        self.tips_box.setStyleSheet("""
            color: #B0B0B0;
            background-color: #222222;
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 12px;
            font-style: italic;
        """)
        main_layout.addWidget(self.tips_box)

        editor_layout = QHBoxLayout()

        input_layout = QVBoxLayout()
        input_label = QLabel("Source Code")
        input_label.setStyleSheet("color: #E0E0E0; font-size: 16px; font-weight: 600;")
        self.input_editor = QTextEdit()
        self.input_editor.setFont(QFont("Consolas", 11))
        self.input_editor.setStyleSheet("background-color: #1B1B1B; color: #FFFFFF; border-radius: 8px; padding: 10px;")
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_editor)

        input_buttons = QHBoxLayout()
        self.add_button("Transpile", self.transpile_code, "#00BFA6", input_buttons)
        self.add_button("Clear Input", self.clear_input, "#D32F2F", input_buttons)
        self.add_button("Load File", self.load_file, "#1976D2", input_buttons)
        input_layout.addLayout(input_buttons)
        editor_layout.addLayout(input_layout)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("color: #444444;")
        editor_layout.addWidget(divider)

        output_layout = QVBoxLayout()
        outputs_side_by_side = QHBoxLayout()

        transpiled_layout = QVBoxLayout()
        output_label = QLabel("Transpiled Output")
        output_label.setStyleSheet("color: #E0E0E0; font-size: 16px; font-weight: 600;")
        self.output_editor = QTextEdit()
        self.output_editor.setFont(QFont("Consolas", 11))
        self.output_editor.setReadOnly(True)
        self.output_editor.setStyleSheet("background-color: #1B1B1B; color: #A0FFA0; border-radius: 8px; padding: 10px;")
        transpiled_layout.addWidget(output_label)
        transpiled_layout.addWidget(self.output_editor)

        outputs_side_by_side.addLayout(transpiled_layout)

        compiled_layout = QVBoxLayout()
        compiled_label = QLabel("Compiled Output")
        compiled_label.setStyleSheet("color: #E0E0E0; font-size: 16px; font-weight: 600;")
        self.compiled_output = QTextEdit()
        self.compiled_output.setFont(QFont("Consolas", 11))
        self.compiled_output.setReadOnly(True)
        self.compiled_output.setStyleSheet("background-color: #1B1B1B; color: #FFFF99; border-radius: 8px; padding: 10px;")
        compiled_layout.addWidget(compiled_label)
        compiled_layout.addWidget(self.compiled_output)

        outputs_side_by_side.addLayout(compiled_layout)
        output_layout.addLayout(outputs_side_by_side)

        output_buttons = QHBoxLayout()
        self.add_button("Clear Output", self.clear_output, "#C62828", output_buttons)
        self.add_button("Save Output", self.save_output, "#F9A825", output_buttons)
        self.add_button("Compile and Run", self.compile_and_run, "#283593", output_buttons)
        output_layout.addLayout(output_buttons)

        editor_layout.addLayout(output_layout)
        main_layout.addLayout(editor_layout)
        self.setLayout(main_layout)

    def set_elegant_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                font-weight: 600;
                font-size: 14px;
                border-radius: 6px;
            }
        """)

    def add_button(self, label, func, hex_color, layout):
        btn = QPushButton(label)
        btn.clicked.connect(func)
        btn.setCursor(Qt.PointingHandCursor)
        base_color = QColor(hex_color)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {base_color.lighter(130).name()},
                    stop:1 {base_color.darker(130).name()}
                );
                color: white;
                border-radius: 10px;
                padding: 12px 22px;
                font-size: 15px;
                border: 1px solid {base_color.darker(150).name()};
            }}
            QPushButton:hover {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {base_color.lighter(150).name()},
                    stop:1 {base_color.darker(150).name()}
                );
                color: #FFFDE7;
                border: 1.5px solid {base_color.lighter(180).name()};
            }}
            QPushButton:pressed {{
                background-color: {base_color.darker(170).name()};
                color: #E0E0E0;
            }}
        """)
        layout.addWidget(btn)

    def compile_and_run(self):
        code = self.input_editor.toPlainText()
        try:
            import io
            import contextlib

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                run_compiler(code)
            self.compiled_output.setPlainText(buffer.getvalue())

        except Exception as e:
            self.compiled_output.setPlainText(f"Interpreter error: {e}")

    def clear_input(self):
        self.input_editor.clear()

    def clear_output(self):
        self.output_editor.clear()
        self.compiled_output.clear()

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Code Files (*.txt *.py *.cpp *.java)")
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                self.input_editor.setPlainText(file.read())

    def save_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Output", "", "Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(self.output_editor.toPlainText())

    def transpile_code(self):
        source_code = self.input_editor.toPlainText()
        selected_lang = self.language_selector.currentText()

        if selected_lang == "Select Language":
            QMessageBox.warning(self, "Language Not Selected", "Please select a language.")
            return

        try:
            if selected_lang == "Python":
                transpiled = transpile_to_python(source_code)
            elif selected_lang == "C++":
                transpiled = transpile_to_cpp(source_code)
            elif selected_lang == "C":
                transpiled = transpile_to_c(source_code)
            elif selected_lang == "Java":
                transpiled = transpile_to_java(source_code)
            else:
                transpiled = "// Transpilation not supported for this language."

            self.output_editor.setPlainText(transpiled)
        except Exception as e:
            QMessageBox.critical(self, "Transpilation Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranspilerGUI()
    window.show()
    sys.exit(app.exec())
