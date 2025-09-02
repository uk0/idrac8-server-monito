import os
import requests
import json
import warnings
from typing import Dict, List, Optional, Any
from datetime import datetime
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

class IDRACRedfishClient:
    """
    iDRAC Redfish API client for hardware monitoring
    Based on Dell's iDRAC-Redfish-Scripting repository
    """
    
    def __init__(self, idrac_ip: str, username: str, password: str):
        self.idrac_ip = idrac_ip
        self.username = username
        self.password = password
        self.base_url = f"https://{idrac_ip}/redfish/v1"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> Optional[Dict]:
        """Make HTTP request to iDRAC Redfish API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PATCH":
                response = self.session.patch(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code in [200, 201, 202, 204]:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"status": "success"}
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None
    
    def get_system_info(self) -> Optional[Dict]:
        """Get basic system information"""
        return self._make_request("/Systems/System.Embedded.1")
    
    def get_storage_controllers(self) -> Optional[Dict]:
        """Get storage controllers information"""
        return self._make_request("/Systems/System.Embedded.1/Storage")
    
    def get_storage_controller_details(self, controller_id: str) -> Optional[Dict]:
        """Get detailed information about a specific storage controller"""
        return self._make_request(f"/Systems/System.Embedded.1/Storage/{controller_id}")
    
    def get_physical_disks(self, controller_id: str) -> Optional[Dict]:
        """Get physical disks for a storage controller"""
        return self._make_request(f"/Systems/System.Embedded.1/Storage/{controller_id}/Drives")
    
    def get_physical_disk_details(self, controller_id: str, disk_id: str) -> Optional[Dict]:
        """Get detailed information about a specific physical disk"""
        return self._make_request(f"/Systems/System.Embedded.1/Storage/{controller_id}/Drives/{disk_id}")
    
    def get_virtual_disks(self, controller_id: str) -> Optional[Dict]:
        """Get virtual disks for a storage controller"""
        return self._make_request(f"/Systems/System.Embedded.1/Storage/{controller_id}/Volumes")
    
    def get_virtual_disk_details(self, controller_id: str, volume_id: str) -> Optional[Dict]:
        """Get detailed information about a specific virtual disk"""
        return self._make_request(f"/Systems/System.Embedded.1/Storage/{controller_id}/Volumes/{volume_id}")
    
    def get_sel_logs(self) -> Optional[Dict]:
        """Get System Event Log entries"""
        return self._make_request("/Managers/iDRAC.Embedded.1/LogServices/Sel/Entries")
    
    def get_lc_logs(self) -> Optional[Dict]:
        """Get Lifecycle Controller log entries"""
        return self._make_request("/Managers/iDRAC.Embedded.1/LogServices/Lclog/Entries")

class IDRACHardwareMonitor:
    """
    Hardware monitoring service that processes iDRAC data
    """
    
    def __init__(self, idrac_client: IDRACRedfishClient):
        self.client = idrac_client
    
    def _normalize_status(self, redfish_status: dict) -> str:
        """Convert Redfish status to our standard format"""
        if not redfish_status:
            return "unknown"
        
        state = redfish_status.get("State", "").lower()
        health = redfish_status.get("Health", "").lower()
        
        if state == "absent" or state == "unavailableoffline":
            return "offline"
        elif health == "critical" or state == "standbyspare":
            return "critical"
        elif health == "warning":
            return "warning"
        elif health == "ok" and state == "enabled":
            return "healthy"
        else:
            return "unknown"
    
    def _convert_bytes_to_gb(self, size_bytes: int) -> float:
        """Convert bytes to GB"""
        if not size_bytes:
            return 0.0
        return round(size_bytes / (1024**3), 2)
    
    def _extract_disk_metrics(self, disk_data: dict) -> dict:
        """Extract key metrics from disk data"""
        metrics = {}
        
        # Extract temperature if available
        if "Oem" in disk_data and "Dell" in disk_data["Oem"]:
            dell_data = disk_data["Oem"]["Dell"]
            if "DellPhysicalDisk" in dell_data:
                disk_info = dell_data["DellPhysicalDisk"]
                metrics["temperature"] = disk_info.get("LastSystemInventoryTime")
                metrics["powerOnHours"] = disk_info.get("PowerOnHours")
                metrics["predictiveFailure"] = disk_info.get("PredictedMediaLifeLeftPercent")
        
        return metrics
    
    def get_physical_disks_status(self) -> List[Dict]:
        """Get status of all physical disks"""
        physical_disks = []
        
        # Get storage controllers
        controllers_data = self.client.get_storage_controllers()
        if not controllers_data or "Members" not in controllers_data:
            return physical_disks
        
        for controller_ref in controllers_data["Members"]:
            controller_id = controller_ref["@odata.id"].split("/")[-1]
            
            # Get physical disks for this controller
            disks_data = self.client.get_physical_disks(controller_id)
            if not disks_data or "Members" not in disks_data:
                continue
            
            for disk_ref in disks_data["Members"]:
                disk_id = disk_ref["@odata.id"].split("/")[-1]
                
                # Get detailed disk information
                disk_details = self.client.get_physical_disk_details(controller_id, disk_id)
                if not disk_details:
                    continue
                
                # Extract disk information
                status = self._normalize_status(disk_details.get("Status", {}))
                size_gb = self._convert_bytes_to_gb(disk_details.get("CapacityBytes", 0))
                metrics = self._extract_disk_metrics(disk_details)
                
                disk_info = {
                    "id": disk_id,
                    "name": disk_details.get("Name", disk_id),
                    "status": status,
                    "size": f"{size_gb} GB",
                    "interface": disk_details.get("Protocol", "Unknown"),
                    "model": disk_details.get("Model", "Unknown"),
                    "serialNumber": disk_details.get("SerialNumber", "Unknown"),
                    "manufacturer": disk_details.get("Manufacturer", "Unknown"),
                    "mediaType": disk_details.get("MediaType", "Unknown"),
                    "location": disk_details.get("PhysicalLocation", {}).get("PartLocation", {}).get("ServiceLabel", "Unknown"),
                    "temperature": metrics.get("temperature", "N/A"),
                    "powerOnHours": metrics.get("powerOnHours", "N/A"),
                    "predictiveFailure": metrics.get("predictiveFailure", "N/A"),
                    "lastUpdated": datetime.now().isoformat()
                }
                
                physical_disks.append(disk_info)
        
        return physical_disks
    
    def get_virtual_disks_status(self) -> List[Dict]:
        """Get status of all virtual disks/RAID arrays"""
        virtual_disks = []
        
        # Get storage controllers
        controllers_data = self.client.get_storage_controllers()
        if not controllers_data or "Members" not in controllers_data:
            return virtual_disks
        
        for controller_ref in controllers_data["Members"]:
            controller_id = controller_ref["@odata.id"].split("/")[-1]
            
            # Get virtual disks for this controller
            volumes_data = self.client.get_virtual_disks(controller_id)
            if not volumes_data or "Members" not in volumes_data:
                continue
            
            for volume_ref in volumes_data["Members"]:
                volume_id = volume_ref["@odata.id"].split("/")[-1]
                
                # Get detailed volume information
                volume_details = self.client.get_virtual_disk_details(controller_id, volume_id)
                if not volume_details:
                    continue
                
                # Extract volume information
                status = self._normalize_status(volume_details.get("Status", {}))
                size_gb = self._convert_bytes_to_gb(volume_details.get("CapacityBytes", 0))
                
                # Extract RAID level from Oem data if available
                raid_type = "Unknown"
                if "Oem" in volume_details and "Dell" in volume_details["Oem"]:
                    dell_data = volume_details["Oem"]["Dell"]
                    if "DellVirtualDisk" in dell_data:
                        raid_type = dell_data["DellVirtualDisk"].get("RAIDType", "Unknown")
                
                virtual_disk_info = {
                    "id": volume_id,
                    "name": volume_details.get("Name", volume_id),
                    "status": status,
                    "size": f"{size_gb} GB",
                    "raidLevel": raid_type,
                    "lastUpdated": datetime.now().isoformat()
                }
                
                virtual_disks.append(virtual_disk_info)
        
        return virtual_disks
    
    def get_system_alerts(self) -> List[Dict]:
        """Get system alerts from event logs"""
        alerts = []
        
        # Get SEL (System Event Log) entries
        sel_data = self.client.get_sel_logs()
        if sel_data and "Members" in sel_data:
            for entry in sel_data["Members"][:10]:  # Get last 10 entries
                severity = entry.get("Severity", "Unknown").lower()
                if severity in ["critical", "warning"]:
                    alert = {
                        "id": entry.get("Id", str(len(alerts))),
                        "message": entry.get("Message", "Unknown alert"),
                        "severity": severity,
                        "timestamp": entry.get("Created", datetime.now().isoformat()),
                        "acknowledged": False
                    }
                    alerts.append(alert)
        
        return alerts
    
    def get_full_hardware_status(self) -> Dict:
        """Get complete hardware status"""
        system_info = self.client.get_system_info()
        
        return {
            "serverInfo": {
                "name": system_info.get("Name", "Unknown") if system_info else "Unknown",
                "model": system_info.get("Model", "Unknown") if system_info else "Unknown",
                "manufacturer": system_info.get("Manufacturer", "Unknown") if system_info else "Unknown",
                "serialNumber": system_info.get("SerialNumber", "Unknown") if system_info else "Unknown",
                "powerState": system_info.get("PowerState", "Unknown") if system_info else "Unknown",
                "lastUpdated": datetime.now().isoformat()
            },
            "physicalDisks": self.get_physical_disks_status(),
            "virtualDisks": self.get_virtual_disks_status(),
            "alerts": self.get_system_alerts(),
            "lastRefresh": datetime.now().isoformat()
        }