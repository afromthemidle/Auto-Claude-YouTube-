package com.recipediet.app.ui.profile

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import com.google.android.material.chip.Chip
import com.google.android.material.slider.Slider
import com.recipediet.app.data.model.Allergy
import com.recipediet.app.data.model.DietType
import com.recipediet.app.data.model.GoalType
import com.recipediet.app.databinding.FragmentProfileBinding
import com.recipediet.app.viewmodel.ProfileViewModel

class ProfileFragment : Fragment() {

    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ProfileViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupDietChips()
        setupAllergyChips()
        setupGoalChips()
        setupCalorieSlider()
        observeData()
        setupSaveButton()
    }

    private fun setupDietChips() {
        binding.chipGroupDiet.removeAllViews()
        DietType.values().forEach { diet ->
            val chip = Chip(requireContext()).apply {
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
            val chip = Chip(requireContext()).apply {
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
            val chip = Chip(requireContext()).apply {
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

    private fun setupCalorieSlider() {
        binding.sliderCalories.apply {
            valueFrom = 1200f
            valueTo = 4000f
            stepSize = 50f
            value = (viewModel.calorieGoal.value ?: 2000).toFloat()

            addOnChangeListener { _, value, _ ->
                viewModel.setCalorieGoal(value.toInt())
                binding.tvCalorieValue.text = "${value.toInt()} kcal/día"
            }
        }
        binding.tvCalorieValue.text = "${viewModel.calorieGoal.value ?: 2000} kcal/día"
    }

    private fun observeData() {
        viewModel.userProfile.observe(viewLifecycleOwner) { profile ->
            binding.etName.setText(profile.name)
            binding.tvCurrentDiet.text = "${profile.dietType.emoji} ${profile.dietType.displayName}"
            binding.tvDietDescription.text = profile.dietType.description
        }
    }

    private fun setupSaveButton() {
        binding.btnSaveProfile.setOnClickListener {
            val name = binding.etName.text.toString().trim()
            if (name.isEmpty()) {
                binding.tilName.error = "Por favor ingresa tu nombre"
                return@setOnClickListener
            }
            binding.tilName.error = null
            viewModel.userName.value = name
            viewModel.saveProfile()
            Toast.makeText(requireContext(), "¡Perfil actualizado! ✅", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
