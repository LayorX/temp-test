import os
import shutil

try:
    from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
    MOVIEPY_INSTALLED = True
except ImportError:
    MOVIEPY_INSTALLED = False
    print("錯誤：無法匯入 'moviepy.editor'。")
    print("請確認你已經在終端機中執行過以下指令來安裝函式庫：")
    print("pip install moviepy")
    print("-" * 20)
    print("如果你遇到 `ModuleNotFoundError` 錯誤，這可能是因為新版本的相容性問題。")
    print("可以嘗試安裝舊版，例如 1.0.3：")
    print("pip install moviepy==1.0.3")
    print("-" * 20)
    print("如果你已經安裝過，請檢查 VS Code 是否使用了正確的 Python 解釋器。")
    print("請點擊 VS Code 編輯器右下角的 Python 版本，切換到正確的環境。")


def convert_videos_in_folder(
    folder_path,
    output_path,
    target_aspect_ratio,
    conversion_method,
    output_suffix="_Shorts"
):
    """
    此函數會遍歷指定資料夾中的影片，並將其轉換為目標長寬比，然後輸出到新的資料夾。

    Args:
        folder_path (str): 影片所在的資料夾路徑。
        output_path (str): 轉換後檔案要儲存的資料夾路徑。
        target_aspect_ratio (str): 目標長寬比，例如 "1:1" 或 "9:16"。
        conversion_method (str): 轉換方法，可以是 "crop" (裁剪) 或 "letterbox" (加黑邊)。
        output_suffix (str): 轉換後檔案名稱的後綴，預設為 "_Shorts"。
    """
    if not MOVIEPY_INSTALLED:
        return

    # 檢查輸入資料夾路徑是否存在
    if not os.path.isdir(folder_path):
        print(f"錯誤：指定的輸入資料夾路徑不存在 -> {folder_path}")
        return

    # 建立輸出資料夾，如果它不存在的話
    if not os.path.exists(output_path):
        print(f"建立輸出資料夾：{output_path}")
        os.makedirs(output_path)

    print(f"正在處理資料夾：{folder_path}")

    # 解析目標長寬比
    try:
        w_ratio, h_ratio = map(int, target_aspect_ratio.split(':'))
        if w_ratio <= 0 or h_ratio <= 0:
            raise ValueError
    except ValueError:
        print("錯誤：長寬比格式不正確。請使用例如 '1:1' 或 '9:16' 的格式。")
        return

    # 遍歷資料夾中的所有項目
    for filename in os.listdir(folder_path):
        old_file_path = os.path.join(folder_path, filename)

        # 只處理影片檔案 (可根據需要添加更多副檔名)
        if os.path.isfile(old_file_path) and filename.lower().endswith(('.mp4', '.mov', '.avi')):
            try:
                # 載入影片
                clip = VideoFileClip(old_file_path)

                # 計算目標尺寸
                original_width, original_height = clip.size
                original_aspect = original_width / original_height
                target_aspect = w_ratio / h_ratio

                new_clip = None

                if conversion_method == "crop":
                    # 裁剪方法：移除多餘的邊緣
                    print(f"  正在使用 '裁剪' 方法轉換 {filename}...")
                    
                    if original_aspect > target_aspect:
                        # 影片較寬，裁剪左右兩側
                        new_width = int(original_height * target_aspect)
                        # 確保寬度為偶數
                        new_width = new_width if new_width % 2 == 0 else new_width - 1
                        x_center = original_width / 2
                        new_clip = clip.crop(x_center=x_center, width=new_width)
                    else:
                        # 影片較高，裁剪上下兩側
                        new_height = int(original_width / target_aspect)
                        # 確保高度為偶數
                        new_height = new_height if new_height % 2 == 0 else new_height - 1
                        y_center = original_height / 2
                        new_clip = clip.crop(y_center=y_center, height=new_height)

                elif conversion_method == "letterbox":
                    # 加黑邊方法：在影片周圍加上黑邊
                    print(f"  正在使用 '加黑邊' 方法轉換 {filename}...")
                    
                    if original_aspect > target_aspect:
                        # 影片較寬，加上下黑邊
                        final_width = original_width
                        final_height = int(original_width / target_aspect)
                        # 確保高度為偶數
                        final_height = final_height if final_height % 2 == 0 else final_height - 1
                    else:
                        # 影片較高，加左右黑邊
                        final_width = int(original_height * target_aspect)
                        # 確保寬度為偶數
                        final_width = final_width if final_width % 2 == 0 else final_width - 1
                        final_height = original_height
                    
                    # 建立一個黑色背景
                    background = ColorClip((final_width, final_height), color=(0,0,0)).set_duration(clip.duration)
                    
                    # 將原始影片置於黑色背景的中央
                    new_clip = CompositeVideoClip([background, clip.set_pos("center")]).set_duration(clip.duration)
                else:
                    print(f"錯誤：無效的轉換方法 '{conversion_method}'。請選擇 'crop' 或 'letterbox'。")
                    continue

                if new_clip:
                    # 產生新的檔名
                    name, extension = os.path.splitext(filename)
                    new_filename = f"{name}{output_suffix}{extension}"
                    new_file_path = os.path.join(output_path, new_filename)

                    # 儲存新影片
                    print(f"  正在儲存新檔案：{new_filename}")
                    new_clip.write_videofile(
                        new_file_path, 
                        codec='mpeg4',
                        preset='medium',
                        fps=clip.fps
                    )
                    print(f"  檔案轉換成功！\n")
            
            except Exception as e:
                print(f"處理檔案 {filename} 時發生錯誤: {e}")
            finally:
                if 'clip' in locals():
                    clip.close()
                if 'new_clip' in locals() and new_clip is not None:
                    new_clip.close()


# --- 主要執行區塊 ---
if __name__ == "__main__":
    # TODO: 在執行此腳本前，請確認已安裝 moviepy 函式庫。
    #      安裝步驟：
    #      1. 打開你的終端機 (Terminal) 或命令提示字元 (Command Prompt)。
    #      2. 複製並貼上以下指令，然後按 Enter：
    #         pip install moviepy
    #      3. 如果你遇到 `ModuleNotFoundError` 錯誤，這可能是因為新版本的相容性問題。
    #         可以嘗試安裝舊版，例如 1.0.3：
    #         pip install moviepy==1.0.3
    #
    #      如果安裝遇到問題，通常是因為缺少 FFmpeg，
    #      moviepy 預設會自動下載，但你也可以手動安裝。
    
    # 1. 指定要處理的資料夾路徑 (絕對或相對路徑皆可)
    folder_to_process = "work_place"
    
    # 2. 指定輸出資料夾路徑 (絕對或相對路徑皆可)
    output_path = "output_place"
    
    # 3. 設定目標長寬比 ("1:1" 或 "9:16")
    target_ratio = "9:16"
    
    # 4. 設定轉換方法 ("crop" (裁剪) 或 "letterbox" (加黑邊))
    method = "crop"
    
    # 5. 設定新檔名的後綴
    suffix = "_Shorts"
    
    # 執行影片轉換
    convert_videos_in_folder(
        folder_to_process,
        output_path,
        target_ratio,
        method,
        suffix
    )
