import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db/drizzle";
import { userProfile, userPreferences } from "@/db/schema";
import { eq } from "drizzle-orm";
import { nanoid } from "nanoid";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get("userId");

    if (!userId) {
      return NextResponse.json({ error: "userId required" }, { status: 400 });
    }

    const profile = await db
      .select()
      .from(userProfile)
      .where(eq(userProfile.userId, userId))
      .limit(1);

    return NextResponse.json(profile[0] || null);
  } catch (error) {
    console.error("Failed to get profile:", error);
    return NextResponse.json({ error: "Failed to get profile" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { userId, ...profileData } = body;

    if (!userId) {
      return NextResponse.json({ error: "userId required" }, { status: 400 });
    }

    // Check if profile exists
    const existing = await db
      .select()
      .from(userProfile)
      .where(eq(userProfile.userId, userId))
      .limit(1);

    if (existing.length > 0) {
      // Update existing profile
      await db
        .update(userProfile)
        .set({
          displayName: profileData.displayName,
          freelanceType: profileData.freelanceType,
          experienceLevel: profileData.experienceLevel,
          platforms: profileData.platforms,
          bio: profileData.bio,
          hourlyRate: profileData.hourlyRate ? parseInt(profileData.hourlyRate) : null,
          portfolioUrl: profileData.portfolioUrl,
          timezone: profileData.timezone,
          language: profileData.language,
          onboardingCompleted: profileData.onboardingCompleted ?? false,
          updatedAt: new Date(),
        })
        .where(eq(userProfile.userId, userId));

      return NextResponse.json({ success: true, updated: true });
    } else {
      // Create new profile
      await db.insert(userProfile).values({
        id: nanoid(),
        userId,
        displayName: profileData.displayName,
        freelanceType: profileData.freelanceType,
        experienceLevel: profileData.experienceLevel,
        platforms: profileData.platforms,
        bio: profileData.bio,
        hourlyRate: profileData.hourlyRate ? parseInt(profileData.hourlyRate) : null,
        portfolioUrl: profileData.portfolioUrl,
        timezone: profileData.timezone,
        language: profileData.language,
        onboardingCompleted: profileData.onboardingCompleted ?? false,
      });

      // Also create default preferences
      await db.insert(userPreferences).values({
        id: nanoid(),
        userId,
        gdprConsent: profileData.gdprConsent ?? false,
        gdprConsentDate: profileData.gdprConsent ? new Date() : null,
        emailNotifications: profileData.emailNotifications ?? true,
        agentAlerts: profileData.agentAlerts ?? true,
      });

      return NextResponse.json({ success: true, created: true });
    }
  } catch (error) {
    console.error("Failed to save profile:", error);
    return NextResponse.json({ error: "Failed to save profile" }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get("userId");

    if (!userId) {
      return NextResponse.json({ error: "userId required" }, { status: 400 });
    }

    await db.delete(userProfile).where(eq(userProfile.userId, userId));
    await db.delete(userPreferences).where(eq(userPreferences.userId, userId));

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Failed to delete profile:", error);
    return NextResponse.json({ error: "Failed to delete profile" }, { status: 500 });
  }
}
