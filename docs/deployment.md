## 🚀 Deployment on Google Cloud (Free Tier)

You can host and run this bot continuously using Google Cloud Platform (GCP) — ideal for cost-effective and scalable execution.

### ✅ Prerequisites

- [Google Cloud account](https://console.cloud.google.com/)
- Billing enabled (Free Tier eligible)
- Project with Compute Engine API enabled

---

### 🧰 1. Launch a VM (F1-micro)

> ⚠️ If F1-micro isn’t visible, choose `e2-micro` with minimal disk

1. Go to [Compute Engine → VM instances](https://console.cloud.google.com/compute/instances)
2. Click **Create Instance**
3. Choose:
   - **Series**: E2
   - **Machine type**: `e2-micro`
   - **OS**: Ubuntu 22.04 LTS
   - **Firewall**: Allow HTTP/S (optional)
4. Create the instance

---

### 🖥️ 2. SSH into VM

Click **SSH** from your instance list to open the terminal.

---

### 🛠️ 3. Install Python & Git

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
