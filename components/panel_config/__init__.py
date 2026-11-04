# -*- coding: utf-8 -*-
"""panel_config: 面板 Web 配置后台 + HA 数据拉取组件.

面板自带配置网页 (端口 8080):
  - 配置 Home Assistant 地址/长期令牌/7 个数据实体/家庭名/通知文本
  - 配置保存到 NVS, 重启不丢
  - 每 15s 通过 HA REST API 拉取实体状态, publish 到自定义 sensor/text_sensor
主页 label 通过现有 ESPHome 动态文本机制读取这些 sensor, 无需直接操作 LVGL.
"""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

AUTO_LOAD = ["sensor", "text_sensor"]
DEPENDENCIES = ["wifi", "network"]

panel_config_ns = cg.esphome_ns.namespace("panel_config")
PanelConfig = panel_config_ns.class_("PanelConfig", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(PanelConfig),
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
