import os
import subprocess
import re
import json
from pymediainfo import MediaInfo

mp4fpsmod_path = "/Users/timfeskens/Documents/GitHub/dv-mkv-to-mp4/mp4fpsmod"

def main():
    # Get the directory where the Python script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a 'Converted' folder if it doesn't exist
    converted_folder = os.path.join(script_dir, 'Converted')
    os.makedirs(converted_folder, exist_ok=True)

    # List all MKV files in the script directory
    files = [f for f in os.listdir(script_dir) if f.endswith(".mkv")]

    successful_files = 0
    unsuccessful_files = 0

    for file in files:
        # Check if the file is an MKV file
        if not file.lower().endswith(".mkv"):
            print(f"Skipping {input_file}. Not an MKV file. \n\n")
            continue

        # Construct the full path of the input file
        input_file = os.path.join(script_dir, file)

        # Extract subtitles using mkvextract
        extract_subtitles(file, converted_folder)

        # Extract the directory path and base name without extension (for output file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]

        # Construct the output file path
        output_file = os.path.join(converted_folder, f"{base_name}.mp4")

        print("Task 5 |".rjust(11), "Getting the framerate from the videostream!")
        
        # Get the frame rate of the input file
        frame_rate = get_frame_rate(input_file)
        print("|".rjust(11), f"Frame rate is: {frame_rate}")
       

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
            "-dn",
            "-map_chapters",
            "-1",
            "-movflags",
            "+faststart",
            "-c:v", "copy",
            "-c:a", "copy",
            "-strict", "-2",
        ]

        ffmpeg_command.extend([output_file])

        try:
            # Run FFmpeg command
            print("Task 6 |".rjust(11), "Getting ffmpeg command")
            subprocess.run(ffmpeg_command, check=True)

            print("|".rjust(11), "Conversion of mkv file complete.")

            # Run MP4FPSMOD command to fix variable framerate
            print("Task 7 |".rjust(11), "Starting MP4FPSMOD to convert framerate")
            if (subprocess.run([mp4fpsmod_path, "--fps", frame_rate, "-i", output_file], check=True)):
                print("|".rjust(11), "MP4FPSMOD command complete")
                successful_files += 1
            else:
                print("|".rjust(11), "MP4FPSMOD command failed")
                unsuccessful_files += 1
        except subprocess.CalledProcessError as e:
            print("|".rjust(11), f"Error: FFmpeg command failed with exit code {e.returncode} \n\n\n")
            unsuccessful_files += 1

    
    print("|".rjust(11), f"All done. successfully converted {successful_files} files, {unsuccessful_files} files failed. \n\n")
    input("Press Enter to finish...")

def get_frame_rate(input_file):
    try:
        media_info = MediaInfo.parse(input_file)
        for track in media_info.tracks:
            if track.track_type == 'Video':
                frame_rate = track.frame_rate
                duration = 0
                
                if frame_rate=="23.976": duration= "0:24000/1001"
                if frame_rate=="24.000": duration= "0:24"
                if frame_rate=="25.000": duration= "0:25"
                if frame_rate=="30.000": duration= "0:30"
                if frame_rate=="48.000": duration= "0:48"
                if frame_rate=="50.000": duration= "0:35"
                if frame_rate=="60.000": duration= "0:60"
                
                return duration
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# Returns the media information from a mkv file
def json_mkvinfo(mkv_file):
    mkv_info = {}
    command_array = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", mkv_file]
    result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if result.returncode == 0:
        mkv_info = json.loads(result.stdout)
        print("Task 1 |".rjust(11), "Received the file info in JSON format!")
    else:
        print("Task 1 |".rjust(11), "ERROR!!", result.stderr)
        exit()

    return mkv_info


def extract_subtitles(mkv_file, converted_folder):
    directory = os.path.dirname(os.path.abspath(__file__))

    print("File Name |", mkv_file)
    mkv_file_path = os.path.join(directory, mkv_file)
    mkv_info = json_mkvinfo(mkv_file_path)

    print("Task 2 |".rjust(11), "Collecting the streams (tracks) info.")
    streams = mkv_info["streams"]

    if len(streams) ==  0:
        print("|".rjust(11),"There are no streams present in this file!!")
    else:
        print("|".rjust(11), "Streams are present!")

        # Creating a suitable directory to store subtitles.
        print("Task 3 |".rjust(11), "Creating a directory to store subtitles")
        subtitles_directory_name = 'Subs'
        subtitles_directory_path = os.path.join(converted_folder, subtitles_directory_name)
        if not os.path.exists(subtitles_directory_path):
            os.makedirs(subtitles_directory_path)
            print("|".rjust(11), "Created :", subtitles_directory_name)

        print("Task 4 |".rjust(11), "Getting the subtitles from the stream!")
        count = 0
        for stream in streams:
            if stream["codec_type"] == "subtitle":
                language = stream["tags"].get("language", "und")
                title = stream["tags"].get("title", "Undefined")
                if language == "dut" or language == "eng":
                    extension = ""
                    if title == "Undefined":
                        extension = "." + language + ".srt"
                    else:
                        extension = "." + language + "." + title + ".srt"
                    subtitle_name = mkv_file.replace(".mkv", extension)
                    subtitle_path = os.path.join(subtitles_directory_path, subtitle_name)

                    # ffmpeg copies the subtitle track from the mkv file to the subtitles folder.
                    command = "ffmpeg -i \"" + mkv_file_path + "\" -map 0:s:" + str(count) + " \"" + subtitle_path + "\" -v quiet"
                    returncode = os.system(command)
                    if returncode == 0:
                        print("|".rjust(11), "Created :", subtitle_name)
                    else:
                        print("Error in creating the subtitle file!")
                count += 1
                
        if count == 0:
            print("|".rjust(11), "There are no subtitle tracks present in this file.")
        else:
            print("Total Subtitle Streams :", count)

        print('')

if __name__ == "__main__":
    main()
