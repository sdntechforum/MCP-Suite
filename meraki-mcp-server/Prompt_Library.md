# Meraki MCP Server — Prompt Library

## Tool Domain Map

The Meraki MCP server exposes tools across the full Meraki Dashboard API surface, covering cloud-managed wireless, switching, security, and SD-WAN.
| Domain | Core Tools |
|---|---|
| **Organizations** | `get_organizations`, `get_organization_details`, `get_organization_inventory` |
| **Networks** | `get_organization_networks`, `get_network_details`, `get_network_devices` |
| **Devices** | `get_devices`, `get_device_details`, `get_device_status`, `reboot_device` |
| **Wireless (MR)** | `get_network_wireless_ssids`, `get_network_wireless_clients`, `get_wireless_rf_profiles` |
| **Switching (MS)** | `get_network_switch_ports`, `get_switch_port_status`, `get_network_switch_stacks` |
| **Security Appliance (MX)** | `get_network_appliance_firewall_rules`, `get_uplink_status`, `get_vpn_peers` |
| **Clients** | `get_network_clients`, `get_client_details`, `get_client_policy` |
| **Events & Alerts** | `get_network_events`, `get_organization_alerts`, `get_alert_settings` |
| **SD-WAN / Uplinks** | `get_organization_uplinks_statuses`, `get_appliance_uplink_settings` |
| **Camera (MV)** | `get_network_camera_snapshots`, `get_camera_analytics` |
| **Insight** | `get_network_insight_applications`, `get_monitored_media_servers` |

***

## 📦 Category 1 — Organization & Network Inventory

For **MSP Admins, Network Architects, and IT Directors** who manage multi-org or multi-site Meraki deployments.

1. **"List all organizations accessible via the Meraki API key and show me the total number of networks, devices, and licensed seats for each."**

2. **"Show me all networks across the organization, grouped by network type (wireless, switching, appliance, combined) and by geographic tag."**

3. **"Pull the full organization device inventory and summarize by device model family — how many MR APs, MS switches, MX appliances, and MV cameras are deployed?"**

4. **"Which networks in the organization have devices that are currently offline or in a degraded state? Show network name, offline device count, and last reported time."**

5. **"List all networks that were created in the last 30 days — include the network name, type, tags, and the admin who created it."**

***

## 📡 Category 2 — Wireless (MR) Management

For **Wireless Engineers, Help Desk, and IT Operations** managing Meraki wireless deployments.

6. **"Show all SSIDs configured across the organization. Flag any that are enabled but have no clients connected in the last 7 days — these may be candidates for cleanup."**

7. **"How many wireless clients are currently associated to the `HQ-Corporate` network? Break them down by SSID, band (2.4GHz vs 5GHz vs 6GHz), and connection status."**

8. **"Which APs in the `Branch-Austin` network have the highest client load right now? List the top 5 by connected client count and their current channel utilization."**

9. **"Show me the RF profile applied to each AP in the `Campus-Main` network. Are there any APs not assigned to a named RF profile (using defaults)?"**

10. **"A user reports intermittent Wi-Fi drops in Building C. Pull the wireless event log for that network filtered to authentication failures, deauth events, and disassociations in the last 4 hours."**

11. **"List all APs that have been offline for more than 15 minutes across the entire organization, along with their network, model, serial, and last-seen timestamp."**

***

## 🔌 Category 3 — Switching (MS) Operations

For **Network Engineers and NOC Teams** managing Meraki switching.

12. **"Show the port status for all ports on switch `Q2HP-XXXX-XXXX` in the `HQ-Switching` network. Flag any ports that are enabled but have been inactive (no traffic) for more than 48 hours."**

13. **"Are there any switch ports across the organization that are currently in an err-disabled state? List the switch, port number, VLAN, and the reason if available."**

14. **"Show me the STP topology for the `Campus-Core` network. Which switch is the current root bridge and are there any topology change notifications (TCNs) recorded in the last 24 hours?"**

