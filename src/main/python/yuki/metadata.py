# Import built-in modules
from pprint import pformat
import os

# Import third-party modules
import ffmpeg

# Import local modules
from yuki.error import FfmpegError


class VideoMetadata:
    data = None

    @classmethod
    def get_metadata(cls, video_file):
        cls.data = ffmpeg.probe(video_file)
        return cls()

    @property
    def fps(self):
        return int(self.video["r_frame_rate"].split("/")[0])

    @property
    def frame_count(self):
        return self.video["duration_ts"]

    def __str__(self):
        return pformat(self.data)

    @property
    def streams(self):
        return self.data["streams"]

    @staticmethod
    def get_temp_thumb_dir(drag_path):
        return os.path.join(drag_path, "thumbs")

    @classmethod
    def export_thumbnail(cls, video_file):
        video_metadata = cls()
        drag_path, mov_name = os.path.split(video_file)
        path, _ = os.path.splitext(video_file)
        thumb_dir = video_metadata.get_temp_thumb_dir(drag_path)
        if not os.path.isdir(thumb_dir):
            os.makedirs(thumb_dir)
        thumb_file = os.path.join(thumb_dir,
                                  '{}.jpg'.format(mov_name.split('.')[0]))
        thumb_file = thumb_file.replace('/', '\\')
        process = (
            ffmpeg
                .input(video_file)
                .filter("scale", 600, -1)
                .output(thumb_file, vframes=1, format='image2', vcodec='mjpeg')
                .overwrite_output()
        )
        ffmpeg_cmd = process.compile()
        process = process.run_async(pipe_stdout=True, pipe_stderr=True)

        out, err = process.communicate()

        if process.returncode:
            raise FfmpegError("", cmd=ffmpeg_cmd, stdout=out, stderr=err)
        return thumb_file

    def __getattribute__(self, item):
        if item == "video" or item == "audio":
            for info in self.streams:
                if info["codec_type"].lower() == item:
                    return info
        return super().__getattribute__(item)

    @property
    def width(self):
        return self.video["width"]

    @property
    def height(self):
        return self.video["height"]

    @property
    def duration(self):
        return self.video["duration"]


if __name__ == '__main__':
    data = VideoMetadata.export_thumbnail(r"C:\test\maya_api.mp4")
    print(data)
