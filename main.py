import traceback

from pkg.plugin.models import *
from pkg.plugin.host import EventContext, PluginHost

import os

from revChatGPT.V1 import Chatbot

"""
接入ChatGPT的逆向库
"""


def check_config():
    this_file = __file__

    template_file = os.path.join(os.path.dirname(this_file), "revcfg-template.py")

    # 检查revlib.py是否存在
    if not os.path.exists("revcfg.py"):
        # 不存在则使用本模块同目录的revcfg-template.py复制创建
        with open(template_file, "r", encoding="utf-8") as f:
            template = f.read()

        with open("revcfg.py", "w", encoding="utf-8") as f:
            f.write(template)

        return False

    return True


# 注册插件
@register(name="revLibs", description="接入acheong08/ChatGPT等逆向库", version="0.1", author="RockChinQ")
class HelloPlugin(Plugin):

    chatbot: Chatbot = None

    # 插件加载时触发
    def __init__(self, plugin_host: PluginHost):
        if not check_config():
            logging.error("[rev] 已生成配置文件(revcfg.py)，请按照其中注释填写配置文件后重启程序")
            # plugin_host.notify_admin("[rev] 已生成配置文件(revcfg.py)，请按照其中注释填写配置文件后重启程序")
            return

        import revcfg

        try:
            self.chatbot = Chatbot(
                config=revcfg.openai_account
            )
            # plugin_host.notify_admin("[rev] 逆向库初始化成功")
        except:
            # 输出完整的错误信息
            # plugin_host.notify_admin("[rev] 逆向库初始化失败，请检查配置文件(revcfg.py)是否正确")
            logging.error("[rev] 逆向库初始化失败，请检查配置文件(revcfg.py)是否正确")
            logging.error("[rev] " + traceback.format_exc())
            return

        # 当收到个人消息时触发
        @on(PersonNormalMessageReceived)
        def person_normal_message_received(inst, event: EventContext, **kwargs):
            if self.chatbot is None:
                return

            reply_dict = inst.make_reply(
                            prompt=kwargs['text_message']
                        )

            logging.debug("[rev] " + str(reply_dict))
            
            event.add_return(
                "reply",
                ["{}".format(revcfg.reply_prefix)+reply_dict['message']],
            )
            event.prevent_default()
            event.prevent_postorder()

        # 当收到群消息时触发
        @on(GroupNormalMessageReceived)
        def group_normal_message_received(inst, event: EventContext, **kwargs):
            pass

    def make_reply(self, prompt, **kwargs) -> dict:
        reply_gen = self.chatbot.ask(prompt, **kwargs)
        reply = {}

        for r in reply_gen:
            reply = r

        return reply

    # 插件卸载时触发
    def __del__(self):
        pass
