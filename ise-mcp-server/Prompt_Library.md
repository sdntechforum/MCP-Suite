Based on the ISE ERS API framework, the ISE MCP tool ecosystem, and how the SDN Tech Forum suite implements ISE tools, here is the full prompt library for the **ISE MCP Server** — arguably the most security-critical server in the suite.

***

# ISE MCP Server — Prompt Library

## Tool Domain Map

The ISE MCP server dynamically exposes Cisco Identity Services Engine APIs across the **ERS (External RESTful Services)**, **MnT (Monitoring & Troubleshooting)**, and **pxGrid** surfaces.

| Domain | Core Tools / Resources |
|---|---|
| **Endpoints** | `get_endpoints`, `get_endpoint_by_mac`, `get_endpoint_detail`, `register_endpoint`, `delete_endpoint` |
| **Identity Groups** | `get_identity_groups`, `get_identity_group_members`, `update_identity_group` |
| **Users & Admins** | `get_internal_users`, `get_admin_users`, `get_user_detail`, `update_user` |
| **Network Devices (NADs)** | `get_network_devices`, `get_network_device_detail`, `get_network_device_groups` |
| **Authorization Profiles** | `get_authorization_profiles`, `get_authorization_profile_detail` |
| **Policy Sets** | `get_policy_sets`, `get_authentication_rules`, `get_authorization_rules` |
| **Security Groups (TrustSec)** | `get_security_groups`, `get_sgacls`, `get_trustsec_egress_matrix` |
| **RADIUS Live Logs** | `get_radius_live_logs`, `get_radius_failures`, `get_authentication_summary` |
| **Posture** | `get_posture_policies`, `get_posture_requirements`, `get_compliance_status` |
| **Guest Access** | `get_guest_types`, `get_sponsor_groups`, `get_guest_users`, `get_portals` |
| **BYOD & MDM** | `get_byod_portals`, `get_mdm_servers`, `get_mdm_endpoints` |
| **Profiling** | `get_profiling_policies`, `get_profiling_profile_detail`, `get_profiler_feeds` |
| **Certificates** | `get_system_certificates`, `get_trusted_certificates` |
| **Licensing** | `get_license_details`, `get_license_consumption` |
| **pxGrid** | `get_pxgrid_services`, `get_connected_pxgrid_clients` |
| **ISE Nodes** | `get_deployment_nodes`, `get_node_roles`, `get_node_health` |

***

## 🔐 Category 1 — Endpoint Visibility & Management

For **Security Operations, NAC Engineers, and Compliance Teams** who need real-time visibility into every device on the network.

1. **"List all endpoints currently registered in ISE. Group them by identity group (Employee, Contractor, IoT, Unknown) and show MAC address, profiled device type, and last authentication time."**

2. **"Find the endpoint with MAC address `a4:c3:f0:9b:12:44` in ISE. Show me its full profile — identity group, profiled device type, registration status, custom attributes, and which policy set matched on its last authentication."**

3. **"How many endpoints in ISE are in the 'Unknown' profiling state? These are devices that ISE has seen on the network but cannot classify — list them by switch port and VLAN where available."**

4. **"Show all endpoints that have been registered in ISE in the last 24 hours. Flag any that were added outside of normal business hours (before 8 AM or after 6 PM) as these may warrant review."**

5. **"List all endpoints currently assigned to the 'Quarantine' identity group. Show their MAC address, profiled type, assigned VLAN or dACL, and the date they were quarantined."**

6. **"Pull all endpoints that ISE has profiled as 'Medical-Device' or 'Industrial-Device' and confirm they are in the correct identity group with the appropriate authorization profile applied."**

***

## 👥 Category 2 — Identity & User Management

For **IAM Teams, Help Desk, and IT Security** managing user identities and access.

7. **"List all internal ISE users and flag any accounts that have not authenticated in the last 90 days. These are stale accounts that may be candidates for deprovisioning."**

8. **"Show all admin users configured in ISE — include their admin role (Super Admin, Read-Only, Network Admin), last login time, and whether MFA is enabled on their account."**

9. **"Which user accounts in ISE are in the 'Contractors' identity group? Show username, email, account expiry date, and flag any that are already expired but still enabled."**

10. **"A user `jdoe@corp.com` has been locked out of the network. Pull their ISE account status, group membership, and the last 5 authentication attempts — show the failure reason for each."**

***

## 🖥️ Category 3 — Network Access Devices (NADs)

For **Network Engineers and Security Architects** managing RADIUS/TACACS+ infrastructure.

11. **"List all Network Access Devices (NADs) registered in ISE. Group them by device type (switch, wireless controller, VPN gateway, firewall) and show their IP address, model, and assigned NAD group."**

12. **"Are there any NADs in ISE that have not sent RADIUS accounting messages in the last 6 hours? These devices may have lost connectivity to ISE or have misconfigured AAA settings."**

