"""
Copyright (c) 2025 Li Beile 李倍乐
                   email: 1617973918@qq.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import base64
import ctypes
import math
import tempfile
import turtle
from time import perf_counter
from dataclasses import dataclass
from tkinter import messagebox as mb
from typing import Tuple, Optional, Union, Literal

from _tkinter import TclError


def _get_windows_scaling() -> float:
    """
    获取Windows DPI感知缩放因子
    :return: DPI缩放因子
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    except OSError:
        return 1.0
    else:
        return max(1.0, scale_factor)


def _draw_coordinate_system(pen: turtle.Turtle, screen: turtle.Screen(), axis_length: Union[int, float] = 300,
                            tick_interval: Union[int, float] = 50, label_offset: Union[int, float] = 20):
    """
    绘制平面直角坐标系
    :param pen: Turtle画笔对象
    :param screen: Turtle屏幕对象
    :param axis_length: 坐标轴长
    :param tick_interval: 刻度间隔
    :param label_offset: 标签偏移量
    """
    tracer = screen.tracer()
    screen.tracer(0)
    pen.pencolor("gray")

    pen.penup()
    pen.goto(-axis_length, 0)
    pen.pendown()
    pen.forward(2 * axis_length)

    pen.setheading(135)
    pen.forward(10)
    pen.backward(10)
    pen.setheading(225)
    pen.forward(10)
    pen.backward(10)
    pen.setheading(0)

    pen.penup()
    pen.goto(0, -axis_length)
    pen.pendown()
    pen.setheading(90)
    pen.forward(2 * axis_length)

    pen.setheading(225)
    pen.forward(10)
    pen.backward(10)
    pen.setheading(315)
    pen.forward(10)
    pen.backward(10)
    pen.setheading(0)

    pen.penup()
    for x in range(-axis_length, axis_length + 1, tick_interval):
        if x == 0:
            continue
        pen.goto(x, 0)
        pen.pendown()
        pen.setheading(90)
        pen.forward(10)
        pen.backward(20)
        pen.penup()
        pen.goto(x, -label_offset)
        pen.write(str(x), align="center", font=("Times New Roman", 8, "normal"))

    pen.penup()
    for y in range(-axis_length, axis_length + 1, tick_interval):
        if y == 0:
            continue
        pen.goto(0, y)
        pen.pendown()
        pen.setheading(0)
        pen.forward(10)
        pen.backward(20)
        pen.penup()
        pen.goto(-label_offset, y)
        pen.write(str(y), align="right", font=("Times New Roman", 8, "normal"))

    pen.penup()
    pen.goto(axis_length + label_offset, 0)
    pen.write("x", font=("Times New Roman", 10, "italic"))
    pen.goto(0, axis_length + label_offset)
    pen.write("y", font=("Times New Roman", 10, "italic"))

    pen.home()
    screen.tracer(tracer)
    screen.update()


