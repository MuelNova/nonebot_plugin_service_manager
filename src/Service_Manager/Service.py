from pathlib import Path
import json

from nonebot.permission import SUPERUSER, Permission
from nonebot.rule import Rule
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp import GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER


def _save_config(service):
    logger.debug(service.__dict__)
    with open(service.loc,'w',encoding='UTF-8') as f:
        json.dump(
            {
                    "enabled_groups": service.enabled_groups,
                    "disabled_groups": service.disabled_groups,
                    "enable_on_default": service.enable_on_default

            },
            f,
            indent=2,
            ensure_ascii=False
         )

def _load_config(service=None,path=None) -> dict:
    if service is not None:
        path = service.loc
    with open(path,'r',encoding='UTF-8') as f:
        try:
            cfg = json.load(f)
            return cfg
        except Exception as e:
            logger.error(e)
            return {}

class Service(object):
    
    def __init__(self, name: str, enable_on_default: bool=True):
        self.name = name
        self.loc = Path(__file__).parent / '_services' / f'{self.name}.json'
        self.enable_on_default = enable_on_default
        # First load
        if not Path.is_dir(self.loc.parent):
            Path.mkdir(self.loc.parent)
        if not Path.is_file(pcfg := self.loc.parent / 'gcfg.json'):
            with open(pcfg,'w',encoding='UTF-8') as f:
                json.dump(
                {
                    "plugins":[self.name]
                },
                f,
                indent=2,
                ensure_ascii=False
                )
        else:
            with open(pcfg,'r',encoding='UTF-8') as f:
                cfg = _load_config(path=pcfg).get('plugins')
                cfg.append(self.name)
            with open(pcfg,'w',encoding='UTF-8') as f:
                json.dump(
                {
                    "plugins":list(cfg)
                },
                f,
                indent=2,
                ensure_ascii=False
                )
         
        if not Path.is_file(self.loc):
            self.enabled_groups = list()
            self.disabled_groups = list()
        else:
            cfg = _load_config(self)
            self.enabled_groups = cfg.get('enabled_groups')
            self.disabled_groups = cfg.get('disabled_groups')
        _save_config(self)
        
    def is_enabled(self) -> Rule:
        async def _is_enabled(bot: Bot, event: Event, state: T_State) -> bool:
            status = check_plugin(event.dict().get('group_id'),self.name)
            return status
        return Rule(_is_enabled)
        
    
def check_plugin(g_id: int, p_name: str) -> bool:
    if not Path.is_file(path := Path(__file__).parent / '_services' / f'{p_name}.json'):
        return False
    cfg = _load_config(path=path)
    if g_id not in cfg.get('disabled_groups'):
        if cfg.get('enable_on_default') or g_id in cfg.get('enabled_groups'):
            return True
    return False

def set_plugin(g_id: int, p_name: str,disable=False):
    cfg = _load_config(path=Path(__file__).parent / '_services' / f'{p_name}.json')
    enabled = set(cfg.get('enabled_groups'))
    disabled = set(cfg.get('disabled_groups'))
    if disable:
        enabled.discard(g_id)
        disabled.add(g_id)
    else:
        enabled.add(g_id)
        disabled.discard(g_id)
    cfg['enabled_groups'] = list(enabled)
    cfg['disabled_groups'] = list(disabled)
    with open(Path(__file__).parent / '_services' / f'{p_name}.json','w',encoding='UTF-8') as f:
        json.dump(cfg,f,indent=2,ensure_ascii=False)
