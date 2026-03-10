# IOS-XE MCP Server — Prompt Library

## Tool Domain Map

The IOS-XE MCP server provides **direct SSH and RESTCONF/NETCONF access** to individual Cisco IOS-XE devices. It is the only server in the suite that operates at the device CLI level — all other servers talk to management platforms; this one talks directly to the box: [developer.cisco](https://developer.cisco.com/codeexchange/github/repo/pamosima/network-mcp-docker-suite/)

| Domain | Core Tools |
|---|---|
| **SSH / CLI Execution** | `run_show_command`, `run_exec_command`, `run_config_command`, `send_cli_command` |
| **Interface Management** | `get_interfaces`, `get_interface_detail`, `get_interface_counters`, `get_interface_status` |
| **Routing & Forwarding** | `get_ip_routes`, `get_bgp_summary`, `get_bgp_neighbors`, `get_ospf_neighbors`, `get_rib` |
| **ARP & MAC** | `get_arp_table`, `get_mac_address_table` |
| **Device State** | `get_device_info`, `get_cpu_utilization`, `get_memory_utilization`, `get_environment` |
| **Configuration** | `get_running_config`, `get_startup_config`, `push_config`, `diff_config` |
| **RESTCONF / YANG** | `restconf_get`, `restconf_patch`, `restconf_put`, `restconf_delete` |
| **NETCONF** | `netconf_get`, `netconf_get_config`, `netconf_edit_config` |
| **Logging & Events** | `get_syslog`, `get_logging_buffer`, `get_debug_output` |
| **QoS & Policies** | `get_policy_map`, `get_qos_stats`, `get_access_lists` |
| **MPLS / Segment Routing** | `get_mpls_forwarding`, `get_segment_routing`, `get_label_table` |
| **VRF** | `get_vrf_list`, `get_vrf_routes`, `get_vrf_interfaces` |
| **Crypto / VPN** | `get_crypto_session`, `get_ipsec_sa`, `get_tunnel_status` |

> **Safety note:** Tools prefixed `run_config_command`, `push_config`, `restconf_patch/put/delete`, and `netconf_edit_config` are **write operations** that directly modify device state. Always include **"show me the proposed change and confirm before executing"** in any prompt that modifies configuration.

***

## 🖥️ Category 1 — Device State & Health Diagnostics

For **NOC Engineers and L2/L3 Support** performing real-time device health checks.

1. **"Connect to device `WAN-EDGE-01` via the IOS-XE MCP server and run `show version`. Return the IOS-XE version, platform model, uptime, reason for last reload, and available DRAM and flash."**

2. **"Get the current CPU and memory utilization on `CORE-SW-01`. If CPU 5-minute average exceeds 70% or memory free is below 20%, flag it as critical and also run `show processes cpu sorted` to identify the top 5 consuming processes."**

3. **"Run `show environment all` on `DC-ROUTER-02`. Report any power supply faults, fan failures, or temperature sensors reading above their threshold values."**

4. **"Get the logging buffer contents from `ACCESS-SW-FLOOR3` for the last 200 lines. Filter for SEVERITY levels 0–3 (emergencies, alerts, critical, errors) only — show the timestamp, facility, and message for each."**

5. **"Run `show platform resources` on `CATALYST-9500-CORE` and return CPU, DRAM, and TCAM utilization. Flag any TCAM resource (IPv4, IPv6, ACL, QoS) that is above 80% capacity."**

6. **"What is the system uptime and last reload reason for each of the following devices: `CORE-SW-01`, `CORE-SW-02`, `WAN-EDGE-01`? Run the command in parallel and compare results."**

***

## 🔌 Category 2 — Interface Operations & Troubleshooting

For **Network Engineers and NOC Teams** diagnosing interface-level issues.

7. **"Get the full interface status for all interfaces on `DIST-SW-01`. Show interface name, description, IP address, line protocol state, speed/duplex, and input/output error counters. Flag any interface with input errors > 0 or output drops > 0."**

8. **"Run `show interfaces GigabitEthernet1/0/24` on `ACC-SW-B2` and show me the full counter output — including CRC errors, giants, runts, input errors, output errors, and collisions. I suspect a physical layer issue on this port."**

9. **"Check for any interfaces in a `line protocol down` state on `WAN-EDGE-01`. For each down interface, show the configured description, last input/output time, and any error counters — I need to determine if these are expected admin-down or unexpected failures."**

10. **"Run `show interface counters errors` on `CORE-SW-01` and identify the top 5 interfaces by total error count. Include both input and output error types."**

11. **"Get interface utilization for all uplinks on `DIST-SW-02`. Calculate the current bandwidth utilization percentage for each uplink — flag any port above 80% utilization as a congestion risk."**

12. **"A user reports their port has been flapping. Run `show logging | include GigabitEthernet2/0/12` on `ACC-SW-WING-A` to retrieve all interface up/down events for that specific port. Show timestamps and count total flaps in the last 24 hours."**

***

## 🗺️ Category 3 — Routing & Forwarding Plane

For **Network Engineers and Architects** validating routing protocol state and forwarding behavior.

13. **"Get the BGP summary from `WAN-EDGE-01`. Show all BGP neighbors, their AS number, state, uptime, prefixes received, and prefixes sent. Flag any neighbor not in the `Established` state."**

14. **"Show the BGP neighbor detail for peer `203.0.113.1` on `WAN-EDGE-01`. I need the full neighbor state — hold time, keepalive intervals, capability negotiation, last reset reason, and inbound/outbound route-map applied."**

15. **"Get the full IP routing table from `CORE-RTR-01`. How many routes are in the RIB total? Break them down by routing protocol source (OSPF, BGP, EIGRP, Static, Connected) and flag if the total route count is approaching the platform's FIB scale limit."**

16. **"Run `show ip route 10.50.100.0 255.255.255.0` on `CORE-RTR-01`. Show the best path, administrative distance, metric, next-hop, and outgoing interface. Is there a more specific route or a backup path in the RIB?"**

17. **"Get the OSPF neighbor table from `DIST-RTR-01`. Show all OSPF neighbors, their state, dead timer countdown, and interface they were discovered on. Flag any neighbor not in the `FULL` state."**

18. **"Run `show ip ospf database summary` on `CORE-RTR-01`. How many LSAs are in the OSPF database by type? Flag if the LSA count is unusually high — this could indicate a route oscillation or flooding issue."**

19. **"Retrieve the VRF route table for VRF `PROD` on `MPLS-PE-01`. Show all prefixes, their source protocol, next-hop, and label information. Cross-reference with VRF `MGMT` to confirm there is no route leakage between the two VRFs."**

***

## 📋 Category 4 — ARP, MAC & Layer 2 Operations

For **NOC Engineers and Help Desk** tracing devices to physical ports.

20. **"Get the ARP table from `CORE-SW-01`. Find the entry for IP `10.10.50.25` — show its MAC address, interface, and age. I need to trace this endpoint to its physical switch port."**

21. **"Get the MAC address table from `ACC-SW-FLOOR2`. Find MAC address `a4:c3:f0:9b:12:44` and show which port it is learned on, its VLAN, and whether it is a dynamic or static entry."**

22. **"Run `show mac address-table dynamic vlan 100` on `DIST-SW-01`. How many MAC addresses are currently learned on VLAN 100? Flag if the count exceeds 500 — this could indicate a spanning tree or loop issue flooding the CAM."**

23. **"Get the ARP table for VRF `PROD` on `CORE-RTR-01`. List all entries and flag any IP addresses with duplicate MAC addresses — these are potential ARP spoofing indicators."**

***

## ⚙️ Category 5 — Configuration Read & Audit

For **Network Engineers and Compliance Teams** auditing device configurations.

24. **"Get the running configuration from `WAN-EDGE-01`. Extract only the BGP configuration section and show all neighbor statements, route-maps applied, prefix-lists referenced, and the local AS number."**

25. **"Get the running configuration from `CORE-SW-01` and check for the following compliance items: NTP servers configured, logging to a remote syslog server, SSH version 2 only, no `service password-recovery`, and `service timestamps debug datetime msec` enabled. Flag any that are missing or incorrectly configured."**

26. **"Compare the running configuration versus the startup configuration on `ACC-SW-B3`. Are there any unsaved changes? Show the diff — list every line present in running-config but absent from startup-config."**

27. **"Pull the access-list configuration from `FIREWALL-RTR-01`. List all ACLs by name/number, the number of ACEs in each, and identify any ACL with a permit-any at any position other than the very end — this may be an overly permissive rule."**

28. **"Get the QoS policy-map configuration applied to the WAN interface on `WAN-EDGE-01`. Show the class hierarchy, match criteria, queuing behaviors, bandwidth allocations, and DSCP markings — confirm VOICE and VIDEO classes are correctly prioritized."**

***

## ✏️ Category 6 — Configuration Push & Change Operations

For **Senior Network Engineers and Change Management** executing controlled device changes.

> ⚠️ All prompts in this category should be executed only during approved change windows with rollback plans in place.

29. **"I need to add a new loopback interface `Loopback100` with IP `10.255.1.1/32` on `CORE-RTR-01`. Show me the configuration commands that will be pushed and the RESTCONF/NETCONF payload before executing. Confirm before applying."**

30. **"Shut down interface `GigabitEthernet1/0/48` on `ACC-SW-FLOOR4` as part of a planned maintenance. Show the current interface state first, then push the `shutdown` command. Confirm the interface reaches `administratively down` state after the change."**

31. **"Update the NTP server configuration on `WAN-EDGE-01` to replace `10.0.0.1` with `10.0.0.5`. Show the current NTP config, generate the config diff, push the change using NETCONF `edit-config`, and verify the new NTP association is formed."**

32. **"Deploy a new prefix-list `PL-BLOCK-RFC1918` to `WAN-EDGE-01` blocking advertisement of `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. Show me the complete configuration before pushing. After deployment, run `show ip prefix-list PL-BLOCK-RFC1918` to confirm."**

***

## 🔐 Category 7 — VPN & Crypto Operations

For **Security Engineers and WAN Teams** managing IPsec and DMVPN tunnels.

33. **"Get the IPsec session status on `WAN-EDGE-01`. Show all crypto sessions — peer IP, tunnel state, inbound/outbound SAs, bytes encrypted/decrypted, and time since last rekeying. Flag any session that is `DOWN` or `DOWN-NEGOTIATING`."**

34. **"Run `show crypto ipsec sa detail` on `HQ-VPN-GW` for peer `203.0.113.50`. I need to confirm both inbound and outbound SAs are active, the correct encryption algorithm (AES-256) is in use, and the SA lifetime remaining is above 10 minutes."**

35. **"Show the DMVPN tunnel status on `HUB-ROUTER-01`. List all registered spoke peers, their NBMA addresses, tunnel source IPs, and registration state. Flag any spoke that has not re-registered in the last 10 minutes."**

***

## 📦 Category 8 — RESTCONF & YANG Model Operations

For **NetDevOps Engineers and Automation Teams** using model-driven programmability. [networktocode](https://networktocode.com/blog/exploring-ios-xe-and-nx-os-based-restconf-implementations-with-yang-and-openconfig/)

36. **"Use RESTCONF GET on `CORE-RTR-01` to retrieve the BGP operational state using the `Cisco-IOS-XE-bgp-oper:bgp-state-data` YANG model. Return the neighbor states as structured JSON — I need this for an automated health check script."**

37. **"Use RESTCONF GET with YANG model `Cisco-IOS-XE-interfaces-oper:interfaces` on `ACC-SW-01` to retrieve the operational state of all interfaces. Return as JSON and filter to show only interfaces where `oper-status` is not `if-oper-status-up`."**

38. **"Use NETCONF `get-config` with the `running` datastore on `WAN-EDGE-01` to retrieve the full BGP configuration in XML. Then use `edit-config` to add a new neighbor — show me the XML payload and validate it against the YANG schema before committing."**

***

## 🏭 Vertical-Specific Prompt Packs

### Data Center / Spine-Leaf
- *"Get the BGP EVPN summary from `DC-SPINE-01`. Show all VTEP peers, their BGP EVPN session state, number of Type-2 and Type-5 routes exchanged, and confirm all leaf nodes are in Established state."*

### WAN / Service Provider Edge
- *"Run `show mpls forwarding-table` on `MPLS-PE-01`. Show the top label bindings, next-hop, outgoing interface, and bytes switched for each label. Flag any label with zero bytes switched in the last hour — it may indicate an inactive LSP."*

### Campus / Access Layer
- *"Run `show spanning-tree vlan 10` on all access layer switches. Identify the current root bridge, all root ports, and any topology change counter (TC count) above 10 in the last hour — high TC counts indicate spanning tree instability."*

### Branch / SD-WAN
- *"Get the IP SLA statistics from `BRANCH-RTR-DALLAS`. Show all configured IP SLA probes — target, protocol, average RTT, jitter, and packet loss. Flag any probe exceeding the defined threshold."*

### Security / Hardening
- *"Audit the running configuration of `EDGE-RTR-01` for STIG/CIS hardening compliance: check for disabled `ip source-routing`, disabled `ip proxy-arp` on all interfaces, enabled `ip tcp adjust-mss`, configured `login block-for`, and no `ip finger` service. Report pass/fail for each check."*

***

## 🔁 Cross-Ecosystem / Multi-MCP Prompts

The IOS-XE MCP server is the **device-level ground truth** in the suite — where Catalyst Center shows what the management plane *knows*, the IOS-XE server shows what the device *is actually doing*. Every cross-server workflow below exploits this distinction. [gblogs.cisco](https://gblogs.cisco.com/ch-tech/network-mcp-docker-suite/)

***

### 🔗 IOS-XE + Catalyst Center — Management Plane vs. Device Plane Correlation

39. **"Catalyst Center shows device `WAN-EDGE-01` as unreachable. Use the IOS-XE MCP server to SSH directly to that device using its out-of-band management IP. Run `show ip interface brief`, `show cdp neighbors`, and `show logging last 20` — compare what the device reports versus what Catalyst Center shows. Is this a management plane connectivity issue or a real forwarding problem?"**

40. **"Catalyst Center reports that `ACC-SW-FLOOR3` has a software compliance violation. Pull the running IOS-XE version directly from the device via the IOS-XE MCP server and compare it against Catalyst Center's golden image designation. If they differ, show the upgrade path and confirm flash space availability."**

***

### 🔗 IOS-XE + ThousandEyes — Path Validation

41. **"ThousandEyes is showing a network path change for traffic from the Chicago branch to AWS. Use the IOS-XE MCP server to run `show ip bgp 52.86.0.0` on `WAN-EDGE-CHI` — has the BGP best path changed? Compare the AS path ThousandEyes is seeing with what the routing table shows on the device. Confirm if this is a deliberate traffic engineering change or an unexpected route shift."**

42. **"ThousandEyes detected packet loss on the path to `api.prod.myapp.com` originating from the Dallas enterprise agent. SSH into `BRANCH-RTR-DALLAS` via IOS-XE MCP and run `show interface statistics` on the WAN interface — are there output drops, queue drops, or output errors that confirm local congestion as the cause?"**

***

### 🔗 IOS-XE + ISE — Policy Enforcement Verification

43. **"ISE assigned a dACL named `RESTRICTED-ACCESS` to an endpoint on port `GigabitEthernet1/0/22` of `ACC-SW-B1`. Use the IOS-XE MCP server to run `show authentication sessions interface GigabitEthernet1/0/22 detail` — confirm the dACL is actually applied in the device's session table, the auth method, and the assigned VLAN. Cross-reference with what ISE reports for that session."**

44. **"ISE is reporting a RADIUS authentication for MAC `b8:27:eb:4f:2a:11` was successful and assigned VLAN 200. SSH into the authenticating switch via IOS-XE MCP and run `show mac address-table address b827.eb4f.2a11` — confirm the MAC is actually learned on a VLAN 200 port. If the VLAN doesn't match, we have a VLAN assignment enforcement failure."**

***

### 🔗 IOS-XE + Splunk — Syslog Corroboration

45. **"Splunk shows a burst of IOS syslog events from `CORE-RTR-01` at 14:22 — specifically `%OSPF-5-ADJCHG` events indicating neighbor state changes. SSH into the device via IOS-XE MCP and run `show ip ospf neighbor` right now — are those adjacencies recovered? Also run `show logging | include OSPF` to get the device-local log and compare it with what Splunk ingested to confirm no syslog messages were dropped."**

***

### 🔗 IOS-XE + All MCP Servers — AgenticOps Root Cause Engine

46. **"We have reports of application slowness from users at three sites. Orchestrate an AgenticOps investigation: (1) ThousandEyes — run instant tests and check for active events; (2) IOS-XE — SSH into the WAN edge routers at each site and pull interface errors, BGP state, and CPU; (3) Catalyst Center — check device health and interface issues; (4) ISE — confirm no policy changes affected those users; (5) Splunk — search for correlated error logs. Produce a ranked root-cause brief with device-level CLI evidence from IOS-XE as the ground truth anchor."**

***

## Prompt Engineering Tips for IOS-XE MCP

| Principle | Guidance |
|---|---|
| **SSH vs. RESTCONF selection** | Use SSH/CLI (`run_show_command`) for quick operational state queries; use RESTCONF/NETCONF for structured data needed in automation pipelines  [cisco](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1717/b_1717_programmability_cg/netconf-protocol.html) |
| **Always confirm before config push** | Any prompt using `push_config`, `restconf_patch`, or `netconf_edit_config` must include "show proposed change and confirm" — these modify live device state  [developer.cisco](https://developer.cisco.com/codeexchange/github/repo/pamosima/network-mcp-docker-suite/) |
| **Scope to specific device** | Unlike platform MCP servers, IOS-XE MCP talks to ONE device per session — always start by specifying the exact hostname or management IP |
| **Use RESTCONF for structured output** | When the output will be used in downstream tools (Splunk, NetBox, dashboards), RESTCONF returns clean JSON vs. unstructured CLI text  [networktocode](https://networktocode.com/blog/exploring-ios-xe-and-nx-os-based-restconf-implementations-with-yang-and-openconfig/) |
| **Pair with Catalyst Center** | IOS-XE MCP is the ground-truth complement to Catalyst Center — when CATC shows a problem, IOS-XE confirms it at the device level  [gblogs.cisco](https://gblogs.cisco.com/ch-tech/network-mcp-docker-suite/) |
| **Leverage `diff_config`** | Before any change window, run `diff_config` (running vs. startup vs. template) to establish a clean baseline for rollback comparison |
| **Avoid interactive commands** | Commands requiring terminal interaction (`debug`, `monitor`, `more` prompts) may not behave well over SSH MCP — use `show logging buffer` instead of live debugs |

***

The IOS-XE MCP server is the **surgical instrument** of the suite  — while Catalyst Center, Meraki, ISE, ThousandEyes, and Splunk all provide platform-aggregated views, the IOS-XE server is the only tool that can look directly inside a device's forwarding plane, routing table, interface counters, and live configuration state. In any multi-MCP investigation, IOS-XE is the final arbiter of device-level ground truth. [developer.cisco](https://developer.cisco.com/codeexchange/github/repo/pamosima/network-mcp-docker-suite/)
