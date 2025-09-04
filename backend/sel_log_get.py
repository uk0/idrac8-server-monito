import os
import sys
import ssl
import time
import warnings
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3 needed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

class WeakDHAdapter(requests.adapters.HTTPAdapter):
    """Adapter to allow weak DH keys for older iDRAC systems."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
        ctx.options |= getattr(ssl, 'OP_LEGACY_SERVER_CONNECT', 0x4)
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

class IDRACSelFetcher:
    """
    Simple fetcher for System Event Log (SEL) entries from iDRAC 13G.
    Tries Redfish API SEL endpoint first, then falls back to legacy XML.
    """
    def __init__(self, host: str, user: str, pwd: str):
        self.base = f"https://{host}"
        self.user = user
        self.pwd = pwd
        # session for Redfish
        self.rf = requests.Session()
        self.rf.verify = False
        self.rf.auth = (user, pwd)
        adapter = WeakDHAdapter()
        self.rf.mount("https://", adapter)
        # session for legacy endpoint
        self.legacy = requests.Session()
        self.legacy.verify = False
        self.legacy.auth = (user, pwd)
        self.legacy.mount("https://", adapter)

    def fetch_sel_redfish(self):
        """Attempt to fetch SEL via Redfish."""
        print("use fetch_sel_redfish")
        endpoints = [
            "/redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Sel/Entries",
            "/redfish/v1/Managers/iDRAC.Embedded.1/Logs/Sel",
            "/redfish/v1/Systems/System.Embedded.1/LogServices/SEL/Entries",
            "/redfish/v1/Managers/1/LogServices/Sel/Entries",
        ]
        for ep in endpoints:
            url = self.base + ep
            print(f"use url :{url}")
            try:
                resp = self.rf.get(url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    members = data.get("Members", [])
                    if members:
                        return members
                # if empty or 404, continue
            except Exception:
                pass
        return []

    def fetch_sel_legacy(self):
        print("use fetch_sel_legacy")
        """Fetch SEL via the legacy XML endpoint."""
        login_url = self.base + "/data/login"
        # ignore login XML, just establish cookies
        self.legacy.post(login_url,
                         data=f"user={self.user}&password={self.pwd}",
                         headers={'Content-Type':'application/x-www-form-urlencoded'},
                         timeout=10)
        url = self.base + "/data?get=eventLogEntries"
        try:
            resp = self.legacy.post(url,
                                    headers={'Accept':'application/xml'},
                                    data="", timeout=15)
            if resp.status_code != 200:
                return []
            root = ET.fromstring(resp.text)
            entries = []
            for e in root.findall(".//eventLogEntry"):
                ts = e.findtext("dateTime") or datetime.now().isoformat()
                msg = e.findtext("description") or "<no desc>"
                sev = (e.findtext("severity") or "Informational").capitalize()
                entries.append({
                    "Id": len(entries)+1,
                    "Created": ts,
                    "Message": msg,
                    "Severity": sev,
                })
            return entries
        except Exception:
            return []

    def get_sel_entries(self):
        """Return combined SEL entries (Redfish first, legacy fallback)."""
        entries = self.fetch_sel_redfish()
        if entries:
            return entries
        return self.fetch_sel_legacy()

def main():
    # Read from environment or use defaults
    host = os.getenv("IDRAC_IP", "10.88.51.66")
    user = os.getenv("IDRAC_USER", "root")
    pwd  = os.getenv("IDRAC_PASS", "uh-WYoKv_p8zeM!t")

    fetcher = IDRACSelFetcher(host, user, pwd)
    print(f"Connecting to iDRAC at {host} for SEL logs...")
    logs = fetcher.get_sel_entries()

    if not logs:
        print("❌ No SEL entries found by either Redfish or legacy API.")
        sys.exit(1)

    print(f"✅ Retrieved {len(logs)} SEL entries:")
    for entry in logs:
        ts = entry.get("Created", "")
        sev = entry.get("Severity", "")
        msg = entry.get("Message", "")
        Id = entry.get("Id", -0)
        print(f"- [{ts}] {sev}: {msg}")
        severity = str(entry.get("Severity", "")).lower()
        entry_type = str(entry.get("EntryType", "")).lower()

        # Include critical, warning, and some informational alerts
        if severity in ["critical", "warning"]:
            alert = {
                "id": Id,
                "message": entry.get("Message", "Unknown alert"),
                "severity": severity if severity else "information",
                "timestamp": entry.get("Created", datetime.now().isoformat()),
                "messageId": entry.get("MessageId", ""),
                "entryType": entry.get("EntryType", "Event"),
                "sensorType": entry.get("SensorType", ""),
                "sensorNumber": entry.get("SensorNumber", 0),
                "acknowledged": False
            }
            print(alert)

if __name__ == "__main__":
    os.environ.setdefault("IDRAC_IP","10.88.51.66")
    os.environ.setdefault("IDRAC_USER","root")
    os.environ.setdefault("IDRAC_PASS","")
    main()