@dataclass(frozen=True)
class Constants:
    """
    常量类，含若干界面语言以及内嵌的Base 64编码图片
    """
    QILOU_DESC = ("骑楼是一种商住建筑，外廊式建筑结构，流行于华南、南洋等地。"
                  "它底层沿街面后退留出公共人行空间，能遮风挡雨、防晒避暑。"
                  "骑楼融合中西方建筑特色，见证了城市的商贸繁荣与多元文化交流，极具历史文化价值。")
    QILOU_NOTICE = "提示: 点击骑楼, DIY任意楼层和列数的骑楼!"
    LIONDANCE_DESC = ("岭南舞狮属南狮流派，以广东醒狮为代表，是岭南民俗文化的重要符号。"
                      "其造型夸张威武，动作刚劲有力，配合锣、鼓、镲节奏展现采青等经典套路，寓意着吉祥如意。"
                      "常出现于节庆、开业等场合，既保留传统武术精髓，又融入岭南地域的灵动风格，是非遗文化与民间智慧的结合。")
    CANTONESE_EXAMPLE = "食咗饭未？"
    CANTONESE_DESC = ("粤语是发源于岭南地区的汉语方言，保留了大量古汉语词汇和音韵特征，与普通话在发音、词汇、语法上均有显著差异。"
                      "它不仅是粤港澳及海外华人的日常交流语言，更承载着岭南文化的独特韵味，在戏曲、歌词、民间文学中广泛使用。"
                      "从“食饭”“睇戏”等日常表达到“人生不如意事十常八九”的哲理俗语，粤语以鲜活的表达记录着生活与传承。")
    LIONDANCE_BASE64 = ("R0lGODlhXgFeAYcAAAAAAAICAgMDBPPz8wQEBAQDAwcHBwQEBgYGBfPz9PPz8fPz9QUFBgkJCQMEAvPy7gwMCwsLC/Pz8g"
                        "gIB/Pz7w4ODQ0NDQUFBPP08QoKCfLy8wUFA3Bwb1RVU1hYV/Ly8QoKDPPy7wcHCAQEBxMTE0A/P/Lx7VtbWREREQUFCAgI"
                        "ClZWVGRkYxcXFxUUFfLy8GJiYmBgXxISEAsLCg8PDwkJCBAQDgcHBvLy9O/v7VlZWGNjYVdXVR0dG2xsaw0MD2ZmZlxcWy"
                        "UlJB8fHfDw8jAwLllZVmhoZxISEV9fXiYmJRYWFUVFRF1dXSMiIwwLDfDw7hAQD19fXR4eHDU1NRoaGSAgH2JhYBQTEiQk"
                        "IvDw8GdnZScnJ4SEg3R0c0dGRQYGBHx9exUVE2VlZBQUEkpKSiIiIVNTUUNCQzIyMFFRT2BgYUtLSlpaWz4+PRkZGisqKk"
                        "5NTVFQUIKCgBkYGEJCQV5eXT09O+zs6oCAfyoqKExMS3JycDs7OSgoKVxcWhgZFx8eH4mIhxUVFm5ubTo6OmFhXiwsKykp"
                        "KElJSBsaG/Lx8BISEmVlY0FBQGRkYnh4dzY2NFVUVW1tbTY2N+rr6h0dHVNTUjc3Ng0NDCQkJTw8PHt7eSEhIS4uLe/v8C"
                        "goJk9OTxwcGldWV/Py92tqaYGBfiAgIDk5OYaGhUREQjg4N0lJR+fn52lpaCwrLDMyM05OTS4tLyUlJhQUFBAPEUhHRlBP"
                        "TgcHBWhnaBwcHZWUlD49PwcGCYyLjDExMn5+fYuLiUVFQ15eW+7u7w4OEXV1dDQ0Mujo6mxrbVRTU+3t7IODgo2NjN/f3l"
                        "hXWYGBgo+PjXJychcXGHd3dXp5eXZ2doaGg9zc2318fhERFJOTkjAvMI6NjllYWqOjocfHx9ra2c/Qz1NSVsPDwpiYlmlp"
                        "alJSU+Pj4oiHhqysquLh4Z+fnra2tL++venp55GRkK+vrZqambm5uc3NzJ2dnebm46ioptTV04aFiZycm9LS0qSkpuzr77"
                        "GxsLy8vCH/C05FVFNDQVBFMi4wAwEAAAAh+QQFAgAAACwAAAAAXgFeAQAI/wABCBxIsKDBgwgTKlzIsKHDhxAjSpxIsaLF"
                        "ixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KtKjRo0iTKl3KtKnTp1CjSp1Kta"
                        "rVq1izat3KtavXr2DDih1LtqzZs2jTql3Ltq3bt3Djyp1Lt67du3jz6t3Lt6/fv4ADCx5MuLDhw4gTK17MuLHjx5AjS55M"
                        "ubLly5gza1bsy1WTGJtDhxwkIIBp0xGaiF6dkcDp16aZsJ490QDs27RzP3R9+/QBGLqDK1TT+3Qt4cgR8iBQ2ncDKsmjA2"
                        "BRMIkdKrMonTHYSHruFLAc5v+ZAsa7XDAE/IxTeSgAgQoMC52Ok3KOIwgIXJgXWiDAiCe8AIESLqYV0IMpCRXCwGlinBSM"
                        "BzT0FwAE+wGVSm8CYGFLGSPxdloBZHCBRiKOzNIAbAT0IJIhO4BiwQW3GVDhT0kUd5oADVhxBUhc3NZcAD+a5kAJHxliRQ"
                        "MH2HjajD4Jo2RvNHjQURhRvJbkbSB00BE0x3j45GnVMMlTGl8WZ8MWHQ3TQwMqIBCAARGQcUc2Bk1SESFvLKhkkK+pJqZO"
                        "ssBmCRkTBHClkjNQJ1EaCMhSkQsqTMTBDGX6h0Uft0n5Z07yvaYoAOOA8Bqfp80QJkQSEoAmREaYlsI5ESH/QSpsAmQAyC"
                        "MCfQPbAUdsmpMOsCVhkCdlEhCGQ2jANsEtDK0hhocCiPDQLV8eoIgXBQlCq6857eFbADogdIeXxTnSUBcS3kaDEJHccgIb"
                        "RbhAgAO9xeIQFl+KghAQsDnALU5bwLZHQlRA8CQBwDRUQrqV9muFQ6x82UJCZcBWwL84TfELGyfoUMpCHpB72xoNNXMHLr"
                        "M+CYE5DeXxZQPUKMSMIU3EsYkTTmCsFA1PMuuQDhmM8CUBILyRi0OQiPwaAZro3JUST4ZykCkrIHRLH4yooIJtDKhQSxHP"
                        "IJQNJgelAqON8DntVbIpByCFQVlsMIVGFRNwkAhKTqx2UjzE/3GIE53okQiLDUV8GwJInHAQLgsScEYeFfnQQAGuAVdQE0"
                        "vQe5uKDe2xwi+Ap9EBD8HsDZMrtDB8eA87KHSHaQcwMIEyCVHjwI8C0PA2RGyc+JqWCAXhhADN6Y1QDFTU4OahKL5i+kqq"
                        "qG7lqKYhYedBWdxAgOIMvdFbA6+wcD1BXbAQicG3WeAQLxMi1AUiSivJxfMnkdBwb29gNEkEBUgfQC8b2MDZbJQB2l2kFM"
                        "W4H2wiQD+SZECBvUmBIjDiCipMoG3FKQAjxoCRL9hAcxA0DY4aGBJmhPA2SYJDRoZBAubZqAAiiEAREnaRUYAAgw2zFwk9"
                        "coMTFocAktBIF/9ioAcbTMAAbroACJBgBR0cSyM3wOH9LrZDjozChze6Tc5+Ugcs+sg0E6yiRnznxd5MwCdkiF8ZHSVGjK"
                        "ixjAzQxU6eUEYlIaCNF9lBHZ/EwJsIQk97LA4eLdLFQNrojDYBoSFvY7lBSgRqi/yhRSyYLhUMgXsTGYIiI/maLzhyImbg"
                        "ZHHSFpEeHIBPzcnAqiCCijcuUhiflIgeRCnIiOiBeEqKgkR6QcveAC+WDzlHL3sDEQuUSQAGeogMhkmrXQATIrlgJmwG4R"
                        "BjvsYAP/BDIRARARGexgwNYYI0X9OLZ0ZknL9jCCWWRohl5OABChhAAshhA9j8EiHXkOIii2H/ToiQEZ0M+ZEIxKGFBAxg"
                        "AQsYgEK1gIrXREohKkCnaUQwsH46xBASNY0MEIQQUJwGDOAYgAQGQAF5KnQAH4CCLl7zh4SIM6OHsChE3qiIH9jGkDVAyA"
                        "lew4oFGJQCGDhpUBNAAWe8hpQGWSQDMoAEJdlNpg9pQ3EOYECBdCEO/8RiMg7igg+FQwKkSIACfDoADJTUpxKop2kYgBA/"
                        "7LEFbSAIMAAJGz9AFSI8u00ksLfHPhakAJoTgQaESlIK+JQChl3EFZd0kD0KAJMD8UBvcHHXiPDpCQe56R6tkdTTNCAECk"
                        "0AQst6UNI+wBivKYdBVmHIIRikEymw0ior2xD7/71GhwNJRY8MSZ+CeKgCJRUtKRKqUOIO4AFekJAA5GEQtQaypQSZRAJP"
                        "41faOoRSpqEQQUzhPy/K6K+nMQAFEhBU45JWoRQopGkO0l0sesMgEvqudSECIwdcoyBDO+F9CVKL5ggAGxpALAYwkADyYk"
                        "ABIXgBEf5pkC+EsL2naaRAigCk+UrETfohSA9ttIlUtAIbeb3fMQqyAjfFxqAKJXBZJSABBZjAHa9BQkGk0E0FWuEd+1iB"
                        "Gp9KkPVa+CEcMA0nCGI4Q1mpE854wQtEuo4aN+yOBSHWafzxggSQArEjPa4CkIE+IB2NIKJQYArcAYXSLuMWKVtCQTwK2R"
                        "8rpP+pPBaIjUqhhZHCMwEvcIYrcWOQAV6gHR/AQTwHS4oX2KMFrwEBfBXIDzw/QJ4UeAE5sHubXvU4zm5OSGwIsoniQIMC"
                        "LR5wPAtMDwUawSBqCFIfxFGJD+TgE5UIg4lhx9Ee348DGhDtBx6QgAeY4AP4mLU31UeQbkIj0wqRwoRKNxC6zucTJigwrx"
                        "WghQ9oIQfAuB/ZDCIGM0ZAs69JhEFWcL8s4KEfrSCGBuL5gEcrYB6I5vNA1rlXZBdEBgJRRAB6K5Ag06oCRFjEoxehYE7Y"
                        "1gKxEFqlaIAQOkyvODeow0EcXKkRUMMFDCgAAhTxjU+INQQUMAE+euPJgUj1oUj/CIS9j5EJgTzhAjsayBp644gPSODRWl"
                        "iHPLrsHn2apgEICcaGlbSBexLkFQ0TQKFeIwZy7JqkIcgBz03j2h4LQCCBMkamHVEA5wHAxwPpQW+wQW2FOgMCG8CifA/S"
                        "h/Y+LCGM8CIC1BFPHCRAAheCzQUKUpohl0EAmKZtNgTggHBxgAFsJcjSXyODB4RAA0SAgsN9WJq1I8QOfqCFClJggCYyhN"
                        "I+v00B7PGBwQ7gHdIriG245/C9z5cDBvMXAHZqeenFIagD0EA8BgjBCIwjFSLZxREisecf3kILJ82BNV9TkAoEQAgCkWoA"
                        "eDFfJwvEozm1NWzgYQKFagATISTA/xRahxInhTADSx6AAnLAjdvwgSCnCEAGBCJZsFc2vgKJu6K1/5p2LEOhn0Bp9xNTA+"
                        "EKcDAEd4AtGiEJfqAHUgA5AtEqEGQAWkAE7bYMiXAbfiIQnRAArvd1piEslRUEEkJZAGAblodC7YB81jZ1ZYJUixcABaAv"
                        "F1ECzFMAljAQmKJABtAPJ2UCjnAbWzUQUwB2p5E/lbVSpvEDAgEjKYBft9ENWqAAD/ABUnY//PcatHAqE3EH/uNXENYbmV"
                        "BmCrUMTiBvAlELRjhRtFUDp8GEJxgAUDYQ0mMLn/ACj1YPQ4MCp0FskOCGxSEtFKEkqiAQrCVCbvVwfdJ96lcJWf8VAKq3"
                        "hvYnU7z0cwLhJrI3EM7lWRrwAQqgASHQbTYyA64QDxLCCgLRVS8kIBJRMTYCZWNwGgjgDEKgJBGADItggQ8wcrCRggGQic"
                        "xXWbHFhgCwdNtAEHDAJwSADESwZBTgbz5SAB2ADciQdgFgaeDWGzHnBy3wfggxBFlAfprwJAMhQjJQCd9gjb1BCUQgARZo"
                        "AuxwGyQAhXMYjHcFiAGQfXEXABJ2BL3BAp8ABUT1Aj5AAiJzBjkwAFrgBqZxPepYHKtiG1WDEKbxZdpAjnJmGv6QAFoQDU"
                        "qTBkSQUD6VA1UCG0FAENCAGuVoGg91V6roY25AL1VQEBegjOggAab/FwJ4IAgugAsEkAHcIA4mMJRQkG0BwEFxqCQTSS8T"
                        "eRBgcACgAQCWgJEguAE3+QED0AqXgB8q8ARZ0A4mEE8DgAPEEA23gWmqYBpYIBDkZhqWZ1HEwVgvJQByQBAUBxuAIJAlJQ"
                        "EUgAOfgAeV8Aka8GsSAAX3cDaWNktKspIniRBpBzzRZCPTIBBhQF2VgHyLgAMfgAfEkANKFlRE8AEvUAjSQ4ADcVPmAgB/"
                        "cBoyRls/siqlUhD4+BpCAAVEQF4KIAF2pwAGlZnvoIfNMQsDAQc/lAYCUSP8mBD9YVcC8UDfchoK6IqmkQnOsABLJloSkA"
                        "CeSF4v8AnUcpadFQA+/yAQkxcATXlX8RYA4gYAHgKBArEDs4IF+zAAIbAI62cCI6UFy0AOs+keBIECpDKeAlGSUdlYb3IJ"
                        "AyFs8zEQTfUaBbALGvACvJmdvZYAJoAOgVAcalAQWSBCAnEJeBMAQDdfxBkAaUMFzZFhA+FRxVEE7tAKOaAFJpADy/APwz"
                        "Mq81gQ3jCMDjA3A9EFp1Gg4RlnsrB0BrAEzVAQ8Rck07ALyJADUBCly0APtmAjb6d9cgQAZ2gaHPBjU0lFAJAuXUoQYqck"
                        "DYAFJLB8sAF9EAFInxKeAUALEFECLih/ZNADNpCNsIECBqFvpkEIGYkAPJBpz1AApwYAS3AlYDoQXP/wRi4EJALAALjlEJ"
                        "nwGqxooKcBHRDRA6F3I51gELEIJIhUChAwA5BgbwCAlD7wI2FUEOlZJgdQC1xoiFhwqVzlKZr2GqOgELcwkwUhCcX3GlJT"
                        "EGkASHYgEAqIqr5ljwXhZE8CBnAgoANxBgEgA8l6EBl6Gm9aEMxjqwZxBhtQBAaRCHt2JeJqEF6irArhAUOXeAbhBYrQNh"
                        "OABmxnGozAXAORBIPApgAAfqfhrVlIMgCwBT+wqwShbAVABwfBAxlwAAoHGyNQDN1xEM5pGhKnrgkxB6OiEEdwC0LQA4HA"
                        "BY6AoLkqgzLQAj/wGjYwEHqkrSULdvXnGgYgA6cQogH/gCsIwQJMEAlT0AOvcAa7gxBqun8YmxDqZRrvhRGv85wOxbK4Sp"
                        "G+MRBS9qimQWwXAQzME3jqmgvG1JIAkIinkYMXAQhfwn/kh6kB4K6b2BtzWBHtNypPBABoUAMVEFfIFgZkRLQCgQgWYwEs"
                        "QxFFSJXseRqG8LKT2YRPsnaCEBHKMIx9aLcCEQqvAQhuBgvgprcCcYWvgQCeMFsHoQMQ0ACyIRB28CQCsIFuQLdbhBCAUA"
                        "wWEAHeGKZPQrkD8QMIsArSihCsUAUi46N2iSKNWVmCIAAPaxqYZRCXMFUBMAFkYAWzcAiagAUGkC4CwE8r+UMRoHUYIQNv"
                        "NKYZKYtR/0AGZgAHQkAo3VUAbHAQDXUbFXVXDxleBJGaArEEWEQQ8Dk9ETCoHcEHZ8gnSkAQLOBDDDcQapAOAzEExSGwMn"
                        "WXsFEe+co5zelDNCQQtmUaIzAIudsRhTAIIHQDXfC71PMlDjADMSMQrIBUongbcipTzZAymSgQP0kQc9ABvKckBYALLbBt"
                        "MlwCsABdCxEEQSAHq5AGRXAIh1AIt2AIqhANDfEFRRC0A7ELncAclVIAKFC4A/EGBkAGBPGIpwHFz+R8NoKUAsEGptEHBi"
                        "EHT3AoV7IBBlALsFCXE2EEj8AFZPSofFIAFUAFQgoRxtAHNkAANXwBCIAFqoDFBIwAAv+QpdfbG1r7SU/yCwVRqaZhCwkR"
                        "Db7gCxYRDKpQp+EnC5ZGEfqQDseoU7whiAPBL0oCsI5EBU9STgVhAT9CAI5wqhuBBgpqSFyQtBohB9lqGiZIECVpIytrTr"
                        "l8G4BaEJFgRpbgBkYwBjDwCGjgB1hwqAvRAc46TC3gwwnBAbowBHDgBqPwCE1QB2bwBKpTAJ8Kp8XhrsBUJirAysTHAA5b"
                        "GoQnQhdQBdacEDGwtug0AZbMEMMQASngAAcQW7gjAvxaENPwJQKgWs90TFeXED6gA6/QA05QBB2wrQmSUTayBGCMENZwBZ"
                        "RgBYGgBJ4QA8CHEK6gT67wTJDQMHy6EaX/oKYebSP/yxGbZCMb+EmqXCk5ahG5wAjBetOooSkX8b5KUlWfhFH3wyEVkQTZ"
                        "bNTFUogVkQ1gWyZI/UmcAEENEhE+8KpUHUIQEEQRQSYKxMp4dD+HsgQTqxBBsI9jvUcGEAjSwBAlCkFG50hh+CQNEAWwEA"
                        "c8YAueQNRzPUwGYAFKwAQ8wAN7AAcoUNTEZE4Ve9iWfT98QrUN008lcNmefdO0a06fPdro5Lmx5MUhpNmkPdqL+kwBs9oK"
                        "pNqwfRqFAFWz/UIZkAGZgAI08AO1UAHDfNsOmswWNQSdeticwIgnhQOLUAnCfRuMIIzP/RrAMACkcFKGNQB4MN0fQluv/8"
                        "3dc/AAC0BgCYUBErAM3G0abmBdXHDcVC0IVYYBC0AKEnBg283d+DZfPsDdgqB+8j3eZSjbnt221lW6z30N7fZoJyUBlSDg"
                        "lg3LbrYDBeDgY50PVIhi2amTwk0Ax4tsXRBR0oQAefANWLDTNtINYsViwaUAzt0wFzAG6kAD7h1++2xvfDhMsfB/62cPZ6"
                        "CnvYHi4k1U6jcA6F0sO4AHL0ABeJAPk9NLSKWsczB0kdQActAKVmadL4AMfDDVt+ELGvAAOLAAdvYClYBDAgACeZADJvDl"
                        "IfABwIAIxWtIIkDGRXsOkm26P1kKlUCfYylSCjBq4NAHFetCJAALiaAMSf+wA8MgCWjAtzZCAl7wDgveazfna9ggDATQ1x"
                        "J9A6NbtAUxB3TgbBCEAEewDi/AYgvQbvQZTzdn3QPwCeBgBDKAJKcR5xZcHAjADb7gDBqwCCYABal+Z3eHXlsGD4HbGxTu"
                        "gSXn6QnRBjxzKJ16Dwcl5KFFUiawAFowCfyQkIh1UJXwD9WwCSRwIiNAL0nSHxcAAVVgC41wD60ABZA3o+GABoJAAX+uUK"
                        "AlT6KVANhAv8WRMsRLAKIrYcy+ENXAA4pgADYLJAVgAHRgBnIASa9xC+SAYuon3o5HBOxQABbwAmGFlQVWYBgABTmQA3hw"
                        "8siABzmwCHypmci3bkSgfgn/cAKCTA4x/wBZZu8Exg41LACOUAKAYACucSUGYAA0QAJuMAwFLxIdQC4FAAMvgJVUuAAKAA"
                        "Xi4Brq8AJkdVJ3hw328AmFdVLyJAEXmmsKpeAHpQU9VAAAZp+552LvsL6vAQcfvPQxIcuwYQHqQASD9QGfgA4yPgtYiXsn"
                        "RQqkIAZggAw4oO/0aVgL0AI1EA4oZlCPRgEf0AzOxwj90GsLgAPOsAvkYgB9bPcV4Qo1PhF1ID2iAA44oAH1MAhyiA0l9d"
                        "/wpFCtkAIFkAMhAFoPUFIKQAEP0GnlkGuP1m4iiQO6EgCysAAaUAk64CWl4asXsdeezgNAIgv5cBHecxuB/xANEiIJ63Zc"
                        "JnVS8SCiCbmb5YVSpRAAVLAO6mdcBCZoy1QAZwCs3oQaf1sRaxAIDKBLpL8HAEEggIAWVwAcRJhQ4UIAvlAwCBBRYoaIBe"
                        "YtGjCAgoSMGT9YC7BEywAcCwZIkGByQBcHLcCdVKkxIyk1EQkIHHgg4o0YDH0yHDbrh4AAEH4eRZpU6VKmTZ0+hRpV6lSl"
                        "kSRKnICoCYxuUO+IuDpRXI6RCRJ0VEDkVIBVJhQkUPBAwQAMDwbEC3Cj1IsPZweE+KCF2DJ1OsMemLDCJ5Cj1NZkuRE2gA"
                        "GqlS1fxpxZ8+anPSQTrXjhZ4Q4P88gkByAABV9rYhQGKABCv8yiBxCyFWAMi4GCfQCFLCk4IOCEIvwiPNCZ4ZE0AiUKGaY"
                        "zMmMnzhTB1DBWft27t29a6ZxXaJohuwiNpjzk4Mu62EJWLmSyp35APo0JMAxYMGCtwsSrKsoHHB8cYSEAgwLqwHofBqiop"
                        "/Ei4iB7yaksEILuwMDwgAkZGiOqxBBioUSQLgKNOYiqqAHODYRRg4jLomlEC60uWoE8SBAA6kVBEDwQQ0vBDJIIYc8SsMN"
                        "F5OMEqVKsaIBI5+s0YAn9vAgqSYMCGsDHyEksksvv/TOSAR8YuO6CJJYio8rzGihBiwRhPCAAxjIpIoSFkxKByw/+6kADS"
                        "UBM1BBB30qCSP/KWPICAgZcEMqYDzYhJISEimjhDKuSA8qObKIc0vxciQ0VFFHBaCEQ30yFEKiIrBjyEnMgHIbn4wUg1Rb"
                        "b+2yAiPJW+gRKM/TBQYKpbDk14jSmVVDDnFlttnvcBHTpx2MtWkIPDcLgwUzcIJTQ2QZMlIAZ8cld7OBNBTBJxaolQyFYx"
                        "rJg6oTeDhlAj/ZlejbhZ68pFx//4UqiCezYygGfBdtoIIpPNmEjQ4MiUGHDsqgRA9FZMgAgW4PlmgXn0wUrxOARyb5KBue"
                        "/MGnDsTTg2OXn7TAAskM+2ljyZYtOeeSHXgyAp8uEe+RCV4m+jpNFL3OU/EEIERnpwFWBUok/3wiRDwAPCs6a4kSAcDqZI"
                        "2k42mxyf2VC6XPpWwVrdcuo+ukP4ZybLlxtePXXM4eCMRU1y6aAwBUSA1RhpyAcpW5Dxf1XiN9/mmD1M4BwAMjG9S6Pa/T"
                        "SI1xnxSH0AHEPw90GCingeaoGiT7wWO3IeQDyjeeNINyLgEoIzUzjqoDyk1A551IOqBcAyldw7r9oAsgJGB1Db14UpXcId"
                        "QSAB9S6wMpKEFwpXftLQwjXAZYSIoKyTpASENRlOfyyR0k0bAGhDiP6FqG4L9uzO3v9w41CAugYSnJw3oEQjIkHvItR0PU"
                        "0d/slhaAKiAkgRJZCqeMhAn8VZAzfthfLZLRFP+QBSAhYoDQGABwByPdbk8KFE8BVIEQsFxFcEnpAi06GBEThcGCN7RMLs"
                        "RDgFdc4yknHEhC0DC7WBhpGAA4hIbCBgAghkUEVToICcJChqc0AgXiSQEOtRiVKXCOAbUoRClUB5UkSuSFQPMa+mbmBQCw"
                        "wWYSOcFBinUdRSTkF1cBgxGkcoRVaKODKNhiIJfCAyH4IRGGkAZmCGEiEChEPBkoH4TIk4cfHWRl12kbQnhwld1dJg+xuM"
                        "IqqnAHQZYSSICLiA0ceZ3zHUQGELIfAByXxj2IpxQJ+YNECmBKXpJsFBJpJUJccJ1GHWST4omCAMWTrkjyKSGii4gLejnN"
                        "f0n/BBQKaVlqoAiAuoknmKe7DhYScp3kJcQcEpEDNdUJpkkoKSmAiAgFE9KI65xhnNdJAfkO0gLx8CAh9AuJQgRxnqXEcZ"
                        "0H3cwWMjABbSyFZ5m8p2TKkZAHXiUDrEAIE8SjLwAcTzJ6dKQDQJqUGojgGQhFKVXcYJ1aKeUMAbjFQiYwQ4UMTzKASMgX"
                        "0niQJkaEIRdYAlNmKYBTMCOlR01KMMoQgbAUoAhMEYMaFqLRsIgrIZfgmWQgepAZYkchjAgAnCawkG80oClNJMAPDIpUpI"
                        "6jBDSw3HgM0RSM7qtELwQAJKKQmnEoBCKSgYVCiiCZbSJkjEuBgHgMwAVhsZWa/26QQVY1lAHwUSU8V+mfQtyQGpmmRgcK"
                        "WQHnDmAZKzyJABBAgd8cK8ihQckPltlCWE6xECncbCGJPcxUJaITs1VGYL8SwmoFaSzGWMaAEUkDuMISS4QMNiyaQ4gPrF"
                        "POykTDWDgTrgVL8Su8TiUMikvnbcMiToX89iqgUggtJGILzFS0ktm9YR+4m5nIRKRVC8mmRIqXU8IypAoQxMxxn7QF+N7Q"
                        "veJhb2YkiKaFcCIs3lCuLn0CCtVIFTNXMFZvC4y/XzH3KEFoChYCAGKGtGeDdgUNCXxCCQIUgimnaFpS6vskXm1Ye4Ptqm"
                        "TasJRBEMCHS6EDGxlSRAAvJDIpUP8NJHwSilgwpRgN6CRSgvHXJ53YxrzDBEAlw0OmDI0A8oOKRxvJkJOppgWVmQOWBGAB"
                        "//2KzVfmXQEkCyFuMOUI5xJAICrDAZ28eSGYC4AjKhOLWfp0Kc+I63WsAefPyfdJ+lwKoK9yX6nYIgBT8AmGnVAZ3F6lsk"
                        "qZQ6JRx2jEidqMkXgKRSRTADZMhRWQVsgRrjkVRHxGAJZ4yl5VFUBSj01mn9nQIL4QlTcOpLBdosZmrwKnCkDFFEMwdXd7"
                        "XbLUHEAADaBCV6ACCU0wYgINSIGcrkKAvnopGbq+SgoMIAIZAEIJUikBOGd2y2nr7Ae6JAAIzCCFzbTBEvArgBP/lBwkD7"
                        "RWl0hYwcAx0wFEaAMBIwANLuqdM1AMwhMn8EAXJnQJeUckBUhoAoXscFnm/IDf35EGDHjRg6BOXLjm+HVYaMCERW8mBlbI"
                        "hGQQsIdEutznnDmBqSGghCasQFZPKccZmEAGPwEURD+HunbgCaWELcEKh0gDKkrQByroYQhIiIABtLxcTkQ96sXUjA5IkG"
                        "O+SSS4m3mq2UtpjN89YTvn6GnbVdPYzcAiADT4hdxvCAQqEAA0XOMOCPUekUwkdzvTisgBfhBewX/OB47otEQ85x0fPKHt"
                        "BgBUmCRjADjwvfJOi4EjbCoZpYRhEkEwRKaeIg0krA0Ef4gKPDgR/4MgVEMpBw5ABjzxDF+cfmSKcFJVJdPAo7TuXOOpwF"
                        "aZIgs/zbDYyx7CEZ4CBEs0USeBPQpVl61zJATP+M4yGJTudhQJiucHVIAKEPSQ9y0bAAKOUDhTskGHOY8+Kf0Xj5Y7P2aZ"
                        "AijxsBJ7EgHQg6nwAjtogzOIgy9gAyPQgWN7iipgu6tICjKAEuoawFvpOAjpl6PgAGrxpy9hql9BBaTgAHTTkGb4wFvpAg"
                        "NMCiVgF1noEvOaL6S4BihptRgklWOAkpNCirGDED8DEkw4GKUQApgBQlIxtavYNKQwBY4hAGoAklc6GPQ6iiiMiM17QkJx"
                        "Pg0xiqRQQpepASH7jv8xeBkPLBIjscAw9JIVMJIMiKmkUDx8AY06mpCTyUAjATKwkcNBAT6JoAWmKKkIQIFioAE1oxYHOE"
                        "Ht4IRNMBYEMYAKoAELMIAIaISlaML3GkQv0SHFKgHL8IZT8MLnOrnMCIMyg5ICqABe4IPKGIUoXMFQ9JIUrCoGODPNQDRj"
                        "QQBUs4w20EUooQNB0AwnEDfJAENcFJIk2BgE8ATuoIRifBIDcIGeeIog0EJjUaXtcAUakQw9c0Yh0RibiAIdMD3u+ER2QQ"
                        "AImIVQcIVYkAJqCANqaAQPGINjcAGxw5cCQLvuOAEXSKADULFyvBAlsIEe6AAfAJJa4hgeaTsCGIX/C0mFHfADLCCBSERI"
                        "3mEDAFy8J6EBSuvIqHOukNzBkhQ8JDBClDQjlTw9X3HJyYHJ1fIBHRACEqgFWtAEb8iepSChmRSPWmiKP3CEr6OFhWkEba"
                        "vJkhkDEoi7o8jD1ICAkToKGxRKyaAOpfCA1asqefoJIICAHWhKUeGAIkANN2QIVKAyG0kNC5C9nxCF58vKG1CKVziR3Rq3"
                        "pEgsBviBPShLL0mCO1A1ieiBpCjEpqorpHiC61sbQEIKX9iAP5QIU0CKW1gubjC/wKSQKhi7pDAGKAGNQ1CKOig0yqRLI9"
                        "EJAmCCpPACkBQP0kQKaOkgB5iAFtA4zuwOCHm7o5gF/3Y5hqUoPCMRAToAMRYYhCd5g3X0iXSgsl9Jii1gO1jTTc5QLKWg"
                        "v8i7Do5MiiCgBDqIgmKIgEGgghjIv4SIhjbog0FAAQjIAG0wg1jQPqY4mJ88ChIQNV6rTs4IBvGwz59YF3whgCkUFYOjlt"
                        "48CkpMDS7cz8wAApARAKIwnA3kmBHYzEHhBdT8DOz6CX5KTQJt0Mzwhg1disTUkAMgR0K5N3yxtqWIAQBkvhDNjHY0I2RM"
                        "Cl8gmlkclOfhGMBUCp1KENyT0QC7ig0QRqVAhTeIhRKAAWgIAxhgATeYARFwS+QhlHBBjFNogj2AgS7IBh64gl+QAaaQg7"
                        "AwgFAYUv/MOKEbCDnM8AYhAJmNaTYweYbk26EsyAxTeKBgSlOqiAgDGILt4EAI6cUuGVHkwSnOaEKikLY+dQopuAAryM27"
                        "a58ucTTxoAUwywxo41BHdQrm3I4xvI4D4IWmOIX//KpOXAppCEHJgAMKsYZ48dRbSYUnaYAyiIafMIIKEIAx8wlR2IALsI"
                        "HP+gllMNDrWMBZ5aVLghIRqIAoqAA3MREBANGFSILnDAARyIQKiNaWvIpBUNZpMtFf2bGjcMxfEdJwNaUqJJroOYphIpp3"
                        "U9deipqXIa+jkEmXMat5lRtTUIMWeAKxMwALOARNXYiccxkRSgqPOphmRIo2eAUIuAD/AwABRuiDEeRXCimBQj0KH5ix65"
                        "gFpSiBAtBQM12KWShZ9zBYhICBxGI7BigdpJCDJZDVjHWKLQAEByiA+UQKsHqStfqJk6SWUlwKr4SSXlCGpLDG6xAATVCK"
                        "iECCdLVZpCgB69jXpDAWJYhLhrCDlPUqphCE7KShsEgBLCRBY1FLhsDKaFLVqfWJ9uBOnxgiY3EAG0IKGlWs1IKKE5gBLY"
                        "M41YAA30MKyDMWK3tDidhKt12IbRiPtGWIceUspTCCFmgiBngCLtDGqQAGVLCADhrYUlWKdMCXGD2KK5KIA1RcAJjbgVjM"
                        "o+gefLFLavtHpTgCayuy1EWIJpCIFFDD/w/jmN71l//BF6NKil4wEabEXQDgBoloKaQghI81FgFAXWfJAtgMl1dNCvELgN"
                        "JIXgAoh1qIkKUYVI4RQHJZA691jxIFDcrD3RMgkQCYNawlGlIil2ZAX8mgN6Q4gXsJ2e6FgV4IgOldCA8wABkoAV44gi7I"
                        "g2E4AUQIOx8kGygxABSQgzqQhjDggGdoAj3IgMNcEj8B1+5FhQ0AA4ytjCvIPPHAU2aJrSdBAWK1jCUIgLHq3ikYgUTNDC"
                        "9ApRJxD8NVisOiENnZoUgwhs0ogNhN3iqwO+1YWw3pAdU6CmUwgE+bCguwgtBrvkC4xknVDBaApO7tBOLVjg6I0CdhAP9G"
                        "oAQYOIETgAGVcwGBEICUsYwz8BMEmOA+8IEkkIJHsIMsmADrDYvm1Y7g7N425Q4ZONe7MgA4voqopIo84BydDYALGCDRRI"
                        "BJ6N6cmQIkexmruoyYcxkCCIZM1hl4IJqnu4y94ZhOJeWRSUXxcFjLAOVfaY5WHpsWopYCQGXMKMGDySxbHhQWSANNoAVa"
                        "cIEiIMumEOIEzCLOGN9faQAu7k4mEAJFsAFa0IMOgGJgtowiwNYSuYAmW4pD/ZUEs05jSdGkKAXTFQ8XUFhulooU3qFpYI"
                        "pV8FYIWNk9i4RUxIIiXorae5ICWGF4hgp2MYil2AE2QIIGMIARYIAJeAL/JYgD5O0OQqCCCriAh/sNA+gBUP0JzDSWGiNo"
                        "puBR0QwAYbgf8aHliNDPkRZfAd0eLvjmJ4kyl1aKQmOX3vmvV9Y5m16KmnAZih4bdj6YGPPpo3hfl0HVp5FndkHQo14Idi"
                        "UaNBWbdOBpQIRqn2hiis2Am8CXitSZkuauTWyits1qhPiCTGgBs04IaCgEAyjjJ6mBbfYXQzjW/VEE7l0IaIiFCYDMs34K"
                        "KUhqM94EHV0IDgAFogSSNNCGZGaIP6iFqwZIwPaOUEDfAtjETGiAexEAkrSQBCqACMiETJhpI8E0yv4OLS6aERgSESsa90"
                        "HtCfEAKXqZWwwSB2tDDYvt/wkxFZfpkrm0QhjebQrhBG+9jswdkoMhgF8e7gtRL2ph7iFJBHfc2ua2kDUQiER23CDBBUAe"
                        "t2Gz7stYgzG4Ao8+ij8IWA2JALrukg5AWPG4ALBkCg4IgivggaOzbkLohLGViLRaoaZIgh5AjQPoBQP4gSmog1FhASEAAZ"
                        "zYAATIgCxgsKXgBE3IOwJwPNT+pSdZImriAijRbaj2WdEMPF7aA+9O36ymQ2o5AMQTJCDgZGN5raPOpYOBy0CS4YNx5JE2"
                        "bggBAUy2IEm46uswbIKGlaKh5/uBhKWFaZe+X/GgA/aWG1kYciPxYVvWAb0zACvgKKdRgh6nljElaKMtGqudsFuxQUmw5m"
                        "aUnBsmzxrSteWQ5MOxYda2u1pgDsmDlpuQbNTuXbxYfhowpxaRbuXFE+CcmaO2I3RSzho4EYDWPJxF0nKCTg3QAI0YD6tR"
                        "xQrQmSHrS40ReKMyDO9RJ/VSN/VTR/VUV/VVZ/VWd/VXh/VYl/VZp/Vat/Vbx/Vc1/Vd5/Ve9/VfB/ZgF/ZhJ/ZiN/ZjR3"
                        "aqmIdkZ/Zmd/Znh/Zol/Zpp/bhDggAOw==")


