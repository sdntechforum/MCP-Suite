
# Catalyst Center MCP Server — Prompt Library

## Tool Domain Map

Before the prompts, here is how Catalyst Center MCP tools map to functional domains: [developer.cisco](https://developer.cisco.com/docs/dna-center/)

| Domain | Core Capabilities |
|---|---|
| **Device Inventory** | List devices, get device detail, reachability, platform info |
| **Network Topology** | Physical/logical topology, site hierarchy, links |
| **Client Assurance** | Client health, onboarding, wireless/wired detail |
| **Network Health** | Overall health score, site-level health, issue counts |
| **Issues & Events** | Active issues, event timeline, P1/P2 issues |
| **Command Runner** | Run CLI commands on devices remotely |
| **Path Trace** | End-to-end path analysis between two endpoints |
| **Configuration** | Templates, compliance, config archive |
| **SWIM** | Software image management, upgrade readiness |
| **Site Management** | Floor maps, building hierarchy, geo-location |

***

## 📦 Category 1 — Device Inventory & Discovery

These prompts target **NetOps, NOC Engineers, and Network Architects** who need rapid visibility into the managed device estate.

1. **"List all network devices currently managed by Catalyst Center and group them by device family (switch, router, wireless controller, AP)."**

2. **"Find all devices in the inventory that are currently unreachable and show me their site location, last contact time, and management IP."**

3. **"What is the full hardware and software inventory for the device with IP address `10.10.20.51`? Include platform, IOS-XE version, serial number, and uptime."**

4. **"Show me all Catalyst 9300 series switches running IOS-XE versions older than 17.9 that may be candidates for a software upgrade."**

5. **"How many devices does Catalyst Center currently manage, broken down by site and device role?"**

***

## 🩺 Category 2 — Network Health & Assurance

Targeted at **NOC teams, SREs, and IT Operations** for real-time visibility and SLA monitoring.

6. **"What is the current overall network health score? Drill down into the site with the lowest score and list the contributing issues."**

7. **"Show me all P1 and P2 issues currently open in Catalyst Center, sorted by impact and time of detection."**

8. **"What is the wireless client health score for the 'HQ-Building-3' site right now? Show the number of onboarded clients vs. those experiencing issues."**

9. **"Have there been any repeated hardware alarms or interface flap events on core switches in the last 24 hours?"**

10. **"Generate a health summary for all sites in the 'APAC' region — include network health, client health, and application health scores."**

***

## 👤 Category 3 — Client Troubleshooting

Designed for **Help Desk, L2 Support Engineers, and Wireless Admins** who handle end-user connectivity issues.

11. **"A user at extension 4521 reports they cannot connect to the corporate Wi-Fi. Their MAC address is `a4:c3:f0:12:ab:cd`. What does Catalyst Center show for their last onboarding attempt — which AP, SSID, auth method, and failure reason?"**

12. **"List all wireless clients currently associated to the AP named `AP-FLOOR4-NW` and show their RSSI, SNR, and data rates."**

13. **"Show me all clients that failed 802.1X authentication in the last 2 hours, including their username, MAC, and the error code returned."**

14. **"How many clients are connected to the 'Guest-WiFi' SSID across all sites right now? Flag any with poor health scores."**

15. **"A VIP user with username `jsmith` is reporting slow application performance. Pull their complete client 360 view from Catalyst Center including roaming history, signal quality, and latency trends."**

***

## 🗺️ Category 4 — Topology & Path Analysis

For **Network Engineers, Architects, and Incident Responders** performing impact analysis and root cause investigation.

16. **"Run a path trace between host `10.10.30.15` and server `172.16.50.10`. Show the full hop-by-hop path, interface names, and any ACLs or QoS policies applied along the path."**

17. **"Show the physical topology for the 'Data Center Core' layer and highlight any links that are currently down or degraded."**

18. **"Which network devices are directly connected to the distribution switch `DIST-SW-01`? List their interfaces, link speeds, and CDP/LLDP neighbor details."**

19. **"Is there a redundant path between building A and building B? Show the active and standby links and the current STP state."**

***

## ⚙️ Category 5 — Configuration & Compliance

For **Change Management, Compliance Officers, and Senior Network Engineers**.

20. **"Run a compliance check across all access layer switches and list any devices that have drifted from the golden configuration template."**

21. **"Show me the configuration archive history for `CORE-SW-02`. What changes were made in the last 7 days, and by which user?"**

22. **"Which devices are currently marked as non-compliant in Catalyst Center and what specific configuration lines are causing the violation?"**

23. **"Deploy the 'NTP-Standard-v2' configuration template to all switches in the 'Branch-Chicago' site. Confirm the target devices before executing."**

***

## 📡 Category 6 — Software Image Management (SWIM)

For **Change Advisory Boards and Network Operations** managing OS lifecycle.

24. **"List all devices that are NOT running the golden software image designated in Catalyst Center. Group by platform and site."**

25. **"What is the upgrade readiness status for the 'Branch-Dallas' site for the planned IOS-XE 17.12 upgrade? Are there any blockers such as insufficient flash or incompatible modules?"**

***

## 🔁 Category 7 — Command Runner (Remote Execution)

For **Troubleshooting Engineers and Incident Response Teams**.

26. **"Run `show ip bgp summary` on all routers tagged with the role 'WAN Edge' and return the neighbor states. Flag any neighbors that are not in Established state."**

27. **"Execute `show environment all` on `CORE-SW-01` and `CORE-SW-02` and report any power supply, fan, or temperature warnings."**

***

## 🌐 Category 8 — Cross-Ecosystem / Multi-MCP Prompts

These prompts **span multiple MCP servers in the SDN Tech Forum suite** — combining Catalyst Center with Splunk, NX-OS, ThousandEyes, and others  — representing the highest-value AI-assisted workflows. [reddit](https://www.reddit.com/r/sdntechforum/)

***

### 🔗 CATC + ThousandEyes — End-to-End Visibility

28. **"ThousandEyes is reporting elevated latency on the path to `salesforce.com` from the Chicago branch. Cross-reference with Catalyst Center — are there any active interface errors, high CPU, or BGP issues on the WAN edge router at that site right now?"**

29. **"A ThousandEyes browser test to our ERP application is failing from 3 enterprise agents. Pull the path trace from Catalyst Center between those branch sites and the data center to identify where the packet loss is occurring."**

***

### 🔗 CATC + Splunk — Correlated Security & Operations

30. **"Splunk has flagged unusual traffic volume from MAC address `b8:27:eb:4f:2a:11`. Query Catalyst Center to identify which user, AP, and physical floor this device is currently associated to, and whether it has roamed in the last hour."**

31. **"Cross-correlate Catalyst Center P1 network events from the last 6 hours with Splunk syslogs from the same devices. Identify if any syslog errors preceded the Catalyst Center alert — build a root-cause timeline."**

***

### 🔗 CATC + NX-OS — Fabric & Data Center Operations

32. **"Catalyst Center shows a link-down event on `DC-NEXUS-LEAF-03`. Run `show interface status` and `show vpc` on that device via the NX-OS MCP server and confirm if a vPC peer-link or member port is affected."**

33. **"Compare the BGP routing table on `DC-NEXUS-SPINE-01` via NX-OS MCP with what Catalyst Center shows for the same device's health and connectivity. Are there route discrepancies that Catalyst Center's assurance engine has not yet flagged?"**

***

### 🔗 CATC + ISE — Policy & Identity Correlation

34. **"Catalyst Center is reporting a large number of 802.1X authentication failures at the Austin site. Query ISE to pull the RADIUS live logs for those failures — correlate MAC address, username, failure reason, and policy rule matched."**

35. **"A device has been quarantined by ISE's Threat Centric NAC. Find it in Catalyst Center's inventory to determine its physical switch port, floor location, and whether it is a managed or unmanaged endpoint."**

***

## 🏭 Vertical-Specific Prompt Packs

### Healthcare
- *"Show all network devices in the 'ICU Wing' and 'OR Block' sites. Are there any reachability issues or health degradations that could impact biomedical devices on those segments?"*

### Manufacturing / OT
- *"List all devices in the OT DMZ site hierarchy in Catalyst Center. Run a compliance check to confirm they match the hardened IOS-XE baseline template for industrial segments."*

### Education / Higher Ed
- *"How many student devices are currently onboarded to the 'Student-WiFi' SSID across campus? Identify the top 5 APs by client load and flag any with capacity issues."*

### Financial Services
- *"Run a path trace between the trading floor subnet and the co-location data center and confirm there are no unplanned hops, ACL drops, or latency anomalies on that critical path."*

***

## Prompt Engineering Tips for CATC MCP

| Principle | Guidance |
|---|---|
| **Be site-specific** | Always include site name or IP range to scope queries |
| **Anchor in time** | Add "in the last X hours/days" to all health/event queries |
| **Chain tools** | For cross-MCP prompts, state both systems explicitly (e.g., "using Catalyst Center and Splunk") |
| **Request action confirmation** | For Command Runner or template deploy prompts, add "confirm before executing" |
| **Request formatted output** | Ask for tables, timelines, or JSON where downstream automation is needed |

This prompt library covers the full breadth of Catalyst Center MCP capabilities and extends naturally into the cross-server ecosystem. As you continue building out the suite with additional MCP servers (Splunk, ThousandEyes, NX-OS, ISE, NetBox), each new server multiplies the value of cross-ecosystem prompts that no single tool could answer alone. 
