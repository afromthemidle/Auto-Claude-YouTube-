package com.recipediet.app.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.os.bundleOf
import androidx.core.widget.addTextChangedListener
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.recipediet.app.R
import com.recipediet.app.databinding.FragmentHomeBinding
import com.recipediet.app.ui.adapters.CategoryAdapter
import com.recipediet.app.ui.adapters.RecipeAdapter
import com.recipediet.app.viewmodel.HomeViewModel

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()

    private lateinit var recipeAdapter: RecipeAdapter
    private lateinit var categoryAdapter: CategoryAdapter

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupRecyclerViews()
        setupSearch()
        observeData()
    }

    override fun onResume() {
        super.onResume()
        viewModel.refreshProfile()
    }

    private fun setupRecyclerViews() {
        recipeAdapter = RecipeAdapter(
            onRecipeClick = { recipe ->
                findNavController().navigate(
                    R.id.action_home_to_detail,
                    bundleOf("recipe_id" to recipe.id)
                )
            },
            onFavoriteClick = { recipe ->
                viewModel.toggleFavorite(recipe)
            }
        )

        categoryAdapter = CategoryAdapter { category ->
            viewModel.setCategory(category)
        }

        binding.rvRecipes.apply {
            adapter = recipeAdapter
            layoutManager = LinearLayoutManager(requireContext())
        }

        binding.rvCategories.apply {
            adapter = categoryAdapter
            layoutManager = LinearLayoutManager(
                requireContext(), LinearLayoutManager.HORIZONTAL, false
            )
        }
    }

    private fun setupSearch() {
        binding.etSearch.addTextChangedListener { text ->
            viewModel.setSearchQuery(text.toString())
        }
    }

    private fun observeData() {
        viewModel.userProfile.observe(viewLifecycleOwner) { profile ->
            val greeting = if (profile.name.isNotEmpty()) {
                "Hola, ${profile.name}! 👋"
            } else {
                "¡Bienvenido! 👋"
            }
            binding.tvGreeting.text = greeting
            binding.tvDietBadge.text = "${profile.dietType.emoji} ${profile.dietType.displayName}"
        }

        viewModel.recipes.observe(viewLifecycleOwner) { recipes ->
            recipeAdapter.submitList(recipes)
            binding.tvRecipeCount.text = "${recipes.size} recetas encontradas"
            binding.tvEmptyState.visibility = if (recipes.isEmpty()) View.VISIBLE else View.GONE
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