class BasicShape:
    def __init__(self, pen: turtle.Turtle) -> None:
        """
        初始化基础图形绘制类
        :param pen: Turtle画笔对象
        """
        self.pen = pen

    def line(self, length: int, heading: int = 0,
             pencolor: Optional[Union[Tuple[int, int, int], str]] = "black") -> None:
        """
        直线
        :param length: 直线长度
        :param heading: 直线的方向（角度）
        :param pencolor: 线条颜色
        """
        self.pen.pencolor(pencolor)
        self.pen.setheading(heading)

        self.pen.pendown()
        self.pen.forward(length)
        self.pen.penup()

    def polygon(self, length: int, side: int = 4, pencolor: Optional[Union[Tuple[int, int, int], str]] = "black",
                fillcolor: Optional[Union[Tuple[int, int, int], str]] = None) -> None:
        """
        正多边形
        :param length: 多边形边长
        :param side: 多边形边数
        :param pencolor: 线条颜色
        :param fillcolor: 填充颜色
        """
        self.pen.pencolor(pencolor)

        self.pen.pendown()
        if fillcolor:
            self.pen.fillcolor(fillcolor)
            self.pen.begin_fill()
        for _ in range(side):
            self.pen.forward(length)
            self.pen.right(360 / side)
        if fillcolor:
            self.pen.end_fill()
        self.pen.penup()

        self.pen.fillcolor("white")

    def rect(self, length: Tuple[int, int], pencolor: Optional[Union[Tuple[int, int, int], str]] = "black",
             fillcolor: Optional[Union[Tuple[int, int, int], str]] = None) -> None:
        """
        矩形
        :param length: 矩形的长和宽
        :param pencolor: 线条颜色
        :param fillcolor: 填充颜色
        """
        self.pen.pencolor(pencolor)

        self.pen.pendown()
        if fillcolor:
            self.pen.fillcolor(fillcolor)
            self.pen.begin_fill()
        for _ in range(2):
            for i in length:
                self.pen.forward(i)
                self.pen.right(90)
        if fillcolor:
            self.pen.end_fill()
        self.pen.penup()

        self.pen.fillcolor("white")

    def half_ellipse(self, a: Union[int, float], b: Union[int, float],
                     center: Tuple[Union[int, float], Union[int, float]],
                     direction: Literal["up", "down"] = "up") -> None:
        """
        半个椭圆
        :param a: 椭圆长半轴
        :param b: 椭圆短半轴
        :param center: 椭圆中心坐标
        :param direction: 椭圆开口方向（"up" 或 "down"）
        """
        if direction == "down":
            start_angle = 180
            self.pen.goto(center[0] - a, center[1])
        elif direction == "up":
            start_angle = 0
            self.pen.goto(center[0] + a, center[1])
        else:
            raise ValueError("unexpected option, should be 'down' or 'up'")
        end_angle = 360 if direction == "down" else 180

        is_first = True
        self.pen.pendown()
        for theta in range(start_angle, end_angle + 1):
            rad = math.radians(theta)
            x = a * math.cos(rad)
            y = b * math.sin(rad)

            if is_first:
                is_first = False
                continue
            else:
                self.pen.goto(center[0] + x, center[1] + y)


