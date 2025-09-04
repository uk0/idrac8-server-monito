import os
import requests
import json
import warnings
from typing import Dict, List, Optional, Any
from datetime import datetime
import urllib3
import ssl
import sys
import time

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")


# Custom adapter to handle weak DH keys
class WeakDHAdapter(requests.adapters.HTTPAdapter):
    """Custom adapter to allow weak DH keys for older iDRAC systems"""

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers('DEFAULT:@SECLEVEL=1')
        context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


class IDRACRedfishClient:
    """
    iDRAC Redfish API client for hardware monitoring
    Based on Dell's iDRAC-Redfish-Scripting repository
    """

    def __init__(self, idrac_ip: str, username: str, password: str):
        self.idrac_ip = idrac_ip
        self.username = username
        self.password = password
        self.base_url = f"https://{idrac_ip}"

        # Create session with custom adapter
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False

        # Mount custom adapter for weak DH keys
        adapter = WeakDHAdapter()
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'OData-Version': '4.0'
        })

        # Test connection and get service root
        self._test_connection()

    def _test_connection(self):
        """Test connection to iDRAC and verify Redfish service is available"""
        try:
            response = self.session.get(f"{self.base_url}/redfish/v1", timeout=10)
            if response.status_code != 200:
                print(f"Warning: Unable to connect to iDRAC at {self.idrac_ip}")
                print(f"Status Code: {response.status_code}")
        except Exception as e:
            print(f"Warning: Connection test failed: {str(e)}")

    def _make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> Optional[Dict]:
        """Make HTTP request to iDRAC Redfish API"""
        # Ensure endpoint starts with /redfish/v1 if not already
        if not endpoint.startswith('/redfish/v1'):
            endpoint = f"/redfish/v1{endpoint}"

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
                if response.text:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"status": "success", "text": response.text}
                else:
                    return {"status": "success"}
            elif response.status_code == 404:
                # Don't print for 404 errors, they might be expected
                return None
            else:
                print(f"HTTP Error {response.status_code} for {url}")
                if response.text:
                    print(f"Response: {response.text[:500]}")
                return None

        except requests.exceptions.SSLError as e:
            print(f"SSL Error for {url}: {str(e)}")
            print("Try updating iDRAC firmware or check SSL settings")
            return None
        except requests.exceptions.Timeout:
            print(f"Request timeout for {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {url}: {str(e)}")
            return None

    def get_system_info(self) -> Optional[Dict]:
        """Get basic system information"""
        return self._make_request("/redfish/v1/Systems/System.Embedded.1")

    def get_storage_controllers(self) -> Optional[Dict]:
        """Get storage controllers information"""
        # Try both possible endpoints
        result = self._make_request("/redfish/v1/Systems/System.Embedded.1/Storage")
        if not result:
            # Try alternative endpoint for older iDRAC versions
            result = self._make_request("/redfish/v1/Systems/System.Embedded.1/SimpleStorage")
        return result

    def get_storage_controller_details(self, controller_id: str) -> Optional[Dict]:
        """Get detailed information about a specific storage controller"""
        return self._make_request(f"/redfish/v1/Systems/System.Embedded.1/Storage/{controller_id}")

    def get_physical_disks(self, controller_id: str) -> Optional[Dict]:
        """Get physical disks for a storage controller"""
        # First try to get controller details which might contain drives
        controller_details = self.get_storage_controller_details(controller_id)
        if controller_details and "Drives" in controller_details:
            # Return the drives from controller details
            return {"Members": controller_details["Drives"]}

        # Otherwise try the Drives endpoint
        return self._make_request(f"/redfish/v1/Systems/System.Embedded.1/Storage/{controller_id}/Drives")

    def get_physical_disk_details(self, disk_odata_id: str) -> Optional[Dict]:
        """Get detailed information about a specific physical disk"""
        # disk_odata_id should be the full @odata.id path
        if disk_odata_id.startswith('/'):
            return self._make_request(disk_odata_id)
        else:
            return self._make_request(f"/redfish/v1/Chassis/System.Embedded.1/Drives/{disk_odata_id}")

    def get_virtual_disks(self, controller_id: str) -> Optional[Dict]:
        """Get virtual disks for a storage controller"""
        # First try to get controller details which might contain volumes
        controller_details = self.get_storage_controller_details(controller_id)
        if controller_details and "Volumes" in controller_details:
            # Get the volumes collection
            volumes_link = controller_details["Volumes"].get("@odata.id")
            if volumes_link:
                return self._make_request(volumes_link)

        # Otherwise try the Volumes endpoint directly
        return self._make_request(f"/redfish/v1/Systems/System.Embedded.1/Storage/{controller_id}/Volumes")

    def get_virtual_disk_details(self, volume_odata_id: str) -> Optional[Dict]:
        """Get detailed information about a specific virtual disk"""
        # If it's a full path, use it directly
        if volume_odata_id.startswith('/'):
            return self._make_request(volume_odata_id)
        # Otherwise construct the path
        return None

    def get_sel_logs(self) -> Optional[Dict]:
        """Get System Event Log entries"""
        return self._make_request("/redfish/v1/Managers/iDRAC.Embedded.1/Logs/Sel",method="GET")

    def get_lc_logs(self) -> Optional[Dict]:
        """Get Lifecycle Controller log entries"""
        return self._make_request("/redfish/v1/Managers/iDRAC.Embedded.1/Logs/Lclog",method="GET")


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

        state = str(redfish_status.get("State", "")).lower()
        health = str(redfish_status.get("Health", "")).lower()
        health_rollup = str(redfish_status.get("HealthRollup", "")).lower()

        # Check health first (most important)
        if health == "critical" or health_rollup == "critical":
            return "critical"
        elif health == "warning" or health_rollup == "warning":
            return "warning"
        elif health == "ok" or health_rollup == "ok":
            if state == "enabled":
                return "healthy"
            elif state == "standbyspare":
                return "standby"
            else:
                return "healthy"
        elif state == "absent" or state == "unavailableoffline":
            return "offline"
        else:
            return "unknown"

    def _convert_bytes_to_gb(self, size_bytes: Any) -> float:
        """Convert bytes to GB"""
        try:
            if not size_bytes:
                return 0.0
            size_bytes = int(size_bytes)
            return round(size_bytes / (1024 ** 3), 2)
        except (ValueError, TypeError):
            return 0.0

    def _extract_disk_metrics(self, disk_data: dict) -> dict:
        """Extract key metrics from disk data"""
        metrics = {}

        # Extract temperature and other metrics
        if "Oem" in disk_data and "Dell" in disk_data["Oem"]:
            dell_data = disk_data["Oem"]["Dell"]
            if "DellPhysicalDisk" in dell_data:
                disk_info = dell_data["DellPhysicalDisk"]
                metrics["temperature"] = disk_info.get("Temperature")
                metrics["powerOnHours"] = disk_info.get("PowerOnHours")
                metrics["predictiveFailure"] = disk_info.get("PredictedMediaLifeLeftPercent")
                metrics["operationPercentComplete"] = disk_info.get("OperationPercentComplete")

        # Try to get metrics from standard fields
        if "Temperature" in disk_data:
            temp_data = disk_data["Temperature"]
            if isinstance(temp_data, dict):
                metrics["temperature"] = temp_data.get("ReadingCelsius")

        if "PredictedMediaLifeLeftPercent" in disk_data:
            metrics["predictiveFailure"] = disk_data["PredictedMediaLifeLeftPercent"]

        return metrics

    def get_physical_disks_status(self) -> List[Dict]:
        """Get status of all physical disks"""
        physical_disks = []

        # Get storage controllers
        controllers_data = self.client.get_storage_controllers()
        if not controllers_data or "Members" not in controllers_data:
            print("No storage controllers found")
            return physical_disks

        for controller_ref in controllers_data["Members"]:
            controller_id = controller_ref["@odata.id"].split("/")[-1]

            # Get controller details to find drives
            controller_details = self.client.get_storage_controller_details(controller_id)
            if not controller_details:
                continue

            # Get drives from controller
            drives = controller_details.get("Drives", [])
            if not drives:
                # Try getting physical disks directly
                disks_data = self.client.get_physical_disks(controller_id)
                if disks_data and "Members" in disks_data:
                    drives = disks_data["Members"]

            for drive_ref in drives:
                if isinstance(drive_ref, dict) and "@odata.id" in drive_ref:
                    disk_odata_id = drive_ref["@odata.id"]
                else:
                    continue

                # Get detailed disk information
                disk_details = self.client.get_physical_disk_details(disk_odata_id)
                if not disk_details:
                    continue

                # Extract disk information
                status = self._normalize_status(disk_details.get("Status", {}))
                size_gb = self._convert_bytes_to_gb(disk_details.get("CapacityBytes", 0))
                metrics = self._extract_disk_metrics(disk_details)

                # Get location info
                location = "Unknown"
                if "PhysicalLocation" in disk_details:
                    loc = disk_details["PhysicalLocation"]
                    if "PartLocation" in loc:
                        location = loc["PartLocation"].get("ServiceLabel", "Unknown")

                disk_info = {
                    "id": disk_details.get("Id", disk_odata_id.split("/")[-1]),
                    "name": disk_details.get("Name", "Unknown"),
                    "status": status,
                    "size": f"{size_gb} GB",
                    "interface": disk_details.get("Protocol", "Unknown"),
                    "model": disk_details.get("Model", "Unknown"),
                    "serialNumber": disk_details.get("SerialNumber", "Unknown"),
                    "manufacturer": disk_details.get("Manufacturer", "Unknown"),
                    "mediaType": disk_details.get("MediaType", "Unknown"),
                    "location": location,
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
            print("No storage controllers found")
            return virtual_disks

        for controller_ref in controllers_data["Members"]:
            controller_id = controller_ref["@odata.id"].split("/")[-1]
            print(f"Checking controller: {controller_id}")

            # Get controller details first
            controller_details = self.client.get_storage_controller_details(controller_id)
            if not controller_details:
                continue

            # Check if controller has Volumes link
            if "Volumes" in controller_details:
                volumes_link = controller_details["Volumes"].get("@odata.id")
                if volumes_link:
                    print(f"Found volumes link: {volumes_link}")
                    volumes_data = self.client._make_request(volumes_link)

                    if volumes_data and "Members" in volumes_data:
                        print(f"Found {len(volumes_data['Members'])} volumes")

                        for volume_ref in volumes_data["Members"]:
                            volume_odata_id = volume_ref.get("@odata.id")
                            if not volume_odata_id:
                                continue

                            print(f"Getting volume details from: {volume_odata_id}")
                            # Get detailed volume information using the full path
                            volume_details = self.client.get_virtual_disk_details(volume_odata_id)
                            if not volume_details:
                                continue

                            # Extract volume information
                            status = self._normalize_status(volume_details.get("Status", {}))
                            size_gb = self._convert_bytes_to_gb(volume_details.get("CapacityBytes", 0))

                            # Extract RAID level
                            raid_type = volume_details.get("RAIDType", "Unknown")
                            if raid_type == "Unknown" and "VolumeType" in volume_details:
                                raid_type = volume_details["VolumeType"]

                            # Try to get from OEM data if not found
                            if raid_type == "Unknown" and "Oem" in volume_details and "Dell" in volume_details["Oem"]:
                                dell_data = volume_details["Oem"]["Dell"]
                                if "DellVirtualDisk" in dell_data:
                                    raid_type = dell_data["DellVirtualDisk"].get("RAIDType", "Unknown")

                            virtual_disk_info = {
                                "id": volume_details.get("Id", volume_odata_id.split("/")[-1]),
                                "name": volume_details.get("Name", "Unknown"),
                                "status": status,
                                "size": f"{size_gb} GB",
                                "raidLevel": raid_type,
                                "encrypted": volume_details.get("Encrypted", False),
                                "optimumIOSize": volume_details.get("OptimumIOSizeBytes", "N/A"),
                                "blockSizeBytes": volume_details.get("BlockSizeBytes", "N/A"),
                                "lastUpdated": datetime.now().isoformat()
                            }

                            virtual_disks.append(virtual_disk_info)
                    else:
                        print(f"No volumes found in response")
            else:
                print(f"Controller {controller_id} has no Volumes link")

        return virtual_disks

    def get_system_alerts(self) -> List[Dict]:
        """Get system alerts from event logs"""
        alerts = []

        try:
            # Get SEL (System Event Log) entries
            print("Fetching SEL logs...")
            sel_data = self.client.get_sel_logs()
            print(sel_data)
            if sel_data and "Members" in sel_data:
                print(f"Found {len(sel_data['Members'])} SEL entries")

                # Process entries and filter for alerts
                for entry in sel_data["Members"]:
                    severity = str(entry.get("Severity", "")).lower()
                    entry_type = str(entry.get("EntryType", "")).lower()

                    # Include critical, warning, and some informational alerts
                    if severity in ["critical", "warning"] or entry_type == "sel" or entry_type == "alert":
                        alert = {
                            "id": entry.get("Id", str(len(alerts))),
                            "message": entry.get("Message", "Unknown alert"),
                            "severity": severity if severity else "information",
                            "timestamp": entry.get("Created", datetime.now().isoformat()),
                            "messageId": entry.get("MessageId", ""),
                            "entryType": entry.get("EntryType", "Event"),
                            "sensorType": entry.get("SensorType", ""),
                            "sensorNumber": entry.get("SensorNumber", 0),
                            "acknowledged": False
                        }
                        alerts.append(alert)

                # Sort by timestamp (newest first) and limit to recent alerts
                alerts.sort(key=lambda x: x["timestamp"], reverse=True)
                alerts = alerts[:20]  # Keep last 20 alerts

            else:
                print("No SEL entries found")

            # Also try to get LC logs for additional alerts
            print("Fetching LC logs...")
            lc_data = self.client.get_lc_logs()
            print(lc_data)
            if lc_data and "Members" in lc_data:
                print(f"Found {len(lc_data['Members'])} LC log entries")

                for entry in lc_data["Members"][:10]:  # Check last 10 LC logs
                    severity = str(entry.get("Severity", "")).lower()
                    if severity in ["critical", "warning"]:
                        # Check if this alert is not already in the list
                        message = entry.get("Message", "")
                        if not any(a["message"] == message for a in alerts):
                            alert = {
                                "id": f"LC_{entry.get('Id', len(alerts))}",
                                "message": message,
                                "severity": severity,
                                "timestamp": entry.get("Created", datetime.now().isoformat()),
                                "messageId": entry.get("MessageId", ""),
                                "entryType": "LifecycleLog",
                                "acknowledged": False
                            }
                            alerts.append(alert)

        except Exception as e:
            print(f"Error fetching alerts: {str(e)}")

        # Sort final list by timestamp
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)

        return alerts[:20]  # Return top 20 most recent alerts

    def get_full_hardware_status(self) -> Dict:
        """Get complete hardware status"""
        print("=" * 60)
        print("Starting full hardware status collection...")
        start_time = time.time()

        # Get system info
        print("1. Fetching system information...")
        system_info = self.client.get_system_info()

        # Extract system info safely
        server_info = {
            "name": "Unknown",
            "model": "Unknown",
            "manufacturer": "Unknown",
            "serialNumber": "Unknown",
            "powerState": "Unknown",
            "biosVersion": "Unknown",
            "processorSummary": {},
            "memorySummary": {},
            "lastUpdated": datetime.now().isoformat()
        }

        if system_info:
            server_info.update({
                "name": system_info.get("Name", "Unknown"),
                "model": system_info.get("Model", "Unknown"),
                "manufacturer": system_info.get("Manufacturer", "Unknown"),
                "serialNumber": system_info.get("SerialNumber", "Unknown"),
                "powerState": system_info.get("PowerState", "Unknown"),
                "biosVersion": system_info.get("BiosVersion", "Unknown"),
                "systemType": system_info.get("SystemType", "Physical"),
                "uuid": system_info.get("UUID", ""),
                "hostName": system_info.get("HostName", ""),
                "indicatorLED": system_info.get("IndicatorLED", ""),
                "status": self._normalize_status(system_info.get("Status", {}))
            })

            # Add processor summary
            if "ProcessorSummary" in system_info:
                proc_summary = system_info["ProcessorSummary"]
                server_info["processorSummary"] = {
                    "count": proc_summary.get("Count", 0),
                    "model": proc_summary.get("Model", "Unknown"),
                    "status": self._normalize_status(proc_summary.get("Status", {}))
                }

            # Add memory summary
            if "MemorySummary" in system_info:
                mem_summary = system_info["MemorySummary"]
                total_memory = mem_summary.get("TotalSystemMemoryGiB", 0)
                server_info["memorySummary"] = {
                    "totalSystemMemoryGiB": total_memory,
                    "status": self._normalize_status(mem_summary.get("Status", {}))
                }

        # Get physical disks
        print("2. Fetching physical disk information...")
        physical_disks = self.get_physical_disks_status()

        # Get virtual disks
        print("3. Fetching virtual disk information...")
        virtual_disks = self.get_virtual_disks_status()

        # Get alerts
        print("4. Fetching system alerts...")
        alerts = self.get_system_alerts()

        elapsed_time = round(time.time() - start_time, 2)
        print(f"Hardware status collection completed in {elapsed_time}s")
        print("=" * 60)

        return {
            "serverInfo": server_info,
            "physicalDisks": physical_disks,
            "virtualDisks": virtual_disks,
            "alerts": alerts,
            "lastRefresh": datetime.now().isoformat(),
            "collectionTimeSeconds": elapsed_time
        }


