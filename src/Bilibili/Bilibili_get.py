import requests


class getDanmu():
    url = "https://api.live.bilibili.com/ajax/msg"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://live.bilibili.com/blanc/55?liteVersion=true",
        "Content-Length": "107",
        "Host": "api.live.bilibili.com"
    }

    def __init__(self, roomid, csrf):
        self.roomid = roomid
        self.csrf_token = csrf
        self.csrf = csrf

    def post_it(self):
        data = {"roomid": self.roomid,
                "csrf_token": self.csrf_token,
                "csrf": self.csrf,
                "visit_id": ""}
        self.session = requests.Session()
        self.json_data = self.session.post(url=self.url,
                                           headers=self.headers,
                                           data=data).json()

    def getDanmu(self):
        datas = self.json_data['data']['room']
        for data in datas:
            try:
                nickname = data['nickname']
            except UnicodeEncodeError:  # 这里的原因是print无法打印特殊字符
                # 虽然有解决方案，但是没必要
                nickname = "非法字符，无法print"
            try:
                text = data['text']
            except UnicodeEncodeError:
                text = "非法字符，无法print"
            print("{} :{}".format(nickname, text))


if __name__ == '__main__':
    roomid = "21937638"  # 填写roomid
    csrf = "b340b0cd129e1ad0b33a8a1e71b2e161"  # 填写csrf
    danmu = getDanmu(roomid, csrf)
    danmu.post_it()
    danmu.getDanmu()