class TextDisplayer:
    def __init__(self, pen: turtle.Turtle, screen: turtle.Screen()) -> None:
        """
        初始化文本显示类
        :param pen: Turtle画笔对象
        :param screen: Turtle屏幕对象
        """
        self.pen = pen
        self.screen = screen
        # 记录画笔初始状态
        self.initial_state = {
            "pos": pen.pos(),
            "heading": pen.heading(),
            "color": pen.pencolor(),
            "pendown": pen.isdown(),
            "visible": pen.isvisible()
        }

    def _get_char_width(self, char: str, font) -> int:
        """
        精确测量字符宽度
        :param char: 要测量的字符
        :param font: 字体
        :return: 字符宽度
        """
        # 记录当前位置和撤销栈状态
        start_x, start_y = self.pen.pos()
        undo_count = self.pen.undobufferentries()  # 记录当前撤销栈长度

        # 临时绘制字符（会被立即撤销）
        self.pen.write(char, font=font, move=True)
        # 计算宽度
        width = self.pen.xcor() - start_x
        # 撤销临时绘制（清除痕迹）
        while self.pen.undobufferentries() > undo_count:
            self.pen.undo()
        # 回到初始位置
        self.pen.goto(start_x, start_y)
        return width

    def write(self, text: str, font: Tuple[str, int, str] = ("SimHei", 12, "normal"), line_height: int = 30,
              max_len: int = 500, pencolor: Optional[Union[Tuple[int, int, int], str]] = "black") -> None:
        """
        输出文本并自动换行
        :param text: 要显示的文本
        :param font: 字体
        :param line_height: 行高
        :param max_len: 每行最大长度
        :param pencolor: 文本颜色
        """
        self.pen.pencolor(pencolor)
        self.pen.undobufferentries()
        self.pen.setundobuffer(1000)

        line_start_x, current_y = self.pen.pos()
        current_x = line_start_x
        self.pen.hideturtle()
        self.pen.penup()

        for char in text:
            if char == "\n":
                current_y -= line_height
                current_x = line_start_x
                self.pen.goto(current_x, current_y)
                continue
            char_width = self._get_char_width(char, font)
            if (current_x - line_start_x) + char_width > max_len:
                current_y -= line_height
                current_x = line_start_x
                self.pen.goto(current_x, current_y)
            self.pen.goto(current_x, current_y)
            self.pen.pendown()
            self.pen.write(char, font=font)
            self.pen.penup()
            current_x += char_width
        self.pen.goto(self.initial_state["pos"][0], self.initial_state["pos"][1])
        self.pen.setheading(self.initial_state["heading"])
        self.pen.pencolor(self.initial_state["color"])
        if self.initial_state["pendown"]:
            self.pen.pendown()
        else:
            self.pen.penup()
        if self.initial_state["visible"]:
            self.pen.showturtle()

        self.pen.setundobuffer(0)
        self.pen.pencolor("black")

        self.screen.update()