15. **"List all switch stacks in the organization — show stack name, member count, model mix, and whether any member is reporting a hardware fault."**

16. **"Which switch ports are configured as trunk ports in the `Distribution` network? Show allowed VLANs, native VLAN, and current link speed."**

***

## 🔒 Category 4 — Security Appliance (MX) & Firewall

For **Security Engineers, Compliance Teams, and Network Architects** managing Meraki MX appliances.

17. **"Show the current outbound firewall rules for the `Branch-Denver` network. Flag any rules with a destination of 'any' and action 'allow' that have not been reviewed in the past 90 days."**

18. **"What is the current WAN uplink status for all MX appliances across the organization? Show primary and secondary WAN states, ISP name if tagged, and current throughput."**

19. **"List all site-to-site VPN peers in the organization. Which tunnels are currently down or in a non-connected state? Show last connected time and the impacted networks."**

20. **"Show me the content filtering and intrusion prevention settings for the `Retail-POS` network. Are IPS signatures up to date and is HTTPS inspection enabled?"**

21. **"Has any MX appliance in the organization triggered an IDS/IPS alert in the last 24 hours? Show the source IP, destination, rule matched, and affected network."**

***

## 👤 Category 5 — Client Visibility & Troubleshooting

For **Help Desk, L2 Support, and Wireless Admins** resolving end-user connectivity issues.

22. **"A user with MAC address `a4:c3:f0:9b:12:44` says they cannot get on the network. Pull their client detail from Meraki — which network, AP or switch port, SSID, VLAN, and IP address are they associated with? Show their last 10 connectivity events."**

23. **"Show me all clients on the `Guest-WiFi` SSID that have been connected for more than 8 hours continuously. These may be policy violations that need to be reviewed."**

24. **"List the top 10 clients by bandwidth consumption in the `HQ-Corporate` network over the last 24 hours. Show MAC, description, SSID, and total up/down bytes."**

25. **"What client policy (group policy, bandwidth limits, splash auth) is applied to the device with MAC `b8:27:eb:44:11:cc` in the `Branch-Miami` network?"**

***

## 🌐 Category 6 — SD-WAN & Uplink Intelligence

For **WAN Engineers and IT Managers** overseeing Meraki SD-WAN deployments.

26. **"Show the uplink health status for all MX appliances organization-wide. Which sites have experienced a WAN failover in the last 7 days and how long was the primary link down?"**

27. **"What is the current traffic split across WAN uplinks for the `HQ` network? Show how much traffic is going over each link and whether traffic shaping policies are actively redirecting any application flows."**

28. **"List all networks using cellular (LTE/5G) as a backup uplink. Have any of them fallen back to cellular in the last 30 days and what was the estimated downtime on the primary link?"**

***

## 📷 Category 7 — MV Smart Camera & Analytics

For **Physical Security Teams and Facilities Managers**.

29. **"List all MV cameras in the organization. Which cameras are currently offline and when was their last snapshot successfully captured?"**

30. **"Pull the motion analytics summary for the `Lobby-Entrance` camera over the last business day — show peak occupancy periods and average dwell times."**

***

## 🏭 Vertical-Specific Prompt Packs

### Retail
- *"Show me all Meraki networks tagged as 'retail-store'. Which stores have an MX appliance with only one WAN uplink active — these are single points of failure for POS systems."*

### Healthcare
- *"List all client devices on the `Medical-Devices` VLAN across hospital networks. Flag any that have not been seen in more than 72 hours — these may be offline biomedical devices needing attention."*

### Education
- *"How many student-owned devices (identified by OUI or policy group) are connected to the campus Wi-Fi right now? Show distribution by building and SSID."*

### MSP / Multi-Tenant
- *"Across all managed customer organizations, which ones have Meraki licensing expiring within the next 90 days? Show org name, license tier, seat count, and expiry date."*

