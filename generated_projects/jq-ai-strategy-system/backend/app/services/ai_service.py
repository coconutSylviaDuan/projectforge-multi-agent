from typing import List, Dict, Any
import random

def generate_code(prompt: str) -> str:
    """Return a simulated strategy code based on prompt."""
    # Default dual moving average strategy
    return '''# 双均线策略
# 策略说明：使用5日均线和20日均线的金叉死叉进行交易
import talib
import numpy as np

def initialize(context):
    context.stock = '000001.XSHE'  # 平安银行
    context.short_window = 5
    context.long_window = 20
    run_daily(strategy, time='every_bar')

def strategy(context, data):
    prices = history(30, '1d', 'close')[context.stock]
    if len(prices) < context.long_window:
        return
    short_ma = talib.SMA(prices, timeperiod=context.short_window)[-1]
    long_ma = talib.SMA(prices, timeperiod=context.long_window)[-1]
    current_position = context.portfolio.positions[context.stock].amount
    if short_ma > long_ma and current_position == 0:
        order_pct(context.stock, 1.0)
    elif short_ma < long_ma and current_position > 0:
        order_pct(context.stock, 0.0)
'''

def continue_chat(message: str, current_code: str, history: List[Dict[str, Any]]) -> tuple:
    """Simulate AI modify code based on user message."""
    # Very simple rule: if user says 'change', we modify parameters
    reply = "好的，已根据您的需求调整策略。"
    new_code = current_code
    if "均线周期" in message or "周期" in message:
        # Simulate changing parameters
        import re
        numbers = re.findall(r'\d+', message)
        if len(numbers) >= 2:
            short = numbers[0]
            long = numbers[1]
            new_code = current_code.replace('short_window = 5', f'short_window = {short}')
            new_code = new_code.replace('long_window = 20', f'long_window = {long}')
            reply = f"已将均线周期调整为{short}日和{long}日。"
        elif len(numbers) == 1:
            reply = "请提供两个周期参数，例如'10和30'。"
        else:
            reply = "请指定短周期和长周期数值。"
    elif "止损" in message or "止盈" in message:
        new_code += '\n# 添加了止损止盈逻辑（占位）'
        reply = "已添加止损止盈逻辑框架，请进一步完善细节。"
    else:
        reply = "收到您的修改请求，但目前仅支持调整均线周期和添加止损止盈。"
    return new_code, reply