class ImageDisplayer:
    def __init__(self, screen: turtle.Screen) -> None:
        """
        初始化图像显示类
        :param screen: Turtle屏幕对象
        """
        self.screen = screen

    def show_img(self, x: int, y: int, base64_data: str) -> turtle.Turtle:
        """
        显示Base64编码的Logo图片
        :param x: 图片显示的x坐标
        :param y: 图片显示的y坐标
        :param base64_data: Base64编码的图片数据，GIF格式
        :return: 显示图片的Turtle对象
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as temp_file:
            temp_path = temp_file.name
            img_data = base64.b64decode(base64_data)
            temp_file.write(img_data)

        self.screen.addshape(temp_path)

        logo_turtle = turtle.Turtle(shape=temp_path)
        logo_turtle.penup()
        logo_turtle.goto(x, y)

        return logo_turtle


class Qilou:
    def __init__(self, pen: turtle.Turtle) -> None:
        """
        初始化骑楼绘制类
        :param pen: Turtle画笔对象
        """
        self.pen = pen
        self.shape = BasicShape(self.pen)

    def draw_window(self, left: bool = True) -> turtle.Vec2D:
        """
        绘制骑楼的窗户
        :param left: 窗户是否在左侧
        :return: 窗户绘制起点的坐标
        """
        start_x, start_y = self.pen.pos()
        self.pen.pensize(1)

        self.shape.polygon(15, fillcolor="#46BFC7")
        self.pen.goto(self.pen.xcor() + 15 * 1.5, self.pen.ycor())
        self.shape.polygon(15, fillcolor="#46BFC7")
        self.pen.goto(self.pen.xcor() - 15 * 1.5, self.pen.ycor() - 15 * 1.5)
        self.shape.polygon(15, fillcolor="#46BFC7")
        self.pen.goto(self.pen.xcor() + 15 * 1.5, self.pen.ycor())
        self.shape.polygon(15, fillcolor="#46BFC7")

        self.pen.pensize(2)
        if left:
            self.pen.goto(start_x - 5, start_y + 20)
        else:
            self.pen.goto(start_x - 5, start_y + 5)
        self.pen.setheading(0)
        self.shape.polygon(48)

        if left:
            self.pen.goto(start_x - 5, start_y + 20)
        else:
            self.pen.goto(start_x - 5, start_y + 5)
        self.pen.pendown()
        self.pen.setheading(90)
        self.pen.circle(-24, 180)
        self.pen.penup()

        self.pen.fillcolor("#46BFC7")
        self.pen.begin_fill()
        if left:
            self.pen.goto(start_x + 6, start_y + 25)
        else:
            self.pen.goto(start_x + 6, start_y + 10)
        self.pen.pendown()
        self.pen.setheading(90)
        self.pen.circle(-14, 180)
        self.pen.penup()
        if left:
            self.pen.goto(start_x + 6, start_y + 25)
        else:
            self.pen.goto(start_x + 6, start_y + 10)
        self.pen.setheading(0)
        self.pen.pendown()
        self.pen.forward(28)
        self.pen.end_fill()
        self.pen.penup()
        self.pen.fillcolor("white")

        return turtle.Vec2D(start_x, start_x)

    def _single_pillar(self, extra: bool = False) -> None:
        """
        绘制一根骑楼的柱子
        :param extra: 是否额外绘制
        """
        start_x, start_y = self.pen.pos()
        self.pen.pensize(3)

        # lower pillar
        self.pen.setheading(180)
        for _ in range(2 if extra else 1): self.shape.rect((15, 120))

        # small pillar between big ones
        self.pen.goto(start_x - 20, start_y + 120)
        self.pen.setheading(90)
        self.shape.rect((10, 25))

        # upper pillar
        self.pen.goto(start_x - 15, start_y + 130)
        self.pen.setheading(90)
        self.shape.rect((60, 15))

    def draw_pillars(self, extra: bool = False) -> turtle.Vec2D:
        """
        绘制骑楼的柱子
        :param extra: 是否需要额外绘制
        :return: 柱子绘制起点的坐标
        """
        start_x, start_y = self.pen.pos()
        if extra:
            self._single_pillar(extra=True)
        else:
            self._single_pillar()
        self.pen.goto(start_x + 180, start_y)
        self._single_pillar()
        self.pen.goto(start_x, start_y + 120 + 10 + 60)
        self.shape.line(165)
        self.pen.goto(start_x, start_y + 120 + 10)
        self.pen.setheading(90)
        self.shape.half_ellipse(82.5, 45, (self.pen.xcor() + 82.5, self.pen.ycor()))
        self.pen.penup()

        return turtle.Vec2D(start_x, start_y)

    def _railing_pattern(self) -> None:
        """
        绘制骑楼栏杆的图案
        """
        start_x, start_y = self.pen.pos()
        self.pen.pencolor("gray")

        self.pen.pendown()
        self.pen.circle(10, 180)
        self.pen.setheading(0)
        self.pen.circle(10, 180)
        self.pen.penup()

        self.pen.goto(start_x + 20, start_y)
        self.pen.pendown()
        self.pen.circle(-10, 180)
        self.pen.setheading(180)
        self.pen.circle(-10, 180)
        self.pen.penup()

        self.pen.goto(start_x + 20, start_y)
        self.pen.setheading(90)
        self.pen.pendown()
        self.pen.forward(40)
        self.pen.penup()

        self.pen.goto(self.pen.xcor() - 10, self.pen.ycor() - 10)
        self.pen.setheading(0)
        self.pen.backward(5)
        self.pen.pendown()
        self.pen.forward(10)
        self.pen.penup()
        self.pen.goto(self.pen.xcor() - 5, self.pen.ycor() - 20)
        self.pen.setheading(0)
        self.pen.backward(5)
        self.pen.pendown()
        self.pen.forward(10)
        self.pen.penup()

        self.pen.goto(start_x + 20, start_y)

    def draw_railing(self) -> None:
        """
        绘制骑楼的栏杆
        """
        start_x, start_y = self.pen.pos()
        self.pen.pensize(3)
        self.pen.pendown()
        self.pen.forward(165)
        self.pen.penup()
        self.pen.goto(start_x, start_y + 40)
        self.pen.pendown()
        self.pen.forward(165)
        self.pen.penup()
        self.pen.pensize(1)
        self.pen.goto(start_x, start_y)
        for _ in range(8):
            self._railing_pattern()
        self.pen.goto(start_x - 15, start_y)

    def draw_roof(self, middle: bool = False) -> None:
        """
        绘制骑楼的屋顶
        :param middle: 是否为中间的屋顶
        """
        start_x, start_y = self.pen.pos()
        self.pen.pensize(3)

        self.shape.rect((15, 50))
        self.pen.goto(start_x + 180, start_y)
        self.shape.rect((15, 50))
        self.pen.goto(start_x + 15, start_y - 10)
        self.shape.line(165, 0)
        border_x = self.pen.xcor()
        self.pen.goto(self.pen.xcor(), self.pen.ycor() - 40)
        self.shape.line(165, 180)

        if middle:
            self.pen.goto(self.pen.xcor() + 5, self.pen.ycor() + 5)
            self.pen.setheading(90)
            self.shape.rect((30, 155), fillcolor="red")
            self.pen.goto(self.pen.xcor() + 82.5, self.pen.ycor())
            self.pen.write("岭南骑楼", font=("LiSu", 12, "normal"), align="center")
            self.pen.goto(start_x + 15, start_y - 10)
        else:
            self.pen.pensize(1)
            self.pen.setheading(0)
            self.pen.pendown()
            while self.pen.xcor() <= border_x:
                self.pen.setheading(80)
                self.pen.forward(40)
                self.pen.setheading(-80)
                self.pen.forward(40)
            self.pen.penup()
            self.pen.goto(start_x + 15, start_y - 10)
            self.pen.setheading(0)
            self.pen.pendown()
            while self.pen.xcor() <= border_x:
                self.pen.setheading(-80)
                self.pen.forward(40)
                self.pen.setheading(80)
                self.pen.forward(40)
            self.pen.penup()

    def draw(self, column: int = 3, floor: int = 2) -> None:
        """
        绘制骑楼
        :param column: 骑楼的列数
        :param floor: 骑楼的层数
        """
        start_x, start_y = self.pen.pos()
        for c in range(column):
            for f in range(floor):
                if c == 0 and f == 0:
                    pillars_start = self.draw_pillars(extra=True)
                else:
                    pillars_start = self.draw_pillars()
                if f != 0:
                    self.pen.goto(pillars_start[0] + 25, pillars_start[1] + 100)
                    self.draw_window(left=True)
                    self.pen.goto(pillars_start[0] + 95, pillars_start[1] + 115)
                    self.draw_window(left=False)
                    self.pen.goto(pillars_start[0], pillars_start[1])
                    self.draw_railing()
                if f == floor - 1:
                    self.pen.goto(pillars_start[0] - 15, pillars_start[1] + 240)
                    if c == column // 2:
                        self.draw_roof(middle=True)
                    else:
                        self.draw_roof()
                self.pen.goto(pillars_start[0], pillars_start[1] + 190)
            self.pen.goto(start_x + (c + 1) * 180, start_y)


class LionDance:
    def __init__(self, pen: turtle.Turtle, screen: turtle.Screen()) -> None:
        """
        初始化舞狮绘制类
        :param pen: Turtle画笔对象
        :param screen: Turtle屏幕对象
        """
        self.pen = pen
        self.screen = screen

        self.img = ImageDisplayer(self.screen)
        self.text = TextDisplayer(self.pen, self.screen)

    def draw(self, pos_img: Tuple[Union[int, float], Union[int, float]],
             pos_desc: Tuple[Union[int, float], Union[int, float]]) -> None:
        """
        绘制舞狮
        :param pos_img: 图像位置
        :param pos_desc: 文本位置
        """
        self.img.show_img(pos_img[0], pos_img[1], Constants.LIONDANCE_BASE64)
        self.pen.goto(pos_desc[0], pos_desc[1])
        self.text.write(Constants.LIONDANCE_DESC, max_len=500, line_height=35, font=("SimHei", 11, "normal"))


class Cantonese:
    def __init__(self, pen: turtle.Turtle, screen: turtle.Screen()):
        self.pen = pen
        self.screen = screen

        self.eg = TextDisplayer(self.pen, self.screen)
        self.desc = TextDisplayer(self.pen, self.screen)

    def draw(self, pos_eg: Tuple[Union[int, float], Union[int, float]],
             pos_desc: Tuple[Union[int, float], Union[int, float]]) -> None:
        self.pen.goto(pos_eg[0], pos_eg[1])
        self.eg.write(Constants.CANTONESE_EXAMPLE, font=("LiSu", 25, "italic"), pencolor="orange")
        self.pen.goto(pos_desc[0], pos_desc[1])
        self.desc.write(Constants.CANTONESE_DESC, max_len=600, font=("SimHei", 11, "normal"))


# 缩放因子
ZOOM_FACTOR = 2
# 基准点
BENCHMARK = (-800, -300)
# 调试模式
DEBUG = False


def main():
    """
    主函数，程序入口
    """
    screen = turtle.Screen()
    screen.title("岭南印记：骑楼・醒狮・粤韵")
    screen.bgcolor("white")
    if DEBUG:
        screen.tracer(0, 0)
    else:
        screen.tracer(1, 0)

    root = screen.getcanvas().winfo_toplevel()
    root.tk.call("tk", "scaling", _get_windows_scaling() * ZOOM_FACTOR)
    root.state("zoomed")

    pen = turtle.Turtle()
    pen.speed(10)
    if DEBUG: _draw_coordinate_system(pen, screen, axis_length=800)

    def _debug_get_point(*args):
        """
        调试函数，打印点击位置
        :param args: 点击位置的坐标
        """
        print(f"clicked at {args}")

    def diy_qilou(x, y):
        """
        绘制DIY骑楼
        :param x: 点击位置的x坐标
        :param y: 点击位置的y坐标
        """
        if -840 <= x <= -250 and -310 <= y <= 150:
            while True:
                column_input = screen.textinput("列", "输入骑楼的列数")
                if column_input is None:
                    return

                try:
                    column = int(column_input)
                    if column <= 0: raise ValueError
                    break
                except ValueError:
                    mb.showerror("错误", "无效的正整数!")

            while True:
                floor_input = screen.textinput("层", "输入骑楼的层数")
                if floor_input is None:
                    return
                try:
                    floor = int(floor_input)
                    if floor <= 1: raise ValueError
                    break
                except ValueError:
                    mb.showerror("错误", "无效的正整数，且必须大于 1 !")

            screen.clear()
            pen.showturtle()
            pen.goto(BENCHMARK)
            if DEBUG:
                screen.tracer(0, 0)
            else:
                screen.tracer(2, 0)
            qilou.draw(column, floor)

    if DEBUG:
        start = perf_counter()

    pen.penup()
    pen.goto(BENCHMARK)
    qilou = Qilou(pen)
    qilou.draw()

    pen.goto(-800, 400)
    qilou_td = TextDisplayer(pen, screen)
    qilou_td.write(Constants.QILOU_DESC, max_len=500, line_height=40, font=("SimHei", 11, "normal"))

    liondance = LionDance(pen, screen)
    liondance.draw((200, 230), (300, 300))

    cantonese = Cantonese(pen, screen)
    cantonese.draw((-50, -150), (-50, -200))

    pen.goto(0, -450)
    pen.pencolor("gray")
    pen.write(Constants.QILOU_NOTICE, True, "center", ("SimHei", 12, "normal"))

    pen.home()
    pen.hideturtle()
    if DEBUG:
        end = perf_counter()
        period = end - start
        print(f"主体绘制总耗时{round(period, 2)}s")
        screen.onclick(_debug_get_point)
    screen.onclick(diy_qilou)
    screen.listen()
    screen.update()
    screen.mainloop()


if __name__ == "__main__":
    try:
        main()
    except (turtle.Terminator, KeyboardInterrupt, TclError):
        print("程序已退出")
    else:
        print("程序已退出")
