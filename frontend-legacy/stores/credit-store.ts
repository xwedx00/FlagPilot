import { create } from 'zustand';
import { creditsApi, type CreditTransaction } from '@/lib/api-client';

interface CreditState {
    balance: number | null;
    history: CreditTransaction[];
    isLoading: boolean;
    error: string | null;

    fetchBalance: () => Promise<void>;
    fetchHistory: () => Promise<void>;
    purchase: (amount: number) => Promise<string | null>;
}

export const useCreditStore = create<CreditState>((set) => ({
    balance: null,
    history: [],
    isLoading: false,
    error: null,

    fetchBalance: async () => {
        set({ isLoading: true, error: null });
        try {
            const data = await creditsApi.getBalance();
            set({ balance: data.current, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    fetchHistory: async () => {
        set({ isLoading: true, error: null });
        try {
            const data = await creditsApi.getHistory();
            set({ history: data, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    purchase: async (amount: number) => {
        set({ isLoading: true, error: null });
        try {
            const { checkoutUrl } = await creditsApi.purchase(amount);

            set({ isLoading: false });

            // If we got a checkout URL, return it
            if (checkoutUrl) return checkoutUrl;

            // If auto-success (demo mode), refresh balance
            await useCreditStore.getState().fetchBalance();
            return null;
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
            return null;
        }
    },
}));