### Manufacturing / OT
- *"List all Meraki networks tagged `OT-zone` or `industrial`. Confirm that IoT traffic isolation group policies are applied to all clients in those networks and report any exceptions."*

***

## 🔁 Cross-Ecosystem / Multi-MCP Prompts

These prompts **chain the Meraki MCP with other servers** in the SDN Tech Forum MCP Suite  for compound, multi-domain investigations. [github](https://github.com/pamosima/network-mcp-docker-suite/blob/main/meraki-mcp-server/README.md)

***

### 🔗 Meraki + Catalyst Center — Unified Campus Visibility

31. **"A client device is roaming between Meraki MR APs at the branch and Catalyst Center-managed APs at HQ. Pull the roaming event history from both MCP servers for MAC `c4:b3:01:aa:55:12` and construct a unified timeline of their connectivity across both domains."**

32. **"The campus has a mix of Meraki MS switches in the access layer and Catalyst Center-managed Catalyst 9000s in the distribution/core. Show me all uplink ports connecting the two domains — confirm link state and speed from both MCP servers."**

***

### 🔗 Meraki + Splunk — Security & Event Correlation

33. **"Meraki IDS has flagged an intrusion attempt from source IP `185.220.101.47` on the `Branch-NYC` network. Query Splunk to determine if this same IP has appeared in firewall deny logs, endpoint AV alerts, or proxy logs across any other site in the last 48 hours."**

34. **"Pull all Meraki client association events for the last 12 hours and cross-reference with Splunk authentication logs. Identify any device that successfully joined the Wi-Fi but then failed Active Directory login — a potential indicator of a rogue device."**

***

### 🔗 Meraki + ThousandEyes — Branch WAN & Application Performance

35. **"ThousandEyes is showing increased packet loss from the `Branch-Seattle` enterprise agent to Microsoft 365. Check the Meraki MX uplink status at that branch — is the primary WAN link healthy, and has there been any uplink failover or traffic shaping event in the last 2 hours?"**

36. **"ThousandEyes reports high latency to a SaaS application from 4 branches simultaneously. Pull Meraki uplink stats for all 4 MX appliances — are they all on the same ISP or using similar WAN paths? Identify if this is an ISP-wide event."**

***

### 🔗 Meraki + Catalyst Center + ThousandEyes — Full-Stack Triage

37. **"We have a reported outage affecting video conferencing quality for remote workers across 3 branch sites. Use all three MCP servers to build a complete root cause timeline: ThousandEyes for application path quality, Meraki for branch WAN/Wi-Fi health, and Catalyst Center for core/distribution device health."**

***

## Prompt Engineering Tips for Meraki MCP

| Principle | Guidance |
|---|---|
| **Scope by org or network** | Always specify `organization`, `network name`, or `tag` to avoid returning data for the entire fleet unnecessarily |
| **Use serial/MAC as anchors** | Client and device prompts are most precise when anchored to MAC address or Meraki serial number |
| **Time-bound event queries** | Meraki event logs are high-volume — always add a time window (`last 2 hours`, `last 7 days`) |
| **Separate read vs. write** | For prompts that trigger reboots or config changes, add **"confirm the target list before executing"** |
| **Tag leveraging** | Meraki's tagging system is powerful — prompt by tag (`retail-store`, `OT-zone`) to target logical groups across hundreds of networks |
| **MSP multi-org pattern** | For MSP use cases, always start with `get_organizations` to scope which org before drilling into networks  [community.meraki](https://community.meraki.com/t5/Developers-APIs/Meraki-MCP-Model-Context-Protocol/m-p/280855) |

***

This Meraki prompt library covers the full cloud-managed network stack from wireless and switching through security and SD-WAN. Combined with the CATC prompt library, these two servers already enable powerful cross-domain queries spanning cloud-managed branches (Meraki) and enterprise campus/DC (Catalyst Center) — a combination that covers the majority of Cisco enterprise deployments. [developer.cisco](https://developer.cisco.com/meraki/api-v1/)
