# -*- coding: utf-8 -*-
"""sensor 平台: panel_config 数值传感器 (temp/hum/air/water/elec)."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_ID

from .. import PanelConfig, panel_config_ns

DEPENDENCIES = ["panel_config"]

CONF_PANEL = "panel"
CONF_SLOT = "slot"

PanelSensor = panel_config_ns.class_("PanelSensor", sensor.Sensor)

CONFIG_SCHEMA = sensor.sensor_schema(PanelSensor).extend(
    {
        cv.GenerateID(CONF_PANEL): cv.use_id(PanelConfig),
        cv.Required(CONF_SLOT): cv.one_of("temp", "hum", "air", "water", "elec"),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_PANEL])
    var = cg.new_Pvariable(config[CONF_ID])
    await sensor.register_sensor(var, config)
    cg.add(var.set_slot(config[CONF_SLOT]))
    cg.add(parent.register_sensor(var, config[CONF_SLOT]))
