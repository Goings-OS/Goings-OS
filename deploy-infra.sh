#!/bin/bash
echo "=========================================================="
echo "   GOINGS-OS-COMMAND: MODEL ARMOR INTEGRATION MATRIX     "
echo "=========================================================="

# 1. Enforce precise route alignment to the target repository folder
TARGET_DIR="$HOME/cloud-networking-solutions/demos/agent-gateway/terraform"

if [ ! -d "$TARGET_DIR" ]; then
    echo "[CRITICAL ERROR] Target path not found. Initializing Git recovery loop..."
    cd $HOME
    git clone https://github.com/GoogleCloudPlatform/cloud-networking-solutions.git
fi

cd "$TARGET_DIR"
echo "Terminal pathing successfully aligned to: $(pwd)"

# 2. Provision local environment infrastructure configuration ledgers
echo "Syncing local backend and variable configuration ledgers..."
cp -f example.backend.conf backend.conf
cp -f example.tfvars terraform.tfvars

# 3. Inject your explicit project parameter baseline into the configuration variables
sed -i 's/YOUR_PROJECT_ID/618999325541/g' terraform.tfvars 2>/dev/null
sed -i 's/your-project-id/618999325541/g' terraform.tfvars 2>/dev/null

# 4. Initialize the Terraform backend state tracking engine
echo "Initializing Terraform backend tracking systems..."
terraform init -backend-config=backend.conf

# 5. Compile the comprehensive deployment blueprint layout
echo "Compiling the deployment architecture blueprint..."
terraform plan -out=tfplan

# 6. Execute the plan to spin up the gateway infrastructure
echo "Applying blueprint configurations to Google Cloud APIs..."
terraform apply -auto-approve "tfplan"

echo "=========================================================="
echo "    INFRASTRUCTURE PROVISIONED UNDER VICTORY STANDARD     "
echo "=========================================================="
