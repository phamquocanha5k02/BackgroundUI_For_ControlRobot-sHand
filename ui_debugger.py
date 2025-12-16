"""
Module UI Debugger
Hiển thị cửa sổ debug với video frame, landmarks, gesture, servo angles và FPS.
"""

import cv2
import time
import numpy as np
import random
from typing import List, Tuple, Dict, Optional


class UIDebugger:
    """Quản lý cửa sổ debug để hiển thị frame, landmarks, gesture, angles và FPS."""
    
    def __init__(self, window_name: str = "Debug Window"):
        """
        Khởi tạo UI Debugger.
        
        Args:
            window_name: Tên cửa sổ OpenCV
        """
        self.window_name = window_name
        self.prev_time = time.time()
        self.fps = 0.0
        self.frame_count = 0
        
    def draw_landmarks(self, frame: np.ndarray, landmarks: List[Tuple[int, int]], 
                      color: Tuple[int, int, int] = (0, 255, 0), 
                      radius: int = 3) -> np.ndarray:
        """
        Vẽ landmarks dạng neon pastel dots với hiệu ứng glow mềm mại.
        """
        if landmarks is None:
            return frame
        
        neon_palette = [
            (180, 105, 255),  # màu hồng (BGR)
            (255, 195, 120),  # màu đào/cyan nhạt
            (220, 160, 255),  # màu tím
            (130, 255, 200),  # màu bạc hà/lime
            (255, 255, 180),  # màu vàng-cyan nhạt
        ]
        
        glow_overlay = frame.copy()
        dot_overlay = frame.copy()
        
        for idx, landmark in enumerate(landmarks):
            if landmark is None or len(landmark) < 2:
                continue
            x, y = int(landmark[0]), int(landmark[1])
            neon_color = neon_palette[idx % len(neon_palette)]
            
            # Vòng ngoài glow
            cv2.circle(glow_overlay, (x, y), radius * 4, neon_color, -1, lineType=cv2.LINE_AA)
            # Chấm trong sắc nét
            cv2.circle(dot_overlay, (x, y), radius + 1, neon_color, -1, lineType=cv2.LINE_AA)
        
        # Trộn glow rồi chấm đặc để tạo hiệu ứng neon mềm
        cv2.addWeighted(glow_overlay, 0.25, frame, 0.75, 0, frame)
        cv2.addWeighted(dot_overlay, 0.90, frame, 0.10, 0, frame)
        return frame
    
    def calculate_fps(self) -> float:
        """
        Tính FPS sử dụng time.time().
        
        Returns:
            Giá trị FPS hiện tại
        """
        current_time = time.time()
        elapsed = current_time - self.prev_time
        
        if elapsed > 0:
            self.fps = 1.0 / elapsed
        
        self.prev_time = current_time
        return self.fps
    
    def draw_text_overlay(self, frame: np.ndarray, gesture: str, 
                         angles: Dict[str, float], fps: float) -> np.ndarray:
        """
        Vẽ overlay phong cách phòng điều khiển robot với khung laser công nghệ.
        """
        # Bảng màu laser công nghệ (BGR)
        laser_cyan = (255, 255, 0)      # cyan sáng
        laser_magenta = (255, 0, 255)   # magenta
        laser_green = (0, 255, 0)       # xanh lá
        laser_blue = (255, 100, 0)      # xanh dương
        text_white = (255, 255, 255)
        card_bg = (5, 5, 15)            # nền đen rất tối
        card_bg_secondary = (10, 5, 20) # nền phụ
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.65
        thickness = 1
        padding = 18
        line_h = 26
        x0, y0 = 20, 20
        
        # Xây dựng các dòng text
        lines = [("GESTURE", f"{gesture if gesture else 'NONE'}", laser_cyan)]
        
        if angles:
            lines.append(("SERVO ANGLES", "", text_white))
            for idx, (name, angle) in enumerate(angles.items()):
                color = laser_green if idx % 2 == 0 else laser_magenta
                lines.append((f"  {name}", f"{angle:.1f}°", color))
        else:
            lines.append(("SERVO ANGLES", "NONE", text_white))
        
        lines.append(("FPS", f"{fps:.1f}", laser_blue))
        
        # Tính kích thước box
        max_width = 0
        for label, value, _ in lines:
            text_size, _ = cv2.getTextSize(f"{label}: {value}", font, font_scale, thickness)
            max_width = max(max_width, text_size[0])
        
        box_width = max_width + padding * 2 + 40
        box_height = padding * 2 + line_h * len(lines) + 10
        box_tl = (x0, y0)
        box_br = (x0 + box_width, y0 + box_height)
        
        # Vẽ nền card đen trong suốt
        overlay = frame.copy()
        cv2.rectangle(overlay, box_tl, box_br, card_bg, -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        
        # Vẽ khung laser công nghệ với góc vuông
        corner_length = 25
        laser_thickness = 2
        
        # Góc trên trái
        cv2.line(frame, box_tl, (box_tl[0] + corner_length, box_tl[1]), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        cv2.line(frame, box_tl, (box_tl[0], box_tl[1] + corner_length), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        
        # Góc trên phải
        cv2.line(frame, (box_br[0], box_tl[1]), (box_br[0] - corner_length, box_tl[1]), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        cv2.line(frame, (box_br[0], box_tl[1]), (box_br[0], box_tl[1] + corner_length), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        
        # Góc dưới trái
        cv2.line(frame, (box_tl[0], box_br[1]), (box_tl[0] + corner_length, box_br[1]), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        cv2.line(frame, (box_tl[0], box_br[1]), (box_tl[0], box_br[1] - corner_length), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        
        # Góc dưới phải
        cv2.line(frame, box_br, (box_br[0] - corner_length, box_br[1]), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        cv2.line(frame, box_br, (box_br[0], box_br[1] - corner_length), laser_cyan, laser_thickness, lineType=cv2.LINE_AA)
        
        # Đường viền laser bên trong
        inner_margin = 3
        inner_tl = (box_tl[0] + inner_margin, box_tl[1] + inner_margin)
        inner_br = (box_br[0] - inner_margin, box_br[1] - inner_margin)
        cv2.rectangle(frame, inner_tl, inner_br, laser_magenta, 1, lineType=cv2.LINE_AA)
        
        # Đường kẻ ngang phân cách (scan lines)
        scan_y = box_tl[1] + padding + line_h
        for i in range(len(lines) - 1):
            scan_y += line_h
            cv2.line(frame, (box_tl[0] + 10, scan_y), (box_br[0] - 10, scan_y), 
                    laser_blue, 1, lineType=cv2.LINE_AA)
        
        # Điểm góc với hiệu ứng glow
        corner_points = [
            box_tl, (box_br[0], box_tl[1]), 
            (box_tl[0], box_br[1]), box_br
        ]
        for pt in corner_points:
            cv2.circle(frame, pt, 3, laser_cyan, -1, lineType=cv2.LINE_AA)
            cv2.circle(frame, pt, 6, laser_cyan, 1, lineType=cv2.LINE_AA)
        
        # Vẽ text với hiệu ứng shadow
        y_cursor = y0 + padding + line_h - 4
        for label, value, color in lines:
            text = f"{label}: {value}".strip()
            # Shadow
            cv2.putText(frame, text, (x0 + padding + 1, y_cursor + 1), 
                       font, font_scale, (0, 0, 0), thickness + 1, lineType=cv2.LINE_AA)
            # Text chính
            cv2.putText(frame, text, (x0 + padding, y_cursor), 
                       font, font_scale, color, thickness + 1, lineType=cv2.LINE_AA)
            y_cursor += line_h
        
        # Thêm các đường scan animation (tùy chọn - có thể làm động sau)
        scan_line_y = box_tl[1] + 5
        if scan_line_y < box_br[1]:
            cv2.line(frame, (box_tl[0] + 5, scan_line_y), (box_br[0] - 5, scan_line_y), 
                    laser_green, 1, lineType=cv2.LINE_AA)
        
        return frame

    def _draw_rounded_rect(self, img: np.ndarray, pt1: Tuple[int, int], pt2: Tuple[int, int], 
                           color: Tuple[int, int, int], radius: int = 12, thickness: int = -1) -> None:
        """
        Vẽ hình chữ nhật bo tròn (đổ đầy hoặc viền) lên img.
        """
        x1, y1 = pt1
        x2, y2 = pt2
        radius = max(1, radius)
        
        # Hình chữ nhật trung tâm
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
        
        # Bốn góc tròn
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness, lineType=cv2.LINE_AA)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness, lineType=cv2.LINE_AA)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness, lineType=cv2.LINE_AA)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness, lineType=cv2.LINE_AA)
    
    def show_debug_window(self, frame: np.ndarray, gesture: str, 
                         angles: Dict[str, float], 
                         landmarks: Optional[List[Tuple[int, int]]] = None) -> None:
        """
        Phương thức chính để hiển thị cửa sổ debug với tất cả thông tin.
        
        Args:
            frame: Video frame (numpy array)
            gesture: Chuỗi text gesture
            angles: Dictionary các góc servo {name: angle}
            landmarks: Danh sách tùy chọn các tọa độ landmark (x, y)
        """
        if frame is None:
            return
        
        # Tính FPS
        fps = self.calculate_fps()
        
        # Tạo bản sao của frame để tránh sửa đổi frame gốc
        debug_frame = frame.copy()
        
        # Vẽ landmarks nếu có
        if landmarks:
            debug_frame = self.draw_landmarks(debug_frame, landmarks)
        
        # Vẽ text overlay
        debug_frame = self.draw_text_overlay(debug_frame, gesture, angles, fps)
        
        # Hiển thị cửa sổ debug
        cv2.imshow(self.window_name, debug_frame)
    
    def close(self):
        """Đóng cửa sổ debug."""
        cv2.destroyWindow(self.window_name)


def show_debug_window(frame: np.ndarray, gesture: str, angles: Dict[str, float],
                     landmarks: Optional[List[Tuple[int, int]]] = None,
                     window_name: str = "Debug Window") -> None:
    """
    Hàm tiện ích để hiển thị cửa sổ debug.
    
    Args:
        frame: Video frame (numpy array)
        gesture: Chuỗi text gesture
        angles: Dictionary các góc servo {name: angle}
        landmarks: Danh sách tùy chọn các tọa độ landmark (x, y)
        window_name: Tên cửa sổ OpenCV
    """
    debugger = UIDebugger(window_name)
    debugger.show_debug_window(frame, gesture, angles, landmarks)


def create_cyberpunk_background(height: int, width: int) -> np.ndarray:
    """
    Tạo nền cyberpunk với gradient, grid lines và hiệu ứng neon.
    
    Args:
        height: Chiều cao frame
        width: Chiều rộng frame
        
    Returns:
        Frame với nền cyberpunk
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Gradient màu cyberpunk (từ đen -> tím đậm -> xanh dương đậm)
    for y in range(height):
        # Tạo gradient từ trên xuống dưới
        ratio = y / height
        # Màu đen -> tím đậm -> xanh dương đậm
        r = int(10 + ratio * 30)  # đỏ nhẹ
        g = int(5 + ratio * 20)   # xanh lá nhẹ
        b = int(20 + ratio * 50)  # xanh dương đậm
        frame[y, :] = [b, g, r]  # BGR format
    
    # Thêm grid lines neon
    grid_color = (255, 100, 200)  # cyan-magenta (BGR)
    grid_spacing = 40
    
    # Đường dọc
    for x in range(0, width, grid_spacing):
        cv2.line(frame, (x, 0), (x, height), grid_color, 1, lineType=cv2.LINE_AA)
    
    # Đường ngang
    for y in range(0, height, grid_spacing):
        cv2.line(frame, (0, y), (width, y), grid_color, 1, lineType=cv2.LINE_AA)
    
    # Thêm một số điểm sáng ngẫu nhiên (neon particles)
    for _ in range(15):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        particle_color = random.choice([
            (255, 200, 100),  # cyan
            (200, 100, 255),   # magenta
            (100, 255, 200),   # lime
        ])
        cv2.circle(frame, (x, y), 2, particle_color, -1, lineType=cv2.LINE_AA)
        # Glow effect
        cv2.circle(frame, (x, y), 5, particle_color, 1, lineType=cv2.LINE_AA)
    
    # Thêm scanline effect (tùy chọn)
    for y in range(0, height, 3):
        if y % 6 == 0:
            cv2.line(frame, (0, y), (width, y), (0, 0, 5), 1)
    
    return frame


# Ví dụ sử dụng
if __name__ == "__main__":
    # Tạo frame test với nền cyberpunk
    test_frame = create_cyberpunk_background(480, 640)
    
    # Ví dụ landmarks (hand landmarks hoặc face landmarks)
    test_landmarks = [
        (100, 100),
        (200, 150),
        (300, 200),
        (400, 250),
        (500, 300)
    ]
    
    # Ví dụ gesture
    test_gesture = "Thumbs Up"
    
    # Ví dụ servo angles (cánh tay robot có 4 servo)
    test_angles = {
        "Servo 1": 45.0,
        "Servo 2": 90.0,
        "Servo 3": 135.0,
        "Servo 4": 60.0
    }
    
    # Tạo instance debugger
    debugger = UIDebugger("Test Debug Window")
    
    # Mô phỏng vòng lặp
    print("Nhấn 'q' để thoát cửa sổ debug")
    while True:
        # Hiển thị cửa sổ debug
        debugger.show_debug_window(test_frame, test_gesture, test_angles, test_landmarks)
        
        # Thoát khi nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    debugger.close()
    cv2.destroyAllWindows()


