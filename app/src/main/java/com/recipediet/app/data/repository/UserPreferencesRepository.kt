package com.recipediet.app.data.repository

import android.content.Context
import android.content.SharedPreferences
import com.recipediet.app.data.model.Allergy
import com.recipediet.app.data.model.DietType
import com.recipediet.app.data.model.GoalType
import com.recipediet.app.data.model.UserProfile

class UserPreferencesRepository(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("user_prefs", Context.MODE_PRIVATE)

    fun saveUserProfile(profile: UserProfile) {
        prefs.edit().apply {
            putString(KEY_NAME, profile.name)
            putString(KEY_DIET_TYPE, profile.dietType.name)
            putStringSet(KEY_ALLERGIES, profile.allergies.map { it.name }.toSet())
            putInt(KEY_CALORIE_GOAL, profile.calorieGoal)
            putString(KEY_GOAL_TYPE, profile.goalType.name)
            putBoolean(KEY_ONBOARDING_DONE, profile.isOnboardingDone)
            apply()
        }
    }

    fun getUserProfile(): UserProfile {
        val dietTypeName = prefs.getString(KEY_DIET_TYPE, DietType.OMNIVORE.name) ?: DietType.OMNIVORE.name
        val goalTypeName = prefs.getString(KEY_GOAL_TYPE, GoalType.MAINTAIN.name) ?: GoalType.MAINTAIN.name
        val allergyNames = prefs.getStringSet(KEY_ALLERGIES, emptySet()) ?: emptySet()

        return UserProfile(
            name = prefs.getString(KEY_NAME, "") ?: "",
            dietType = runCatching { DietType.valueOf(dietTypeName) }.getOrDefault(DietType.OMNIVORE),
            allergies = allergyNames.mapNotNull { runCatching { Allergy.valueOf(it) }.getOrNull() },
            calorieGoal = prefs.getInt(KEY_CALORIE_GOAL, 2000),
            goalType = runCatching { GoalType.valueOf(goalTypeName) }.getOrDefault(GoalType.MAINTAIN),
            isOnboardingDone = prefs.getBoolean(KEY_ONBOARDING_DONE, false)
        )
    }

    fun isOnboardingDone(): Boolean = prefs.getBoolean(KEY_ONBOARDING_DONE, false)

    fun getDietType(): DietType {
        val name = prefs.getString(KEY_DIET_TYPE, DietType.OMNIVORE.name) ?: DietType.OMNIVORE.name
        return runCatching { DietType.valueOf(name) }.getOrDefault(DietType.OMNIVORE)
    }

    companion object {
        private const val KEY_NAME = "user_name"
        private const val KEY_DIET_TYPE = "diet_type"
        private const val KEY_ALLERGIES = "allergies"
        private const val KEY_CALORIE_GOAL = "calorie_goal"
        private const val KEY_GOAL_TYPE = "goal_type"
        private const val KEY_ONBOARDING_DONE = "onboarding_done"
    }
}
