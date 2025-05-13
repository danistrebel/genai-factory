# GenAI Factory

A collection of scripts to deploy AI infrastructures and applications in GCP, following security best-practices.

- Embraces IaC best practices. Infrastructure implemented in [Terraform](https://developer.hashicorp.com/terraform), leveraging [Terraform resources](https://registry.terraform.io/providers/hashicorp/google/latest/docs) and [Cloud Foundations Fabric modules](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules).
- Follows the least-privilege principle: no default service accounts, primitive roles, minimal permissions.
- Compatible with [Cloud Foundation Fabric FAST](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric) [project-factory](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/project-factory) and application templates.

## Applications

- [Single Cloud Run](./cloud-run-single/README.md) - A single, secure public Cloud Run behind an external application load balancer and interact with Gemini.
- [RAG with Cloud Run](./cloud-run-single/README.md) - A "Retrieval-Augmented Generation" (RAG) system, leveraging Cloud Run, Vertex AI, Cloud SQL and BigQuery.

## Quick Start

```shell
# Enter a module, for example cloud-run-single
cd cloud-run-single

# Make your own terraform.tfvars
cp terraform.tfvars.sample terraform.tfvars

# Initialize Terraform and deploy
terraform init
terraform apply

# Deploy the application: follow the commands in the output screen to deploy the application(s).
```

## Modules content

Each module contains:

- A `projects` folder with one or more (.yaml) [Fabric FAST project application templates](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/project-factory). By default, modules create new projects, activate GCP services and set IAM roles based on the content of these files. See other options in the [Projects Configuration section](#projects-configuration).
- One or more Terraform files that create infrastructure resources.
- An `apps` folder with sample generative AI applications.

## Projects Configuration

In each module, the `projects` folder contains one or more (.yaml) [Fabric FAST project application templates](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/project-factory).

### Default: create and manage new projects

By default, in each module application templates create projects, activate services, create service accounts and set IAM roles.
Projects are named `{prefix}-{project_name}`. `prefix` is controlled through the variable `project_config.prefix`. It's set set to null by default and it can be customized in your `terraform.tfvars`. `project_name` is controlled in application templates through the `name` property. This also generally corresponds to the default value of the variable `name`, used to name resources in the projects.

### Control existing projects

You may want to reuse existing projects but still configure them: activate services, create service accounts, set IAM roles. To do so:

- Add this configuration to your `terraform.tfvars`:

```hcl
project_config = {
  billing_id = YOUR_BILLING_ID
  create     = false
}
```

- Configure the `name` property in the application templates to match your existing project ids.

### Create and control projects outside genai-factory

You can also create and control projects outside genai-factory. For example, through [FAST project factory](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/fast/stages/2-project-factory) or your own way. Genai-factory will only deploy resources and applications inside these projects.

To do so, make sure your `terraform.tfvars` contains this configuration:

```hcl
project_config = {
  control    = false
  create     = false
}
```

You'll need to configure your projects as expected by each module. Application templates are quite self-explanatory, as they list the requirements for each project. Alternatively, you can application templates directly into [FAST project factory](https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/fast/stages/2-project-factory).

# Networking Configuration

By default, modules create VPCs and other networking components if these are needed by their infrastructure and applications.
These include subnets, routes, DNS zones, private Google access and more.

You also have the option to leverage existing VPCs. To do so, make sure your `terraform.tfvars` contains this configuration:

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
