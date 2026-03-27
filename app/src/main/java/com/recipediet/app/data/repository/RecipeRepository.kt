package com.recipediet.app.data.repository

import android.content.Context
import androidx.lifecycle.LiveData
import androidx.lifecycle.MediatorLiveData
import androidx.lifecycle.MutableLiveData
import com.recipediet.app.data.db.AppDatabase
import com.recipediet.app.data.model.DietType
import com.recipediet.app.data.model.Recipe
import com.recipediet.app.data.model.RecipeCategory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class RecipeRepository(context: Context) {

    private val recipeDao = AppDatabase.getInstance(context).recipeDao()

    val allRecipes: LiveData<List<Recipe>> = recipeDao.getAllRecipes()
    val favoriteRecipes: LiveData<List<Recipe>> = recipeDao.getFavoriteRecipes()

    suspend fun initialize() {
        withContext(Dispatchers.IO) {
            if (recipeDao.getCount() == 0) {
                recipeDao.insertAll(RecipeDataSource.getSampleRecipes())
            }
        }
    }

    fun getRecipesByDiet(dietType: DietType): LiveData<List<Recipe>> {
        val result = MediatorLiveData<List<Recipe>>()
        result.addSource(allRecipes) { recipes ->
            result.value = recipes.filter { recipe ->
                recipe.dietTypes.contains(dietType)
            }
        }
        return result
    }

    fun getRecipesByCategory(category: RecipeCategory): LiveData<List<Recipe>> {
        val result = MediatorLiveData<List<Recipe>>()
        result.addSource(allRecipes) { recipes ->
            result.value = recipes.filter { it.category == category }
        }
        return result
    }

    fun getFilteredRecipes(dietType: DietType?, category: RecipeCategory?): LiveData<List<Recipe>> {
        val result = MediatorLiveData<List<Recipe>>()
        result.addSource(allRecipes) { recipes ->
            result.value = recipes.filter { recipe ->
                val dietMatch = dietType == null || recipe.dietTypes.contains(dietType)
                val categoryMatch = category == null || recipe.category == category
                dietMatch && categoryMatch
            }
        }
        return result
    }

    fun searchRecipes(query: String): LiveData<List<Recipe>> {
        return if (query.isBlank()) allRecipes
        else recipeDao.searchRecipes(query)
    }

    suspend fun toggleFavorite(recipe: Recipe) {
        withContext(Dispatchers.IO) {
            recipeDao.updateFavorite(recipe.id, !recipe.isFavorite)
        }
    }

    suspend fun getRecipeById(id: Int): Recipe? {
        return withContext(Dispatchers.IO) {
            recipeDao.getRecipeById(id)
        }
    }
}
