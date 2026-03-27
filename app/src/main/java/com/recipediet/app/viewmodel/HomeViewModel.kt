package com.recipediet.app.viewmodel

import android.app.Application
import androidx.lifecycle.*
import com.recipediet.app.data.model.DietType
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

    val recipes: LiveData<List<Recipe>> = MediatorLiveData<List<Recipe>>().apply {
        fun update() {
            val query = _searchQuery.value ?: ""
            val category = _selectedCategory.value
            val diet = userProfile.value?.dietType

            val source = if (query.isNotBlank()) {
                recipeRepo.searchRecipes(query)
            } else {
                recipeRepo.getFilteredRecipes(diet, category)
            }

            addSource(source) { value = it }
        }

        addSource(_searchQuery) { update() }
        addSource(_selectedCategory) { update() }
        addSource(userProfile) { update() }
        update()
    }

    val featuredRecipes: LiveData<List<Recipe>> = recipeRepo.allRecipes.map { list ->
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
