# Service_Manager
A plugin to help control multi-groups plugins

# 使用方法
- 将```Service_Manager```文件夹放入```不同于```Nonebot2所生成的```plugins```文件夹的目录下
>由于目前load_plugins方法对加载插件顺序不能定义，所以必须将其单独放出插件文件夹外

- 在```Bot.py```插件引用行的首行引入插件
```python
nonebot.load_plugin("nogger.Service_Manager")
nonebot.load_plugins("nogger/plugins")
# 一个可能的例子
# 在这个例子下我的plugins文件夹位于"./nogger/plugins"，换而言之意味着我的Service_Manager文件夹与他同级
```
>(目录树待更新）

- 在自己的插件中导入Service
```python
from nonebot import require

Service = require('nogger.Service_Manager').Service # 位置应与上面保持同步
sv = Service('your_plugin_name') # enable_on_default = True
```

- 为自己的事件处理器添加Rule
```python
pixiv_daily_call = on_command('车来',rule=to_me() & sv.is_enabled(),priority=5)
# 一个经过测试的例子
```

- 发送```@Bot lssv```查看权限开关

# 更新计划
- 把我上课时候偷偷写的Service的__init__重新搞一下，看着很脑残（
- 添加```manage_permission```,```use_permission```
- ...
