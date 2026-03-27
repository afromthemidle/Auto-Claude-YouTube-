package com.recipediet.app.ui.detail

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.recipediet.app.databinding.FragmentRecipeDetailBinding
import com.recipediet.app.ui.adapters.IngredientAdapter
import com.recipediet.app.ui.adapters.StepAdapter
import com.recipediet.app.viewmodel.HomeViewModel

class RecipeDetailFragment : Fragment() {

    private var _binding: FragmentRecipeDetailBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentRecipeDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recipeId = arguments?.getInt("recipe_id") ?: return

        binding.toolbar.setNavigationOnClickListener { findNavController().navigateUp() }

        viewModel.recipes.observe(viewLifecycleOwner) { recipes ->
            val recipe = recipes.find { it.id == recipeId } ?: return@observe

            binding.apply {
                tvEmojiLarge.text = recipe.imageEmoji
                tvRecipeName.text = recipe.name
                tvDescription.text = recipe.description
                tvCalories.text = "${recipe.calories} kcal"
                tvProtein.text = "${recipe.protein}g prot"
                tvCarbs.text = "${recipe.carbs}g carbs"
                tvFat.text = "${recipe.fat}g grasas"
                tvTime.text = "${recipe.prepTimeMinutes + recipe.cookTimeMinutes} min"
                tvServings.text = "${recipe.servings} porciones"
                tvDifficulty.text = recipe.difficulty.displayName
                tvRating.text = "★ ${recipe.rating}"
                tvCategory.text = "${recipe.category.emoji} ${recipe.category.displayName}"

                val dietTags = recipe.dietTypes.joinToString(" · ") { "${it.emoji} ${it.displayName}" }
                tvDietTags.text = dietTags

                btnFavorite.setIconResource(
                    if (recipe.isFavorite) android.R.drawable.btn_star_big_on
                    else android.R.drawable.btn_star_big_off
                )
                btnFavorite.text = if (recipe.isFavorite) "Guardado" else "Guardar"
                btnFavorite.setOnClickListener { viewModel.toggleFavorite(recipe) }

                rvIngredients.apply {
                    adapter = IngredientAdapter(recipe.ingredients)
                    layoutManager = LinearLayoutManager(requireContext())
                    isNestedScrollingEnabled = false
                }

                rvSteps.apply {
                    adapter = StepAdapter(recipe.steps)
                    layoutManager = LinearLayoutManager(requireContext())
                    isNestedScrollingEnabled = false
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
