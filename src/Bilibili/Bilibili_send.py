import requests
import time

class sendDanmu():
    def __init__(self,room):
        self.url   = 'https://api.live.bilibili.com/msg/send'
        self.form =  {
                    'color': '65532',
                    'fontsize': '25',
                    'mode': '1',
                    'msg': '1', #需要发送的内容
                    'rnd': 'None',
                    'roomid': '{}'.format(room),
                    'bubble': '0',
                    'csrf_token': 'b340b0cd129e1ad0b33a8a1e71b2e161',
                    'csrf': 'b340b0cd129e1ad0b33a8a1e71b2e161',
                }  #表单 -->  字典
        self.cookie = {
        'Cookie':"_uuid=C5BACEF2-1514-3461-D15C-585BE0A1399272735infoc; LIVE_BUVID=AUTO8315659675725482; INTVER=1; sid=jekf8012; bsource=seo_baidu; CURRENT_FNVAL=16; rpdid=|(J|)RY~JmJl0J'ulm|)kJu)|; DedeUserID=25661604; DedeUserID__ckMd5=7a26f5c94805d217; SESSDATA=95d08c25%2C1606375269%2Ca4fdb*51; bili_jct=b340b0cd129e1ad0b33a8a1e71b2e161; CURRENT_QUALITY=120; bp_t_offset_25661604=399139454077114386; buvid3=902ACE2E-E2A6-4DED-98FB-8AE2894DBE8B155838infoc; _dfcaptcha=6b4ba732932c5c73043d46802f80e661; PVID=3"
    }
    #构造请求
    def send(self,danmu,room):
        t = int(time.time())
        self.form['msg'] = danmu
        self.form['rnd'] = t
        self.form['roomid'] = room
        try:
            requests.post(self.url,data=self.form,cookies=self.cookie)
            print('发送{}完成。'.format(danmu))
        except:
            print("发送失败！")
