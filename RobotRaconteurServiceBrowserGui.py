# This example will show a PyQt5 window of all discovered devices.
# Devices can then be selected to drive with a gamepad

import time
import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from RobotRaconteur.Client import *
import traceback
import threading
from urllib.parse import urlparse

if (sys.version_info > (3, 0)):
    def cmp(x, y):
        return (x > y) - (x < y)
    
   
class ServiceBrowser(QObject):
    
    detected_nodes_updated = Signal()    
    
    def __init__(self, app):
        super(ServiceBrowser,self).__init__(app)       
        
        self.app=app
        self.update_lock = threading.Lock()

        self.detected_nodes_updated.connect(self.update_subscriber_window)
                               
        self.service_subscriber = RRN.SubscribeServiceInfo2([])
        self.service_subscriber.ServiceDetected += self.service_detected
        self.service_subscriber.ServiceLost += self.service_lost
               
    def run(self):
       self.subscriber_window()       
    
    def service_detected(self, subscription, client_id, client_info):
        self.detected_nodes_updated.emit()
            
    def service_lost(self, subscription, client_id, client_info):
        self.detected_nodes_updated.emit()
                
    def update_subscriber_window(self):
        with self.update_lock:
            l = self.service_list_widget
            if l is None:
                return
            list_values = []
            
            #Find services, assume that nodes with the same IP address are related
            for s in self.service_subscriber.GetDetectedServiceInfo2().values():
                list_values.append(ServiceQListWidgetItem(s))
                        
            current_item = l.currentItem()
            if (current_item is not None):
                current_nodeid = current_item.service_info.NodeID
                current_service_name = current_item.service_info.Name
            else:
                current_nodeid = None
                current_service_name= None
                             
            l.clear()
            
            if len(list_values) == 0:
                if self.service_info_widget is not None:
                    self.service_info_widget.setText("")
                return
                        
            for lv in list_values:
                l.addItem(lv)
            for lv in list_values:
                if current_nodeid == lv.service_info.NodeID \
                  and current_service_name == lv.service_info.Name:
                    l.setCurrentItem(lv)
            
    
    def subscriber_window(self):
    
        w = QFrame()
        w.resize(850,500)
                
        service_list_widget = QListWidget()        
        service_info_label = QLabel()
        service_info_label.setFixedHeight(200)
        service_info_font = service_info_label.font()
        service_info_font.setFamily("Courier New")
        service_info_label.setFont(service_info_font)
        service_info_label.setTextInteractionFlags(Qt.TextSelectableByMouse |
                                            Qt.TextSelectableByKeyboard)
        service_info_label.setCursor(QCursor(Qt.IBeamCursor))
        service_info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        vbox = QVBoxLayout()
        vbox.addWidget(service_list_widget)        
        vbox.addWidget(service_info_label)        
        w.setLayout(vbox)
        
        w.setWindowTitle("Available Services")
                            
        service_selected=False
        service_info=None
        webcam_service_info=None                    
            
        
        def selection_changed():
            try:
                current_item = service_list_widget.currentItem()
                if current_item is None:
                    service_info_label.setText("")
                else:
                    service_info=current_item.service_info
                    info_text = "Service:\n" \
                        "    NodeID:     " + str(service_info.NodeID) + "\n" \
                        "    NodeName:   " + service_info.NodeName + "\n" \
                        "    Service:    "  + service_info.Name + "\n" \
                        "    Type:       " + service_info.RootObjectType + "\n" \
                        "    Implements: " + ', '.join(service_info.RootObjectImplements) +"\n" \
                        "    URL:        " + service_info.ConnectionURL[0] + "\n"
                    if len(service_info.Attributes) > 0:
                        info_text += "    Attributes:\n"
                        for k,v in service_info.Attributes.items():
                            info_text += "        " + str(k) + ": " + str(v) + "\n"
                    service_info_label.setText(info_text)
            except:
                traceback.print_exc()
               
        service_list_widget.itemSelectionChanged.connect(selection_changed)
        
        self.service_list_widget=service_list_widget
        self.service_info_widget=service_info
        try:
            self.update_subscriber_window()
            w.show()
            self.app.exec_()
        finally:        
            self.service_list_widget = None
            self.service_info_widget = None    
        
    
          
class ServiceQListWidgetItem(QListWidgetItem):
    def __init__(self, service_info):
        super(ServiceQListWidgetItem,self).__init__()
        self.service_info = service_info        
        self.setText(service_info.ConnectionURL[0])

def main():
    
    app=QApplication(sys.argv)        
    icon = QIcon('RRIcon.bmp')
    app.setWindowIcon(icon)    
    with RR.ClientNodeSetup():
        c = ServiceBrowser(app)
        c.run()
      
if __name__ == '__main__':
    main()
