from typing import Tuple
from plugins.revLibs.pkg.models.interface import RevLibInterface

 # from revChatGPT.V1 import Chatbot
import asyncio
from EdgeGPT import Chatbot

import threading
__thr_lock__: threading.Lock = threading.Lock()

import logging
# 一个名为 `RevChatGPTV1` 的类，该类继承了 `RevLibInterface` 类。
# 它是一个逆向库接口，用于与 `ChatGPT` 聊天机器人进行交互。
class RevChatGPTV1(RevLibInterface):
    """acheong08/ChatGPT的逆向库接口 V1"""
    chatbot: Chatbot = None
# 在类的初始化函数 `__init__` 中，它创建了一个名为 `chatbot` 的 `Chatbot` 对象，
    # 用于与 `ChatGPT` 进行通信。`Chatbot` 对象的配置信息取自 `revcfg.openai_account`。
    def __init__(self):
        import revcfg
        self.chatbot = Chatbot(
            cookiePath="C://cookies.json"
            # config=revcfg.openai_account
        )
#`get_rev_lib_inst` 方法返回 `chatbot` 对象。
    def get_rev_lib_inst(self):
        return self.chatbot
#`get_reply` 方法接收一个字符串类型的 `prompt` 参数作为输入，并返回一个元组，
    # 包含两个值：一个字符串类型的响应消息和一个字典类型的响应信息。
    # 该方法的实现主要是通过调用 `chatbot` 对象的 `ask` 方法来获取回复。
    # 在获取到回复后，它会检查回复消息的长度是否达到了 `revcfg.blog_msg_threshold`，
    # 如果是，则将消息进行分节处理。函数中的 `yield` 关键字用于返回生成器对象，每次迭代会产生一组回复。
    def get_reply(self, prompt: str, **kwargs) -> Tuple[str, dict]:
        import revcfg
        try:
            __thr_lock__.acquire()
            if self.chatbot is None:
                raise Exception("acheong08/ChatGPT.V1 逆向接口未初始化")
            
            reply_gen = self.chatbot.generate_response(prompt, **kwargs)
            already_reply_msg = ""
            reply = {}

            first_received = False
            for r in reply_gen:
                if not first_received:
                    first_received = True
                    logging.debug("已响应，正在接收...")
                reply = r

                if "message" in reply:
                    assert isinstance(reply['message'], str)
                    reply['message'] = reply['message'].replace(already_reply_msg, "")

                # 判断是否达到分节长度
                if "message" in reply and len(reply['message']) >= revcfg.blog_msg_threshold:
                    yield reply['message'], reply
                    already_reply_msg += reply['message']
                    reply = {}

            logging.debug("接收完毕: {}".format(reply))

            yield reply['message'], reply
        finally:
            __thr_lock__.release()

    def reset_chat(self):
        self.chatbot.reset_chat()

    def rollback(self):
        self.chatbot.rollback_conversation()