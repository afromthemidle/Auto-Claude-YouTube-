package com.recipediet.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.recipediet.app.data.model.Recipe
import com.recipediet.app.data.repository.RecipeRepository
import kotlinx.coroutines.launch

class FavoritesViewModel(application: Application) : AndroidViewModel(application) {

    private val recipeRepo = RecipeRepository(application)

    val favoriteRecipes = recipeRepo.favoriteRecipes

    fun toggleFavorite(recipe: Recipe) {
        viewModelScope.launch {
            recipeRepo.toggleFavorite(recipe)
        }
    }
}
