"use client";

import { useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { AppLayout } from '@/components/flagpilot';
import { WarRoom } from '@/components/mission/war-room';
import { authClient } from '@/lib/auth-client';
import { redirect } from 'next/navigation';
import { Loader } from '@/components/ui/loader';
import { useMissions, useCredits } from '@/hooks/use-api';
import { useMissionStore } from '@/stores/mission-store';

function MissionContent() {
  const { data: session, isPending: sessionPending } = authClient.useSession();
  const searchParams = useSearchParams();
  const missionType = searchParams.get('type') || 'general';

  // API hooks - fetches real data from backend
  const { missions, isLoading: missionsLoading } = useMissions();
  const { balance, isLoading: creditsLoading } = useCredits();

  // Mission store
  const { currentMission, startMission } = useMissionStore();

  // Get mission title based on type
  const getMissionTitle = (type: string) => {
    switch (type) {
      case 'contract': return 'Contract Review';
      case 'verification': return 'Job Verification';
      case 'payment': return 'Payment Collection';
      case 'dispute': return 'Dispute Resolution';
      default: return 'New Mission';
    }
  };

  // Create mission on mount if none exists
  useEffect(() => {
    if (session?.user && !currentMission) {
      const missionTitle = getMissionTitle(missionType);
      startMission(missionTitle);
    }
  }, [session, missionType, currentMission, startMission]);

  if (sessionPending || missionsLoading || creditsLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950">
        <Loader variant="dots" size="lg" />
      </div>
    );
  }

  if (!session) {
    redirect('/');
  }

  // Convert API missions to sidebar format
  const sidebarMissions = missions.map((m) => ({
    id: m.id,
    name: m.title,
    status: m.status as 'active' | 'completed' | 'paused',
    createdAt: new Date(m.createdAt),
  }));

  return (
    <AppLayout
      breadcrumbs={[
        { label: 'Home', href: '/' },
        { label: 'Mission' },
        { label: currentMission?.title || 'New Mission' },
      ]}
      user={{
        name: session.user?.name || 'User',
        email: session.user?.email || '',
        avatarUrl: session.user?.image || undefined,
      }}
      missions={sidebarMissions}
      credits={balance ? { current: balance.current, total: balance.total } : { current: 0, total: 0 }}
    >
      <WarRoom />
    </AppLayout>
  );
}

export default function MissionPage() {
  return (
    <Suspense fallback={
      <div className="flex h-screen items-center justify-center bg-zinc-950">
        <Loader variant="dots" size="lg" />
      </div>
    }>
      <MissionContent />
    </Suspense>
  );
}
