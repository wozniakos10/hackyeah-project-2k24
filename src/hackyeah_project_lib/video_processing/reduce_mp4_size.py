import os

import ffmpeg

"""
REDUCE MP4 to 20 MB
"""


# inpt = '/Users/dtomal/Documents/hackyeah-project-2k24/data_mp4/HY_2024_film_09.mp4'
def compress_video(video_full_path: str, output_file_name: str, target_size: int = 7 * 1000) -> None:
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe["format"]["duration"])
    # Audio bitrate, in bps.
    audio_bitrate = float(
        next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)["bit_rate"]  # type: ignore
    )
    # Target total bitrate, in bps.
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    # Target audio bitrate, in bps
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(
        i, os.devnull, **{"c:v": "libx264", "b:v": video_bitrate, "pass": 1, "f": "mp4"}
    ).overwrite_output().run()
    ffmpeg.output(
        i, output_file_name, **{"c:v": "libx264", "b:v": video_bitrate, "pass": 2, "c:a": "aac", "b:a": audio_bitrate}
    ).overwrite_output().run()


# Compress input.mp4 to 20MB and save as output.mp4
# compress_video(inpt, 'output.mp4', 10 * 1000)
