# Roadmap

Cannlytics has planted a seed with the open source Cannlytics LIMS. Please recommend features to <dev@cannlytics.com> and stay tuned for progress and improvements.

## 🧪 Labs

| Package     | Notes                 | Status         |
| ----------- | --------------------- | --------------- |
| Dashboard   | Welcome tutorial, placeholders, and analytics for users with data. | 🟡 In-progress |
| Analysis    | A simple C.R.U.D. interface is built for analyses. Logic to incorporate an analysis' analytes is needed. | ✔️ Completed |
| Clients     | A simple C.R.U.D. interface is built for contacts. More CRM functionality will likely be needed. | ✔️ Completed |
| Intake      | Will implement on demand when a lab needs to receive incoming transfers to create new projects / samples. | ❌ Not started |
| Logistics   | Will implement on demand when a lab needs to schedule sample pick ups. | ❌ Not started |
| Settings    | All core settings are built out to facilitate workflow. Custom data models need to be added. | ✔️ Completed |
| Traceability | Integration with state traceability systems, such as Metrc. | 🟡 In-progress |
| Help        | Provide minimal support options, including a feedback form. | ✔️ Completed |

The implementation of core data models is given in the table below.

| Model | UI | JavaScript | API | Logic |
| -- | -- | -------- | --- | ----- |
| Analyses | ✔️ | ✔️ | ✔️ | ✔️ |
| Areas | ✔️ | ✔️ | ✔️ | ✔️ |
| Contacts | ✔️ | ✔️ | ✔️ | ✔️ |
| Instruments | ✔️ | ✔️ | ✔️ | ✔️ |
| Inventory | ✔️ | ✔️ | ✔️ | ✔️ |
| Invoices | ❌ | ❌ | ✔️ | ❌ |
| Organizations | ✔️ | ✔️ | ✔️ | ✔️ |
| Projects | ✔️ | ✔️ | ✔️ | ✔️ |
| Samples | ✔️ | ✔️ | ✔️ | ✔️ |
| Transfers | ✔️ | ✔️ | ✔️ | ✔️ |
| Traceability | 🟡 | ✔️ | ✔️ | 🟡 |
| Settings | ✔️ | ✔️ | ✔️ | ✔️ |
| Help | ✔️ | ✔️ | n/a | n/a |

## 🌱 Cultivators / Processors

| Package     | Notes                 | Status         |
| ----------- | --------------------- | --------------- |
| Dashboard   | Will use a similar dashboard as the labs. | 🟡 In-progress |
| Results     | Will use a similar results page as the labs. | 🟡 In-progress |
| Scheduling  | Not started.                      | ❌ Not started |
| Analytics   | Analytics are being embedded into the interface. | 🟡 In-progress |

## 🛍️ Retailers / Consumers / Researchers

| Package     | Notes                 | Status         |
| ----------- | --------------------- | --------------- |
| Dashboard   | Will use a similar dashboard as the labs. | 🟡 In-progress |
| Results     | Will use a similar results page as the labs. | 🟡 In-progress |
| Purchases   | Not started.                     | ❌ Not started |
| Analytics   | Analytics are being embedded into the interface. | 🟡 In-progress |