# Example usage
if __name__ == "__main__":
    # Test connection
    IDRAC_IP = "10.88.51.66"
    USERNAME = "root"
    PASSWORD = "uh-WYoKv_p8zeM!t"

    try:
        print(f"Connecting to iDRAC at {IDRAC_IP}...")
        client = IDRACRedfishClient(IDRAC_IP, USERNAME, PASSWORD)
        monitor = IDRACHardwareMonitor(client)

        print("\nGetting hardware status...")
        status = monitor.get_full_hardware_status()

        print("\n=== Server Information ===")
        for key, value in status["serverInfo"].items():
            if not isinstance(value, dict):
                print(f"{key}: {value}")

        print(f"\n=== Physical Disks ({len(status['physicalDisks'])}) ===")
        for disk in status["physicalDisks"]:
            print(f"- {disk['name']}: {disk['status']} ({disk['size']}) - {disk['location']}")

        print(f"\n=== Virtual Disks ({len(status['virtualDisks'])}) ===")
        for vdisk in status["virtualDisks"]:
            print(f"- {vdisk['name']}: {vdisk['status']} ({vdisk['size']}) - RAID: {vdisk['raidLevel']}")

        print(f"\n=== Alerts ({len(status['alerts'])}) ===")
        for alert in status["alerts"][:5]:  # Show first 5 alerts
            print(f"- [{alert['severity'].upper()}] {alert['message']} - {alert['timestamp']}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()