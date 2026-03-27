package com.recipediet.app.data.model

import android.os.Parcelable
import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverter
import androidx.room.TypeConverters
import kotlinx.parcelize.Parcelize

@Parcelize
@Entity(tableName = "recipes")
@TypeConverters(ListConverters::class)
data class Recipe(
    @PrimaryKey val id: Int,
    val name: String,
    val description: String,
    val imageEmoji: String,
    val calories: Int,
    val prepTimeMinutes: Int,
    val cookTimeMinutes: Int,
    val servings: Int,
    val difficulty: Difficulty,
    val category: RecipeCategory,
    val dietTypes: List<DietType>,
    val ingredients: List<String>,
    val steps: List<String>,
    val tags: List<String>,
    val isFavorite: Boolean = false,
    val rating: Float = 0f,
    val protein: Int = 0,
    val carbs: Int = 0,
    val fat: Int = 0
) : Parcelable

enum class Difficulty(val displayName: String) {
    EASY("Fácil"),
    MEDIUM("Medio"),
    HARD("Difícil")
}

enum class RecipeCategory(val displayName: String, val emoji: String) {
    BREAKFAST("Desayuno", "🌅"),
    LUNCH("Almuerzo", "☀️"),
    DINNER("Cena", "🌙"),
    SNACK("Merienda", "🍎"),
    DESSERT("Postre", "🍰"),
    DRINK("Bebida", "🥤")
}
