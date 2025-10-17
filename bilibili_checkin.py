import json
import os
import time
import requests

class BiliBili:
    def __init__(self, check_item: dict):
        self.check_item = check_item

    @staticmethod
    def get_nav(session):
        url = "https://api.bilibili.com/x/web-interface/nav"
        ret = session.get(url=url).json()
        uname = ret.get("data", {}).get("uname")
        uid = ret.get("data", {}).get("mid")
        is_login = ret.get("data", {}).get("isLogin")
        coin = ret.get("data", {}).get("money")
        vip_type = ret.get("data", {}).get("vipType")
        current_exp = ret.get("data", {}).get("level_info", {}).get("current_exp")
        return uname, uid, is_login, coin, vip_type, current_exp

    @staticmethod
    def get_today_exp(session: requests.Session) -> list:
        """GET 获取今日经验信息"""
        url = "https://api.bilibili.com/x/member/web/exp/log?jsonp=jsonp"
        today = time.strftime("%Y-%m-%d", time.localtime())
        return list(
            filter(
                lambda x: x["time"].split()[0] == today,
                session.get(url=url).json().get("data").get("list"),
            )
        )

    @staticmethod
    def vip_privilege_my(session) -> dict:
        """取B站大会员硬币经验信息"""
        url = "https://api.bilibili.com/x/vip/privilege/my"
        ret = session.get(url=url).json()
        return ret

    @staticmethod
    def live_sign(session) -> str:
        """B站直播签到"""
        try:
            url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
            ret = session.get(url=url).json()
            if ret["code"] == 0:
                msg = f"签到成功，{ret['data']['text']}，特别信息:{ret['data']['specialText']}，本月已签到{ret['data']['hadSignDays']}天"
            elif ret["code"] == 1011040:
                msg = "今日已签到过,无法重复签到"
            else:
                msg = f"签到失败，信息为: {ret['message']}"
        except Exception as e:
            msg = f"签到异常，原因为{e}"
        return msg

    @staticmethod
    def manga_sign(session, platform="android") -> str:
        """模拟B站漫画客户端签到"""
        try:
            url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
            post_data = {"platform": platform}
            ret = session.post(url=url, data=post_data).json()
            if ret["code"] == 0:
                msg = "签到成功"
            elif ret["msg"] == "clockin clockin is duplicate":
                msg = "今天已经签到过了"
            else:
                msg = f"签到失败，信息为({ret['msg']})"
        except Exception as e:
            msg = f"签到异常,原因为: {e}"
        return msg

    @staticmethod
    def vip_privilege_receive(session, bili_jct, receive_type: int = 1) -> dict:
        """领取B站大会员权益"""
        url = "https://api.bilibili.com/x/vip/privilege/receive"
        post_data = {"type": receive_type, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def report_task(session, bili_jct, aid: int, cid: int, progres: int = 300) -> dict:
        """B站上报视频观看进度"""
        url = "http://api.bilibili.com/x/v2/history/report"
        post_data = {"aid": aid, "cid": cid, "progres": progres, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def share_task(session, bili_jct, aid) -> dict:
        """分享指定av号视频"""
        url = "https://api.bilibili.com/x/web-interface/share/add"
        post_data = {"aid": aid, "csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def get_followings(session, uid: int, pn: int = 1, ps: int = 50) -> dict:
        """获取指定用户关注的up主"""
        params = {
            "vmid": uid,
            "pn": pn,
            "ps": ps,
            "order": "desc",
            "order_type": "attention",
        }
        url = "https://api.bilibili.com/x/relation/followings"
        ret = session.get(url=url, params=params).json()
        return ret

    @staticmethod
    def space_arc_search(session, uid: int, pn: int = 1, ps: int = 30) -> tuple:
        """获取指定up主空间视频投稿信息"""
        params = {
            "mid": uid,
            "pn": pn,
            "Ps": ps,
            "tid": 0,
            "order": "pubdate",
            "keyword": "",
        }
        url = "https://api.bilibili.com/x/space/arc/search"
        ret = session.get(url=url, params=params).json()
        count = 2
        data_list = [
            {
                "aid": one.get("aid"),
                "cid": 0,
                "title": one.get("title"),
                "owner": one.get("author"),
            }
            for one in ret.get("data", {}).get("list", {}).get("vlist", [])[:count]
        ]
        return data_list, count

    @staticmethod
    def coin_add(session, bili_jct, aid: int, num: int = 1, select_like: int = 1) -> dict:
        """给指定 av 号视频投币"""
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        post_data = {
            "aid": aid,
            "multiply": num,
            "select_like": select_like,
            "cross_domain": "true",
            "csrf": bili_jct,
        }
        ret = session.post(url=url, data=post_data).json()
        return ret

    @staticmethod
    def live_status(session) -> list:
        """B站直播获取金银瓜子状态"""
        url = "https://api.live.bilibili.com/pay/v1/Exchange/getStatus"
        ret = session.get(url=url).json()
        data = ret.get("data")
        silver = data.get("silver", 0)
        gold = data.get("gold", 0)
        coin = data.get("coin", 0)
        msg = [
            {"name": "硬币数量", "value": coin},
            {"name": "金瓜子数", "value": gold},
            {"name": "银瓜子数", "value": silver},
        ]
        return msg

    @staticmethod
    def get_region(session, rid=1, num=6) -> list:
        """获取 B站分区视频信息"""
        url = "https://api.bilibili.com/x/web-interface/dynamic/region?ps=" + str(num) + "&rid=" + str(rid)
        ret = session.get(url=url).json()
        data_list = [
            {
                "aid": one.get("aid"),
                "cid": one.get("cid"),
                "title": one.get("title"),
                "owner": one.get("owner", {}).get("name"),
            }
            for one in ret.get("data", {}).get("archives", [])
        ]
        return data_list

    @staticmethod
    def silver2coin(session, bili_jct) -> dict:
        """B站银瓜子换硬币"""
        url = "https://api.live.bilibili.com/xlive/revenue/v1/wallet/silver2coin"
        post_data = {"csrf": bili_jct}
        ret = session.post(url=url, data=post_data).json()
        return ret

    def main(self):
        bilibili_cookie = {item.split("=")[0]: item.split("=")[1] for item in self.check_item.get("cookie").split("; ")}
        bili_jct = bilibili_cookie.get("bili_jct")
        coin_num = self.check_item.get("coin_num", 0)
        coin_type = self.check_item.get("coin_type", 1)
        silver2coin = self.check_item.get("silver2coin", True)
        
        session = requests.session()
        requests.utils.add_dict_to_cookiejar(session.cookies, bilibili_cookie)
        session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
                "Referer": "https://www.bilibili.com/",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Connection": "keep-alive",
            }
        )
        
        success_count = 0
        uname, uid, is_login, coin, vip_type, current_exp = self.get_nav(session=session)
        
        if not is_login:
            return "登录失败，请检查cookie是否有效"
            
        manhua_msg = self.manga_sign(session=session)
        live_msg = self.live_sign(session=session)
        
        # 获取视频列表用于投币、分享、观看
        aid_list = self.get_region(session=session)
        
        # 大会员权益领取
        vip_privilege_my_ret = self.vip_privilege_my(session=session)
        welfare_list = vip_privilege_my_ret.get("data", {}).get("list", [])
        for welfare in welfare_list:
            if welfare.get("state") == 0 and welfare.get("vip_type") == vip_type:
                self.vip_privilege_receive(
                    session=session,
                    bili_jct=bili_jct,
                    receive_type=welfare.get("type"),
                )
        
        # 投币任务
        coins_av_count = len(
            list(
                filter(
                    lambda x: x["reason"] == "视频投币奖励",
                    self.get_today_exp(session=session),
                )
            )
        )
        coin_num = coin_num - coins_av_count
        coin_num = coin_num if coin_num < coin else coin
        
        if coin_type == 1 and coin_num > 0:
            following_list = self.get_followings(session=session, uid=uid)
            count = 0
            for following in following_list.get("data", {}).get("list", []):
                mid = following.get("mid")
                if mid:
                    tmplist, tmpcount = self.space_arc_search(session=session, uid=mid)
                    aid_list += tmplist
                    count += tmpcount
                    if count > coin_num:
                        break
        
        if coin_num > 0:
            for aid in aid_list[::-1]:
                if coin_num <= 0:
                    break
                ret = self.coin_add(session=session, aid=aid.get("aid"), bili_jct=bili_jct)
                if ret["code"] == 0:
                    coin_num -= 1
                    success_count += 1
                elif ret["code"] == 34005:
                    continue
                else:
                    break
            coin_msg = f"今日成功投币{success_count + coins_av_count}/{self.check_item.get('coin_num', 5)}个"
        else:
            coin_msg = f"今日成功投币{coins_av_count}/{self.check_item.get('coin_num', 5)}个"
        
        # 观看和分享任务
        if aid_list:
            aid = aid_list[0].get("aid")
            cid = aid_list[0].get("cid")
            title = aid_list[0].get("title")
            
            report_ret = self.report_task(session=session, bili_jct=bili_jct, aid=aid, cid=cid)
            report_msg = f"观看《{title}》300秒" if report_ret.get("code") == 0 else "观看任务失败"
            
            share_ret = self.share_task(session=session, bili_jct=bili_jct, aid=aid)
            share_msg = f"分享《{title}》成功" if share_ret.get("code") == 0 else "分享失败"
        else:
            report_msg = "观看任务失败"
            share_msg = "分享失败"
        
        # 银瓜子兑换
        s2c_msg = ""
        if silver2coin:
            silver2coin_ret = self.silver2coin(session=session, bili_jct=bili_jct)
            if silver2coin_ret["code"] == 0:
                s2c_msg = "银瓜子兑换硬币成功"
            else:
                s2c_msg = f"银瓜子兑换失败: {silver2coin_ret['message']}"
        
        # 获取最新状态
        live_stats = self.live_status(session=session)
        uname, uid, is_login, new_coin, vip_type, new_current_exp = self.get_nav(session=session)
        today_exp = sum(map(lambda x: x["delta"], self.get_today_exp(session=session)))
        update_data = (28800 - new_current_exp) // (today_exp if today_exp else 1)
        
        msg = [
            {"name": "帐号信息", "value": uname},
            {"name": "漫画签到", "value": manhua_msg},
            {"name": "直播签到", "value": live_msg},
            {"name": "登陆任务", "value": "今日已登陆"},
            {"name": "观看视频", "value": report_msg},
            {"name": "分享任务", "value": share_msg},
            {"name": "投币任务", "value": coin_msg},
            {"name": "银瓜子兑换", "value": s2c_msg},
            {"name": "今日经验", "value": today_exp},
            {"name": "当前经验", "value": new_current_exp},
            {"name": "升级还需", "value": f"{update_data}天"},
            *live_stats,
        ]
        
        result_msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
        return result_msg

def load_config_from_env():
    """从环境变量加载配置"""
    config_json = os.getenv('BILIBILI_CONFIGS')
    if config_json:
        try:
            return json.loads(config_json)
        except json.JSONDecodeError:
            print("错误: BILIBILI_CONFIGS JSON格式错误")
            return None
    
    # 兼容旧版本的单账号配置
    cookie = os.getenv('BILIBILI_COOKIE')
    if cookie:
        coin_num = int(os.getenv('COIN_NUM', '5'))
        coin_type = int(os.getenv('COIN_TYPE', '0'))
        silver2coin = os.getenv('SILVER2COIN', 'True').lower() == 'true'
        
        return [{
            "cookie": cookie,
            "coin_num": coin_num,
            "coin_type": coin_type,
            "silver2coin": silver2coin
        }]
    
    return None

if __name__ == "__main__":
    # 加载配置
    configs = load_config_from_env()
    
    if not configs:
        print("错误: 未设置BILIBILI_CONFIGS环境变量或BILIBILI_COOKIE环境变量")
        exit(1)
    
    all_results = []
    
    for i, config in enumerate(configs, 1):
        print(f"\n{'='*50}")
        print(f"开始执行第 {i} 个账号签到任务")
        print(f"{'='*50}")
        
        try:
            result = BiliBili(config).main()
            all_results.append(f"账号 {i} 签到结果:\n{result}")
            print(f"第 {i} 个账号签到完成")
        except Exception as e:
            error_msg = f"账号 {i} 签到失败: {str(e)}"
            all_results.append(error_msg)
            print(error_msg)
    
    # 输出所有结果
    print(f"\n{'='*50}")
    print("所有账号签到完成")
    print(f"{'='*50}")
    
    for result in all_results:
        print(f"\n{result}")
        print("-" * 30)
