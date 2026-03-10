# ThousandEyes MCP Server — Prompt Library

## Tool Domain Map

The ThousandEyes MCP server reached **General Availability in March 2026**, hosted directly at `https://api.thousandeyes.com/mcp`. It exposes tools across six functional domains: [thousandeyes](https://www.thousandeyes.com/blog/thousandeyes-mcp-server-now-generally-available)

| Domain | Tools |
|---|---|
| **Core Monitoring** | `list_tests`, `get_test_details`, `list_events`, `get_event_details`, `list_alerts`, `get_alert_details`, `search_outages`, `instant_tests` |
| **Advanced Analysis** | `get_anomalies`, `get_metrics` |
| **AI-Powered Skills** | `views_explanations` |
| **Endpoint Monitoring** | `list_endpoint_agents_and_tests`, `get_endpoint_agent_metrics` |
| **Network Path Analysis** | `get_path_visualization`, `get_full_path_visualization`, `get_bgp_test_results`, `get_bgp_route_details` |
| **Account Management** | `get_account_groups` |

> **Important:** ThousandEyes covers three agent types — **Cloud Agents** (globally distributed), **Enterprise Agents** (on-prem deployed), and **Endpoint Agents** (user device installed). Specify which agent type you are targeting in every prompt for best results. [thousandeyes](https://www.thousandeyes.com/blog/thousandeyes-mcp-server-now-generally-available)

***

## 📡 Category 1 — Test Inventory & Visibility

For **NOC Engineers, Network Architects, and IT Operations** who need to understand what is being monitored and from where.

1. **"List all ThousandEyes tests currently configured across all account groups. Group them by test type (HTTP Server, Page Load, Agent-to-Server, DNS, BGP, Web Transaction) and show the target, assigned agents, and test interval."**

2. **"What tests are we running to Salesforce and from which agent locations? Include both Cloud Agents and Enterprise Agents, and show current test status."**

3. **"Show me all ThousandEyes tests targeting internal applications (non-internet targets). Which ones are only covered by Enterprise Agents with no Cloud Agent baseline for comparison?"**

4. **"Are there any ThousandEyes tests that are currently disabled or paused? List them with the test name, type, target, and when they were last active."**

5. **"Which of our applications have the most ThousandEyes tests configured against them? Show a ranked list — this helps identify where we have strong observability vs. gaps."**

***

## 🚨 Category 2 — Events & Outage Detection

For **Incident Commanders, NOC Teams, and SREs** during active incidents or post-incident reviews.

6. **"Do we have any active ThousandEyes events right now? For each event, show the affected test, impacted agent locations, event severity, start time, and a summary of what is being detected."**

7. **"Were there any ThousandEyes events between 2:00 PM and 4:00 PM today? I need to correlate with a reported user impact window — show every event that was open or triggered during that time."**

8. **"Search for all network and application outages detected in the last 7 days. Group by affected application and show duration, impacted agent count, and whether the outage was resolved or still ongoing."**

9. **"Get the full detail for the most recent event affecting Microsoft Teams. Which agent locations were impacted, what metrics triggered the event (latency, packet loss, availability), and when did it clear?"**

10. **"Show me all ThousandEyes events from the last 30 days that lasted longer than 30 minutes. These prolonged events represent the highest business-impact incidents — rank them by duration."**

***

## 🔔 Category 3 — Alerts & Alert Rules

For **Operations Teams and Application Owners** managing SLA thresholds and alerting hygiene.

11. **"List all currently active ThousandEyes alerts. For each, show the alert rule name, test name, triggering metric and value, affected agents, and time since triggered."**

12. **"Show me all alerts that triggered and then cleared in the last 24 hours. I want to identify flapping conditions — alerts that triggered and cleared more than twice in the same window for the same test."**

13. **"Which ThousandEyes alert rules are configured with a critical severity and have never triggered? These may be misconfigured thresholds that are set too high to be useful."**

14. **"Get full details for the active critical alert on the `AWS-EastUS-API-Prod` HTTP Server test. What threshold was breached, from how many agent locations, and what is the current metric value?"**

***

## ⚡ Category 4 — Instant Tests & Active Troubleshooting

For **L2/L3 Support Engineers and Incident Responders** who need on-demand active measurement during a live issue.

15. **"Run an HTTP Server instant test to `https://myapp.corp.com` from our Chicago and New York Enterprise Agents right now. Return availability, response time, and any HTTP error codes observed."**

16. **"Run an Agent-to-Server instant test on TCP port 443 to `api.servicenow.com` from our London, Frankfurt, and Singapore Cloud Agents. Show packet loss, latency, and jitter for each location."**

17. **"A user in the Dallas office is reporting slowness accessing the ERP system. Run an instant HTTP Page Load test to `https://erp.internal.corp` from the `Dallas-Enterprise-Agent` and show the full waterfall breakdown — where is the time being spent?"**

18. **"Run a DNS Server instant test for `salesforce.com` resolving against our internal DNS server from three Enterprise Agents. Compare resolution times and confirm all agents are getting consistent IP responses."**

19. **"We just pushed a change to the load balancer. Run an instant test to `https://api.prod.myapp.com` from 5 Cloud Agent locations simultaneously and confirm availability and response time have not degraded versus the pre-change baseline."**

***

## 📊 Category 5 — Metrics & Anomaly Detection

For **Platform Engineers, SREs, and Capacity Teams** tracking performance trends and detecting anomalies early.

20. **"Retrieve the aggregated metrics for the `Webex-HQ-Monitor` HTTP Server test for the last 7 days. Show average availability, mean response time, and peak latency per day — I need this for our weekly service review."**

21. **"Find anomalies in the `Azure-ExpressRoute-Latency` Agent-to-Server test data for the last 24 hours. Which metric showed the anomaly — was it latency, jitter, or packet loss — and from which agent location did it first appear?"**

22. **"Can you find anomalies during last Tuesday's maintenance window (11 PM–2 AM) for all tests tagged with `production`? I want to confirm whether any metric degradations occurred that correlate with the change we pushed."**

23. **"Retrieve the metrics for all HTTP Server tests targeting our CDN endpoints for the last hour. Flag any test where availability has dropped below 99% or response time has exceeded 500ms."**

***

## 🗺️ Category 6 — Network Path Analysis

For **Network Engineers and Architects** investigating routing behavior, BGP changes, and hop-by-hop performance.

24. **"Show me the hop-by-hop network path for the `NYC-to-AWS-East-HTTP` test from the New York Enterprise Agent at 3:15 PM today. I want to see every router hop, IP, AS number, and per-hop latency."**

25. **"Get the full path visualization for the `Salesforce-Global-Monitor` test across all agent locations right now. Which agent locations are traversing different network exchange points or taking asymmetric paths?"**

26. **"Are there any MPLS label-switched hops in the network path for the `Branch-Chicago-SAP` test? Show which hops carry MPLS labels and identify if any MPLS hops changed compared to 6 hours ago."**

27. **"What are the BGP test results for the `Corporate-IP-Space-Monitor` BGP test over the last 4 hours? Show reachability by vantage point, any route withdrawals, and which ASNs are in the current AS path."**

28. **"Get the BGP route details for prefix `203.0.113.0/24` from all BGP route monitors. Show the full AS path from each monitor, origin AS, and whether any monitors are seeing route instability or path changes."**

29. **"Explain the network path visualization for the `London-to-Office365-Exchange` test at 9:00 AM this morning. I need a plain-language explanation of the path — which carrier networks were traversed, where the latency is concentrated, and whether the path is optimal."**

***

## 💻 Category 7 — Endpoint Agent Monitoring

For **IT Help Desk, End-User Experience Teams, and Digital Experience Monitoring** programs.

30. **"List all Endpoint Agents deployed in the organization. Show agent name, OS platform, version, assigned user, location (office/remote), and last active time. Flag any agents that have not reported in the last 2 hours."**

31. **"Get all Endpoint Agent metrics for the last hour for agents in the `Remote-Workers` group. Show Wi-Fi signal quality, DNS resolution time, gateway response time, and VPN tunnel latency — identify the bottom 10% of performers."**

32. **"Which Endpoint Agents are showing poor wireless metrics right now? Filter for agents with RSSI below -70 dBm or SNR below 20 dB and show their username, building/floor if tagged, and current SSID."**

33. **"Show me the cellular vs. Wi-Fi vs. VPN network performance breakdown from Endpoint Agents over the last business day. Which connectivity type has the highest average latency to corporate resources?"**

***

## 🏭 Vertical-Specific Prompt Packs

### Financial Services / Trading
- *"Show latency trends for all tests targeting our trading infrastructure (`exchange-feed-monitor`, `order-mgmt-api-test`) for the last 4 hours. Flag any test where latency exceeded 10ms — even briefly — as this is our SLA threshold for market data feeds."*

### Healthcare
- *"Run instant tests to our EHR system (`epic.hospital.internal`) from all hospital campus Enterprise Agents. Confirm response times are below the 2-second clinical SLA threshold and flag any location that is non-compliant."*

### Retail / E-Commerce
- *"During the past Black Friday sale window, what events and anomalies did ThousandEyes detect on our checkout API and payment gateway tests? Show peak latency, any availability drops, and which geographic agent locations were most impacted."*

### Enterprise SaaS Operations
- *"What is our current availability and response time for Microsoft 365, Salesforce, ServiceNow, and Workday as measured by ThousandEyes? Give me a live SaaS health scorecard across all four platforms."*

### SD-WAN / Multi-Site Branch
- *"Show the Agent-to-Server test results for all branch Enterprise Agents targeting the data center over the last 24 hours. Which branches are showing the worst packet loss or latency and do those correlate with branches that have had WAN failover events?"*

***

## 🔁 Cross-Ecosystem / Multi-MCP Prompts

These prompts chain **ThousandEyes with every other server in the SDN Tech Forum MCP Suite** — delivering the most powerful compound workflows in the entire ecosystem. [thousandeyes](https://www.thousandeyes.com/blog/optimize-aiops-with-thousandeyes-mcp-server)

***

### 🔗 ThousandEyes + Catalyst Center — Inside-Out & Outside-In Correlation

34. **"ThousandEyes is showing packet loss from our San Jose Enterprise Agent to AWS. At the same time, pull Catalyst Center health data for the WAN edge router at that site — are there interface errors, high CPU, or BGP neighbor state changes that correlate with the ThousandEyes degradation window?"**

35. **"ThousandEyes detected a 15-minute application availability dip starting at 14:22 from the Chicago Enterprise Agent. Run a Catalyst Center path trace between the Chicago agent's subnet and the application server — was there any network path change, ACL drop, or link event during that window?"**

***

### 🔗 ThousandEyes + Meraki — Branch Experience Correlation

36. **"ThousandEyes Endpoint Agents at the Austin branch are showing high latency to Microsoft Teams. Simultaneously check the Meraki MX uplink status at that branch — did the primary WAN link degrade or fail during the same window? Also check if the Meraki APs serving those users show any wireless degradation."**

37. **"Three branch Enterprise Agents are all showing simultaneous degradation to Zoom. Pull the Meraki uplink stats for all three MX appliances — are they on the same upstream ISP or peering point? Cross-reference with ThousandEyes BGP test results to determine if this is a common-carrier event."**

***

### 🔗 ThousandEyes + ISE — Identity-Aware Experience Monitoring

38. **"ThousandEyes Endpoint Agent on `LAPTOP-JSMITH` is showing poor network performance. Pull that user's ISE authentication record — what VLAN, SGT, and authorization profile are they on right now? Confirm the policy is correct and they haven't been inadvertently placed in a restricted VLAN that would explain the degraded path."**

***

### 🔗 ThousandEyes + Splunk — AIOps Incident Timeline

39. **"ThousandEyes fired a critical alert on our payment gateway test at 10:47 AM. Query Splunk for application error logs, firewall deny logs, and server CPU/memory metrics from the payment gateway servers during the same 10-minute window. Build a unified root-cause timeline combining ThousandEyes network evidence with Splunk infrastructure evidence."**

***

### 🔗 ThousandEyes + Catalyst Center + Meraki + ISE + Splunk — Full-Stack Incident Bridge

40. **"We have a P1 incident: users across 3 sites cannot reach the ERP system. Orchestrate a full-stack triage using all MCP servers: ThousandEyes for active path testing and event lookup; Catalyst Center for campus network and WAN edge health; Meraki for branch WAN failover status; ISE for authentication and policy correctness; and Splunk for application and infrastructure logs. Produce a structured incident brief with evidence from each domain and a ranked list of probable root causes."**

***

## Prompt Engineering Tips for ThousandEyes MCP

| Principle | Guidance |
|---|---|
| **Specify agent type** | Always state Cloud Agent, Enterprise Agent, or Endpoint Agent — they answer fundamentally different questions  [thousandeyes](https://www.thousandeyes.com/blog/thousandeyes-mcp-server-now-generally-available) |
| **Anchor to time precisely** | For event/anomaly queries, use absolute timestamps (`10:30 AM today`) not relative (`recently`) for accurate data retrieval |
| **Use instant tests proactively** | Don't wait for alerts — during a live incident, trigger instant tests first to establish current-state baseline before pulling historical data |
| **Scope by account group** | Multi-org deployments should prefix prompts with the target account group name to avoid cross-tenant data bleed  [developer.cisco](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/ThousandEyes-MCP-Server-official/) |
| **Chain AI explanations** | After retrieving path visualization or metrics data, append *"explain what this means in plain language"* to invoke the `views_explanations` AI skill  [developer.cisco](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/ThousandEyes-MCP-Server-official/) |
| **Enable selectively** | ThousandEyes' own documentation recommends enabling only the tools needed per session — too many tools simultaneously degrades MCP response time  [developer.cisco](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/ThousandEyes-MCP-Server-official/) |

***

ThousandEyes is the **outside-in observability anchor** of the entire MCP-Suite  — the only server that can see what real users experience across the internet, SaaS, and cloud paths that Catalyst Center, Meraki, and ISE have no visibility into. Every cross-ecosystem prompt that involves a user-reported performance complaint should start here, then work inward through the other MCP servers to locate where in the stack the issue originates. [thousandeyes](https://www.thousandeyes.com/blog/optimize-aiops-with-thousandeyes-mcp-server)
