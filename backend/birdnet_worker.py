"""Isolated official Analyzer process. Assets are mandatory; never auto-download."""
import os, sys
from pathlib import Path
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ.setdefault('MPLCONFIGDIR', str(Path(sys.argv[3]) / '.mpl'))
from birdnet_analyzer import config as cfg, utils
from birdnet_analyzer.analyze import analyze
root = Path(sys.argv[3]).resolve()
cfg.BIRDNET_MODEL_PATH = str(root / 'BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite')
cfg.BIRDNET_LABELS_FILE = str(root / 'BirdNET_GLOBAL_6K_V2.4_Labels.txt')
cfg.MDATA_MODEL_PATH = str(root / 'BirdNET_GLOBAL_6K_V2.4_MData_Model_V2_FP16.tflite')
def require_assets(*args, **kwargs):
    for name in (cfg.BIRDNET_MODEL_PATH, cfg.BIRDNET_LABELS_FILE):
        if not Path(name).exists():
            raise RuntimeError('Run scripts/setup_birdnet.py online first: ' + name)
utils.ensure_model_exists = require_assets
# Defense against runtime downloads, telemetry or model fetching in dependencies.
import socket
socket.socket.connect = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError('BirdNET worker network disabled'))
if __name__ == '__main__':
    analyze(sys.argv[1], output=sys.argv[2], min_conf=.5, rtype={'csv'}, threads=1)