13. **"Show the NAD group hierarchy in ISE. Which device groups are used for policy segmentation and how many devices are in each group?"**

14. **"I need to add a new branch switch at IP `192.168.50.10` to ISE as a NAD. What is the current NAD template for branch switches and what shared secret and RADIUS attributes should be used?"**

***

## 📋 Category 4 — Policy Sets & Authorization Rules

For **Senior Security Engineers and Policy Architects** building and auditing NAC policy.

15. **"List all Policy Sets in ISE with their authentication and authorization rules. Flag any policy sets that have a 'catch-all' rule with a PERMIT result at the top of the order — this could be a misconfiguration allowing unrestricted access."**

16. **"Show the full authorization policy for the 'Corporate-Employees' policy set — list every rule, the conditions it matches (AD group, certificate attribute, device type), and the resulting authorization profile (VLAN, dACL, SGT)."**

17. **"Which authorization rules in ISE result in a VLAN assignment to the production VLAN 100? I need to audit who can land on the production network and under what conditions."**

18. **"Are there any authorization rules in ISE that reference AD groups which no longer exist in Active Directory? These orphaned rules could cause unexpected deny results."**

***

## 📊 Category 5 — RADIUS Live Logs & Authentication Troubleshooting

For **NOC, Help Desk, and Security Operations** performing real-time and historical authentication triage.

19. **"Show the RADIUS live logs for the last 30 minutes filtered to authentication failures only. Group by failure reason and show the top 5 most frequent causes."**

20. **"Pull all RADIUS authentication events for user `mwilson` in the last 4 hours. Show each attempt — timestamp, NAS IP (which switch or AP), authentication method, policy set matched, and pass/fail result."**

21. **"How many 802.1X authentication failures occurred at the `Branch-Denver` site in the last 24 hours? Break them down by failure type: wrong credential, certificate error, machine-auth failure, timeout."**

22. **"Identify all endpoints that successfully authenticated via MAC Authentication Bypass (MAB) in the last hour and landed on a VLAN other than the designated IoT VLAN. These may be unauthorized devices gaining inappropriate access."**

23. **"Show me all RADIUS authentications that triggered the 'Guest Redirect' authorization rule in the last 8 hours — how many unique users hit the guest portal and how many successfully sponsored themselves through?"**

***

## 🛡️ Category 6 — TrustSec & Security Group Tags (SGTs)

For **Security Architects and Zero Trust teams** implementing micro-segmentation.

24. **"List all Security Group Tags (SGTs) defined in ISE — show the SGT name, tag value, description, and the number of endpoints currently assigned to each."**

25. **"Show the TrustSec egress policy matrix. Which SGT-to-SGT pairs have an explicit DENY SGACL applied and which pairs are currently using the default policy? Flag any unexpected PERMIT entries between sensitive SGT pairs like 'PCI-Servers' and 'Guest'."**

26. **"Which endpoints are currently tagged with the 'Unknown' or 'Unclassified' SGT? These devices are operating outside the defined segmentation model and need profiling review."**

27. **"Show me all SGACLs (Security Group ACLs) defined in ISE and the specific ACE entries for the 'Block-Lateral-Movement' SGACL. When was it last modified and by which admin?"**

***

## 🧪 Category 7 — Posture & Compliance

For **Endpoint Security Teams and Compliance Officers** enforcing device health.

28. **"List all posture policies in ISE — show the policy name, operating system target, compliance conditions (AV installed, patch level, disk encryption), and the resulting authorization profile for compliant vs. non-compliant endpoints."**

29. **"How many endpoints are currently in a 'Non-Compliant' posture state? Show their MAC address, username, device type, and which specific posture requirement they are failing."**

30. **"A user's laptop is being redirected to the remediation portal instead of getting full network access. Pull their posture assessment detail from ISE — which compliance checks passed and which failed, and what remediation action is prescribed?"**

***

## 🌐 Category 8 — Guest Access & Sponsor Management

For **IT Help Desk and Facility Managers** handling visitor and temporary access.

31. **"List all active guest user accounts in ISE. Show username, sponsor name, creation time, expiry time, and current connection status. Flag any accounts that are expired but still showing as active."**

32. **"Which sponsor groups are configured in ISE and what are their permissions — can they create bulk accounts, set custom expiry times, or sponsor guests from specific locations only?"**

33. **"Show me all guest portal configurations in ISE — which portals use SMS OTP, which use sponsor approval, and which use self-registration? Flag any portals that do not have an AUP (Acceptable Use Policy) page enabled."**

***

## 🏭 Vertical-Specific Prompt Packs

### Healthcare / HIPAA
- *"List all endpoints profiled as medical devices (infusion pumps, patient monitors, imaging systems) in ISE. Confirm each is assigned to the 'BioMed-Devices' SGT and is NOT able to reach the internet based on the egress SGACL matrix."*

