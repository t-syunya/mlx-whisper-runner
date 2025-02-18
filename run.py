import os
import subprocess
from glob import glob
from pathlib import Path

# 設定
file = "2025-01-22_2.mp3"
base_dir = Path("data")
input_file = base_dir / "inputs" / file
split_dir = base_dir / "split_audio" / file.split(".")[0]
output_dir = base_dir / "outputs/" / file.split(".")[0]
segment_time = 180  # 分割時間（秒）

os.makedirs(split_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# ffmpeg で音声を分割
split_command = (
    "ffmpeg",
    "-i",
    input_file,
    "-f",
    "segment",
    "-segment_time",
    str(segment_time),
    "-c",
    "copy",
    os.path.join(split_dir, "part_%03d" + file.split(".")[1]),
)
subprocess.run(split_command, check=True)

# Step 2: mlx_whisper で各ファイルを処理
split_files = sorted(glob(os.path.join(split_dir, "part_*.mp3")))
output_texts = []

for file in split_files:
    whisper_command = (
        "mlx_whisper",
        "--model",
        "mlx-community/whisper-large-v3-mlx",
        "--output-dir",
        output_dir,
        file,
    )
    subprocess.run(whisper_command, check=True)

    # 出力されたテキストファイルを取得
    txt_file = os.path.join(
        output_dir, os.path.basename(file).replace(file.split(".")[1], ".txt")
    )
    if os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            output_texts.append(f.read())

# Step 3: すべてのテキストを結合
final_output_file = os.path.join(output_dir, "final_transcription.txt")
with open(final_output_file, "w", encoding="utf-8") as f:
    f.write("\n\n".join(output_texts))

print(f"処理完了！結果は {final_output_file} に保存されました。")
