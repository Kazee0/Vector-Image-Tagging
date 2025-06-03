import sys,os
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox, QDialog
from PyQt6.QtGui import QImage, QPixmap, QPainter, QKeySequence, QShortcut
from PyQt6.QtCore import Qt
import cv2
import numpy as np
import bin.image_processor as image_processor
from interfaces import BandpassFilterDialog, ContrastDialog

class TIFFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.setWindowTitle("TIFF Viewer")
        self.resize(800, 600)
        self.image_processor = image_processor.ImageProcessor()
        self.zoom_factor = 1.1
        
    def initUI(self):
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.dragging = False
        self.last_mouse_pos = None
        self.move_mode = False
        menubar = self.menuBar()
        self.cwd = None
        
        #Create Menu
        file_menu = menubar.addMenu("Files")
        tool_menu = menubar.addMenu("Adjust")
        helps_menu = menubar.addMenu('Help')
    
        log_action = tool_menu.addAction("Log Transfer")
        log_action.triggered.connect(self.apply_log)
        
        reverse_action = tool_menu.addAction("Reverse Image")
        reverse_action.triggered.connect(self.reset)
        
        open_action = file_menu.addAction("Open TIF File")
        open_action.triggered.connect(self.open_tif_file)
        
        save_action = file_menu.addAction("Save File")
        save_action.triggered.connect(self.save_action)
        
        exit_action = file_menu.addAction("exit")
        exit_action.triggered.connect(self.close)
        
        fft_action = tool_menu.addAction("FFT...")
        fft_action.triggered.connect(self.apply_banpass_filter)
        
        zoom_in = tool_menu.addAction("Zoom In")
        zoom_in.triggered.connect(self.zoom_in)
        
        zoom_out = tool_menu.addAction("Zoom Out")
        zoom_out.triggered.connect(self.zoom_out)
        
        adjust_rest = tool_menu.addAction("Reset")
        adjust_rest.triggered.connect(self.rest_change)
        
        about_action = helps_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        
        #Hot Keys
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"),self)
        save_shortcut.activated.connect(self.save_action)
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.open_tif_file)
        
        self.view.wheelEvent = self.wheelEvent
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setInteractive(True)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
    
        tool_menu.addAction("Drag")
        tool_menu.triggered.connect(self.toggle_move)
        
        self.orginal_mousePress = self.view.mousePressEvent
        self.orginal_mouseMove = self.view.mouseMoveEvent
        self.orginal_mouseRelease = self.view.mouseReleaseEvent
        
        self.view.mousePressEvent = self.mousePressEvent
        self.view.mouseMoveEvent = self.mouseMoveEvent 
        self.view.mouseReleaseEvent = self.mouseReleaseEvent
    
    def apply_banpass_filter(self):
        if not self.scene.items():
            QMessageBox.warning(self,"Warning", "No present image")
            return
        dialog = BandpassFilterDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            params = dialog.get_values()
            pixmap = self.scene.items()[0].pixmap()
            processed = self.image_processor.apply_banpass_filter(pixmap, params)
            self.scene.clear()
            self.scene.addPixmap(processed)
            #Diplay Filter Not Implmented
    def toggle_move(self, checked):
        self.move_mode = checked
        if self.move_mode:
            self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.view.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
        
    def mousePressEvent(self, a0):
        if self.move_mode and a0.button()==Qt.MouseButton.LeftButton:
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.orginal_mousePress(a0)
        else:
            self.orginal_mousePress(a0)
    def mouseMoveEvent(self, a0):
        self.orginal_mouseMove(a0)
    def mouseReleaseEvent(self, a0):
        if self.move_mode and a0.button() == Qt.MouseButton.LeftButton:
            self.view.setCursor(Qt.CursorShape.OpenHandCursor)
        self.orginal_mouseRelease(a0)
        
    def reset(self):
        orginal = self.image_processor.reset_image()
        if orginal:
            self.scene.clear()
            self.scene.addPixmap(orginal)
    
    def apply_log(self):
        if not self.scene.items():
            QMessageBox.warning(self, "Warning", "No available Image")
            return
        pixmap_item = self.scene.items()[0]
        processed = self.image_processor.apply_log_transform(pixmap_item.pixmap())
        if processed:
            self.scene.clear()
            self.scene.addPixmap(processed)
            
    def open_tif_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 TIF 文件", "", "TIF Files (*.tif *.tiff);;All FIles(*)"
        )
        self.cwd = os.path.dirname(file_path)
        if not file_path:
            return
        try:
            # 使用OpenCV读取图像
            img = cv2.imread(file_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
            
            if img is None:
                raise ValueError("无法读取图像文件")
                
            height, width = img.shape[:2]
            channels = 1 if len(img.shape) == 2 else img.shape[2]

            if img.dtype == np.uint16:
                img = self._convert_16bit_to_8bit(img)
            
            if channels == 1:
                bytes_per_line = width
                qimage = QImage(img.data, width, height, bytes_per_line, 
                            QImage.Format.Format_Grayscale8)
            elif channels == 3:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                bytes_per_line = 3 * width
                qimage = QImage(img_rgb.data, width, height, bytes_per_line, 
                            QImage.Format.Format_RGB888)
            elif channels == 4:
                img_rgba = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
                bytes_per_line = 4 * width
                qimage = QImage(img_rgba.data, width, height, bytes_per_line, 
                            QImage.Format.Format_RGBA8888)
            else:
                raise ValueError(f"不支持的通道数: {channels}")
            self._display_image(qimage, file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
            
    def _display_image(self, qimage, file_path):
        self.scene.clear()
        pixmap = QPixmap.fromImage(qimage)
        self.scene.addPixmap(pixmap)
        self.view.fitInView(self.scene.itemsBoundingRect(), 
                        Qt.AspectRatioMode.KeepAspectRatio)
        self.image_processor.set_orginal_image(pixmap)
        self.current_file_path = file_path   
        
    def _convert_16bit_to_8bit(self, img):
        min_val = np.min(img)
        max_val = np.max(img)
        if max_val > min_val:
            img_8bit = ((img - min_val) * (255.0 / (max_val - min_val))).astype(np.uint8)
        else:
            img_8bit = np.zeros_like(img, dtype=np.uint8)
        return img_8bit
    
    def save_action(self):
        filepath, filetype = QFileDialog.getSaveFileName(self, "",self.cwd, "TIFF Files(*tif)")
        print(filepath, filetype)
        if not filepath:
            return
        if not filepath.lower().endswith(('.tif','.tiff')):
            filepath+='.tif'
        try: 
            if not self.scene.items():
                raise ValueError("场景中没有图像")
            
            pixmap_item = self.scene.items()[0]
            qimage = pixmap_item.pixmap().toImage()

            if qimage.format() not in (QImage.Format.Format_RGB888, QImage.Format.Format_RGBA8888):
                qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
            

            width = qimage.width()
            height = qimage.height()
            bytes_per_line = qimage.bytesPerLine()
            channels = 4 if qimage.hasAlphaChannel() else 3
            
            ptr = qimage.bits()
            ptr.setsize(height * bytes_per_line)
            arr = np.frombuffer(ptr, np.uint8)
            
            if bytes_per_line == width * channels:
                arr = arr.reshape((height, width, channels))
            else:
                arr = arr.reshape((height, bytes_per_line))[:, :width*channels]
                arr = arr.reshape((height, width, channels))

            if channels == 3:
                cv_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            elif channels == 4:
                cv_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
            else:
                cv_image = arr
            if not cv2.imwrite(filepath, cv_image):
                raise ValueError("保存文件失败")
                
            QMessageBox.information(self, "成功", f"图像已保存为:\n{filepath}")
            self.cwd = os.path.dirname(filepath)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件时出错:\n{str(e)}")
            
                
        
        
        
        
        
    
    def zoom_in(self):
        self.view.scale(self.zoom_factor, self.zoom_factor)
    
    def zoom_out(self):
        self.view.scale(1/self.zoom_factor, 1/self.zoom_factor)
    
    def rest_change(self):
        self.view.resetTransform()
        if hasattr(self, 'scene') and self.scene.items():
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def show_about(self):
        QMessageBox.about(self, "About", "TIF 文件查看器\n 使用PyQt6和Pillow库创建。")
    
    def resizeEvent(self, event):
        if hasattr(self, 'scene') and self.scene.items():
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            super().resizeEvent(event)
            
    def wheelEvent(self, a0):
        if a0.modifiers() & Qt.KeyboardModifier.ControlModifier:
            #Preseeed Ctrl
            if a0.angleDelta().y()>0:
                self.zoom_in()
            else:
                self.zoom_out()
        return super().wheelEvent(a0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TIFFViewer()
    viewer.show()
    sys.exit(app.exec())
            