from pathlib import Path
import json

from nonebot.permission import SUPERUSER, Permission
from nonebot.rule import Rule
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp import GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER


class Service(object):
    
    def __init__(self, name: str, enable_on_default: bool=True):
        self.name = name
        self.loc = Path(__file__).parent / '_services' / f'{self.name}.json'
        
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
                cfg = json.load(f).get('plugins')
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
            self.enabled_group = []
            self.disabled_group = []
            with open(self.loc,'w',encoding='UTF-8') as f:
                json.dump(
                    {
                    "enabled_groups": list(),
                    "disabled_groups": list(),
                    "enable_on_default": enable_on_default

                    },
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        else:
            with open(self.loc,'r',encoding='UTF-8') as f:
                cfg = json.load(f)
                self.enabled_group = cfg.get('enabled_groups')
                self.disabled_group = cfg.get('disabled_groups')
            with open(self.loc,'w',encoding='UTF-8') as f:
                json.dump(
                    {
                    "enabled_groups": self.enabled_group,
                    "disabled_groups": self.disabled_group,
                    "enable_on_default": enable_on_default

                    },
                    f,
                    indent=2,
                    ensure_ascii=False
                )
    def is_enabled(self) -> Rule:
        async def _is_enabled(bot: Bot, event: Event, state: T_State) -> bool:
            status = check_plugin(event.dict().get('group_id'),self.name)
            return status
        return Rule(_is_enabled)
        
    
def check_plugin(g_id: int, p_name: str) -> bool:
    with open(Path(__file__).parent / '_services' / f'{p_name}.json','r',encoding='UTF-8') as f:
        cfg = json.load(f)
    if g_id not in cfg.get('disabled_groups'):
        if cfg.get('enable_on_default') or g_id in cfg.get('enabled_groups'):
            return True
    return False

def disable_plugin(g_id: int, p_name: str):
    with open(Path(__file__).parent / '_services' / f'{p_name}.json','r',encoding='UTF-8') as f:
        cfg = json.load(f)
    enabled = set(cfg.get('enabled_groups'))
    enabled.discard(g_id)
    disabled = set(cfg.get('disabled_groups'))
    disabled.add(g_id)
    cfg['enabled_groups'] = list(enabled)
    cfg['disabled_groups'] = list(disabled)
    with open(Path(__file__).parent / '_services' / f'{p_name}.json','w',encoding='UTF-8') as f:
        f.write(json.dumps(cfg,indent=2,ensure_ascii=False))
        
def enable_plugin(g_id: int, p_name: str):
    with open(Path(__file__).parent / '_services' / f'{p_name}.json','r',encoding='UTF-8') as f:
        cfg = json.load(f)
    enabled = set(cfg.get('enabled_groups'))
    enabled.add(g_id)
    disabled = set(cfg.get('disabled_groups'))
    disabled.discard(g_id)
    cfg['enabled_groups'] = list(enabled)
    cfg['disabled_groups'] = list(disabled)
    with open(Path(__file__).parent / '_services' / f'{p_name}.json','w',encoding='UTF-8') as f:
        f.write(json.dumps(cfg,indent=2,ensure_ascii=False))
    