### Financial Services / PCI-DSS
- *"Pull all authorization policy rules that grant access to the 'PCI-Servers' SGT. For each rule, show the conditions required — is multi-factor authentication or valid certificate mandatory? Flag any rule that grants PCI access without a certificate condition."*

### Education
- *"How many student-owned BYOD devices are currently registered in ISE's My Devices portal? Show device type distribution and flag any students who have registered more than 5 personal devices."*

### Manufacturing / OT
- *"Show all endpoints on OT network segments that authenticated via MAB (no 802.1X). These devices are likely PLCs or legacy OT equipment — confirm they are assigned to the correct SGT and authorization profile for OT device isolation."*

### Government / Zero Trust
- *"Generate a full access audit for the last 7 days: which users authenticated with certificate-based EAP-TLS, which used PEAP-MSCHAPv2 only, and which used MAB? Classify each by assurance level for Zero Trust posture reporting."*

***

## 🔁 Cross-Ecosystem / Multi-MCP Prompts

These prompts chain the **ISE MCP with Catalyst Center, Meraki, Splunk, and ThousandEyes** for compound security and operations investigations. [linkedin](https://www.linkedin.com/posts/john-capobianco-644a1515_cisco-identity-server-engine-ise-mcp-activity-7329191948525649920-KU6J)

***

### 🔗 ISE + Catalyst Center — Identity-Aware Network Operations

34. **"Catalyst Center is showing high CPU on access switch `ACC-SW-Floor3`. Pull the RADIUS live logs from ISE for that NAS IP — are there an abnormally high number of authentication requests coming from that switch suggesting a broadcast storm, loop, or dot1x supplicant misbehavior?"**

35. **"A Catalyst Center health alert shows a new device connecting to port `GigabitEthernet1/0/14` on `ACC-SW-B2`. Cross-reference ISE — did this device authenticate successfully? What identity group and authorization profile was it assigned, and is it a known corporate asset?"**

***

### 🔗 ISE + Meraki — Unified Policy Enforcement

36. **"A Meraki MX firewall at the branch has blocked traffic from a client device. Pull that device's MAC from ISE — what is its profiled device type, identity group, SGT, and authorization profile? Confirm whether the Meraki block was consistent with the ISE policy intent or a misconfiguration."**

37. **"Cross-check all endpoints currently connected to Meraki branch networks against ISE's endpoint database. Identify any MAC addresses present in Meraki's client list that are NOT registered or have never authenticated in ISE — these may be shadow IT devices."**

***

### 🔗 ISE + Splunk — Security Event Correlation

38. **"Splunk has detected a potential credential stuffing attack — 50+ failed logins in 5 minutes for different usernames from the same source IP. Query ISE RADIUS live logs for those usernames over the same time window — did any of those attempts succeed? If so, identify the endpoint MAC, switch port, and assigned VLAN immediately."**

39. **"Build a correlated security timeline: pull ISE authentication events for endpoint `b8:27:eb:4f:2a:11` over the last 24 hours and overlay with Splunk endpoint security logs for the same device. Did any lateral movement, new process execution, or AV events occur within 10 minutes of a successful ISE authentication?"**

***

### 🔗 ISE + Catalyst Center + Meraki + Splunk — Full Zero Trust Audit

40. **"Generate a Zero Trust access audit report for user `jsmith` for the last 7 days: use ISE for authentication method and policy outcomes, Catalyst Center for campus network path and device health, Meraki for branch Wi-Fi association, and Splunk for application access logs. Identify any access event that did not meet the minimum assurance level required by policy."**

***

## Prompt Engineering Tips for ISE MCP

| Principle | Guidance |
|---|---|
| **Anchor to MAC or username** | ISE queries are most precise when scoped to a MAC address or UPN — always include these when available |
| **Separate ERS vs. MnT tools** | Read-only visibility (ERS) vs. live logs (MnT) serve different purposes — be explicit about which data you need |
| **Time-window live logs** | RADIUS live logs are extremely high-volume — always bound queries to `last N minutes/hours` |
| **Confirm before write ops** | Endpoint quarantine, group reassignment, and account disablement are destructive — always include "list targets and confirm before executing" |
| **Policy audit cadence** | Schedule prompts #15–18 as weekly or monthly audit runs — orphaned rules and catch-all PERMITs are a persistent risk |
| **pxGrid for streaming** | For real-time event-driven workflows (e.g., auto-quarantine on Splunk alert), note that pxGrid tools enable event subscription rather than polling  [developer.cisco](https://developer.cisco.com/docs/identity-services-engine/latest/) |

***

This ISE prompt library is the **security and identity spine** of the entire MCP-Suite. ISE's deep integration with every other server — Catalyst Center (wired NAC), Meraki (cloud branch NAC), Splunk (SIEM correlation), and ThousandEyes (user experience + identity) — makes it the most powerful cross-ecosystem multiplier in the suite. The prompts above progressively build toward a full AI-driven Zero Trust operations model. [mcpmarket](https://mcpmarket.com/server/ise)
