import { create } from "zustand";

export type Tier = "basic" | "ai";
export type DeployTarget = "docker" | "gcloud" | "aws";

interface WizardState {
  address: string | null;
  tier: Tier | null;
  deployTarget: DeployTarget | null;
  telegramToken: string;
  telegramChatId: string;
  agentPubKey: string | null;

  setAddress: (address: string | null) => void;
  setTier: (tier: Tier) => void;
  setDeployTarget: (target: DeployTarget) => void;
  setTelegramToken: (token: string) => void;
  setTelegramChatId: (id: string) => void;
  setAgentPubKey: (key: string) => void;
}

export const useWizardStore = create<WizardState>((set) => ({
  address: null,
  tier: null,
  deployTarget: null,
  telegramToken: "",
  telegramChatId: "",
  agentPubKey: null,

  setAddress: (address) => set({ address }),
  setTier: (tier) => set({ tier }),
  setDeployTarget: (deployTarget) => set({ deployTarget }),
  setTelegramToken: (telegramToken) => set({ telegramToken }),
  setTelegramChatId: (telegramChatId) => set({ telegramChatId }),
  setAgentPubKey: (agentPubKey) => set({ agentPubKey }),
}));
