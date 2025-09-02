package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

// IDRAC8 API client configuration
type IDRACConfig struct {
	Host     string `json:"host"`
	Username string `json:"username"`
	Password string `json:"password"`
}

// Data structures matching the frontend types
type PhysicalDisk struct {
	ID                string    `json:"id"`
	Name              string    `json:"name"`
	Model             string    `json:"model"`
	SerialNumber      string    `json:"serialNumber"`
	Capacity          string    `json:"capacity"`
	Status            string    `json:"status"`
	Temperature       int       `json:"temperature"`
	SmartStatus       string    `json:"smartStatus"`
	BadSectors        int       `json:"badSectors"`
	PowerOnHours      int       `json:"powerOnHours"`
	PredictiveFailure bool      `json:"predictiveFailure"`
	LastChecked       time.Time `json:"lastChecked"`
}

type VirtualDisk struct {
	ID              string    `json:"id"`
	Name            string    `json:"name"`
	RaidLevel       string    `json:"raidLevel"`
	Status          string    `json:"status"`
	Capacity        string    `json:"capacity"`
	UsedSpace       string    `json:"usedSpace"`
	PhysicalDisks   []string  `json:"physicalDisks"`
	RebuildProgress *int      `json:"rebuildProgress,omitempty"`
	LastChecked     time.Time `json:"lastChecked"`
}

type RaidController struct {
	ID            string    `json:"id"`
	Name          string    `json:"name"`
	Model         string    `json:"model"`
	Status        string    `json:"status"`
	BatteryStatus string    `json:"batteryStatus"`
	CacheSize     string    `json:"cacheSize"`
	Temperature   int       `json:"temperature"`
	LastChecked   time.Time `json:"lastChecked"`
}

type SystemAlert struct {
	ID           string    `json:"id"`
	Severity     string    `json:"severity"`
	Title        string    `json:"title"`
	Message      string    `json:"message"`
	Component    string    `json:"component"`
	Timestamp    time.Time `json:"timestamp"`
	Acknowledged bool      `json:"acknowledged"`
}

type ServerStatus struct {
	ServerName       string            `json:"serverName"`
	IPAddress        string            `json:"ipAddress"`
	LastUpdate       time.Time         `json:"lastUpdate"`
	ConnectionStatus string            `json:"connectionStatus"`
	PhysicalDisks    []PhysicalDisk    `json:"physicalDisks"`
	VirtualDisks     []VirtualDisk     `json:"virtualDisks"`
	RaidControllers  []RaidController  `json:"raidControllers"`
	Alerts           []SystemAlert     `json:"alerts"`
}

// IDRAC API client
type IDRACClient struct {
	config     IDRACConfig
	httpClient *http.Client
	token      string
}

func NewIDRACClient(config IDRACConfig) *IDRACClient {
	// Create HTTP client with TLS configuration for IDRAC
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	httpClient := &http.Client{
		Transport: tr,
		Timeout:   30 * time.Second,
	}

	return &IDRACClient{
		config:     config,
		httpClient: httpClient,
	}
}

// Authenticate with IDRAC and get session token
func (c *IDRACClient) authenticate() error {
	authURL := fmt.Sprintf("https://%s/redfish/v1/SessionService/Sessions", c.config.Host)
	
	authData := map[string]string{
		"UserName": c.config.Username,
		"Password": c.config.Password,
	}
	
	authJSON, _ := json.Marshal(authData)
	
	req, err := http.NewRequest("POST", authURL, nil)
	if err != nil {
		return err
	}
	
	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(c.config.Username, c.config.Password)
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode == 200 || resp.StatusCode == 201 {
		c.token = resp.Header.Get("X-Auth-Token")
		return nil
	}
	
	return fmt.Errorf("authentication failed with status: %d", resp.StatusCode)
}

// Get physical disk information from IDRAC
func (c *IDRACClient) getPhysicalDisks() ([]PhysicalDisk, error) {
	if c.token == "" {
		if err := c.authenticate(); err != nil {
			return nil, err
		}
	}

	// IDRAC8 Redfish API endpoint for physical disks
	url := fmt.Sprintf("https://%s/redfish/v1/Systems/System.Embedded.1/Storage", c.config.Host)
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("X-Auth-Token", c.token)
	req.Header.Set("Accept", "application/json")
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	
	// Parse the response and convert to our PhysicalDisk structure
	// This is a simplified version - you'll need to adapt based on actual IDRAC8 API response
	var disks []PhysicalDisk
	
	if members, ok := result["Members"].([]interface{}); ok {
		for i, member := range members {
			if memberMap, ok := member.(map[string]interface{}); ok {
				disk := PhysicalDisk{
					ID:                fmt.Sprintf("disk-%d", i),
					Name:              getStringValue(memberMap, "Name"),
					Model:             getStringValue(memberMap, "Model"),
					SerialNumber:      getStringValue(memberMap, "SerialNumber"),
					Capacity:          getStringValue(memberMap, "CapacityBytes"),
					Status:            mapStatus(getStringValue(memberMap, "Status.Health")),
					Temperature:       getIntValue(memberMap, "Temperature"),
					SmartStatus:       mapSmartStatus(getStringValue(memberMap, "Status.Health")),
					BadSectors:        0, // Would need additional API call
					PowerOnHours:      0, // Would need additional API call
					PredictiveFailure: false,
					LastChecked:       time.Now(),
				}
				disks = append(disks, disk)
			}
		}
	}
	
	return disks, nil
}

