import cv2
import numpy as np
import os

# 测试图片读取功能
test_image_path = r"d:\project\AIproject\异环小工具\images\shop_templates\image1.png"

print(f"测试图片路径: {test_image_path}")
print(f"文件是否存在: {os.path.exists(test_image_path)}")
if os.path.exists(test_image_path):
    print(f"文件大小: {os.path.getsize(test_image_path)} 字节")
    
    # 测试方法1: 直接使用cv2.imread
    print("\n--- 测试 cv2.imread ---")
    img1 = cv2.imread(test_image_path)
    if img1 is not None:
        print(f"成功读取! 形状: {img1.shape}")
    else:
        print("读取失败!")
    
    # 测试方法2: 使用numpy.fromfile + cv2.imdecode
    print("\n--- 测试 numpy.fromfile + cv2.imdecode ---")
    try:
        img_data = np.fromfile(test_image_path, dtype=np.uint8)
        print(f"读取到 {len(img_data)} 字节数据")
        img2 = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        if img2 is not None:
            print(f"成功解码! 形状: {img2.shape}")
        else:
            print("解码失败!")
    except Exception as e:
        print(f"发生异常: {e}")
