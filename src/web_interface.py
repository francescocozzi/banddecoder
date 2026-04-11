#!/usr/bin/env python3
"""
Web Interface
Flask-based web interface for band decoder monitoring and control
"""

import sys
import json
import time
import logging
import threading
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Import band decoder modules
from config_loader import ConfigLoader

# Global state
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state storage
state = {
    'radio1': {
        'band': 'N/A',
        'bcd_value': 0,
        'relay_active': None,
        'last_update': 0
    },
    'radio2': {
        'band': 'N/A',
        'bcd_value': 0,
        'relay_active': None,
        'last_update': 0
    },
    'relays': {
        'board1': [False] * 8,
        'board2': [False] * 8
    },
    'antenna_mode': 'r1a_r2b',
    'manual_mode': False,
    'pending_relay_command': None,  # {'board': 1, 'relay': 0, 'state': True}
    'system': {
        'uptime': 0,
        'start_time': time.time(),
        'status': 'running'
    }
}

config = None


def load_configuration():
    """Load configuration from YAML"""
    global config
    try:
        config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
        config = ConfigLoader(str(config_path))
        logger.info("Configuration loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return False


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Get current system status"""
    try:
        # Update uptime
        state['system']['uptime'] = int(time.time() - state['system']['start_time'])

        return jsonify({
            'success': True,
            'data': state
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config')
def api_config():
    """Get current configuration"""
    try:
        if config is None:
            return jsonify({
                'success': False,
                'error': 'Configuration not loaded'
            }), 500

        return jsonify({
            'success': True,
            'data': {
                'bands': config.get('bands'),
                'radios': {
                    'radio1': {
                        'name': config.get('radios.radio1.name'),
                        'type': config.get('radios.radio1.type')
                    },
                    'radio2': {
                        'name': config.get('radios.radio2.name'),
                        'type': config.get('radios.radio2.type')
                    }
                },
                'timing': config.get('timing'),
                'antenna_switch': config.get('antenna_switch')
            }
        })
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/radio/<int:radio_num>')
def api_radio_status(radio_num):
    """Get status of specific radio"""
    try:
        if radio_num not in [1, 2]:
            return jsonify({
                'success': False,
                'error': 'Invalid radio number'
            }), 400

        radio_key = f'radio{radio_num}'
        return jsonify({
            'success': True,
            'data': state[radio_key]
        })
    except Exception as e:
        logger.error(f"Error getting radio status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/relays')
def api_relays():
    """Get relay states"""
    try:
        return jsonify({
            'success': True,
            'data': state['relays']
        })
    except Exception as e:
        logger.error(f"Error getting relay states: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/antenna', methods=['GET', 'POST'])
def api_antenna():
    """Get or set antenna mode"""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'data': {
                    'mode': state['antenna_mode'],
                    'available_modes': config.get('antenna_switch.modes') if config else {}
                }
            })

        elif request.method == 'POST':
            data = request.get_json()
            mode = data.get('mode')

            # Validate mode
            if config:
                valid_modes = config.get('antenna_switch.modes', {}).keys()
                if mode not in valid_modes:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid mode. Valid modes: {list(valid_modes)}'
                    }), 400

            state['antenna_mode'] = mode
            logger.info(f"Antenna mode changed to: {mode}")

            return jsonify({
                'success': True,
                'data': {'mode': mode}
            })

    except Exception as e:
        logger.error(f"Error with antenna API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/relay/test', methods=['POST'])
def api_relay_test():
    """Test relay (for debugging)"""
    try:
        data = request.get_json()
        board = data.get('board', 1)
        relay = data.get('relay', 0)
        state_val = data.get('state', False)

        if board not in [1, 2]:
            return jsonify({
                'success': False,
                'error': 'Invalid board number'
            }), 400

        if relay < 0 or relay >= 8:
            return jsonify({
                'success': False,
                'error': 'Invalid relay number (0-7)'
            }), 400

        board_key = f'board{board}'
        state['relays'][board_key][relay] = state_val

        logger.info(f"Relay test: Board {board}, Relay {relay} → {state_val}")

        return jsonify({
            'success': True,
            'data': {
                'board': board,
                'relay': relay,
                'state': state_val
            }
        })

    except Exception as e:
        logger.error(f"Error testing relay: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/system/restart', methods=['POST'])
def api_system_restart():
    """Restart band decoder service (placeholder)"""
    try:
        logger.warning("System restart requested")
        return jsonify({
            'success': True,
            'message': 'Restart signal sent'
        })
    except Exception as e:
        logger.error(f"Error restarting system: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/manual/mode', methods=['GET', 'POST'])
def api_manual_mode():
    """Get or set manual mode"""
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'manual_mode': state['manual_mode']})

        data = request.get_json()
        enabled = data.get('enabled', False)
        state['manual_mode'] = enabled
        if not enabled:
            state['pending_relay_command'] = None
        logger.info(f"Manual mode: {'ON' if enabled else 'OFF'}")
        return jsonify({'success': True, 'manual_mode': state['manual_mode']})

    except Exception as e:
        logger.error(f"Error setting manual mode: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/manual/relay', methods=['POST'])
def api_manual_relay():
    """Queue a manual relay command (executed by band_decoder with interlock check)"""
    try:
        if not state['manual_mode']:
            return jsonify({'success': False, 'error': 'Manual mode not active'}), 400

        data = request.get_json()
        board = data.get('board')
        relay = data.get('relay')
        relay_state = data.get('state')

        if board not in [1, 2] or not isinstance(relay, int) or relay < 0 or relay >= 8:
            return jsonify({'success': False, 'error': 'Invalid parameters'}), 400

        state['pending_relay_command'] = {'board': board, 'relay': relay, 'state': relay_state}
        logger.info(f"Manual relay queued: Board{board} Relay{relay} → {relay_state}")
        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error queuing relay command: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/update_state', methods=['POST'])
def api_update_state():
    """
    Update state from band decoder main process.
    Returns manual_mode flag and any pending relay command to be executed.
    """
    try:
        data = request.get_json()

        # Always update radio band/BCD info
        if 'radio1' in data:
            state['radio1'].update(data['radio1'])
            state['radio1']['last_update'] = time.time()
        if 'radio2' in data:
            state['radio2'].update(data['radio2'])
            state['radio2']['last_update'] = time.time()

        # Always accept relay states from band_decoder: it reads actual hardware state
        # In manual mode, band_decoder skips switch_band() so these updates
        # only arrive after manual commands are executed
        if 'relays' in data:
            state['relays'].update(data['relays'])

        if not state['manual_mode']:
            if 'antenna_mode' in data:
                state['antenna_mode'] = data['antenna_mode']

        # Return manual mode flag and pending command (clears it after sending)
        pending = state['pending_relay_command']
        if pending:
            state['pending_relay_command'] = None

        return jsonify({
            'success': True,
            'manual_mode': state['manual_mode'],
            'relay_command': pending
        })

    except Exception as e:
        logger.error(f"Error updating state: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run Flask server"""
    logger.info(f"Starting web interface on {host}:{port}")
    logger.info(f"Access at: http://{host}:{port}")

    app.run(host=host, port=port, debug=debug, threaded=True)


def main():
    """Main entry point"""
    print("=" * 70)
    print("BAND DECODER - Web Interface")
    print("=" * 70)
    print()

    # Load configuration
    if not load_configuration():
        print("ERROR: Failed to load configuration")
        return 1

    # Get web interface settings
    host = config.get('web_interface.host', '0.0.0.0')
    port = config.get('web_interface.port', 5000)
    debug = config.get('web_interface.debug', False)

    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print()

    try:
        run_server(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\nShutdown requested")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
