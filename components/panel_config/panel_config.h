#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"

#include <esp_http_server.h>
#include <nvs.h>

#include <cstring>
#include <mutex>
#include <queue>
#include <string>
#include <vector>

namespace esphome {
namespace panel_config {

// 数值传感器: 温度/湿度/空气质量/水质/电费 (slot = temp/hum/air/water/elec)
class PanelSensor : public sensor::Sensor {
 public:
  void set_slot(const std::string &slot) { this->slot_ = slot; }
  std::string slot_;
};

// 文本传感器: 包裹/通知/家庭名 (slot = pkg/notice/home_name)
class PanelTextSensor : public text_sensor::TextSensor {
 public:
  void set_slot(const std::string &slot) { this->slot_ = slot; }
  std::string slot_;
};

class PanelConfig : public Component {
 public:
  void setup() override;
  void loop() override;
  float get_setup_priority() const override { return setup_priority::AFTER_WIFI; }

  void register_sensor(PanelSensor *s, const std::string &slot);
  void register_text(PanelTextSensor *s, const std::string &slot);

 protected:
  // ---- NVS 配置 ----
  void load_nvs_();
  void save_nvs_();
  void nvs_get_(nvs_handle_t h, const char *key, std::string &out);
  void nvs_set_(nvs_handle_t h, const char *key, const std::string &val);

  // ---- 应用配置 ----
  void apply_config_();

  // ---- HTTP 拉取 ----
  static void fetch_task_(void *arg);
  void fetch_all_();
  void fetch_entity_(const std::string &entity, const std::string &slot);

  // ---- Web 配置服务 ----
  static esp_err_t http_get_root_(httpd_req_t *req);
  static esp_err_t http_get_config_(httpd_req_t *req);
  static esp_err_t http_post_config_(httpd_req_t *req);
  void handle_post_(const std::string &body);
  static std::string url_decode_(const std::string &s);
  static std::string json_escape_(const std::string &s);

  // ---- 主循环消费队列 (slot, value) ----
  void push_result_(const std::string &slot, const std::string &value);

  httpd_handle_t server_{nullptr};
  TaskHandle_t fetch_task_{nullptr};
  std::vector<PanelSensor *> sensors_;
  std::vector<PanelTextSensor *> texts_;
  std::queue<std::pair<std::string, std::string>> pending_;
  std::mutex mutex_;
  bool configured_{false};

  // 配置字段
  std::string ha_url_;
  std::string ha_token_;
  std::string ent_temp_, ent_hum_, ent_air_, ent_water_, ent_elec_, ent_pkg_, ent_notice_;
  std::string home_name_, notice_;
};

}  // namespace panel_config
}  // namespace esphome
