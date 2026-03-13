Title: Install and configure the CircleCI local CLI

URL Source: https://circleci.com/docs/guides/toolkit/local-cli/

Markdown Content:
Install and configure the CircleCI local CLI - CircleCI Docs
===============

[![Image 1: CircleCI Logo](https://circleci.com/docs/_/img/logo.svg)![Image 2: CircleCI Logo](https://circleci.com/docs/_/img/logo-dark.svg)](https://circleci.com/docs/)

 Clear 

Light

Dark

Auto

[Go to Application](https://app.circleci.com/)

*   [Home](https://circleci.com/docs/)
*   [Guides](https://circleci.com/docs/guides/getting-started/first-steps/)
*   [Reference](https://circleci.com/docs/reference/configuration-reference/)
*   [Server](https://circleci.com/docs/server-admin/latest/overview/circleci-server-overview/)
*   [Orbs](https://circleci.com/docs/orbs/use/orb-intro/)
*   [Services](https://circleci.com/docs/services/services-overview/)
*   [Contributors](https://circleci.com/docs/contributors/docs-style/)

*   [Dev Hub](https://circleci.com/developer/)![Image 3: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [API](https://circleci.com/docs/reference/api-homepage/)![Image 4: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [Support](https://support.circleci.com/hc/en-us/)![Image 5: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [Discuss](https://discuss.circleci.com/)![Image 6: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [CircleCI.com](https://circleci.com/)![Image 7: Go to](https://circleci.com/docs/_/img/link-arrow.svg)

[path]
------

[numberOfHits]

1 2...12

![Image 8: Arrow Back](https://circleci.com/docs/_/img/arrow-back.svg)
### Guides

 Clear 

[path]
------

[numberOfHits]

1 2...12

*   [Home](https://circleci.com/docs/)
*   [Guides](https://circleci.com/docs/guides/getting-started/first-steps/)
*   [Reference](https://circleci.com/docs/reference/configuration-reference/)
*   [Server](https://circleci.com/docs/server-admin/latest/overview/circleci-server-overview/)
*   [Orbs](https://circleci.com/docs/orbs/use/orb-intro/)
*   [Services](https://circleci.com/docs/services/services-overview/)
*   [Contributors](https://circleci.com/docs/contributors/docs-style/)

*   [Dev Hub](https://circleci.com/developer/)![Image 9: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [API](https://circleci.com/docs/reference/api-homepage/)![Image 10: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [Support](https://support.circleci.com/hc/en-us/)![Image 11: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [Discuss](https://discuss.circleci.com/)![Image 12: Go to](https://circleci.com/docs/_/img/link-arrow.svg)
*   [CircleCI.com](https://circleci.com/)![Image 13: Go to](https://circleci.com/docs/_/img/link-arrow.svg)

*       *   About CircleCI 
    *           *   [CircleCI overview](https://circleci.com/docs/guides/about-circleci/about-circleci/) 

        *   [Benefits of CircleCI](https://circleci.com/docs/guides/about-circleci/benefits-of-circleci/) 

        *   [Concepts](https://circleci.com/docs/guides/about-circleci/concepts/) 

        *   [Intro to the CircleCI web app](https://circleci.com/docs/guides/about-circleci/introduction-to-the-circleci-web-app/) 

        *   [Open source acknowledgements](https://circleci.com/docs/guides/about-circleci/open-source/) 

    *   Getting started 
    *           *   First steps 
        *               *   [Sign up and try CircleCI](https://circleci.com/docs/guides/getting-started/first-steps/) 

            *   [Join teammates on CircleCI](https://circleci.com/docs/guides/getting-started/invite-your-team/) 

            *   [Create a project](https://circleci.com/docs/guides/getting-started/create-project/) 

            *   [Quickstart guide](https://circleci.com/docs/guides/getting-started/getting-started/) 

        *   How-to guides 
        *               *   [Hello World](https://circleci.com/docs/guides/getting-started/hello-world/) 

            *   [Intro to YAML configuration](https://circleci.com/docs/guides/getting-started/introduction-to-yaml-configurations/) 

            *   [In-app config editor](https://circleci.com/docs/guides/getting-started/config-editor/) 

            *   [Node.js quickstart](https://circleci.com/docs/guides/getting-started/language-javascript/) 

            *   [Python quickstart](https://circleci.com/docs/guides/getting-started/language-python/) 

            *   [Go quickstart](https://circleci.com/docs/guides/getting-started/language-go/) 

            *   [Create an organization](https://circleci.com/docs/guides/getting-started/create-an-organization/) 

        *   Tutorials 
        *               *   [Configuration intro](https://circleci.com/docs/guides/getting-started/config-intro/) 

            *   [Use the Slack orb to set up notifications](https://circleci.com/docs/guides/getting-started/slack-orb-tutorial/) 

    *   Migrate to CircleCI 
    *           *   [Migration intro](https://circleci.com/docs/guides/migrate/migration-intro/) 

        *   [Migrate from AWS](https://circleci.com/docs/guides/migrate/migrating-from-aws/) 

        *   [Migrate from Azure DevOps](https://circleci.com/docs/guides/migrate/migrating-from-azuredevops/) 

        *   [Migrate from Buildkite](https://circleci.com/docs/guides/migrate/migrating-from-buildkite/) 

        *   [Migrate from GitHub](https://circleci.com/docs/guides/migrate/migrating-from-github/) 

        *   [Migrate from GitLab](https://circleci.com/docs/guides/migrate/migrating-from-gitlab/) 

        *   [Migrate from Jenkins](https://circleci.com/docs/guides/migrate/migrating-from-jenkins/) 

        *   [Migrate from TeamCity](https://circleci.com/docs/guides/migrate/migrating-from-teamcity/) 

        *   [Migrate from Travis CI](https://circleci.com/docs/guides/migrate/migrating-from-travis/) 

    *   Orchestrate 
    *           *   Pipelines 
        *               *   [Pipeline overview and setup](https://circleci.com/docs/guides/orchestrate/pipelines/) 

            *   [Jobs and steps overview](https://circleci.com/docs/guides/orchestrate/jobs-steps/) 

            *   [Workflow orchestration](https://circleci.com/docs/guides/orchestrate/workflows/) 

            *   [Automatic reruns](https://circleci.com/docs/guides/orchestrate/automatic-reruns/) 

            *   [Use workspaces to share data between jobs](https://circleci.com/docs/guides/orchestrate/workspaces/) 

            *   [Use dynamic configuration](https://circleci.com/docs/guides/orchestrate/dynamic-config/) 

            *   [Skip CI, auto-cancel, and block new pipelines](https://circleci.com/docs/guides/orchestrate/skip-build/) 

            *   [Controlling serial execution across your organization](https://circleci.com/docs/guides/orchestrate/controlling-serial-execution-across-your-organization/) 

            *   [Pipeline values and parameters](https://circleci.com/docs/guides/orchestrate/pipeline-variables/) 

        *   Triggers 
        *               *   [Trigger options](https://circleci.com/docs/guides/orchestrate/triggers-overview/) 

            *   [Set up triggers](https://circleci.com/docs/guides/orchestrate/set-up-triggers/) 

            *   [GitHub trigger event options](https://circleci.com/docs/guides/orchestrate/github-trigger-event-options/) 

            *   [GitLab trigger options](https://circleci.com/docs/guides/orchestrate/gitlab-trigger-options/) 

            *   [Custom webhooks](https://circleci.com/docs/guides/orchestrate/custom-webhooks/) 

            *   [Schedule triggers](https://circleci.com/docs/guides/orchestrate/schedule-triggers/) 

        *   How-to guides 
        *               *   [Orchestration cookbook](https://circleci.com/docs/guides/orchestrate/orchestration-cookbook/) 

            *   [How to override config](https://circleci.com/docs/guides/orchestrate/how-to-override-config/) 

            *   [Set up multiple configuration files for a project](https://circleci.com/docs/guides/orchestrate/set-up-multiple-configuration-files-for-a-project/) 

            *   [Notify a Slack channel of a paused workflow](https://circleci.com/docs/guides/orchestrate/notify-a-slack-channel-of-a-paused-workflow/) 

            *   [Using branch filters](https://circleci.com/docs/guides/orchestrate/using-branch-filters/) 

            *   [Select a workflow to run using pipeline parameters](https://circleci.com/docs/guides/orchestrate/selecting-a-workflow-to-run-using-pipeline-parameters/) 

            *   [Migrate scheduled workflows to schedule triggers](https://circleci.com/docs/guides/orchestrate/migrate-scheduled-workflows-to-schedule-triggers/) 

            *   [Schedule triggers with multiple workflows](https://circleci.com/docs/guides/orchestrate/schedule-triggers-with-multiple-workflows/) 

            *   [Set a nightly schedule trigger](https://circleci.com/docs/guides/orchestrate/set-a-nightly-schedule-trigger/) 

            *   [Using dynamic configuration](https://circleci.com/docs/guides/orchestrate/using-dynamic-configuration/) 

            *   [Configure databases](https://circleci.com/docs/guides/orchestrate/databases/) 

            *   [Migrate from deploy to run](https://circleci.com/docs/guides/orchestrate/migrate-from-deploy-to-run/) 

            *   [Using shell scripts](https://circleci.com/docs/guides/orchestrate/using-shell-scripts/) 

    *   Execute on managed compute 
    *           *   [Execution environments overview](https://circleci.com/docs/guides/execution-managed/executor-intro/) 

        *   [Resource class overview](https://circleci.com/docs/guides/execution-managed/resource-class-overview/) 

        *   [Resource class lifecycle](https://circleci.com/docs/guides/execution-managed/resource-class-lifecycle/) 

        *   Docker 
        *               *   [Using Docker](https://circleci.com/docs/guides/execution-managed/using-docker/) 

            *   [Convenience images](https://circleci.com/docs/guides/execution-managed/circleci-images/) 

            *   [Migrating to next-gen images](https://circleci.com/docs/guides/execution-managed/next-gen-migration-guide/) 

            *   [Using custom-built Docker images](https://circleci.com/docs/guides/execution-managed/custom-images/) 

            *   [Docker authenticated pulls](https://circleci.com/docs/guides/execution-managed/private-images/) 

            *   [Running Docker commands](https://circleci.com/docs/guides/execution-managed/building-docker-images/) 

        *   Linux VM 
        *               *   [Using the Linux VM execution environment](https://circleci.com/docs/guides/execution-managed/using-linuxvm/) 

            *   [Using Android images with the machine executor](https://circleci.com/docs/guides/execution-managed/android-machine-image/) 

        *   macOS 
        *               *   [Using the macOS execution environment](https://circleci.com/docs/guides/execution-managed/using-macos/) 

            *   [Configuring a macOS app](https://circleci.com/docs/guides/execution-managed/hello-world-macos/) 

            *   [iOS code signing](https://circleci.com/docs/guides/execution-managed/ios-codesigning/) 

        *   Windows 
        *               *   [Using the Windows execution environment](https://circleci.com/docs/guides/execution-managed/using-windows/) 

            *   [Hello world Windows](https://circleci.com/docs/guides/execution-managed/hello-world-windows/) 

        *   Arm 
        *               *   [Using the Arm VM execution environment](https://circleci.com/docs/guides/execution-managed/using-arm/) 

        *   GPU 
        *               *   [Using the GPU execution environment](https://circleci.com/docs/guides/execution-managed/using-gpu/) 

        *   How-to guides 
        *               *   [Pull an image from AWS ECR with OIDC](https://circleci.com/docs/guides/permissions-authentication/pull-an-image-from-aws-ecr-with-oidc/) 

            *   [Pull an image from GCP Artifact Registry with OIDC](https://circleci.com/docs/guides/permissions-authentication/pull-an-image-from-gcp-gar-with-oidc/) 

            *   [Run a job in a container on your machine with Docker](https://circleci.com/docs/guides/execution-managed/run-a-job-in-a-container/) 

            *   [Installing and using Docker Compose](https://circleci.com/docs/guides/execution-managed/docker-compose/) 

            *   [Debugging container ID cannot be mapped to host ID error](https://circleci.com/docs/guides/execution-managed/high-uid-error/) 

            *   [Migrating between the Docker machine executors](https://circleci.com/docs/guides/execution-managed/docker-to-machine/) 

        *   Image support policies 
        *               *   [Android images support policy](https://circleci.com/docs/guides/execution-managed/android-images-support-policy/) 

            *   [Convenience images support policy](https://circleci.com/docs/guides/execution-managed/convenience-images-support-policy/) 

            *   [Linux VM images support policy](https://circleci.com/docs/guides/execution-managed/linux-vm-support-policy/) 

            *   [Linux CUDA images support policy](https://circleci.com/docs/guides/execution-managed/linux-cuda-images-support-policy/) 

            *   [Remote Docker images support policy](https://circleci.com/docs/guides/execution-managed/remote-docker-images-support-policy/) 

            *   [Windows images support policy](https://circleci.com/docs/guides/execution-managed/windows-images-support-policy/) 

            *   [Xcode image policy](https://circleci.com/docs/guides/execution-managed/xcode-policy/) 

            *   [CircleCI image lifecycle: A complete guide](https://circleci.com/docs/guides/execution-managed/machine-convenience-image-lifecycle/) 

    *   Execute jobs on self-hosted runners 
    *           *   [Self-hosted runner overview](https://circleci.com/docs/guides/execution-runner/runner-overview/) 

        *   [Self-hosted runner concepts](https://circleci.com/docs/guides/execution-runner/runner-concepts/) 

        *   [Runner feature comparison matrix](https://circleci.com/docs/guides/execution-runner/runner-feature-comparison-matrix/) 

        *   Container runner 
        *               *   [Container runner installation](https://circleci.com/docs/guides/execution-runner/container-runner-installation/) 

            *   [Container runner performance benchmarks](https://circleci.com/docs/guides/execution-runner/container-runner-performance-benchmarks/) 

            *   [Container runner reference](https://circleci.com/docs/guides/execution-runner/container-runner/) 

        *   Machine runner 3 
        *               *   [Install machine runner 3 on Linux](https://circleci.com/docs/guides/execution-runner/install-machine-runner-3-on-linux/) 

            *   [Install machine runner 3 on macOS](https://circleci.com/docs/guides/execution-runner/install-machine-runner-3-on-macos/) 

            *   [Install machine runner 3 on Windows](https://circleci.com/docs/guides/execution-runner/install-machine-runner-3-on-windows/) 

            *   [Install machine runner 3 on Docker](https://circleci.com/docs/guides/execution-runner/install-machine-runner-3-on-docker/) 

            *   [Manual install on Linux and macOS](https://circleci.com/docs/guides/execution-runner/machine-runner-3-manual-installation/) 

            *   [Manual install on Windows](https://circleci.com/docs/guides/execution-runner/machine-runner-3-manual-installation-on-windows/) 

            *   [Migrate from launch agent to machine runner 3 on Linux](https://circleci.com/docs/guides/execution-runner/migrate-from-launch-agent-to-machine-runner-3-on-linux/) 

            *   [Migrate from launch agent to machine runner 3 on macOS](https://circleci.com/docs/guides/execution-runner/migrate-from-launch-agent-to-machine-runner-3-on-macos/) 

            *   [Migrate from launch agent to machine runner 3 on Windows](https://circleci.com/docs/guides/execution-runner/migrate-from-launch-agent-to-machine-runner-3-on-windows/) 

            *   [Machine runner 3 configuration reference](https://circleci.com/docs/guides/execution-runner/machine-runner-3-configuration-reference/) 

        *   Self-hosted runner reference 
        *               *   [Self-hosted runner API](https://circleci.com/docs/guides/execution-runner/runner-api/) 

            *   [Self-hosted runner FAQ](https://circleci.com/docs/guides/execution-runner/runner-faqs/) 

            *   [Troubleshoot self-hosted runner](https://circleci.com/docs/guides/execution-runner/troubleshoot-self-hosted-runner/) 

            *   [Scaling self-hosted runner](https://circleci.com/docs/guides/execution-runner/runner-scaling/) 

    *   Testing on CircleCI 
    *           *   Run tests on CircleCI 
        *               *   [Automated testing](https://circleci.com/docs/guides/test/test/) 

            *   [Collecting test data](https://circleci.com/docs/guides/test/collect-test-data/) 

            *   [Test Insights](https://circleci.com/docs/guides/insights/insights-tests/) 

        *   Manage and optimize tests 
        *               *   [Fix flaky tests](https://circleci.com/docs/guides/test/fix-flaky-tests/) 

        *   Testing strategies 
        *               *   [Testing LLM-enabled applications through evaluations](https://circleci.com/docs/guides/test/testing-llm-enabled-applications-through-evaluations/) 

            *   [Browser testing](https://circleci.com/docs/guides/test/browser-testing/) 

            *   [Generate code coverage metrics](https://circleci.com/docs/guides/test/code-coverage/) 

            *   [Re-run failed tests overview](https://circleci.com/docs/guides/test/rerun-failed-tests/) 

            *   [Test splitting and parallelism](https://circleci.com/docs/guides/optimize/parallelism-faster-jobs/) 

        *   Tutorials 
        *               *   [Speed up pipelines with test splitting](https://circleci.com/docs/guides/test/test-splitting-tutorial/) 

            *   [Testing iOS applications](https://circleci.com/docs/guides/test/testing-ios/) 

            *   [Testing macOS applications](https://circleci.com/docs/guides/test/testing-macos/) 

        *   How-to guides 
        *               *   [Use the environment CLI to split tests](https://circleci.com/docs/guides/optimize/use-the-circleci-cli-to-split-tests/) 

            *   [Automate LLM evaluation testing with the CircleCI Evals orb](https://circleci.com/docs/guides/test/automate-llm-evaluation-testing-with-the-circleci-evals-orb/) 

        *   Reference 
        *               *   [Troubleshoot test splitting](https://circleci.com/docs/guides/test/troubleshoot-test-splitting/) 

    *   Deploy with CircleCI 
    *           *   [Deployment and deploy management](https://circleci.com/docs/guides/deploy/deployment-overview/) 

        *   Deploys and rollbacks 
        *               *   [Set up a rollback pipeline](https://circleci.com/docs/guides/deploy/set-up-rollbacks/) 

            *   [Set up a deploy pipeline](https://circleci.com/docs/guides/deploy/set-up-deploys/) 

            *   [Deploy a component](https://circleci.com/docs/guides/deploy/deploy-a-component/) 

            *   [Rollback a deployment](https://circleci.com/docs/guides/deploy/rollback-a-deployment/) 

            *   [Configure deploy markers](https://circleci.com/docs/guides/deploy/configure-deploy-markers/) 

        *   Release agent setup 
        *               *   [Release agent overview](https://circleci.com/docs/guides/deploy/release-agent-overview/) 

            *   [Set up the CircleCI release agent](https://circleci.com/docs/guides/deploy/set-up-the-circleci-release-agent/) 

            *   [Configure your Kubernetes components](https://circleci.com/docs/guides/deploy/configure-your-kubernetes-components/) 

            *   [Update the Kubernetes release agent](https://circleci.com/docs/guides/deploy/update-the-kubernetes-release-agent/) 

            *   [Manage releases](https://circleci.com/docs/guides/deploy/manage-releases/) 

        *   How-to guides 
        *               *   [Deploy Android applications](https://circleci.com/docs/guides/deploy/deploy-android-applications/) 

            *   [Deploy to Artifactory](https://circleci.com/docs/guides/deploy/deploy-to-artifactory/) 

            *   [Deploy to AWS](https://circleci.com/docs/guides/deploy/deploy-to-aws/) 

            *   [Push image to ECR and deploy to ECS](https://circleci.com/docs/guides/deploy/ecs-ecr/) 

            *   [Deploy service update to AWS ECS](https://circleci.com/docs/guides/deploy/deploy-service-update-to-aws-ecs/) 

            *   [Deploy to Azure Container Registry](https://circleci.com/docs/guides/deploy/deploy-to-azure-container-registry/) 

            *   [Deploy to Capistrano](https://circleci.com/docs/guides/deploy/deploy-to-capistrano/) 

            *   [Deploy to Cloud Foundry](https://circleci.com/docs/guides/deploy/deploy-to-cloud-foundry/) 

            *   [Deploy to Firebase](https://circleci.com/docs/guides/deploy/deploy-to-firebase/) 

            *   [Deploy to Google Cloud Platform](https://circleci.com/docs/guides/deploy/deploy-to-google-cloud-platform/) 

            *   [Deploy to Heroku](https://circleci.com/docs/guides/deploy/deploy-to-heroku/) 

            *   [Deploy iOS applications](https://circleci.com/docs/guides/deploy/deploy-ios-applications/) 

            *   [Deploy over SSH](https://circleci.com/docs/guides/deploy/deploy-over-ssh/) 

            *   [Publish packages to Packagecloud](https://circleci.com/docs/guides/deploy/publish-packages-to-packagecloud/) 

            *   [Deploy to npm registry](https://circleci.com/docs/guides/deploy/deploy-to-npm-registry/) 

    *   Optimize 
    *           *   [Optimizations reference](https://circleci.com/docs/guides/optimize/optimizations/) 

        *   Data 
        *               *   [Persisting data overview](https://circleci.com/docs/guides/optimize/persist-data/) 

            *   [Caching dependencies](https://circleci.com/docs/guides/optimize/caching/) 

            *   [Caching strategies](https://circleci.com/docs/guides/optimize/caching-strategy/) 

            *   [Store build artifacts](https://circleci.com/docs/guides/optimize/artifacts/) 

        *   Speed 
        *               *   [Concurrency](https://circleci.com/docs/guides/optimize/concurrency/) 

            *   [Test splitting and parallelism](https://circleci.com/docs/guides/optimize/parallelism-faster-jobs/) 

            *   [Docker layer caching overview](https://circleci.com/docs/guides/optimize/docker-layer-caching/) 

        *   Config 
        *               *   [Dynamic configuration](https://circleci.com/docs/guides/orchestrate/dynamic-config/) 

        *   Tutorials 
        *               *   [Speed up pipelines with test splitting](https://circleci.com/docs/guides/test/test-splitting-tutorial/) 

        *   How-to guides 
        *               *   [Use matrix jobs](https://circleci.com/docs/guides/orchestrate/using-matrix-jobs/) 

            *   [Using dynamic configuration](https://circleci.com/docs/guides/orchestrate/using-dynamic-configuration/) 

            *   [Avoid and debug Java memory errors](https://circleci.com/docs/guides/optimize/java-oom/) 

    *   Insights 
    *           *   [Use Insights](https://circleci.com/docs/guides/insights/insights/) 

        *   [Test Insights](https://circleci.com/docs/guides/insights/insights-tests/) 

        *   [Generate an Insights snapshot badge](https://circleci.com/docs/guides/insights/insights-snapshot-badge/) 

        *   [Insights glossary](https://circleci.com/docs/guides/insights/insights-glossary/) 

    *   Manage roles, permissions, and authentication 
    *           *   [Users, organizations, and integrations guide](https://circleci.com/docs/guides/permissions-authentication/users-organizations-and-integrations-guide/) 

        *   Roles and permissions 
        *               *   [Roles and permissions overview](https://circleci.com/docs/guides/permissions-authentication/roles-and-permissions-overview/) 

            *   [Manage roles and permissions](https://circleci.com/docs/guides/permissions-authentication/manage-roles-and-permissions/) 

            *   [Manage groups](https://circleci.com/docs/guides/permissions-authentication/manage-groups/) 

            *   [Prevent unregistered users from spending credits](https://circleci.com/docs/guides/plans-pricing/prevent-unregistered-users-from-spending-credits/) 

        *   SSO authentication 
        *               *   [SSO overview](https://circleci.com/docs/guides/permissions-authentication/sso-overview/) 

            *   [SSO setup](https://circleci.com/docs/guides/permissions-authentication/set-up-sso/) 

            *   [Set up SSO group mapping with Okta](https://circleci.com/docs/guides/permissions-authentication/sso-group-mapping/) 

            *   [Sign in to an SSO-enabled org](https://circleci.com/docs/guides/permissions-authentication/sign-in-to-an-sso-enabled-organization/) 

        *   Multi-factor authentication (MFA) 
        *               *   [MFA overview](https://circleci.com/docs/guides/permissions-authentication/mfa/) 

        *   OIDC tokens 
        *               *   [Use OpenID Connect tokens in jobs](https://circleci.com/docs/guides/permissions-authentication/openid-connect-tokens/) 

            *   [OIDC tokens with custom claims](https://circleci.com/docs/guides/permissions-authentication/oidc-tokens-with-custom-claims/) 

    *   Manage security and secrets 
    *           *   Security features 
        *               *   [How CircleCI handles security](https://circleci.com/docs/guides/security/security/) 

            *   [Intro to environment variables](https://circleci.com/docs/guides/security/env-vars/) 

            *   [Using contexts](https://circleci.com/docs/guides/security/contexts/) 

            *   [IP ranges](https://circleci.com/docs/guides/security/ip-ranges/) 

            *   [Audit logs](https://circleci.com/docs/guides/security/audit-logs/) 

        *   Security recommendations 
        *               *   [Security overview](https://circleci.com/docs/guides/security/security-overview/) 

            *   [Protecting against supply chain attacks](https://circleci.com/docs/guides/security/security-supply-chain/) 

            *   [Secure secrets handling](https://circleci.com/docs/guides/security/security-recommendations/) 

        *   How-to guides 
        *               *   [Set an environment variable](https://circleci.com/docs/guides/security/set-environment-variable/) 

            *   [Inject environment variables with the API](https://circleci.com/docs/guides/security/inject-environment-variables-with-api/) 

            *   [Debug with SSH](https://circleci.com/docs/guides/execution-managed/ssh-access-jobs/) 

            *   [Rotate project SSH keys](https://circleci.com/docs/guides/security/rotate-project-ssh-keys/) 

            *   [Stop building a project on CircleCI](https://circleci.com/docs/guides/security/stop-building-a-project-on-circleci/) 

            *   [Rename organizations and repositories](https://circleci.com/docs/guides/security/rename-organizations-and-repositories/) 

            *   [Delete organizations and projects](https://circleci.com/docs/guides/security/delete-organizations-and-projects/) 

    *   Manage config policies 
    *           *   [Config policy management overview](https://circleci.com/docs/guides/config-policies/config-policy-management-overview/) 

        *   [Config policy reference](https://circleci.com/docs/guides/config-policies/config-policy-reference/) 

        *   How-to guides 
        *               *   [Create and manage config policies](https://circleci.com/docs/guides/config-policies/create-and-manage-config-policies/) 

            *   [Test config policies](https://circleci.com/docs/guides/config-policies/test-config-policies/) 

            *   [Use the CLI for config and policy development](https://circleci.com/docs/guides/config-policies/use-the-cli-for-config-and-policy-development/) 

            *   [Config policies for self-hosted runner](https://circleci.com/docs/guides/config-policies/config-policies-for-self-hosted-runner/) 

            *   [Manage contexts with config policies](https://circleci.com/docs/guides/config-policies/manage-contexts-with-config-policies/) 

    *   Integration 
    *           *   Integration features 
        *               *   [Outbound webhooks](https://circleci.com/docs/guides/integration/outbound-webhooks/) 

            *   [Outbound webhooks reference](https://circleci.com/docs/reference/outbound-webhooks-reference/) 

            *   [Notifications](https://circleci.com/docs/guides/integration/notifications/) 

        *   VCS integration 
        *               *   [VCS, pipeline types, and feature support](https://circleci.com/docs/guides/integration/version-control-system-integration-overview/) 

            *   [Using the CircleCI GitHub App in an OAuth org](https://circleci.com/docs/guides/integration/using-the-circleci-github-app-in-an-oauth-org/) 

            *   [Build open source projects](https://circleci.com/docs/guides/integration/oss/) 

        *   Third-party integrations 
        *               *   [Enable GitHub Checks](https://circleci.com/docs/guides/integration/enable-checks/) 

            *   [Connect with Jira](https://circleci.com/docs/guides/integration/jira-plugin/) 

            *   [New Relic integration](https://circleci.com/docs/guides/integration/new-relic-integration/) 

            *   [Datadog integration](https://circleci.com/docs/guides/integration/datadog-integration/) 

            *   [Sumo Logic integration](https://circleci.com/docs/guides/integration/sumo-logic-integration/) 

        *   How-to guides 
        *               *   [Adding status badges](https://circleci.com/docs/guides/integration/status-badges/) 

            *   [CircleCI webhooks with Airtable](https://circleci.com/docs/guides/integration/webhooks-airtable/) 

            *   [Add additional SSH keys](https://circleci.com/docs/guides/integration/add-ssh-key/) 

            *   [Authorize Google Cloud SDK](https://circleci.com/docs/guides/integration/authorize-google-cloud-sdk/) 

    *   Developer toolkit 
    *           *   [How to find IDs](https://circleci.com/docs/guides/toolkit/how-to-find-ids/) 

        *   AI features 
        *               *   [Chunk Setup and Overview](https://circleci.com/docs/guides/toolkit/chunk-setup-and-overview/) 

            *   [Using the CircleCI MCP server](https://circleci.com/docs/guides/toolkit/using-the-circleci-mcp-server/) 

            *   [Intelligent summaries](https://circleci.com/docs/guides/toolkit/intelligent-summaries/) 

        *   CLI 
        *               *   [CircleCI environment CLI usage guide](https://circleci.com/docs/guides/toolkit/environment-cli-usage-guide/) 

            *   Install and configure the CircleCI local CLI 

            *   [How to use the CircleCI local CLI](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/) 

        *   APIs 
        *               *   [API v2 intro](https://circleci.com/docs/guides/toolkit/api-intro/) 

            *   [API v2 developers guide](https://circleci.com/docs/guides/toolkit/api-developers-guide/) 

            *   [Managing API tokens](https://circleci.com/docs/guides/toolkit/managing-api-tokens/) 

        *   IDE tools 
        *               *   [VS Code extension overview](https://circleci.com/docs/guides/toolkit/vs-code-extension-overview/) 

            *   [Get started with the VS Code extension](https://circleci.com/docs/guides/toolkit/get-started-with-the-vs-code-extension/) 

        *   Config tools 
        *               *   [Config SDK](https://circleci.com/docs/guides/toolkit/circleci-config-sdk/) 

            *   [Orb development kit](https://circleci.com/docs/orbs/author/orb-author/) 

            *   [Image Updater](https://circleci.com/docs/guides/toolkit/circleci-image-updater/) 

        *   Example projects and configs 
        *               *   [Examples and guides overview](https://circleci.com/docs/guides/toolkit/examples-and-guides-overview/) 

            *   [Sample config.yml files](https://circleci.com/docs/guides/toolkit/sample-config/) 

            *   [Database examples](https://circleci.com/docs/guides/toolkit/postgres-config/) 

    *   Plans and pricing 
    *           *   [CircleCI plans overview](https://circleci.com/docs/guides/plans-pricing/plan-overview/) 

        *   [Credits overview](https://circleci.com/docs/guides/plans-pricing/credits/) 

        *   [Manage budgets](https://circleci.com/docs/guides/plans-pricing/manage-budgets/) 

        *   [Free Plan overview](https://circleci.com/docs/guides/plans-pricing/plan-free/) 

        *   [Performance Plan overview](https://circleci.com/docs/guides/plans-pricing/plan-performance/) 

        *   [Scale Plan overview](https://circleci.com/docs/guides/plans-pricing/plan-scale/) 

        *   [Server Plan overview](https://circleci.com/docs/guides/plans-pricing/plan-server/) 

[Go to Application](https://app.circleci.com/)

Guides![Image 14: Toggle](https://circleci.com/docs/_/img/arrow-down.svg)
*   [Home](https://circleci.com/docs/)
*   [Guides](https://circleci.com/docs/guides/getting-started/first-steps/)
*   [Reference](https://circleci.com/docs/reference/configuration-reference/)
*   [Server](https://circleci.com/docs/server-admin/latest/overview/circleci-server-overview/)
*   [Orbs](https://circleci.com/docs/orbs/use/orb-intro/)
*   [Services](https://circleci.com/docs/services/services-overview/)
*   [Contributors](https://circleci.com/docs/contributors/docs-style/)

*   [Home](https://circleci.com/docs/)
*   [Guides](https://circleci.com/docs/guides/getting-started/first-steps/)
*   Developer toolkit
*   CLI

Install and configure the CircleCI local CLI
============================================

[7 days ago](https://github.com/circleci/circleci-docs/commit/e1fa9113d2ac28b12272ff30323754a04cc32737)

Cloud Server v4+

Markdown
*   [View markdown](https://circleci.com/docs/guides/toolkit/local-cli/index.md)
*    Copy markdown 

### On This Page

*   [The CircleCI CLI and the task runner](https://circleci.com/docs/guides/toolkit/local-cli/#the-circleci-cli-and-the-task-runner)
*   [Installation](https://circleci.com/docs/guides/toolkit/local-cli/#installation)
*   [Linux install with Snap](https://circleci.com/docs/guides/toolkit/local-cli/#linux-install-with-snap)
*   [macOS install with Homebrew](https://circleci.com/docs/guides/toolkit/local-cli/#macos-install-with-homebrew)
*   [Windows install with Chocolatey](https://circleci.com/docs/guides/toolkit/local-cli/#windows-install-with-chocolatey)
*   [Alternative installation method](https://circleci.com/docs/guides/toolkit/local-cli/#alternative-installation-method)
*   [Manual install](https://circleci.com/docs/guides/toolkit/local-cli/#manual-download)
*   [Updating the CLI](https://circleci.com/docs/guides/toolkit/local-cli/#updating-the-cli)
*   [Updating the legacy CLI](https://circleci.com/docs/guides/toolkit/local-cli/#updating-the-legacy-cli)
*   [Configure the CLI](https://circleci.com/docs/guides/toolkit/local-cli/#configure-the-cli)
*   [Telemetry](https://circleci.com/docs/guides/toolkit/local-cli/#telemetry)
*   [Uninstall](https://circleci.com/docs/guides/toolkit/local-cli/#uninstallation)
*   [Next steps](https://circleci.com/docs/guides/toolkit/local-cli/#next-steps)
*   [CLI articles in the support centre](https://circleci.com/docs/guides/toolkit/local-cli/#useful-links)
*   [Troubleshooting](https://circleci.com/docs/guides/toolkit/local-cli/#troubleshooting)

The [CircleCI local command line interface (CLI)](https://circleci-public.github.io/circleci-cli/) brings CircleCI’s advanced and powerful tools to your terminal.

Some of the things you can do with the CLI include:

*   [Debug and validate your CircleCI configuration](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#validate-a-circleci-config)

*   [Run jobs locally](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#run-a-job-in-a-container-on-your-machine)

*   Query CircleCI’s API

*   [Create, publish, view, and manage orbs](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#orb-development-kit)

*   [Manage contexts](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#context-management)

This page covers the installation and usage of the CircleCI local CLI. The expectation is you have basic knowledge of CI/CD and [CircleCI’s concepts](https://circleci.com/docs/guides/about-circleci/concepts/). You should already have a CircleCI account, an account with a supported VCS.

[](https://circleci.com/docs/guides/toolkit/local-cli/#the-circleci-cli-and-the-task-runner)The CircleCI CLI and the task runner
--------------------------------------------------------------------------------------------------------------------------------

The CircleCI local CLI
The development tool used on your local machine for day-to-day development tasks. It handles testing and local workflow management.

CircleCI environment CLI
A specialized command-line interface that retrieves and configures a task. It manages the execution of the job within a chosen compute environment.

Both tools may share some conceptual similarities. However, they serve different purposes and operate in different contexts with different capabilities and permissions.

[](https://circleci.com/docs/guides/toolkit/local-cli/#installation)Installation
--------------------------------------------------------------------------------

Install the CircleCI CLI using one of the methods described below.

If you have previously installed CLI prior to October 2018, you may need to do an extra one-time step to switch to the new CLI. See the [upgrade instructions](https://circleci.com/docs/guides/toolkit/local-cli/#updating-the-legacy-cli).

For the majority of installations, we recommend one of the package managers outlined in the sections below to install the CircleCI CLI.

### [](https://circleci.com/docs/guides/toolkit/local-cli/#linux-install-with-snap)Linux install with Snap

The following commands will install the CircleCI CLI, Docker, and both the security and auto-update features that come along with [Snap packages](https://snapcraft.io/).

```
sudo snap install docker circleci
sudo snap connect circleci:docker docker
```

shell

With snap packages, the Docker command will use the Docker snap, not a version of Docker you may have previously installed. For security purposes, snap packages can only read/write files from within `$HOME`.

### [](https://circleci.com/docs/guides/toolkit/local-cli/#macos-install-with-homebrew)macOS install with Homebrew

If you are using [Homebrew](https://brew.sh/) with macOS, you can install the CLI with the following command:

`brew install circleci`

shell

If you already have Docker for Mac installed, you can use this command instead:

`brew install --ignore-dependencies circleci`

shell

### [](https://circleci.com/docs/guides/toolkit/local-cli/#windows-install-with-chocolatey)Windows install with Chocolatey

For Windows users, CircleCI provides a [Chocolatey](https://chocolatey.org/) package:

`choco install circleci-cli -y`

shell

### [](https://circleci.com/docs/guides/toolkit/local-cli/#alternative-installation-method)Alternative installation method

**Mac and Linux:**

`curl -fLSs https://raw.githubusercontent.com/CircleCI-Public/circleci-cli/main/install.sh | bash`

shell

By default, the CircleCI CLI tool will be installed to the `/usr/local/bin` directory. If you do not have write permissions to `/usr/local/bin`, you may need to run the above command with `sudo` after the pipe and before `bash`:

`curl -fLSs https://raw.githubusercontent.com/CircleCI-Public/circleci-cli/main/install.sh | sudo bash`

shell

You can also install to an alternate location by defining the `DESTDIR` environment variable when invoking Bash:

`curl -fLSs https://raw.githubusercontent.com/CircleCI-Public/circleci-cli/main/install.sh | DESTDIR=/opt/bin bash`

shell

### [](https://circleci.com/docs/guides/toolkit/local-cli/#manual-download)Manual install

You can visit the [GitHub releases](https://github.com/CircleCI-Public/circleci-cli/releases) page for the CLI to manually download and install. This approach is best if you would like the installed CLI to be in a specific path on your system.

[](https://circleci.com/docs/guides/toolkit/local-cli/#updating-the-cli)Updating the CLI
----------------------------------------------------------------------------------------

If you would just like to check for updates manually (and not install them), use the command:

`circleci update check`

shell

For **Linux and Windows** installs, you can update to the newest version of the CLI using the following command:

`circleci update`

shell

For **macOS** installations with Homebrew, you will need to run the following command to update:

`brew upgrade circleci`

shell

### [](https://circleci.com/docs/guides/toolkit/local-cli/#updating-the-legacy-cli)Updating the legacy CLI

The newest version of the CLI is a [CircleCI-Public open source project](https://github.com/CircleCI-Public/circleci-cli). If you have the [old CLI installed](https://github.com/circleci/local-cli), run the following commands to update and switch to the new CLI:

```
circleci update
circleci switch
```

shell

This command may prompt you for `sudo` if your user does not have write permissions to the install directory, `/usr/local/bin`.

[](https://circleci.com/docs/guides/toolkit/local-cli/#configure-the-cli)Configure the CLI
------------------------------------------------------------------------------------------

Before using the CLI, you need to generate a CircleCI API token from the [Personal API Token tab](https://app.circleci.com/settings/user/tokens). After you get your token, configure the CLI by running:

`circleci setup`

shell

The set up process will prompt you for configuration settings. If you are using the CLI with CircleCI cloud, use the default CircleCI host. If you are using CircleCI server, change the value to your installation address (for example, `circleci.your-org.com`).

[](https://circleci.com/docs/guides/toolkit/local-cli/#telemetry)Telemetry
--------------------------------------------------------------------------

The CircleCI CLI includes a telemetry feature that collects basic errors and feature usage data in order to help us improve the experience for everyone.

Telemetry works on an opt-in basis. When running a command for the first time, you will be asked for consent to enable telemetry. Telemetry is disabled by default for non-interactive terminals, ensuring that scripts that leverage the CLI run smoothly.

You can disable or enable telemetry any time in one of the following ways:

*   Run one of the following commands: `circleci telemetry enable` or `circleci telemetry disable`

*   To disable telemetry, set the `CIRCLECI_CLI_TELEMETRY_OPTOUT` environment variable to `1` or `true`

[](https://circleci.com/docs/guides/toolkit/local-cli/#uninstallation)Uninstall
-------------------------------------------------------------------------------

The commands for uninstalling the CircleCI CLI will vary depending on your original installation method.

**Linux uninstall with Snap**:

`sudo snap remove circleci`

shell

**macOS uninstall with Homebrew**:

`brew uninstall circleci`

shell

**Windows uninstall with Chocolatey**:

`choco uninstall circleci-cli -y --remove dependencies`

shell

**Alternative curl uninstall**: Remove the `circleci` executable from `/usr/local/bin`

[](https://circleci.com/docs/guides/toolkit/local-cli/#next-steps)Next steps
----------------------------------------------------------------------------

*   [How to validate your CircleCI configuration](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#validate-a-circleci-config)

*   [How to run a job in a container on your local machine](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#run-a-job-in-a-container-on-your-machine)

*   [How to create, publish, view, and manage orbs](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#orb-development-kit)

*   [How to manage contexts](https://circleci.com/docs/guides/toolkit/how-to-use-the-circleci-local-cli/#context-management)

* * *

[](https://circleci.com/docs/guides/toolkit/local-cli/#useful-links)CLI articles in the support centre
------------------------------------------------------------------------------------------------------

If you wish to suggest ways we could improve the CLI [share your suggestion on the GitHub repository](https://github.com/CircleCI-Public/circleci-cli).

*   [How to check private repositories with local jobs using the CircleCI CLI?](https://support.circleci.com/hc/en-us/articles/360033753374-Checkout-private-repositories-with-local-jobs-run-through-circleci-cli)

*   [How to know if your project is using deprecated Machine images with the CLI?](https://support.circleci.com/hc/en-us/articles/4421154407195-Deprecating-Ubuntu-14-04-and-16-04-images-EOL-5-31-22)

*   [How to validate a config that uses private Orbs with the CLI?](https://support.circleci.com/hc/en-us/articles/10643012267291-How-to-validate-a-config-that-uses-private-Orbs)

*   [Understanding the difference between public, private and unlisted orbs](https://support.circleci.com/hc/en-us/articles/4406826701339-Orbs-Public-vs-Private-vs-Unlisted)

*   [How to make your orbs private using the CircleCI CLI?](https://support.circleci.com/hc/en-us/articles/360035341894-How-can-I-make-my-orbs-private-)

*   [How to list your private orb using the CircleCI CLI?](https://support.circleci.com/hc/en-us/articles/15222621603355-How-to-Find-your-Private-Orb-s-Documentation)

*   [How to delete an orb using the CircleCI CLI?](https://support.circleci.com/hc/en-us/articles/360045977834-Can-I-delete-an-Orb-)

*   [How to delete a project Docker Layer Cache with the CircleCI CLI?](https://support.circleci.com/hc/en-us/articles/14027411555355-How-to-delete-a-projects-Docker-Layer-Cache)

*   [Docker Layer Cache FAQ](https://support.circleci.com/hc/en-us/articles/4407580027675-Docker-Layer-Caching-FAQ)

*   [How to rotate your self-hosted runner resource class tokens using the CircleCI CLI?](https://support.circleci.com/hc/en-us/articles/14031352897819-How-to-Rotate-your-Self-Hosted-Runner-Resource-Class-Tokens)

*   [How to use the CLI to verify namespaces and resource classes have been created correctly when installing the CircleCI runner?](https://support.circleci.com/hc/en-us/articles/360057144631-CircleCI-Runner-Error-Message-We-cannot-run-this-job-using-the-selected-resource-class-)

*   [How to use Reality Check to validate your CircleCI server installation for GitHub Enterprise via the CLI?](https://support.circleci.com/hc/en-us/articles/360011235534-Using-realitycheck-to-validate-your-CircleCI-installation)

### [](https://circleci.com/docs/guides/toolkit/local-cli/#troubleshooting)Troubleshooting

*   [What if the CLI context commands error with "Must have admin permission"?](https://support.circleci.com/hc/en-us/articles/360047644153-CircleCI-CLI-Context-Command-errors-with-Must-have-admin-permission-)

*   [What if the CLI fails with `panic: yaml: line 4: could not find expected ':'`?](https://support.circleci.com/hc/en-us/articles/360046871833-CircleCI-CLI-Fails-With-panic-yaml-line-4-could-not-find-expected-Error)

*   [What if the CLI command `circleci local execute` fails with `--storage-opt is supported only for overlay over xfs with 'pquota' mount option`?](https://support.circleci.com/hc/en-us/articles/7060937560859-How-to-resolve-error-storage-opt-is-supported-only-for-overlay-over-xfs-with-pquota-mount-option-when-running-jobs-locally-with-the-cli)

*   [What if the CLI command `circleci local execute` fails with `not implemented for cgroup v2 unified hierarchy`?](https://support.circleci.com/hc/en-us/articles/4413013337371-CircleCI-CLI-Running-circleci-local-execute-Results-in-not-implemented-for-cgroup-v2-unified-hierarchy-Error)

### On This Page

*   [The CircleCI CLI and the task runner](https://circleci.com/docs/guides/toolkit/local-cli/#the-circleci-cli-and-the-task-runner)
*   [Installation](https://circleci.com/docs/guides/toolkit/local-cli/#installation)
*   [Linux install with Snap](https://circleci.com/docs/guides/toolkit/local-cli/#linux-install-with-snap)
*   [macOS install with Homebrew](https://circleci.com/docs/guides/toolkit/local-cli/#macos-install-with-homebrew)
*   [Windows install with Chocolatey](https://circleci.com/docs/guides/toolkit/local-cli/#windows-install-with-chocolatey)
*   [Alternative installation method](https://circleci.com/docs/guides/toolkit/local-cli/#alternative-installation-method)
*   [Manual install](https://circleci.com/docs/guides/toolkit/local-cli/#manual-download)
*   [Updating the CLI](https://circleci.com/docs/guides/toolkit/local-cli/#updating-the-cli)
*   [Updating the legacy CLI](https://circleci.com/docs/guides/toolkit/local-cli/#updating-the-legacy-cli)
*   [Configure the CLI](https://circleci.com/docs/guides/toolkit/local-cli/#configure-the-cli)
*   [Telemetry](https://circleci.com/docs/guides/toolkit/local-cli/#telemetry)
*   [Uninstall](https://circleci.com/docs/guides/toolkit/local-cli/#uninstallation)
*   [Next steps](https://circleci.com/docs/guides/toolkit/local-cli/#next-steps)
*   [CLI articles in the support centre](https://circleci.com/docs/guides/toolkit/local-cli/#useful-links)
*   [Troubleshooting](https://circleci.com/docs/guides/toolkit/local-cli/#troubleshooting)

#### Suggest an edit to this page

*   [Make a contribution](https://github.com/circleci/circleci-docs/edit/main/docs/guides/modules/toolkit/pages/local-cli.adoc)
*   [Learn how to contribute](https://github.com/circleci/circleci-docs/blob/main/CONTRIBUTING.md)

#### Still need help?

*   [Ask the CircleCI community](https://discuss.circleci.com/)
*   [Join the research community](https://circleci.com/research/)
*   [Visit our support site](https://support.circleci.com/hc/en-us/)

![Image 15: CircleCI Logo](https://circleci.com/docs/_/img/logo.svg)![Image 16: CircleCI Logo](https://circleci.com/docs/_/img/logo-dark.svg)

*   © CircleCI, Inc. All rights reserved.

    *   [Terms of Service](https://circleci.com/legal/terms-of-service/)
    *   [Privacy Policy](https://circleci.com/legal/privacy/)
    *   [Cookie Policy](https://circleci.com/legal/cookie-policy/)
    *   [Security](https://circleci.com/security/)

*   [](https://github.com/circleci)
*   [](https://circleci.com/blog/feed.xml)
*   [](https://x.com/circleci)
*   [](https://www.twitch.tv/circleci)
*   [](https://www.linkedin.com/company/circleci)

Feedback

We use your feedback to help improve our content.
-------------------------------------------------

Next

![Image 17](https://circleci.com/docs/guides/toolkit/local-cli/)
