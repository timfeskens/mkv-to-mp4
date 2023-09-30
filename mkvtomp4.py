import os
import subprocess
from pymediainfo import MediaInfo

def main():
    # Get the directory where the Python script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a 'Converted' folder if it doesn't exist
    converted_folder = os.path.join(script_dir, 'Converted')
    os.makedirs(converted_folder, exist_ok=True)

    # List all MKV files in the script directory
    files = [f for f in os.listdir(script_dir) if f.endswith(".mkv")]

    succesful_files = 0
    unsuccessful_files = 0

    for input_file in files:
        # Check if the file is an MKV file
        if not input_file.lower().endswith(".mkv"):
            print(f"Skipping {input_file}. Not an MKV file. \n\n")
            continue

        # Construct the full path of the input file
        input_file = os.path.join(script_dir, input_file)

        # Extract the directory path and base name without extension (for output file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]

        # Construct the output file path
        output_file = os.path.join(converted_folder, f"{base_name}.mp4")

        frame_rate = get_frame_rate(input_file)

        # Construct the FFmpeg command
        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-strict", 
            "experimental", 
            "-loglevel", 
            "error", 
            "-stats",
            "-map",
            "0:v?",
            "-map",
            "0:a?",
            "-map",
            "0:s?",
            "-dn",
            "-map_chapters",
            "-1",
            "-movflags",
            "+faststart",
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text",
            "-strict", "-2",
        ]

        ffmpeg_command.extend([output_file])

        try:
            # Run FFmpeg command
            print(f"Command is: {ffmpeg_command}")
            subprocess.run(ffmpeg_command, check=True)
            print(f"Conversion of file complete. Temp file: {output_file} \n\n\n")

            # Run MP4FPSMOD command to fix variable framerate
            subprocess.run(["./mp4fpsmod", frame_rate, "-1", output_file])
            succesful_files += 1
        except subprocess.CalledProcessError as e:
            print(f"Error: FFmpeg command failed with exit code {e.returncode} \n\n\n")
            unsuccessful_files += 1

    
    print(f"All done. succesfully converted {succesful_files} files, {unsuccessful_files} files failed. \n\n")
    input("Press Enter to finish...")

def get_stream_count(input_file, stream_type):
    try:
        # Run FFprobe to get stream count of the specified type
        ffprobe_command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", f"{stream_type}",
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

def get_frame_rate(input_file):
    try:
        media_info = MediaInfo.parse(input_file)
        for track in media_info.tracks:
            if track.track_type == 'Video':
                frame_rate = track.frame_rate
                duration = 0
                
                if frame_rate=="23.976": duration= "--fps 0:24000/1001"
                if frame_rate=="24.000": duration= "--fps 0:24"
                if frame_rate=="25.000": duration= "--fps 0:25"
                if frame_rate=="30.000": duration= "--fps 0:30"
                if frame_rate=="48.000": duration= "--fps 0:48"
                if frame_rate=="50.000": duration= "--fps 0:35"
                if frame_rate=="60.000": duration= "--fps 0:60"
                
                return duration
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    main()