// Get virtual disk information from IDRAC
func (c *IDRACClient) getVirtualDisks() ([]VirtualDisk, error) {
	if c.token == "" {
		if err := c.authenticate(); err != nil {
			return nil, err
		}
	}

	url := fmt.Sprintf("https://%s/redfish/v1/Systems/System.Embedded.1/Storage/Volumes", c.config.Host)
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("X-Auth-Token", c.token)
	req.Header.Set("Accept", "application/json")
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	
	var virtualDisks []VirtualDisk
	
	if members, ok := result["Members"].([]interface{}); ok {
		for i, member := range members {
			if memberMap, ok := member.(map[string]interface{}); ok {
				vdisk := VirtualDisk{
					ID:            fmt.Sprintf("vdisk-%d", i),
					Name:          getStringValue(memberMap, "Name"),
					RaidLevel:     getStringValue(memberMap, "RAIDType"),
					Status:        mapVirtualDiskStatus(getStringValue(memberMap, "Status.Health")),
					Capacity:      getStringValue(memberMap, "CapacityBytes"),
					UsedSpace:     "0", // Would need calculation
					PhysicalDisks: []string{}, // Would need additional API call
					LastChecked:   time.Now(),
				}
				virtualDisks = append(virtualDisks, vdisk)
			}
		}
	}
	
	return virtualDisks, nil
}

// Get RAID controller information
func (c *IDRACClient) getRaidControllers() ([]RaidController, error) {
	if c.token == "" {
		if err := c.authenticate(); err != nil {
			return nil, err
		}
	}

	url := fmt.Sprintf("https://%s/redfish/v1/Systems/System.Embedded.1/Storage", c.config.Host)
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("X-Auth-Token", c.token)
	req.Header.Set("Accept", "application/json")
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	
	var controllers []RaidController
	
	// Parse RAID controller information from the storage response
	if members, ok := result["Members"].([]interface{}); ok {
		for i, member := range members {
			if memberMap, ok := member.(map[string]interface{}); ok {
				controller := RaidController{
					ID:            fmt.Sprintf("controller-%d", i),
					Name:          getStringValue(memberMap, "Name"),
					Model:         getStringValue(memberMap, "Model"),
					Status:        mapStatus(getStringValue(memberMap, "Status.Health")),
					BatteryStatus: "healthy", // Would need separate API call
					CacheSize:     "1GB",     // Would need separate API call
					Temperature:   35,        // Would need separate API call
					LastChecked:   time.Now(),
				}
				controllers = append(controllers, controller)
			}
		}
	}
	
	return controllers, nil
}

// Get system alerts
func (c *IDRACClient) getSystemAlerts() ([]SystemAlert, error) {
	var alerts []SystemAlert
	
	// For now, generate alerts based on disk status
	// In a real implementation, you'd query IDRAC event logs
	
	return alerts, nil
}

// Utility functions
func getStringValue(data map[string]interface{}, key string) string {
	if val, ok := data[key]; ok {
		if str, ok := val.(string); ok {
			return str
		}
	}
	return ""
}

func getIntValue(data map[string]interface{}, key string) int {
	if val, ok := data[key]; ok {
		if num, ok := val.(float64); ok {
			return int(num)
		}
	}
	return 0
}

func mapStatus(idracStatus string) string {
	switch idracStatus {
	case "OK":
		return "healthy"
	case "Warning":
		return "warning"
	case "Critical":
		return "critical"
	default:
		return "unknown"
	}
}

func mapSmartStatus(idracStatus string) string {
	switch idracStatus {
	case "OK":
		return "passed"
	default:
		return "failed"
	}
}

func mapVirtualDiskStatus(idracStatus string) string {
	switch idracStatus {
	case "OK":
		return "optimal"
	case "Warning":
		return "degraded"
	case "Critical":
		return "failed"
	default:
		return "unknown"
	}
}

// HTTP handlers
func getServerStatus(c *gin.Context) {
	config := LoadConfig()
	
	idracConfig := IDRACConfig{
		Host:     config.IDRACHost,
		Username: config.IDRACUsername,
		Password: config.IDRACPassword,
	}
	
	client := NewIDRACClient(idracConfig)
	
	// Get all hardware information
	physicalDisks, err := client.getPhysicalDisks()
	if err != nil {
		log.Printf("Error getting physical disks: %v", err)
		physicalDisks = []PhysicalDisk{} // Return empty array on error
	}
	
	virtualDisks, err := client.getVirtualDisks()
	if err != nil {
		log.Printf("Error getting virtual disks: %v", err)
		virtualDisks = []VirtualDisk{}
	}
	
	raidControllers, err := client.getRaidControllers()
	if err != nil {
		log.Printf("Error getting RAID controllers: %v", err)
		raidControllers = []RaidController{}
	}
	
	alerts, err := client.getSystemAlerts()
	if err != nil {
		log.Printf("Error getting alerts: %v", err)
		alerts = []SystemAlert{}
	}
	
	status := ServerStatus{
		ServerName:       "Dell PowerEdge Server",
		IPAddress:        idracConfig.Host,
		LastUpdate:       time.Now(),
		ConnectionStatus: "connected",
		PhysicalDisks:    physicalDisks,
		VirtualDisks:     virtualDisks,
		RaidControllers:  raidControllers,
		Alerts:           alerts,
	}
	
	c.JSON(http.StatusOK, status)
}

func main() {
	config := LoadConfig()
	
	// Create Gin router
	r := gin.Default()
	
	// Configure CORS
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:5173", "http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		AllowCredentials: true,
	}))
	
	// API routes
	api := r.Group("/api/v1")
	{
		api.GET("/server/status", getServerStatus)
	}
	
	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})
	
	log.Printf("Starting IDRAC8 Monitor API server on :%s", config.ServerPort)
	log.Printf("Monitoring IDRAC at: %s", config.IDRACHost)
	log.Fatal(r.Run(":" + config.ServerPort))
}