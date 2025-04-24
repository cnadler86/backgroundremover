import subprocess as sp
import os
import ffmpeg
from pydantic import FilePath

def transparentvideo_bluescreen_compressed(file_path, matte_key_file, output=None,*, mode="slow", bg_color="blue"):
    # Get video information
    file_path= os.path.abspath(file_path)
    matte_key_file= os.path.abspath(matte_key_file)
    probe = ffmpeg.probe(file_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    print(f"Starting background color merge with compression for video {width}x{height}")

    if output is None:
        base, ext = os.path.splitext(file_path)
        output = base + "_out" + ".mp4"

    # Adjust preset based on mode
    preset = "slow" if mode == "slow" else "fast"

    # Using the matte as a mask to blend between original video and solid color
    cmd = [
        'ffmpeg', '-y',
        '-i', file_path,      # Input 0: Original video
        '-i', matte_key_file,      # Input 1: Matte video
        '-f', 'lavfi',
        '-i', f'color=c={bg_color}:s={width}x{height}:r=25',  # Input 2: Solid color with matching dimensions
        '-filter_complex',
        '[0:v][1:v]scale2ref[main][mask];[2:v][main]scale2ref=flags=neighbor[bg][main];[main][mask][bg]maskedmerge',
        '-c:v', 'libx264', '-crf', '0', '-preset', preset, '-pix_fmt', 'yuv420p', '-shortest', output
    ]

    cmd = [
        'ffmpeg', '-y',
        '-i', file_path,
        '-i', matte_key_file,
        '-filter_complex', f"[1][0]scale2ref[mask][main];[main][mask]alphamerge[fg];color=c={bg_color}:s={width}x{height}[bg];[bg][fg]overlay=format=auto:shortest=1",
        '-pix_fmt', 'yuv420p', output
    ]

    sp.run(cmd)
    print("Process finished")

if __name__ == "__main__":
    transparentvideo_bluescreen_compressed("/home/nadlech/vision-dl/backgroundremover/IMG_0750.mov", "/home/nadlech/vision-dl/backgroundremover/IMG_0750_MK.mp4")