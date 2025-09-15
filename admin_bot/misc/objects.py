from typing import TypedDict, NotRequired


class UploadData(TypedDict):
    video: NotRequired[str]
    video_duration: NotRequired[int]
    cover_photo: NotRequired[str]
    setup_photo: NotRequired[str]
    finish_photo: NotRequired[str]
