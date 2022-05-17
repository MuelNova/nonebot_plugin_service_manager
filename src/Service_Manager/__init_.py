from pathlib import Path
import json

from .Service import *
from nonebot import export, get_driver, on_command
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

# Initialization
driver = get_driver()
export().Service = Service

plugins = []
cfg = Path(__file__).parent / '_services' / 'gcfg.json'

def _init():
    if Path.is_file(cfg):
        Path.unlink(cfg)

async def _get_plugins():
    if not Path.is_file(cfg):
        return
    with open(cfg,'r',encoding='UTF-8') as f:
        global plugins
        try:
            plugins = list(json.load(f).get('plugins'))
            logger.info('成功添加%d个插件于分群管理'%len(plugins))
            logger.info(str(plugins))
        except Exception as e:
            logger.error(e)
        

_init()
driver.on_startup(_get_plugins)

# Event Handler

lssv = on_command('lssv',rule=to_me(),priority=1)

@lssv.handle()
async def lssv_h(bot: Bot, event: Event, state: T_State):
    plus = ''
    for i in plugins:
        state = check_plugin(event.dict().get('group_id'),i)
        txt = '| {} | {}\n'.format('○'if state else '×',i)
        plus += txt
    
    await lssv.finish('群%d的插件有：\n===========\n%s\n===========\n通过 “启用/禁用 插件名「复数个用","隔开开关插件」”'%(event.dict().get('group_id'),plus))

enable_ = on_command('启用',rule=to_me(),priority=1,permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)
disable_ = on_command('禁用',rule=to_me(),priority=1,permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)

@enable_.handle()
async def enable_h(bot: Bot, event: Event, state: T_State):
    if args := str(event.get_message()).strip():
        state['p_name'] = args
@disable_.handle()
async def disable_h(bot: Bot, event: Event, state: T_State):
    if args := str(event.get_message()).strip():
        state['p_name'] = args

@enable_.got('p_name',prompt='你想启用哪些插件？')
async def enable_g(bot: Bot, event: Event, state: T_State):
    p_name = state['p_name'].split(',')
    done_plugins = []
    for i in p_name:
        if i in plugins:
            set_plugin(event.dict().get('group_id'),i)
            done_plugins.append(i)
    await enable_.finish(f"成功启用插件： {' | '.join(done_plugins)}")
        
@disable_.got('p_name',prompt='你想禁用哪些插件？')
async def disable_g(bot: Bot, event: Event, state: T_State):
    p_name = state['p_name'].split(',')
    done_plugins = []
    for i in p_name:
        if i in plugins:
            set_plugin(event.dict().get('group_id'),i,disable=True)
            done_plugins.append(i)
    await disable_.finish(f"成功禁用插件： {' | '.join(done_plugins)}")
