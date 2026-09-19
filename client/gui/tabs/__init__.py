# client/gui/tabs/__init__.py
from client.gui.tabs.tab_dashboard import DashboardTab
from client.gui.tabs.tab_manual import ManualInputTab
from client.gui.tabs.tab_upload import UploadTab
from client.gui.tabs.tab_setting import SettingTab
from client.gui.tabs.tab_anomaly import AnomalyTab
from client.gui.tabs.tab_scheduler import SchedulerTab
from client.gui.tabs.tab_placeholder import PlaceholderTab

__all__ = [
    "DashboardTab",
    "ManualInputTab",
    "UploadTab",
    "SettingTab",
    "AnomalyTab",
    "SchedulerTab",
    "PlaceholderTab",
]
