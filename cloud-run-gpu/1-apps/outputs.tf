# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

locals {

  external_lb_setup = var.lbs_config.external.enable ? "Ensure the external load balancer and certificate are ready" : ""

  _internal_lb_setup = <<EOT
  ## First set up a jump host in the internal VPC

  gcloud compute instances create demo-client \
  --project=${var.project_config.id} \
  --zone=${var.region}-b \
  --machine-type=e2-micro \
  --network=${var.networking_config.vpc_id} \
  --subnet=${var.networking_config.subnet.name} \
  --service-account=${var.service_accounts["project/gf-rgpu-demo-0"].email} \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --tags=allow-ssh \
  --no-address

  gcloud compute firewall-rules create allow-ssh --network=net-0 --allow=tcp:22 --project=${var.project_config.id}

  gcloud compute ssh demo-client \
    --project=${var.project_config.id} \
    --zone=${var.region}-b --tunnel-through-iap
  EOT

  internal_lb_setup = var.lbs_config.internal.enable ? local._internal_lb_setup : ""
  
  direct_cloud_run_setup = <<EOT
  ## Allow external access the cloud run service

  You have not created any load balancers. To test your cloud run service you would have to allow all ingress traffic on your Cloud Run service

  gcloud run services update ${module.cloud_run.service_name} \
  --project=${var.project_config.id} \
  --region=${var.region} \
  --ingress all
  EOT


  preparations = coalesce(local.external_lb_setup, local.internal_lb_setup, local.direct_cloud_run_setup)

  _internal_endpoint = var.lbs_config.internal.enable ? module.lb_internal[0].address : null
  _external_endpoint = var.lbs_config.external.enable ? module.lb_external[0].address[""] : null
  endpoint = coalesce(local._external_endpoint, local._internal_endpoint, module.cloud_run.service_uri)
}

output "commands" {
  description = "Run the following commands when the deployment completes to deploy the app."
  value       = <<EOT
  # Run the following commands to interact with the deployed model:

  ${local.preparations}

  curl https://${local.endpoint}/api/generate \
    -k \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $(gcloud auth print-identity-token --audiences ${module.cloud_run.service_uri})" \
    -X POST \
    -d '{
      "model": "gemma3:1b",
      "prompt": "Why is the sky blue?"
    }'

  EOT
}

output "ip_addresses" {
  description = "The load balancers IP addresses."
  value = {
    external = (
      var.lbs_config.external.enable
      ? module.lb_external[0].address[""]
      : null
    )
    internal = (
      var.lbs_config.internal.enable
      ? module.lb_internal[0].address
      : null
    )
  }
}
