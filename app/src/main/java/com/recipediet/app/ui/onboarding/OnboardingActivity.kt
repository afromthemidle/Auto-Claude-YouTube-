package com.recipediet.app.ui.onboarding

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import com.google.android.material.chip.Chip
import com.recipediet.app.R
import com.recipediet.app.data.model.Allergy
import com.recipediet.app.data.model.DietType
import com.recipediet.app.data.model.GoalType
import com.recipediet.app.databinding.ActivityOnboardingBinding
import com.recipediet.app.ui.MainActivity
import com.recipediet.app.viewmodel.ProfileViewModel

class OnboardingActivity : AppCompatActivity() {

    private lateinit var binding: ActivityOnboardingBinding
    private val viewModel: ProfileViewModel by viewModels()
    private var currentStep = 0
    private val totalSteps = 4

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOnboardingBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupSteps()
        setupNavigation()
        showStep(0)
    }

    private fun setupSteps() {
        setupDietChips()
        setupAllergyChips()
        setupGoalChips()
    }

    private fun setupDietChips() {
        binding.chipGroupDiet.removeAllViews()
        DietType.values().forEach { diet ->
            val chip = Chip(this).apply {
                text = "${diet.emoji} ${diet.displayName}"
                isCheckable = true
                isChecked = diet == viewModel.selectedDiet.value
                setOnCheckedChangeListener { _, isChecked ->
                    if (isChecked) viewModel.setDiet(diet)
                }
            }
            binding.chipGroupDiet.addView(chip)
        }
    }

    private fun setupAllergyChips() {
        binding.chipGroupAllergies.removeAllViews()
        Allergy.values().forEach { allergy ->
            val chip = Chip(this).apply {
                text = "${allergy.emoji} ${allergy.displayName}"
                isCheckable = true
                isChecked = viewModel.selectedAllergies.value?.contains(allergy) == true
                setOnCheckedChangeListener { _, _ ->
                    viewModel.toggleAllergy(allergy)
                }
            }
            binding.chipGroupAllergies.addView(chip)
        }
    }

    private fun setupGoalChips() {
        binding.chipGroupGoal.removeAllViews()
        GoalType.values().forEach { goal ->
            val chip = Chip(this).apply {
                text = "${goal.emoji} ${goal.displayName}"
                isCheckable = true
                isChecked = goal == viewModel.selectedGoal.value
                setOnCheckedChangeListener { _, isChecked ->
                    if (isChecked) viewModel.setGoal(goal)
                }
            }
            binding.chipGroupGoal.addView(chip)
        }
    }

    private fun setupNavigation() {
        binding.btnNext.setOnClickListener {
            if (currentStep < totalSteps - 1) {
                if (validateStep(currentStep)) {
                    currentStep++
                    showStep(currentStep)
                }
            } else {
                finishOnboarding()
            }
        }

        binding.btnBack.setOnClickListener {
            if (currentStep > 0) {
                currentStep--
                showStep(currentStep)
            }
        }
    }

    private fun validateStep(step: Int): Boolean {
        return when (step) {
            0 -> {
                val name = binding.etName.text.toString().trim()
                if (name.isEmpty()) {
                    binding.tilName.error = "Por favor ingresa tu nombre"
                    false
                } else {
                    binding.tilName.error = null
                    viewModel.userName.value = name
                    true
                }
            }
            else -> true
        }
    }

    private fun showStep(step: Int) {
        binding.apply {
            stepWelcome.isVisible = step == 0
            stepDiet.isVisible = step == 1
            stepAllergies.isVisible = step == 2
            stepGoal.isVisible = step == 3

            btnBack.isVisible = step > 0
            btnNext.text = if (step == totalSteps - 1) "¡Comenzar!" else "Siguiente"

            progressIndicator.progress = ((step + 1) * 100 / totalSteps)
            tvStepIndicator.text = "Paso ${step + 1} de $totalSteps"
        }
    }

    private fun finishOnboarding() {
        viewModel.saveProfile()
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
