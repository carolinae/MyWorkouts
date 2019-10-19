import uuid


class Workout:
    def __init__(self, name, description, length, video_url, type, user_id, id=None):
        self.name = name.title()
        self.description = description.title()
        self.length = length
        self.video_url = video_url
        self.type = type
        self.user_id = user_id


        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

    def get_yt_id(self):
        return self.video_url[self.video_url.find("=")+1:]

    def get_img_url(self):
        yt_id = self.get_yt_id()
        return "https://img.youtube.com/vi/" + yt_id + "/hqdefault.jpg"

    def get_video_frame(self):
        yt_id = self.get_yt_id()
        return '<iframe width="560" height="315" src="https://www.youtube.com/embed/'+yt_id+'?rel=0&amp;autoplay=1&amp;controls=0&amp;showinfo=0" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
