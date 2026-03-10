# Splunk MCP Server — Prompt Library

## Tool Domain Map

The Splunk MCP server exposes tools across the **Core Platform**, **Search & Analytics**, **Knowledge Management**, and **AI-Assisted SPL** namespaces. Tools follow the `splunk_` and `saia_` naming conventions: [splunk](https://www.splunk.com/en_us/blog/artificial-intelligence/unlock-the-power-of-splunk-cloud-platform-with-the-mcp-server.html)

| Domain | Core Tools |
|---|---|
| **Search Execution** | `splunk_search`, `splunk_run_saved_search`, `splunk_get_job_results`, `splunk_cancel_job` |
| **Index Management** | `splunk_list_indexes`, `splunk_get_index_details`, `splunk_get_index_stats` |
| **Saved Searches & Alerts** | `splunk_list_saved_searches`, `splunk_get_saved_search`, `splunk_list_alerts`, `splunk_get_triggered_alerts` |
| **Dashboards & Reports** | `splunk_list_dashboards`, `splunk_get_dashboard`, `splunk_list_reports` |
| **Lookups** | `splunk_list_lookups`, `splunk_get_lookup`, `splunk_update_lookup` |
| **KV Store** | `splunk_list_kvstore_collections`, `splunk_get_kvstore`, `splunk_upsert_kvstore` |
| **Users & RBAC** | `splunk_list_users`, `splunk_get_user`, `splunk_list_roles` |
| **Data Models / CIM** | `splunk_list_datamodels`, `splunk_get_datamodel` |
| **Apps** | `splunk_list_apps`, `splunk_get_app` |
| **AI-Assisted SPL** | `saia_generate_spl`, `saia_explain_spl`, `saia_ask_splunk_question` |
| **Connection** | `splunk_test_connection`, `splunk_get_server_info` |

> **Namespace note:** Tools prefixed `splunk_` are core platform capabilities. Tools prefixed `saia_` require the Splunk AI Assistant for SPL add-on to be installed. [help.splunk](https://help.splunk.com/splunk-cloud-platform/mcp-server-for-splunk-platform/about-mcp-server-for-splunk-platform)

***

## 🔍 Category 1 — Search Execution & SPL Operations

For **SOC Analysts, NOC Engineers, and Data Engineers** who need to run ad-hoc queries, scheduled searches, or investigate specific conditions in Splunk data.

1. **"Search Splunk for all events from `sourcetype=cisco:ios` in the last 1 hour that contain the keyword `%LINK-3-UPDOWN` (interface state change). Return the device hostname, interface name, new state, and timestamp — sorted by most recent first."**

2. **"Run the saved search named `Daily-Network-Health-Summary` and return the results. Show me which network devices had error rates above the defined threshold in the last 24 hours."**

3. **"Search `index=network_events sourcetype=meraki` for all events where `event_type=vpn_connectivity_change` in the last 6 hours. Group by site name and show the VPN tunnel state transitions."**

4. **"Search `index=security` for all firewall deny events in the last 30 minutes where the destination port is 22 (SSH) or 3389 (RDP). Group by source IP, count occurrences, and flag any source that has triggered more than 10 denies."**

5. **"I need to find all log entries from `index=netops` for device `CORE-SW-01` in the last 4 hours. Show me the full raw event, sourcetype, and index for each result — I need this for an incident RCA."**

6. **"Generate the SPL query needed to find all authentication failures from `sourcetype=cisco:ise:syslog` in the last 24 hours, grouped by failure reason and username. I don't know SPL well — use `saia_generate_spl` to build it for me."**

7. **"Explain what this SPL query does in plain language: `index=network | stats count by src_ip, dest_ip | where count > 100 | sort -count`. Use `saia_explain_spl` to break it down step by step."**

***

## 📁 Category 2 — Index & Data Source Management

For **Splunk Admins and Data Engineers** managing data ingestion and index health.

8. **"List all Splunk indexes and show their current size, event count, earliest event time, and latest event time. Flag any indexes that have not received new data in the last 2 hours — these may indicate a broken forwarder or data pipeline issue."**

9. **"Get detailed stats for the `network_events` index — what is its current retention policy, total disk usage, and daily ingest volume? Is it approaching its size limit?"**

10. **"Which indexes are receiving the highest data volume right now? Show the top 10 by events-per-minute ingestion rate — I need to identify any unexpected data spikes that could be consuming license."**

11. **"List all data inputs and sourcetypes currently feeding the `security` index. Are there any sourcetypes that stopped sending data in the last 24 hours compared to their historical baseline?"**

***

## 🚨 Category 3 — Alerts, Triggered Alerts & Scheduled Searches

For **SOC Teams, NOC Engineers, and IT Operations** managing alert hygiene and responding to triggered conditions.

12. **"List all currently triggered alerts in Splunk that have not been acknowledged. Show the alert name, severity, trigger time, triggering condition, and the associated Splunk app."**

13. **"Show me all alerts that have triggered more than 5 times in the last 24 hours. Rank them by trigger count — these high-frequency alerts may need threshold tuning to reduce noise."**

14. **"List all saved searches in Splunk that are scheduled as alerts (not reports). For each, show the search name, SPL query, schedule, alert condition, and notification actions configured (email, webhook, PagerDuty)."**

15. **"Which Splunk alerts are configured with `Real-Time` search mode? These consume significant compute — list them with their associated app and owner so we can review if real-time is truly needed."**

16. **"Pull all triggered alert events for the `Critical-BGP-Down` alert over the last 7 days. Show each trigger timestamp, the matching events that caused it, and how long each alert condition lasted before it cleared."**

***

## 📊 Category 4 — Dashboards & Reports

For **IT Managers, NOC Leads, and Operations Teams** accessing visualized operational data.

17. **"List all Splunk dashboards in the `Network_Operations` app. For each, show the dashboard title, owner, last modified date, and whether it has any scheduled PDF delivery configured."**

18. **"Show me the underlying SPL searches for all panels in the `WAN-Health-Overview` dashboard. I need to review whether the data sources and time ranges are still valid after our recent index restructuring."**

19. **"List all scheduled reports in Splunk that are emailed to distribution groups. Show the report name, schedule, recipients, and the app it belongs to. Flag any reports being sent to email addresses outside the corporate domain."**

***

## 📚 Category 5 — Lookups & KV Store

For **Splunk Developers and Data Engineers** managing enrichment tables and state stores.

20. **"List all lookup tables currently defined in Splunk. Show the lookup name, associated app, file size, and when it was last updated. Flag any lookups that haven't been refreshed in more than 30 days."**

21. **"Get the contents of the `network_device_inventory` lookup table. Cross-reference it against the current live device list — are there any devices in the lookup that are no longer in the production network, or new devices missing from the lookup?"**

22. **"Check the `endpoint_quarantine_state` KV Store collection. List all entries currently flagged as `quarantined=true`, along with the MAC address, username, reason, and timestamp when they were quarantined."**

23. **"Update the `critical_assets` lookup to add a new entry for the newly deployed server at IP `10.50.100.25` with asset_class=`PCI`, owner=`payments-team`, and criticality=`high`. Confirm the entry before writing."**

***

## 👥 Category 6 — User, Role & Access Management

For **Splunk Admins and Security Teams** auditing access and managing RBAC.

24. **"List all Splunk users and their assigned roles. Flag any users with the `admin` or `sc_admin` role who are not in the approved Splunk admin group, as these may be unauthorized privilege escalations."**

25. **"Which Splunk users have not logged in during the last 60 days? Show their username, role, last login timestamp, and whether their account is currently enabled — these are candidates for deprovisioning."**

26. **"List all Splunk roles and their associated capabilities. I need to audit which roles have `edit_monitor`, `delete_by_keyword`, or `change_own_password` capabilities — these are high-impact permissions."**

***

## 🧠 Category 7 — AI-Assisted SPL & Natural Language Queries

For **Any team member** who needs Splunk insights without deep SPL expertise. [lantern.splunk](https://lantern.splunk.com/Platform_Data_Management/Analysis_with_AI/Leveraging_Splunk_MCP_and_AI_for_enhanced_IT_operations_and_security_investigations)

27. **"Ask Splunk: 'What were the top 10 source IPs generating the most network traffic in the last 24 hours?' Use `saia_ask_splunk_question` to generate and execute the right query automatically."**

28. **"Generate the SPL to calculate the mean, p95, and p99 latency for all HTTP Server tests from `sourcetype=thousandeyes` indexed in the last 7 days, grouped by test name. Use `saia_generate_spl` and show me the query before running it."**

29. **"Ask Splunk to compare authentication failure rates this week versus last week across all sourcetypes in `index=security`. Identify which days and hours had the highest anomalous failure rates."**

***

## 🏭 Vertical-Specific Prompt Packs

### SOC / Cybersecurity
- *"Search `index=security` for any events matching known threat IOCs in our threat intelligence lookup `ti_iocs`. Show matches by source IP, destination, event time, and IOC type (IP, domain, hash) — sorted by most recent."*

### NOC / Network Operations
- *"Search `index=network_events sourcetype=cisco:ios` for all `%OSPF` and `%BGP` events in the last 4 hours. Group by router hostname and event type — flag any device with more than 3 routing protocol events as potentially unstable."*

### Financial Services / PCI Compliance
- *"Run a saved search `PCI-CardHolder-Data-Access-Audit` and return results. Show every access event to PCI-scoped systems in the last 24 hours with username, source IP, access time, and whether it occurred outside business hours."*

### Healthcare / HIPAA
- *"Search `index=ehr_audit` for all accesses to patient records by non-treating staff in the last 7 days. Flag any access where the accessing user's department does not match the patient's assigned department."*

### Manufacturing / OT Security
- *"Search `index=ot_events` for any Modbus, DNP3, or IEC-104 command events where the command type is a `WRITE` or `CONTROL` operation in the last 12 hours. These are high-risk actions on OT devices and need immediate review."*

### MSP / Multi-Tenant
- *"List all Splunk apps installed across the deployment. Show app name, version, whether it is enabled, and the last update date. Flag any apps that are more than 2 major versions behind their latest release on Splunkbase."*

***

## 🔁 Cross-Ecosystem / Multi-MCP Prompts

Splunk is the **log and event aggregation backbone** of the MCP Suite — every other server generates data that ultimately lands in Splunk, making these cross-server prompts the most analytically powerful workflows in the entire ecosystem. [github](https://github.com/deslicer/mcp-for-splunk)

***

### 🔗 Splunk + Catalyst Center — Network Event Enrichment

30. **"Catalyst Center has flagged a P1 issue on `CORE-SW-02`. Run a Splunk search against `index=network_events` for all syslog events from that device's management IP in the last 30 minutes. Show the raw syslog messages, severity codes, and timestamps — did Splunk receive error messages before Catalyst Center raised the alert?"**

31. **"Search Splunk for all `%LINK-3-UPDOWN` interface events in the last 24 hours across all Cisco IOS devices. Cross-reference with Catalyst Center's device inventory to map each hostname to its site location and device role — build a ranked list of sites experiencing the most interface instability."**

***

### 🔗 Splunk + Meraki — Cloud-Managed Branch Intelligence

32. **"Meraki has flagged 3 MX appliances at branch sites that experienced WAN failover today. Search Splunk's `index=meraki_events` for those 3 sites and show all events from the 10-minute window surrounding each failover — include upstream ISP syslog events, DHCP events, and any DNS failures that preceded the failover."**

33. **"Search Splunk for all Meraki IDS alert events in `index=security sourcetype=meraki:ids` in the last 7 days. Group by signature name and severity — which signatures are firing most frequently and which branch sites are the most targeted?"**

***

### 🔗 Splunk + ISE — Identity & Access Event Correlation

34. **"ISE is showing a spike in RADIUS failures at the Boston site. Search Splunk's `index=ise_logs sourcetype=cisco:ise:syslog` for all authentication events from the Boston NAS devices in the last 2 hours. Build a timeline showing failure volume per minute — did the spike coincide with a specific event like a switch reboot or AD sync failure?"**

35. **"A security incident has been raised for user `bsmith`. Search Splunk across `index=security`, `index=ise_logs`, and `index=network_events` simultaneously for all events associated with that username in the last 48 hours. Produce a unified chronological timeline of their network access, authentication attempts, application usage, and any security alerts triggered."**

***

### 🔗 Splunk + ThousandEyes — Application Performance + Log Correlation

36. **"ThousandEyes detected a 12-minute availability degradation to our ERP application starting at 09:14 AM. Search Splunk for application server error logs, load balancer access logs, and database slow query logs from `09:10 AM to 09:30 AM`. Identify which infrastructure component shows the first error signature — this is our probable root cause."**

37. **"ThousandEyes BGP monitors detected a route change for our primary IP prefix at 3:45 PM. Search Splunk's `index=network_events` for BGP state change syslogs from our WAN routers at that exact time. Did our own routers log the BGP event — or did the change originate upstream at the carrier level with no corresponding internal log?"**

***

### 🔗 Splunk + All MCP Servers — Full AIOps Incident Investigation

38. **"We have a P1 application outage starting at 11:00 AM. Orchestrate a full AIOps investigation using all MCP servers: search Splunk for error logs across `index=network_events`, `index=security`, `index=application_logs`; pull ThousandEyes active event and path data; check Catalyst Center for device health issues; query ISE for any policy changes in the last 30 minutes; and check Meraki for WAN events. Produce a consolidated root-cause brief with supporting evidence from each data source ranked by likelihood of being the origin."**

39. **"Generate a weekly operational health report using Splunk as the data source: run the saved searches `Weekly-Network-Error-Summary`, `Weekly-Auth-Failure-Summary`, and `Weekly-Application-Latency-Trends`. Then enrich with current open alerts from ISE, active events from ThousandEyes, and unresolved issues from Catalyst Center. Format as a structured executive summary with key findings, trend direction, and recommended actions."**

***

### 🔗 Splunk Self-Monitoring — MCP Infrastructure Observability

40. **"Search `index=_internal sourcetype=splunkd` for any errors, warnings, or license usage events in the last 24 hours. Are there any forwarder connectivity issues, indexer queue backlogs, or license warning thresholds being approached that I need to be aware of?"**

***

## Prompt Engineering Tips for Splunk MCP

| Principle | Guidance |
|---|---|
| **Always specify index + sourcetype** | Scoping to `index=X sourcetype=Y` dramatically reduces query cost and improves result relevance  
| **Use time anchors precisely** | Use absolute timestamps for incident investigations (`earliest="11/01/2025:09:00:00" latest="11/01/2025:09:30:00"`) rather than relative (`-1h`) |
| **Leverage `saia_generate_spl` for complex SPL** | For multi-step statistical queries or unfamiliar sourcetypes, let the AI Assistant generate the SPL rather than composing it manually |
| **Request output format explicitly** | Ask for `JSON`, `CSV`, `Markdown table`, or `summary` depending on downstream use — the MCP server supports all four   |
| **Set `max_results` deliberately** | High-volume indexes can return millions of events — always cap results or use `stats`/`timechart` aggregation in the query   |
| **Saved searches for repeatable ops** | For weekly reports or recurring audits, use `splunk_run_saved_search` rather than re-composing the SPL each time — it's faster and version-controlled |
| **KV Store for stateful workflows** | Use KV Store prompts for cross-session state tracking (e.g., quarantine lists, change records, known-good baselines) that need to persist between AI sessions  |

***

Splunk is the **unified data gravity center** of the MCP-Suite  — every syslog, SNMP trap, authentication event, application log, and ThousandEyes metric ultimately lands here. This makes the Splunk MCP server uniquely powerful for cross-domain correlation: while each other server sees its own slice of truth, Splunk holds the complete operational timeline that ties all of them together. [lantern.splunk](https://lantern.splunk.com/Platform_Data_Management/Analysis_with_AI/Leveraging_Splunk_MCP_and_AI_for_enhanced_IT_operations_and_security_investigations)
