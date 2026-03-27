package com.recipediet.app.data.model

data class UserProfile(
    val name: String = "",
    val dietType: DietType = DietType.OMNIVORE,
    val allergies: List<Allergy> = emptyList(),
    val calorieGoal: Int = 2000,
    val goalType: GoalType = GoalType.MAINTAIN,
    val isOnboardingDone: Boolean = false
)

enum class GoalType(val displayName: String, val emoji: String) {
    LOSE_WEIGHT("Perder peso", "📉"),
    MAINTAIN("Mantener peso", "⚖️"),
    GAIN_MUSCLE("Ganar músculo", "💪"),
    EAT_HEALTHIER("Comer más sano", "🥗")
}
