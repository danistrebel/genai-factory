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

module "cloud_run_ingestion" {
  source           = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/cloud-run-v2"
  project_id       = local.project.project_id
  name             = "${var.name}-ingestion"
  region           = var.region
  create_job       = true
  ingress          = var.cloud_run_configs.ingestion.ingress
  containers       = var.cloud_run_configs.ingestion.containers
  service_account  = module.projects.service_accounts["project/gf-rrag-ing-0"].email
  managed_revision = false
  iam = {
    "roles/run.invoker" = concat(
      [module.projects.service_accounts["project/gf-rrag-ing-sched-0"].iam_email],
      var.cloud_run_configs.ingestion.service_invokers
    )
  }
  revision = {
    gen2_execution_environment = true
    max_instance_count         = var.cloud_run_configs.ingestion.max_instance_count
    vpc_access = {
      egress = var.cloud_run_configs.ingestion.vpc_access_egress
      network = (var.networking_config.create
        ? module.vpc[0].id
        : var.networking_config.vpc_id
      )
      subnet = (
        var.networking_config.create
        ? module.vpc[0].subnet_ids["${var.region}/${var.networking_config.subnet_id}"]
        : var.networking_config.subnet_id
      )
      tags = var.cloud_run_configs.ingestion.vpc_access_tags
    }
  }
  deletion_protection = var.enable_deletion_protection
}

resource "google_cloud_scheduler_job" "ingestion_scheduler" {
  name             = var.name
  description      = "Scheduler to periodically trigger the data ingestion."
  schedule         = var.ingestion_schedule_configs.schedule
  attempt_deadline = var.ingestion_schedule_configs.attempt_deadline
  region           = var.region
  project          = local.project.project_id

  retry_config {
    retry_count = var.ingestion_schedule_configs.retry_count
  }

  http_target {
    http_method = "POST"
    uri         = "https://run.googleapis.com/v2/projects/${local.project.project_id}/locations/${var.region}/jobs/${module.cloud_run_ingestion.job.name}"

    oauth_token {
      service_account_email = module.projects.service_accounts["project/gf-rrag-ing-sched-0"].email
    }
  }
}
