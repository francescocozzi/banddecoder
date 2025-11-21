# Dual Band Decoder - Ham Radio Station Controller

Automatic band decoder for dual radio operation with 6-band support (160m-10m) and 6x2 antenna switching for ham radio contesting and SO2R operation.

## 🎯 Features

- **Dual Radio Support**: Simultaneous monitoring of two transceivers (YAESU/ICOM/KENWOOD)
- **6 HF Bands**: 160m, 80m, 40m, 20m, 15m, 10m
- **Band Detection Methods**:
  - BCD input (YAESU/KENWOOD)
  - Voltage sensing via ADS1115 (ICOM)
  - Auto-detection of radio type
- **Antenna Control**: 6x2 antenna switch with flexible routing
- **16 Relay Outputs**: 
  - 12 for band-pass filters (6 per radio)
  - 2 for antenna switching
  - 2 spare outputs
- **Real-time Monitoring**: Live band detection with <50ms latency
- **Web Interface**: Optional Flask-based control panel

## 🔧 Hardware Requirements

### Components
- Raspberry Pi 5 (or 3B/4 with legacy GPIO)
- 2× SainSmart 8-Channel Relay Modules
- 2× ADS1115 16-bit ADC (I2C) - for ICOM radios
- Resistors: 4× 1kΩ (BCD protection), 4× 10kΩ (voltage dividers)
- Dupont cables and jumpers

### Supported Radios
- **YAESU**: FT-991, FT-891, FT-dx10, etc. (BCD output)
- **KENWOOD**: TS-590, TS-890, etc. (BCD output)
- **ICOM**: IC-7300, IC-7610, IC-9700, etc. (Band Voltage output)

## 📐 Wiring Diagram

See [docs/WIRING.md](docs/WIRING.md) for complete pinout and connection diagrams.

### Quick Reference
```
Radio 1 BCD: GPIO 14,15,10,9
Radio 2 BCD: GPIO 13,19,26,11
Software I2C: GPIO 5 (SDA), GPIO 6 (SCL)
ADS1115 #1: 0x48 (Radio 1 ICOM)
ADS1115 #2: 0x49 (Radio 2 ICOM)
Relay Board 1: GPIO 18,23,24,25,8,7,12,16
Relay Board 2: GPIO 20,21,2,3,4,17,27,22
```

## 🚀 Installation

### 1. Operating System
```bash
# Flash Raspberry Pi OS Lite (64-bit) to SD card
# Use Raspberry Pi Imager with SSH pre-enabled
```

### 2. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies for Raspberry Pi 5
sudo apt install -y python3-pip python3-dev git python3-lgpio

# Enable I2C (optional, but recommended)
sudo raspi-config
# Interface Options → I2C → Enable
```

### 3. Clone Repository
```bash
cd ~
git clone git@github.com:IO7T/dual-band-decoder.git
cd dual-band-decoder
```

### 4. Install Python Requirements
```bash
pip3 install -r requirements.txt
```

### 5. Hardware Test
```bash
# Test relay outputs
sudo python3 tests/test_relays.py

# Test BCD inputs
sudo python3 tests/test_bcd.py

# Test ADS1115 (ICOM)
sudo python3 tests/test_ads1115.py
```

### 6. Run Band Decoder
```bash
sudo python3 src/band_decoder.py
```

## ⚙️ Configuration

Edit `config/settings.yaml` to customize:
- Band frequency ranges
- Relay assignments
- Antenna switching logic
- Radio types (auto/manual)
- Logging level

## 🔄 Systemd Service (Auto-start)
```bash
# Install service
sudo cp scripts/banddecoder.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable banddecoder.service
sudo systemctl start banddecoder.service

# Check status
sudo systemctl status banddecoder.service

# View logs
sudo journalctl -u banddecoder.service -f
```

## 📊 Web Interface (Optional)
```bash
# Start web interface
python3 src/web_interface.py

# Access: http://banddecoder.local:5000
```

Features:
- Live band display for both radios
- Antenna routing configuration
- Relay status monitoring
- System diagnostics

## 🧪 Testing
```bash
# Run all tests
cd tests
sudo python3 run_all_tests.py

# Individual component tests
sudo python3 test_gpio.py          # GPIO basic test
sudo python3 test_relays.py        # Relay sequential test
sudo python3 test_bcd.py           # BCD input test
sudo python3 test_ads1115.py       # ADS1115 I2C test
sudo python3 test_integration.py   # Full system test
```

## 📖 Documentation

- [Complete Wiring Diagram](docs/WIRING.md)
- [Hardware Assembly Guide](docs/HARDWARE.md)
- [Software Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🐛 Debugging
```bash
# Enable verbose logging
sudo python3 src/band_decoder.py --verbose

# Test individual components
sudo python3 src/band_decoder.py --test-mode

# Monitor GPIO states
watch -n 0.1 'raspi-gpio get'
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 👤 Author

**IZ7KHR** - Amateur Radio Station
- Callsign: IZ7KHR
- GitHub: [@IZ7KHR](https://github.com/francescocozzi)

## 🙏 Acknowledgments

- Raspberry Pi Foundation for excellent hardware and documentation
- Ham radio community for testing and feedback
- Contributors to lgpio and ADS1115 libraries

## 📡 Ham Radio Application

Perfect for:
- **SO2R (Single Operator Two Radios)**: Automatic band selection
- **Multi-Multi Contests**: Filter switching for multiple stations
- **Field Day**: Rapid band changes
- **DXpeditions**: Reliable antenna routing

### Contest Logger Integration
Compatible with:
- N1MM+
- Win-Test  
- WriteLog
- DXLog.net

## 🔧 Calibration

See [docs/CALIBRATION.md](docs/CALIBRATION.md) for:
- ICOM voltage calibration
- BCD signal verification
- Relay timing adjustment
- Antenna switch testing

## 📈 Performance

- Band detection latency: <50ms
- Relay switching time: 10ms
- Antenna switching: 15ms
- CPU usage: <5% (RPi 5)
- Memory: ~50MB

## 🛠️ Roadmap

- [ ] Support for 2m/70cm bands
- [ ] N1MM+ UDP integration
- [ ] Web-based calibration wizard
- [ ] Frequency-based detection (CAT control)
- [ ] MQTT support for home automation

---

**73 de IZ7KHR** 📻

*Good luck and good DX!*
