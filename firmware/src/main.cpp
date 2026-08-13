#include <Arduino.h>

enum class TrackerState {
  BOOT,
  MODEM_INIT,
  SIM_CHECK,
  NETWORK_REGISTRATION,
  DATA_SESSION,
  GNSS,
  POSITION,
  TRANSMISSION,
  SLEEP_WAIT,
  RECOVERY,
  FAILED
};

struct TrackerStats {
  unsigned long retries = 0;
  unsigned long watchdogKicks = 0;
  unsigned long modemResets = 0;
  unsigned long transmissions = 0;
};

TrackerState state = TrackerState::BOOT;
TrackerStats stats;

const char* stateName(TrackerState value) {
  switch (value) {
    case TrackerState::BOOT: return "BOOT";
    case TrackerState::MODEM_INIT: return "MODEM_INIT";
    case TrackerState::SIM_CHECK: return "SIM_CHECK";
    case TrackerState::NETWORK_REGISTRATION: return "NETWORK_REGISTRATION";
    case TrackerState::DATA_SESSION: return "DATA_SESSION";
    case TrackerState::GNSS: return "GNSS";
    case TrackerState::POSITION: return "POSITION";
    case TrackerState::TRANSMISSION: return "TRANSMISSION";
    case TrackerState::SLEEP_WAIT: return "SLEEP_WAIT";
    case TrackerState::RECOVERY: return "RECOVERY";
    case TrackerState::FAILED: return "FAILED";
  }
  return "UNKNOWN";
}

bool sendAtCommand(const char* command, unsigned long timeoutMs) {
  Serial.print("AT>");
  Serial.println(command);
  unsigned long started = millis();
  while (millis() - started < timeoutMs) {
    // Independent public placeholder. Replace with modem serial parsing for hardware validation.
    return true;
  }
  return false;
}

void kickWatchdog() {
  stats.watchdogKicks++;
}

void resetModem() {
  stats.modemResets++;
  Serial.println("MODEM_RESET");
}

TrackerState recoverFromFailure() {
  kickWatchdog();
  resetModem();
  stats.retries++;
  if (stats.retries > 3) {
    return TrackerState::FAILED;
  }
  return TrackerState::MODEM_INIT;
}

TrackerState step(TrackerState current) {
  Serial.print("STATE=");
  Serial.println(stateName(current));
  switch (current) {
    case TrackerState::BOOT:
      return TrackerState::MODEM_INIT;
    case TrackerState::MODEM_INIT:
      return sendAtCommand("AT", 5000) ? TrackerState::SIM_CHECK : recoverFromFailure();
    case TrackerState::SIM_CHECK:
      return sendAtCommand("AT+CPIN?", 5000) ? TrackerState::NETWORK_REGISTRATION : TrackerState::SIM_CHECK;
    case TrackerState::NETWORK_REGISTRATION:
      return sendAtCommand("AT+CREG?", 5000) ? TrackerState::DATA_SESSION : recoverFromFailure();
    case TrackerState::DATA_SESSION:
      return sendAtCommand("AT+CGATT?", 5000) ? TrackerState::GNSS : recoverFromFailure();
    case TrackerState::GNSS:
      return sendAtCommand("AT+QGPS=1", 5000) ? TrackerState::POSITION : TrackerState::GNSS;
    case TrackerState::POSITION:
      return sendAtCommand("AT+QGPSLOC?", 30000) ? TrackerState::TRANSMISSION : TrackerState::GNSS;
    case TrackerState::TRANSMISSION:
      stats.transmissions++;
      return TrackerState::SLEEP_WAIT;
    case TrackerState::SLEEP_WAIT:
      delay(1000);
      return TrackerState::MODEM_INIT;
    case TrackerState::RECOVERY:
      return recoverFromFailure();
    case TrackerState::FAILED:
      return TrackerState::FAILED;
  }
  return TrackerState::FAILED;
}

void setup() {
  Serial.begin(115200);
  Serial.println("CELLULAR_GNSS_TRACKER_LAB_BOOT");
}

void loop() {
  state = step(state);
  if (state == TrackerState::FAILED) {
    Serial.println("TRACKER_FAILED");
    delay(5000);
  }
}

