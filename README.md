# Монитор энергии WAVIoT для Home Assistant
![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
Пользовательская интеграция для Home Assistant для мониторинга **энергомеров WAVIoT** через официальный API [waviot.ru](https://lk.waviot.ru).
Она предоставляет сенсоры текущих показаний счетчика электроэнергии, суточный баланс потребления энергии и с начала месяца, выраженную как в kWh так и в деньгах. Интеграция полностью конфигурируется через UI.
---
## ✨ Возможности
-  **Сенсор текущих показаний в разрезе действующих тарифов абонента**
- ️ **Сенсор суточного баланса и с начала месяца (в kWh и в денежном выражении) **
-  **Конфигурирование текущих тарифов абонента**
  -  Автоматические обновление показаний
  -  Данные получаются напрямую из API WAVIoT
- ⚙️ Полная конфигурация через UI
- 🧩 Совместима с HACS (пользовательское хранилище)
---
## 🧰 Установка
### Метод 1: HACS (Рекомендуется)
Предпочтительный способ — использовать HACS:
1. Найдите и загрузите эту интеграцию в вашу установку HA через HACS, или нажмите:  
   [![Открыть репозиторий HACS][hacs-repo-badge]](https://my.home-assistant.io/redirect/hacs_repository/?owner=Yury1873&repository=hass-waviot&category=integration)
2. Перезапустите Home Assistant
3. Добавьте эту интеграцию в Home Assistant, или нажмите:  
   [![Добавить интеграцию][config-flow-badge]](https://my.home-assistant.io/redirect/config_flow_start?domain=waviot_updater)

### Метод 2: Ручная установка
1. Скопируйте папку `custom_components/waviot_updater` в директорию `config/custom_components/` вашего Home Assistant.
2. Перезапустите Home Assistant.
---
## ⚙️ Конфигурация
После установки и перезапуска:
1. Перейдите в **Настройки → Устройства и сервисы → Добавить интеграцию**
2. Найдите **WAVIoT Updater**
3. Введите:
- **API-ключ** (из вашего аккаунта WAVIoT)
4. Готово! Интеграция создаст следующие сенсоры:
| Entity ID | Описание | Единица |
|-----------|----------|---------|
| `sensor.waviot_<modem_id>_energy_total` | Общая накопленная энергия, тариф "Ночь" (T1) | кВт·ч |
| `sensor.waviot_<modem_id>_energy_total` | Общая накопленная энергия, тариф "День" (T2) | кВт·ч |
| `sensor.waviot_<modem_id>_energy_total` | Общая накопленная энергия (T1) | кВт·ч |
---
## 🔄 Источник данных
Все данные получаются из:
https://lk.waviot.ru/api**
с использованием вашего **API-ключа** и **ID модема**.
---
## 🧪 Пример вывода
| Сенсор | Пример значения | Описание |
|--------|------------------|----------|
| `sensor.waviot_86145d_energy_total` | 21149.162 | Общее показание |
---
## ⚠️ Примечания
- Интеграция получает новые данные каждые **10 минут**.
- Убедитесь, что ваш API-ключ действителен для вашего аккаунта WAVIoT.
---
## 🧑‍💻 Разработчик
**Автор:** [soulripper13](https://github.com/yury1873)
**Лицензия:** [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
**Репозиторий:** [hass-waviot](https://github.com/yury1873/hass-waviot)
---
## 🩵 Поддержка
Если эта интеграция вам полезна, пожалуйста, ⭐️ репозиторию или [откройте issue](https://github.com/yury1873/hass-waviot/issues) для предложений и отчетов об ошибках.

---

# WAVIoT Energy Monitor for Home Assistant
![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
A custom Home Assistant integration to monitor **WAVIoT energy meters** via the official [curog.ru](https://lk.curog.ru) API.
It provides electricity usage, battery level, and temperature sensors — with full UI configuration.
---
## ✨ Features
- 🔋 **Battery Level Sensor**
- 🌡️ **Temperature Sensor**
- 🔁 Automatic updates every 10 minutes
- 🧠 Data fetched directly from the WAVIoT API
- ⚙️ Full configuration via the UI
- 🧩 HACS compatible (custom repository)
---
## 🧰 Installation
### Method 1: HACS (Recommended)
The preferred way is to use HACS:
1. Search and download this integration to your HA installation via HACS, or click:  
   [![Open HACS Repository][hacs-repo-badge]](https://my.home-assistant.io/redirect/hacs_repository/?owner=soulripper13&repository=hass-waviot&category=integration)
2. Restart Home Assistant
3. Add this integration to Home Assistant, or click:  
   [![Add Integration][config-flow-badge]](https://my.home-assistant.io/redirect/config_flow_start?domain=waviot_updater)

### Method 2: Manual Installation
1. Copy the folder `custom_components/waviot_updater` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
---
## ⚙️ Configuration
After installing and restarting:
1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **WAVIoT Updater**
3. Enter:
- **API Key** (from your WAVIoT account)
- **Modem ID** (e.g. `86145D`)
4. Done! The integration will create the following sensors:
| Entity ID | Description | Unit |
|-----------|-------------|------|
| `sensor.waviot_<modem_id>_energy_total` | Total accumulated energy (T1) | kWh |
| `sensor.waviot_<modem_id>_battery` | Battery level | % |
| `sensor.waviot_<modem_id>_temperature` | Device temperature | °C |
---
## 🔄 Data Source
All data is fetched from:
https://lk.waviot.ru/api.data/get_modem_channel_values/
using your **API key** and **modem ID**.
---
## 🧪 Example Output
| Sensor | Example Value | Description |
|--------|---------------|-------------|
| `sensor.waviot_86145d_energy_total` | 21149.162 | Total reading |
| `sensor.waviot_86145d_battery` | 85 | Battery level |
| `sensor.waviot_86145d_temperature` | 22.5 | Device temperature |
---
## ⚠️ Notes
- The integration fetches new data every **10 minutes**.
- Ensure your API key is valid and that the modem ID exists on your WAVIoT account.
- You can reconfigure at any time by removing and re-adding the integration.
---
## 🧑‍💻 Developer
**Author:** [Yury1873](https://github.com/Yury1873)
**License:** [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
**Repository:** [hass-waviot](https://github.com/soulripper13/hass-waviot)
---
## 🩵 Support
If you find this integration helpful, please ⭐️ the repo or [open an issue](https://github.com/Yury1873/hass-waviot/issues) for suggestions and bug reports.

---

[hacs-repo-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[config-flow-badge]: https://my.home-assistant.io/badges/config_flow_start.svg
