import { create } from "zustand";

export type Tier = "basic" | "ai";
export type DeployTarget = "docker" | "gcloud" | "aws" | "tee";

interface WizardState {
  address: string | null;
  tier: Tier | null;
  deployTarget: DeployTarget | null;
  rpcUrl: string;
  openAiApiKey: string;
  tenderlyAccessKey: string;
  tenderlyAccountSlug: string;
  tenderlyProjectSlug: string;
  tenderlyNetworkId: string;
  dashboardPort: string;
  telegramToken: string;
  agentPubKey: string | null;
  safeAddress: string | null;

  setAddress: (address: string | null) => void;
  setTier: (tier: Tier) => void;
  setDeployTarget: (target: DeployTarget) => void;
  setRpcUrl: (rpcUrl: string) => void;
  setOpenAiApiKey: (openAiApiKey: string) => void;
  setTenderlyAccessKey: (tenderlyAccessKey: string) => void;
  setTenderlyAccountSlug: (tenderlyAccountSlug: string) => void;
  setTenderlyProjectSlug: (tenderlyProjectSlug: string) => void;
  setTenderlyNetworkId: (tenderlyNetworkId: string) => void;
  setDashboardPort: (dashboardPort: string) => void;
  setTelegramToken: (telegramToken: string) => void;
  setAgentPubKey: (key: string) => void;
  setSafeAddress: (safeAddress: string) => void;
}

export const useWizardStore = create<WizardState>((set) => ({
  address: null,
  tier: null,
  deployTarget: null,
  rpcUrl: "",
  openAiApiKey: "",
  tenderlyAccessKey: "",
  tenderlyAccountSlug: "",
  tenderlyProjectSlug: "",
  tenderlyNetworkId: "",
  dashboardPort: "8501",
  telegramToken: "",
  agentPubKey: null,
  safeAddress: null,

  setAddress: (address) => set({ address }),
  setTier: (tier) => set({ tier }),
  setDeployTarget: (deployTarget) => set({ deployTarget }),
  setRpcUrl: (rpcUrl) => set({ rpcUrl }),
  setOpenAiApiKey: (openAiApiKey) => set({ openAiApiKey }),
  setTenderlyAccessKey: (tenderlyAccessKey) => set({ tenderlyAccessKey }),
  setTenderlyAccountSlug: (tenderlyAccountSlug) => set({ tenderlyAccountSlug }),
  setTenderlyProjectSlug: (tenderlyProjectSlug) => set({ tenderlyProjectSlug }),
  setTenderlyNetworkId: (tenderlyNetworkId) => set({ tenderlyNetworkId }),
  setDashboardPort: (dashboardPort) => set({ dashboardPort }),
  setTelegramToken: (telegramToken) => set({ telegramToken }),
  setAgentPubKey: (agentPubKey) => set({ agentPubKey }),
  setSafeAddress: (safeAddress) => set({ safeAddress }),
}));
