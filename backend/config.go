package main

import (
	"os"
	"strconv"
)

type Config struct {
	IDRACHost     string
	IDRACUsername string
	IDRACPassword string
	PollInterval  int
	ServerPort    string
}

func LoadConfig() Config {
	config := Config{
		IDRACHost:     getEnv("IDRAC_HOST", "10.88.51.66"),
		IDRACUsername: getEnv("IDRAC_USERNAME", "root"),
		IDRACPassword: getEnv("IDRAC_PASSWORD", "uh-WYoKv_p8zeM!t"),
		PollInterval:  getEnvAsInt("POLL_INTERVAL", 300000), // 5 minutes in milliseconds
		ServerPort:    getEnv("SERVER_PORT", "8080"),
	}

	return config
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
