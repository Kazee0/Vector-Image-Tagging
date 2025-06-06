import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMessageBox
import cv2


class ImageProcessor:
    def __init__(self):
        self.original_pixmap = None
    
    def set_orginal_image(self, pixmap):
        self.original_pixmap = pixmap.copy() if pixmap else None
    
    def apply_log_transform(self, pixmap):
        if pixmap is None:
            return None
        image = pixmap.toImage()
        width, height, format = image.width(), image.height(), image.format()
        if format in(QImage.Format.Format_RGB32, QImage.Format.Format_ARGB32):
            return self._rgb_log(image, width, height)
        elif format == QImage.Format.Format_Grayscale8:
            return self._grayscale_log(image, width, height)
        else:
            image = image.convertToFormat(QImage.Format.Format_RGB32)
            return self._rgb_log(image, width, height)
    
    def _rgb_log(self, img, width, height):
        print("Performing Log On RGB ")
        if isinstance(img, QPixmap):
            img = img.toImage()
        if img.format() not in (QImage.Format.Format_RGB32, QImage.Format.Format_RGBA8888):
            img = img.convertToFormat(QImage.Format.Format_RGB32)
        ptr = img.bits()
        ptr.setsize(img.sizeInBytes())
        if img.format() == QImage.Format.Format_RGBA8888:
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
            channels = 4
        else:
            arr  = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))[:, :, :3]
            channels =3
        if arr.size ==0:
            return QPixmap.fromImage(img)
        
        max_val = np.max(arr)
        
        if max_val <=0:
            return QPixmap.fromImage(img)
        try:
            log_max = np.log1p(max_val)
            c = 255.0/log_max
            result = np.zeros((height, width, 3), dtype=np.uint8)
            for i in range(3):
                channel = arr[:,:,i].astype(np.float32)
                log_channel = np.log1p(channel)
                result[:,:,i] = np.clip(c*log_channel, 0, 255)
            bytes_per_line = 3*width
            processed = QImage(result.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            return QPixmap.fromImage(processed)
        except Exception as e:
            print("Error")
     
    def _grayscale_log(self, img, width, height):
        ptr = img.bits()
        ptr.setsize(img.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width))
        max_val = np.max(arr)
        
        c = 255/np.log(1+max_val)
        result = np.clip(c*np.log(1+arr),0,255).astype(np.uint8)
        
        processed = QImage(result.date, width, height, img.bytesPerLine(), QImage.Format.Format_Grayscale8)
        return QPixmap.fromImage(processed)
    
    def apply_banpass_filter(self, pixmap, params):
        qimage = pixmap.toImage()
        qimage = qimage.convertToFormat(QImage.Format.Format_Grayscale8)
        
        ptr=qimage.bits()
        ptr.setsize(qimage.sizeInBytes())
        arr = np.frombuffer(ptr, np.uint8).reshape((qimage.height(), qimage.width()))
        blurred = cv2.GaussianBlur(arr, (5, 5), 0)
        img_filtered = cv2.addWeighted(arr, 1.5, blurred, -0.5, 0)
        fft = np.fft.fft2(arr.astype(np.float32))
        fft_shift = np.fft.fftshift(fft)
        
        rows, cols = arr.shape
        crow,ccol = rows//2, cols//2
        """
        mask = np.ones((rows, cols), np.float32)
        
        if params['large_cutoff']>0:
            radius = min(params['large_cutoff'], min(rows, cols)//2)
            y,x = np.ogrid[:rows, :cols]
            mask_area = (x-ccol)**2 + (y-crow)**2 <= radius **2
            mask[mask_area] = 0
            
        if params['small_cutoff']>0:
            radius = min(params['small_cutoff'], min(rows, cols)//2)
            y,x = np.ogrid[:rows, :cols]
            mask_area = (x -ccol)**2+(y-crow) ** 2<= radius ** 2
            mask[mask_area] = 0
            
                # Add debug logging
        print(f"Bandpass filter: large={params['large_cutoff']}, small={params['small_cutoff']}")
        print(f"FFT min: {np.min(np.abs(fft_shift))}, max: {np.max(np.abs(fft_shift))}")
        
        fft_filtered = fft_shift*mask
        
        ifft_shift = np.fft.ifftshift(fft_filtered)
        img_filtered = np.fft.ifft2(ifft_shift)
        img_filtered = np.abs(img_filtered) 
        
        if params['autoscale']:
            min_val = np.min(img_filtered)
            max_val = np.max(img_filtered)
            if max_val>min_val:
                img_filtered = 255*(img_filtered-min_val)/(max_val-min_val)
                if params['saturate']:
                    img_filtered = np.clip(img_filtered,0,255)"""
        img_filtered=img_filtered.astype(np.uint8)
        processed = QImage(img_filtered.data, cols, rows, cols, QImage.Format.Format_Grayscale8)
        return QPixmap.fromImage(processed)

    def adjust_contrast(self, pixmap, params):
        qimage = pixmap.toImage()
        
        ptr = qimage.bits()
        ptr.setsize(qimage.sizeInBytes())

        if qimage.format() == QImage.Format.Format_Grayscale8:
            arr = np.frombuffer(ptr, np.uint8).reshape((qimage.height(), qimage.width()))
            channels = 1
        else:
            arr = np.frombuffer(ptr, np.uint8).reshape((qimage.height(), qimage.width(), 4))
            channels =3
        if params['auto']:
            if channels == 1:
                arr = self._auto_contrast_mono(arr)
            else:
                for c in range(channels):
                    arr[:,:,c]  = self._auto_contrast_mono(arr[:,:,c])
        else:
            brightness = params['brightness']
            contrast = params['contrast']
            if channels == 1:
                arr = self._manual_contrast_mono(arr, brightness, contrast)
            else:
                for c in range(channels):
                    arr[:,:,c] = self._manual_contrast_mono(arr[:,:,c], brightness, contrast)
        
        if channels == 1:
            processd = QImage(arr.data, qimage.width(), qimage.height(), qimage.bytesPerLine(), QImage.Format.Format_Grayscale8)
        else:
            processd = QImage(arr.data, qimage.width(), qimage.height(), qimage.bytesPerLine(), QImage.Format.Format_RGBA8888)
        
        return QPixmap.fromImage(processd)
    
    def _auto_contrast_mono(self, arr):
        min_val = np.min(arr)
        max_val = np.max(arr) 
        if max_val > min_val:
            return np.clip((arr-min_val)/(max_val-min_val)*255, 0, 255).astype(np.uint8)
        return arr
    
    def _manual_contrast_mono(self, arr, b, c):
        arr = arr.astype(np.float32)
        arr = (arr-128)*c + 128
        arr = arr * b
        return np.clip(arr, 0, 255).astype(np.uint8)    
            
    def reset_image(self):
        return self.original_pixmap.copy() if self.original_pixmap else None