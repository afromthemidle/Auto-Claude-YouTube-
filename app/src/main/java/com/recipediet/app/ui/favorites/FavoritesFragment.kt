package com.recipediet.app.ui.favorites

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.recipediet.app.R
import com.recipediet.app.databinding.FragmentFavoritesBinding
import com.recipediet.app.ui.adapters.RecipeAdapter
import com.recipediet.app.viewmodel.FavoritesViewModel

class FavoritesFragment : Fragment() {

    private var _binding: FragmentFavoritesBinding? = null
    private val binding get() = _binding!!
    private val viewModel: FavoritesViewModel by viewModels()

    private lateinit var recipeAdapter: RecipeAdapter

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentFavoritesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recipeAdapter = RecipeAdapter(
            onRecipeClick = { recipe ->
                findNavController().navigate(
                    R.id.action_favorites_to_detail,
                    bundleOf("recipe_id" to recipe.id)
                )
            },
            onFavoriteClick = { recipe ->
                viewModel.toggleFavorite(recipe)
            }
        )

        binding.rvFavorites.apply {
            adapter = recipeAdapter
            layoutManager = LinearLayoutManager(requireContext())
        }

        viewModel.favoriteRecipes.observe(viewLifecycleOwner) { recipes ->
            recipeAdapter.submitList(recipes)
            binding.tvEmptyFavorites.visibility = if (recipes.isEmpty()) View.VISIBLE else View.GONE
            binding.tvFavoriteCount.text = "${recipes.size} recetas guardadas"
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
