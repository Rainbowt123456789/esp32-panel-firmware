# -*- coding: utf-8 -*-
"""text_sensor 平台: panel_config 文本传感器 (pkg/notice/home_name)."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_ID

from .. import PanelConfig, panel_config_ns

DEPENDENCIES = ["panel_config"]

CONF_PANEL = "panel"
CONF_SLOT = "slot"

PanelTextSensor = panel_config_ns.class_("PanelTextSensor", text_sensor.TextSensor)

CONFIG_SCHEMA = text_sensor.text_sensor_schema(PanelTextSensor).extend(
    {
        cv.GenerateID(CONF_PANEL): cv.use_id(PanelConfig),
        cv.Required(CONF_SLOT): cv.one_of("pkg", "notice", "home_name"),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_PANEL])
    var = cg.new_Pvariable(config[CONF_ID])
    await text_sensor.register_text_sensor(var, config)
    cg.add(var.set_slot(config[CONF_SLOT]))
    cg.add(parent.register_text(var, config[CONF_SLOT]))
