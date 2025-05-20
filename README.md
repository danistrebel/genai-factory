# GenAI Factory

A collection of scripts to deploy AI infrastructures and applications in GCP, following security best-practices.

- Embraces IaC best practices. Infrastructure implemented in [Terraform](https://developer.hashicorp.com/terraform), leveraging [Terraform resources](https://registry.terraform.io/providers/hashicorp/google/latest/docs) and [Cloud Foundations Fabric modules](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules).
- Follows the least-privilege principle: no default service accounts, primitive roles, minimal permissions.
- Compatible with [Cloud Foundation Fabric FAST](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric) [project-factory](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/project-factory) and application templates.

## Applications

- [Single Cloud Run](./cloud-run-single/README.md) - A single, secure public Cloud Run behind an external application load balancer and interact with Gemini.
- [RAG with Cloud Run](./cloud-run-single/README.md) - A "Retrieval-Augmented Generation" (RAG) system, leveraging Cloud Run, Vertex AI, Cloud SQL and BigQuery.

## Quickstart

The quickstart assumes you have permissions to create and manage projects and link
to the billing account.

```shell
# Enter your favorite factory
cd cloud-run-single

# Create the project, the SAs and grant permissions.
cd 0-projects
cp terraform.tfvars.sample terraform.tfvars # Replace prefix, billing account and parent.
terraform init
terraform apply

cd ..

# Deploy the platform services.
# If you ran the previous step, providers.tf and terraform.auto.tfvars will be there.
cd 1-apps
cp terraform.tfvars.sample terraform.tfvars # Customize.
terraform init
terraform apply

# Deploy the application, follow the commands in output.
```

## Factories Structure

Each factory contains two modules:

### 0-projects

It creates projects and service accounts, it enables APIs and grants IAM roles using [Fabric FAST project application templates](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/project-factory).

Running this module is optional. If you can create projects, use it. Alternatively, you can give the yaml project definitions to your platform team. They can use it with their [FAST project factory](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/fast/stages/2-project-factory) or easily derive the requirements and implement them with their own mechanism.

The module also creates in the same project components to allow the `1-apps` module to run. This includes Terraform service accounts, roles, state bucket. Finally, the module writes a `providers.tf` and a `terraform.auto.tfvars` files in the `1-apps` folder.

### 1-apps

It deploys the core platform resources inside the project and the AI application on top.

Running this module is required. Note the module expects projects, service accounts and roles created by `0-project`. If you don't run `0-projects` it's your responsibility to ensure these requirements are met.

## Projects Configuration

Factories allow you to create existing projects or leverage existing projects.

### Default: create and manage new projects

You can use the `0-projects` module within each factory to create projects and service accounts, activate APIs, grant IAM roles. By default, projects are named `{prefix}-{project_name}`.

- `prefix` is controlled through the variable `project_config.prefix`. It's set set to null by default and it can be customized in your `terraform.tfvars`.
- `suffix` is controlled in application templates (yaml files in the `data` subfolder) through the `name` property. This also generally corresponds to the default value of the variable `name`, used to name resources in the projects.

### Control existing projects

You may want to reuse existing projects but still configure them: activate services, create service accounts, set IAM roles. To do so:

- Add this configuration to your `0-projects` module `terraform.tfvars`:

```hcl
project_config = {
  billing_id = YOUR_BILLING_ID
  create     = false
}
```

- Configure the `name` property in the application templates to match your existing project ids.

### Create and control projects outside genai-factory

You can create and control projects outside genai-factory.
Genai-factory will only deploy resources and applications inside these projects.

To do so, make sure your `terraform.tfvars` contains this configuration:

```hcl
project_config = {
  control    = false
  create     = false
}
```

You'll need to configure your projects as expected by the `1-apps` module of each factory.
On the other hand, you will need to configure the `terraform.tfvars` of `1-apps` with all the values expected (by default automatically populated by `0-projects`).
If your platform team doesn't use [FAST project factory](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/fast/stages/2-project-factory), they can read requirements from the yaml files defining each project in the data folder under each `0-project module`.

# Networking Configuration

By default, `1-apps` modules create VPCs and other networking components if these are needed by the infrastructure and applications.
These include VPCs, subnets, routes, DNS zones, private Google access and more.

You also have the option to leverage existing VPCs. In this case it will be your responsibility to create everything is needed by the application to work.

To do so, make sure your `terraform.tfvars` in `1-apps` contains this configuration:

```hcl
networking_config = {
  create    = false
  subnet_id = "YOUR_SUBNET_ID"
  vpc_id    = "YOUR_VPC_ID"
}
```

## Credits

Thanks to the [Cloud Foundation Fabric](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric) community for ideas, inputs and useful tools.

## Contribute

Contributions are welcome! You can follow the guidelines in the [Contributing section](./CONTRIBUTING.md).
