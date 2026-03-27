package com.recipediet.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.MutableLiveData
import com.recipediet.app.data.model.*
import com.recipediet.app.data.repository.UserPreferencesRepository

class ProfileViewModel(application: Application) : AndroidViewModel(application) {

    private val userRepo = UserPreferencesRepository(application)

    val userProfile = MutableLiveData(userRepo.getUserProfile())
    val selectedDiet = MutableLiveData(userRepo.getUserProfile().dietType)
    val selectedAllergies = MutableLiveData(userRepo.getUserProfile().allergies.toMutableList())
    val calorieGoal = MutableLiveData(userRepo.getUserProfile().calorieGoal)
    val selectedGoal = MutableLiveData(userRepo.getUserProfile().goalType)
    val userName = MutableLiveData(userRepo.getUserProfile().name)

    fun saveProfile() {
        val profile = UserProfile(
            name = userName.value ?: "",
            dietType = selectedDiet.value ?: DietType.OMNIVORE,
            allergies = selectedAllergies.value ?: emptyList(),
            calorieGoal = calorieGoal.value ?: 2000,
            goalType = selectedGoal.value ?: GoalType.MAINTAIN,
            isOnboardingDone = true
        )
        userRepo.saveUserProfile(profile)
        userProfile.value = profile
    }

    fun toggleAllergy(allergy: Allergy) {
        val current = selectedAllergies.value?.toMutableList() ?: mutableListOf()
        if (current.contains(allergy)) current.remove(allergy) else current.add(allergy)
        selectedAllergies.value = current
    }

    fun setDiet(diet: DietType) {
        selectedDiet.value = diet
    }

    fun setGoal(goal: GoalType) {
        selectedGoal.value = goal
    }

    fun setCalorieGoal(calories: Int) {
        calorieGoal.value = calories
    }
}
