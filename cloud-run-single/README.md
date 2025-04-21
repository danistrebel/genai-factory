# Single Cloud Run

The module deploys Cloud Run that communicates with Gemini APIs.

This inlcudes

- A Global external application load balancer (+ Cloud Armor IP allowlist security backend policy)
- Cloud Run (accessible with custom service account, authentication, direct VPC egress)
- By default, a VPC, a subnet, private Google APIs routes and DNS policies
- By default, a project

## Deployment

```shell
# Create terraform.tfvars
cp terraform.tfvars.sample terraform.tfvars

# Customize it with your billing account and parent

# Initialize Terraform and deploy
terraform init
terraform apply

# Deploy the applicaiton: follow the commands in the output screen to deploy the application(s).
```
<!-- BEGIN TFDOC -->
## Variables

| name | description | type | required | default |
|---|---|:---:|:---:|:---:|
| [project_config](variables.tf#L64) | The project configuration. Billing id and parent are mandatory if  | <code title="object&#40;&#123;&#10;  billing_account_id &#61; optional&#40;string&#41;     &#35; if create or control equals true&#10;  control            &#61; optional&#40;bool, true&#41; &#35; control an existing project&#10;  create             &#61; optional&#40;bool, true&#41; &#35; create and control project&#10;  parent             &#61; optional&#40;string&#41;     &#35; if control equals true&#10;&#125;&#41;">object&#40;&#123;&#8230;&#125;&#41;</code> | ✓ |  |
| [allowed_ip_ranges](variables.tf#L15) | The ip ranges that can call the Cloud Run service. | <code>list&#40;string&#41;</code> |  | <code>&#91;&#34;0.0.0.0&#47;0&#34;&#93;</code> |
| [cloud_run_configs](variables.tf#L22) | The Cloud Run configurations. | <code title="object&#40;&#123;&#10;  containers &#61; optional&#40;map&#40;any&#41;, &#123;&#10;    hello &#61; &#123;&#10;      image &#61; &#34;us-docker.pkg.dev&#47;cloudrun&#47;container&#47;hello&#34;&#10;    &#125;&#10;  &#125;&#41;&#10;  deletion_protection &#61; optional&#40;bool, true&#41;&#10;  ingress             &#61; optional&#40;string, &#34;INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER&#34;&#41;&#10;  max_instance_count  &#61; optional&#40;number, 3&#41;&#10;  vpc_access_egress   &#61; optional&#40;string, &#34;ALL_TRAFFIC&#34;&#41;&#10;  vpc_access_tags     &#61; optional&#40;list&#40;string&#41;, &#91;&#93;&#41;&#10;&#125;&#41;">object&#40;&#123;&#8230;&#125;&#41;</code> |  | <code>&#123;&#125;</code> |
| [ip_address](variables.tf#L40) | The optional load balancer IP address. If not specified, the module will create one. | <code>string</code> |  | <code>null</code> |
| [name](variables.tf#L46) | The name of the resources. This is also the project suffix if a new project is created. | <code>string</code> |  | <code>&#34;gf-srun-0&#34;</code> |
| [networking_config](variables.tf#L52) | The networking configuration. | <code title="object&#40;&#123;&#10;  create      &#61; optional&#40;bool, true&#41;&#10;  subnet_cidr &#61; optional&#40;string, &#34;10.0.0.0&#47;24&#34;&#41;&#10;  subnet_id   &#61; optional&#40;string, &#34;sub-0&#34;&#41;&#10;  vpc_id      &#61; optional&#40;string, &#34;net-0&#34;&#41;&#10;&#125;&#41;">object&#40;&#123;&#8230;&#125;&#41;</code> |  | <code>&#123;&#125;</code> |
| [prefix](variables.tf#L81) | The prefix to use for projects and GCS buckets. | <code>string</code> |  | <code>null</code> |
| [public_domains](variables.tf#L87) | The list of domains connected to the public load balancer. | <code>list&#40;string&#41;</code> |  | <code>&#91;&#34;example.com&#34;&#93;</code> |
| [region](variables.tf#L94) | The GCP region where to deploy the resources. | <code>string</code> |  | <code>&#34;europe-west1&#34;</code> |
| [service_invokers](variables.tf#L101) | The list of identities who can call the Cloud Run service. | <code>list&#40;string&#41;</code> |  | <code>&#91;&#93;</code> |

## Outputs

| name | description | sensitive |
|---|---|:---:|
| [commands](outputs.tf#L15) | Run the following commands when the deployment completes. |  |
| [ip_address](outputs.tf#L20) | The load balancer IP address. |  |
<!-- END TFDOC -->
