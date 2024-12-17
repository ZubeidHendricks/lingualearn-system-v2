# Troubleshooting Guide

## Development Issues

### Node.js/React Issues

#### 'react-scripts' Not Found
**Problem:** Error when starting the application
**Solution:**
```bash
npm install react-scripts --legacy-peer-deps
```

#### Dependency Conflicts
**Problem:** npm dependency resolution errors
**Solution:**
```bash
npm install --legacy-peer-deps
```

### Python/ML Issues

#### Model Loading Errors
**Problem:** SAM model not loading
**Solution:**
1. Check model path in config
2. Verify model file exists
3. Check Python environment

#### CUDA Issues
**Problem:** GPU not detected
**Solution:**
1. Install CUDA toolkit
2. Update GPU drivers
3. Verify torch installation:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## Runtime Issues

### Camera Problems

1. Check permissions:
   - Windows: Settings > Privacy > Camera
   - macOS: System Preferences > Security
   - Linux: Check udev rules

2. Test camera:
```python
import cv2
cap = cv2.VideoCapture(0)
print(cap.isOpened())
```

### Audio Problems

1. Check microphone permissions
2. Test audio setup:
```python
import sounddevice as sd
print(sd.query_devices())
```

### Performance Issues

1. Monitor resources:
```bash
# GPU usage
nvidia-smi

# Memory usage
top
```

2. Optimize settings:
- Reduce video resolution
- Adjust processing frequency
- Use lighter model variant

## Error Messages

### Common Errors

#### "No module named 'torch'"
```bash
pip install torch torchvision
```

#### "Error: no CUDA GPUs"
- Using CPU fallback
- Check NVIDIA drivers
- Verify CUDA installation

#### "WebSocket connection failed"
1. Check if backend is running
2. Verify port availability
3. Check firewall settings

## Logs

### Location
- Windows: `%APPDATA%\LinguaLearn\logs`
- macOS: `~/Library/Logs/LinguaLearn`
- Linux: `~/.config/LinguaLearn/logs`

### Debug Mode
```bash
DEBUG=true npm start
```

## Getting Help

1. Check GitHub Issues
2. Review documentation
3. Contact support

## Data Recovery

### Backup Location
```bash
~/.lingualearn/backups
```

### Restore Backup
```bash
python tools/restore_backup.py --date YYYY-MM-DD
```