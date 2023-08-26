# This example will show a PyQt5 window of all discovered devices.
# Devices can then be selected to drive with a gamepad

import time
import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from RobotRaconteur.Client import *
import traceback
import threading
from urllib.parse import urlparse
import importlib_resources
import io

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
        refresh_button_widget = QPushButton()
        refresh_button_widget.setText("Refresh")
        service_info_font = service_info_label.font()
        service_info_font.setFamily("Courier New")
        service_info_label.setFont(service_info_font)
        service_info_label.setTextInteractionFlags(Qt.TextSelectableByMouse |
                                            Qt.TextSelectableByKeyboard)
        service_info_label.setCursor(QCursor(Qt.IBeamCursor))
        service_info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        service_info_label_scroll = QScrollArea()
        service_info_label_scroll.setFixedHeight(200)
        service_info_label_scroll.setWidget(service_info_label)
        service_info_label_scroll.setWidgetResizable(True)
        
        vbox = QVBoxLayout()
        vbox.addWidget(service_list_widget)        
        vbox.addWidget(service_info_label_scroll) 
        vbox.addWidget(refresh_button_widget)
        w.setLayout(vbox)
        
        w.setWindowTitle("Available Services")
                            
        service_selected=False
        service_info=None
        webcam_service_info=None                    
           

        def refresh():
            RRN.UpdateDetectedNodes(['rr+tcp','rrs+tcp','rr+quic'])

        refresh_button_widget.clicked.connect(refresh)
        
        def selection_changed():
            try:
                current_item = service_list_widget.currentItem()
                if current_item is None:
                    service_info_label.setText("")
                else:
                    service_info=current_item.service_info
                    candidate_urls = []
                    try:
                        node_info = RRN.GetDetectedNodeCacheInfo(service_info.NodeID)
                        for node_url in node_info.ConnectionURL:
                            node_short_url = node_url.split('?')[0]
                            candidate_urls.append(f"{node_short_url}?nodeid={service_info.NodeID.ToString('D')}&service={service_info.Name}")
                            candidate_urls.append(f"{node_short_url}?nodename={service_info.NodeName}&service={service_info.Name}")                            
                    except:
                        traceback.print_exc()
                        
                    info_text = io.StringIO()
                    print("Service:", file=info_text)
                    print(f"    NodeID:     {service_info.NodeID}", file=info_text)
                    print(f"    NodeName:   {service_info.NodeName}", file=info_text)
                    print(f"    Service:    {service_info.Name}", file=info_text)
                    print(f"    Type:       {service_info.RootObjectType}", file=info_text)
                    print(f"    Implements: {', '.join(service_info.RootObjectImplements)}", file=info_text)
                    print(f"    URL:        {service_info.ConnectionURL[0]}", file=info_text)
                    if len(service_info.Attributes) > 0:
                        print("    Attributes:", file=info_text)
                        for k,v in service_info.Attributes.items():
                            print(f"        {k}: {v}", file=info_text)
                    if len(candidate_urls) > 0:
                        print("    Candidate URLs:", file=info_text)
                        for candidate_url in candidate_urls:
                            print(f"        {candidate_url}", file=info_text)
                    service_info_label.setText(info_text.getvalue())
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
    
    icon_path = str(importlib_resources.files(__package__) / 'RRIcon.bmp')

    app=QApplication(sys.argv)
    icon = QIcon(icon_path)
    app.setWindowIcon(icon)    
    with RR.ClientNodeSetup():
        c = ServiceBrowser(app)
        c.run()
      
if __name__ == '__main__':
    main()
