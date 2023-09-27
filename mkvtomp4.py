import os
import subprocess

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
        input_dir = os.path.dirname(input_file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]

        # Construct the output file path
        output_file = os.path.join(converted_folder, f"{base_name}.mp4")

        # Construct the FFmpeg command
        ffmpeg_command = [
            "ffmpeg",
            "-i", input_file,
            "-c", "copy",
        ]

        # Check for the presence of subtitle streams
        subtitle_stream_count = get_stream_count(input_file, "s")
        if subtitle_stream_count > 0:
            print(f"Subtitle stream(s) detected : {subtitle_stream_count}\n\n")
            ffmpeg_command.extend(["-c:s", "mov_text"]) #this doesnt work yet

        ffmpeg_command.extend(["-strict", "unofficial", output_file])

        try:
            # Run FFmpeg command
            subprocess.run(ffmpeg_command, check=True)
            print(f"Conversion of file complete. Output file: {output_file} \n\n\n")
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

if __name__ == "__main__":
    main()
