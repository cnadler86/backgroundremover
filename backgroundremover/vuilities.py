import subprocess as sp
import os
import ffmpeg
from pydantic import FilePath

def transparentvideo_bluescreen_compressed(file_path, matte_key_file, output=None,*, mode="slow", bg_color="blue"):
    # Inputs
    file_path= os.path.abspath(file_path)
    matte_key_file= os.path.abspath(matte_key_file)
    preset = "slow" if mode == "slow" else "fast"

    probe = ffmpeg.probe(file_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    print(f"Starting background color merge with compression for video {width}x{height}")

    if output is None:
        base, _ = os.path.splitext(file_path)
        output = base + "_out" + ".mp4"

    # Adjust preset based on mode


    # Using the matte as a mask to blend between original video and solid color
    cmd = [
        'ffmpeg', '-y',
        '-i', file_path,
        '-i', matte_key_file,
        '-filter_complex', f"[1][0]scale2ref[mask][main];[main][mask]alphamerge[fg];color=c={bg_color}:s={width}x{height}[bg];[bg][fg]overlay=format=auto",
        '-shortest', '-preset', preset, '-pix_fmt', 'yuv420p', output
    ]

    sp.run(cmd)
    print("Process finished")

if __name__ == "__main__":
    transparentvideo_bluescreen_compressed("/home/nadlech/vision-dl/backgroundremover/Test1.mp4", "/home/nadlech/vision-dl/backgroundremover/Test1_MK.mp4")
    