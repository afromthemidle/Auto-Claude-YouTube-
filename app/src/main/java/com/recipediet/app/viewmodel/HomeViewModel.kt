package com.recipediet.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MediatorLiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.map
import androidx.lifecycle.viewModelScope
import com.recipediet.app.data.model.Recipe
import com.recipediet.app.data.model.RecipeCategory
import com.recipediet.app.data.repository.RecipeRepository
import com.recipediet.app.data.repository.UserPreferencesRepository
import kotlinx.coroutines.launch

class HomeViewModel(application: Application) : AndroidViewModel(application) {

    private val recipeRepo = RecipeRepository(application)
    private val userRepo = UserPreferencesRepository(application)

    private val _searchQuery = MutableLiveData("")
    private val _selectedCategory = MutableLiveData<RecipeCategory?>(null)

    val userProfile = MutableLiveData(userRepo.getUserProfile())

    private val allRecipes: LiveData<List<Recipe>> = recipeRepo.allRecipes

    // Static sources only — no dynamic addSource inside observers
    val recipes: LiveData<List<Recipe>> = MediatorLiveData<List<Recipe>>().also { mediator ->
        fun recompute() {
            val all = allRecipes.value ?: return
            val query = _searchQuery.value.orEmpty()
            val category = _selectedCategory.value
            val diet = userProfile.value?.dietType
            mediator.value = if (query.isNotBlank()) {
                all.filter { r ->
                    r.name.contains(query, ignoreCase = true) ||
                    r.description.contains(query, ignoreCase = true) ||
                    r.tags.any { it.contains(query, ignoreCase = true) }
                }
            } else {
                all.filter { r ->
                    (diet == null || r.dietTypes.contains(diet)) &&
                    (category == null || r.category == category)
                }
            }
        }
        mediator.addSource(allRecipes) { recompute() }
        mediator.addSource(_searchQuery) { recompute() }
        mediator.addSource(_selectedCategory) { recompute() }
        mediator.addSource(userProfile) { recompute() }
    }

    val featuredRecipes: LiveData<List<Recipe>> = allRecipes.map { list ->
        list.sortedByDescending { it.rating }.take(5)
    }

    init {
        viewModelScope.launch {
            recipeRepo.initialize()
        }
    }

    fun setSearchQuery(query: String) {
        _searchQuery.value = query
    }

    fun setCategory(category: RecipeCategory?) {
        _selectedCategory.value = category
    }

    fun toggleFavorite(recipe: Recipe) {
        viewModelScope.launch {
            recipeRepo.toggleFavorite(recipe)
        }
    }

    fun refreshProfile() {
        userProfile.value = userRepo.getUserProfile()
    }
}
