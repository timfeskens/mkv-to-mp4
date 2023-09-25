import os
import subprocess
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python mkvtomp4.py <movie_file.mkv>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' does not exist.")
        sys.exit(1)

    # Extract the directory path and base name without extension (for output file)
    input_dir = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Construct the output file path
    output_file = os.path.join(input_dir, f"{base_name}.mp4")

    # Construct the FFmpeg command
    ffmpeg_command = [
        "ffmpeg",
        "-i", input_file,
        "-map", "0:v:0",
        "-c", "copy",
    ]

    # Check for the presence of audio streams
    audio_stream_count = get_stream_count(input_file, "a")
    if audio_stream_count > 0:
        ffmpeg_command.extend(["-map", "0", "-c:a", "copy"])
        print(f"Audio stream count: {audio_stream_count}")

    # Check for the presence of subtitle streams
    subtitle_stream_count = get_stream_count(input_file, "s")
    if subtitle_stream_count > 0:
        ffmpeg_command.extend(["-c:s", "copy"])
        print(f"Subtitle stream count: {subtitle_stream_count}")
    else:
        print("No subtitle streams found in the input file. Subtitles will not be included.")

    ffmpeg_command.extend(["-strict", "unofficial", output_file])

    try:
        # Run FFmpeg command
        subprocess.run(ffmpeg_command, check=True)
        print(f"Conversion complete. Output file: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg command failed with exit code {e.returncode}")

def get_stream_count(input_file, stream_type):
    try:
        # Run FFprobe to get stream count of the specified type
        ffprobe_command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", f"{stream_type}:0",
            "-show_entries", "stream=index",
            "-of", "default=nw=1:nk=1",
            input_file,
        ]

        result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip()

        if result.returncode == 0:
            # Parse and return the stream count
            return len(output.split("\n"))
        else:
            return 0

    except Exception as e:
        return 0

if __name__ == "__main__":
    main()
