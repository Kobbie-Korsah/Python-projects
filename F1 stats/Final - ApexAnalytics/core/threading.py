"""
F1 Analytics Suite - Threading Module
QThread workers for background data processing
"""

from PyQt6.QtCore import QThread, pyqtSignal
from typing import Callable, Any, Dict, List

class GenericWorker(QThread):
    """Generic worker thread for any background task"""
    
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, target_function: Callable, *args, **kwargs):
        super().__init__()
        self.target_function = target_function
        self.args = args
        self.kwargs = kwargs
        self.result = None
    
    def run(self):
        """Execute the target function"""
        try:
            self.result = self.target_function(*self.args, **self.kwargs)
            self.finished.emit(self.result)
        except Exception as e:
            self.error.emit(str(e))

class TelemetryWorker(QThread):
    """Worker for fetching telemetry data"""
    
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int, str)
    
    def __init__(self, year: int, race: str, drivers: List[str], session_type: str = 'R'):
        super().__init__()
        self.year = year
        self.race = race
        self.drivers = drivers
        self.session_type = session_type
    
    def run(self):
        """Fetch telemetry data in background"""
        try:
            from utils.fastf1_utils import fetch_session_data, fetch_driver_telemetry, fetch_driver_laps
            
            self.progress_update.emit(10, "Loading session...")
            session = fetch_session_data(self.year, self.race, self.session_type)
            
            telemetry_data = {}
            total_drivers = len(self.drivers)
            
            for i, driver in enumerate(self.drivers):
                progress = 10 + int((i / total_drivers) * 80)
                self.progress_update.emit(progress, f"Loading data for {driver}...")
                
                telemetry = fetch_driver_telemetry(session, driver)
                laps = fetch_driver_laps(session, driver)
                
                telemetry_data[driver] = {
                    'telemetry': telemetry,
                    'laps': laps,
                    'session': session
                }
            
            self.progress_update.emit(100, "Complete!")
            self.data_ready.emit(telemetry_data)
            
        except Exception as e:
            self.error_occurred.emit(f"Telemetry fetch failed: {str(e)}")

class APIWorker(QThread):
    """Worker for API calls"""
    
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_function: Callable, *args, **kwargs):
        super().__init__()
        self.api_function = api_function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Execute API call"""
        try:
            result = self.api_function(*self.args, **self.kwargs)
            self.data_ready.emit({'result': result})
        except Exception as e:
            self.error_occurred.emit(f"API call failed: {str(e)}")

class MLTrainingWorker(QThread):
    """Worker for ML model training"""
    
    training_complete = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int, str)
    
    def __init__(self, training_data: Dict, model_type: str):
        super().__init__()
        self.training_data = training_data
        self.model_type = model_type
    
    def run(self):
        """Train ML model in background"""
        try:
            self.progress_update.emit(10, "Preparing training data...")
            # Add ML training logic here
            self.progress_update.emit(100, "Training complete!")
        except Exception as e:
            self.error_occurred.emit(f"ML training failed: {str(e)}")

class DataExportWorker(QThread):
    """Worker for exporting data"""
    
    export_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data: Any, file_path: str, export_format: str):
        super().__init__()
        self.data = data
        self.file_path = file_path
        self.export_format = export_format
    
    def run(self):
        """Export data in background"""
        try:
            if self.export_format == 'csv':
                import pandas as pd
                if isinstance(self.data, pd.DataFrame):
                    self.data.to_csv(self.file_path, index=False)
            elif self.export_format == 'json':
                import json
                with open(self.file_path, 'w') as f:
                    json.dump(self.data, f, indent=2, default=str)
            
            self.export_complete.emit(self.file_path)
        except Exception as e:
            self.error_occurred.emit(f"Export failed: {str(e)}")