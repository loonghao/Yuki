class YukiError(Exception):
    """Base class for all Yuki exceptions."""
    pass


class FfmpegError(Exception):
    """Basic exception for errors raised by ffmpeg.

    Attributes:
        cmd (list): The ffmpeg command that was run when the error was raised.
        stdout (str): The output captured from the ffmpeg execution.
        stderr (str): The error captured from the ffmpeg execution.

    """

    def __init__(self, msg, cmd, stdout, stderr):
        """Use last line as error message when given empty msg."""
        if not msg:
            msg = stderr.splitlines()[-1]
        super(FfmpegError, self).__init__(msg)
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr
