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

output "commands" {
  description = "Run the following commands when the deployment completes to deploy the app."
  value       = <<EOT
  # Run the following commands to deploy the application.
  # Alternatively, deploy the application through your CI/CD pipeline.

  # Load sample data into BigQuery
  bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --autodetect \
    ${local.project.project_id}:${local.bigquery_id}.${local.bigquery_id} \
    ./data/top-100-imdb-movies.csv

  # Ingestion Cloud Run
  gcloud run deploy ${var.name}-ingestion \
    --source ./apps/rag/ingestion \
    --set-env-vars DB_INSTANCE_NAME=xxx,GOOGLE_CLOUD_PROJECT=${local.project.project_id},GOOGLE_CLOUD_LOCATION=${var.region} \
    --project ${local.project.project_id} \
    --region ${var.region} \
    --build-service-account ${module.projects.service_accounts["project/gf-rrag-ing-build-0"].id} \
    --quiet

  # Frontend Cloud Run
  gcloud run deploy ${var.name}-frontend \
    --source ./apps/rag/frontend \
    --set-env-vars GOOGLE_CLOUD_PROJECT=${local.project.project_id},GOOGLE_CLOUD_LOCATION=${var.region} \
    --project ${local.project.project_id} \
    --region ${var.region} \
    --build-service-account ${module.projects.service_accounts["project/gf-rrag-fe-build-0"].id} \
    --quiet
  EOT
}

output "ip_address" {
  description = "The load balancer IP address of the frontend."
  value = (var.ip_address == null
    ? google_compute_global_address.address[0].address
    : var.ip_address
  )
}
