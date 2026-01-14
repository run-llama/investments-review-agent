import { type ApiClients, createWorkflowsClient } from "@llamaindex/ui";

const deploymentName = import.meta.env.VITE_LLAMA_DEPLOY_DEPLOYMENT_NAME;

export const clients: ApiClients = {
  workflowsClient: createWorkflowsClient({
    baseUrl: `/deployments/${deploymentName}`,
  }),
};
